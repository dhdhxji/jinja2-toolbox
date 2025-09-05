import argparse
from pathlib import Path
from .json_provider import JsonProvider
from jinja2 import Environment, FileSystemLoader, StrictUndefined


DATA_PROVIDERS = {
    'json': JsonProvider
}

def deduce_data_type(filename: Path, _args: argparse.Namespace) -> str:
    extension = filename.name.split('.')[-1]

    if extension not in DATA_PROVIDERS.keys():
        raise RuntimeError(f'Can\'t determine the input data file format {str(filename)}')
    else:
        return extension

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('datafile', help=f'Template data file path. Supported formats: {", ".join(DATA_PROVIDERS.keys())}')
    ap.add_argument('templatefile', help='Jinja2 template file path.')
    ap.add_argument('outputfile', help='Generated output file path. stdout by default')

    args = ap.parse_args()

    data_file: Path = Path(args.datafile)
    template_file: Path = Path(args.templatefile)
    output_file: Path = Path(args.outputfile)

    data_provider = DATA_PROVIDERS[deduce_data_type(data_file, args)]()
    with data_file.open() as f:
        template_context = data_provider.load(f)

    env = Environment(
        loader=FileSystemLoader('.'),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True
    )

    template = env.get_template(str(template_file))

    with output_file.open('w') as f:
        f.write(template.render(**template_context))