import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from .json_provider import JsonProvider
from .data_proxies import wrap
import inspect
import sys

DATA_PROVIDERS = {
    'json': JsonProvider
}


def deduce_data_type(filename: Path, override: str) -> str:
    if override:
        return override

    extension = Path(filename).name.split('.')[-1]

    if extension not in DATA_PROVIDERS.keys():
        raise RuntimeError(
            f'Can\'t determine the input data file format {str(filename)}')
    else:
        return extension


def read_data(datapath: str, data_format: str) -> dict:
    provider = DATA_PROVIDERS[deduce_data_type(datapath, data_format)]()
    if datapath == '-':
        return provider.load(sys.stdin)
    else:
        with Path(datapath).open() as f:
            return provider.load(f)


def add_j2_cli_args(ap: argparse.ArgumentParser) -> None:
    forward_args_help = {
        'block_start_string': 'The string marking the beginning of a block.',
        'block_end_string': 'The string marking the end of a block.',
        'variable_start_string': 'The string marking the beginning of a print statement.',
        'variable_end_string': 'The string marking the end of a print statement.',
        'comment_start_string': 'The string marking the beginning of a comment.',
        'comment_end_string': 'The string marking the end of a comment.',
        'line_statement_prefix': 'The string marking the beginning of a block.',
        'line_statement_prefix': 'If given and a string, this will be used as prefix for line based '
        'statements.  See also :ref:`line-statements`.',
        'line_comment_prefix': 'If given and a string, this will be used as prefix for line based '
        'comments.  See also :ref:`line-statements`.',
        'newline_sequence': r'The sequence that starts a newline.  Must be one of ``\'\r\'``, '
        r'``\'\n\'`` or ``\'\r\n\'``.  The default is ``\'\n\'`` which is a '
        r'useful default for Linux and OS X systems as well as web '
        r'applications.',
        'cache_size': 'The size of the cache.  Per default this is ``400`` which means '
        'that if more than 400 templates are loaded the loader will clean '
        'out the least recently used template.  If the cache size is set to '
        '``0`` templates are recompiled all the time, if the cache size is '
        '``-1`` the cache will not be cleaned.',

    }

    true_false_params_help = {
        'trim_blocks': 'If this is set to ``True`` the first newline after a block is '
        'removed (block, not variable tag!).',
        'lstrip_blocks': 'If this is set to ``True`` leading spaces and tabs are stripped '
        'from the start of a line to a block.',
        'keep_trailing_newline': 'Preserve the trailing newline when rendering templates. '
        'The default is ``False``, which causes a single newline, '
        'if present, to be stripped from the end of the template.',
        'autoescape': 'If set to ``True`` the XML/HTML autoescaping feature is enabled by '
        'default.  For more details about autoescaping see '
        ':class:`~markupsafe.Markup`.  As of Jinja 2.4 this can also '
        'be a callable that is passed the template name and has to '
        'return ``True`` or ``False`` depending on autoescape should be '
        'enabled by default.',
        'auto_reload': 'Some loaders load templates from locations where the template '
        'sources may change (ie: file system or database).  If '
        '``auto_reload`` is set to ``True`` (default) every time a template is '
        'requested the loader checks if the source changed and if yes, it '
        'will reload the template.  For higher performance it\'s possible to '
        'disable that.',
        'optimized': 'should the optimizer be enabled?',
    }

    refl_args = inspect.signature(Environment.__init__).parameters

    for name, param in refl_args.items():
        if name in forward_args_help:
            ap.add_argument(
                f'--j2_{name}', default=param.default, help=forward_args_help[name])
        elif name in true_false_params_help:
            ap.add_argument(f'--j2_{name}',
                            action='store_true',
                            default=param.default,
                            help=true_false_params_help[name])
        elif name == 'extensions':
            ap.add_argument(
                '--j2_extensions',
                default=[],
                nargs='+',
                help='List of Jinja extensions to use.  This can either be import paths '
                'as strings or extension classes.  For more information have a '
                'look at :ref:`the extensions documentation <jinja-extensions>`.')

    # TODO:
    # 'undefined'
    # 'finalize'
    # 'loader'
    # 'bytecode_cache'
    # 'enable_async'

    pass


def main() -> None:
    ap = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('template', help='Jinja2 template file path.')
    ap.add_argument(
        '--data',
        default='-',
        help=f'Template data file path. Supported formats: {", ".join(DATA_PROVIDERS.keys())}. '
        '"-" to read the data from stdin.')
    ap.add_argument('--output', default='-',
                    help='Generated output file path. stdout by default')
    ap.add_argument(
        '--data-format', choices=tuple(DATA_PROVIDERS.keys()), help='Override automatically-detected data format')
    ap.add_argument('--enrich', action='store_true',
                    help='Automatically enrich the input data')

    add_j2_cli_args(ap)

    args = ap.parse_args()

    if args.data == '-' and not args.data_format:
        raise RuntimeError(
            f'The --data-format option must be specified when reading the data from the stdin')

    template_context = read_data(args.data, args.data_format)
    if args.enrich:
        template_context = wrap(template_context)

    j2_args = {
        key.lstrip('j2_'): value
        for key, value in vars(args).items()
        if key.startswith('j2_')
    }

    env = Environment(
        loader=FileSystemLoader('.'),
        undefined=StrictUndefined,
        **j2_args
    )

    env.filters['enrich'] = wrap

    template = env.get_template(args.template)

    if args.output is None or args.output == '-':
        sys.stdout.write(template.render(**template_context))
    else:
        with Path(args.output).open('w') as f:
            f.write(template.render(**template_context))
