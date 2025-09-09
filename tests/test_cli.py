import io
from pyfakefs.fake_filesystem import FakeFilesystem
from dataclasses import dataclass
from jinja2_toolbox.cli import main as toolbox_main
from jinja2_toolbox.data_proxies import *
import pytest


@dataclass
class File:
    filename: str
    content: str


@dataclass
class Case:
    title: str
    stdin: str = ''
    argv: list[str] = ()
    files: list[File] = ()
    expected_files: list[File] = ()
    expected_stdout: str = ''
    expected_stderr: str = ''

    # TODO: Expect specific exception
    expected_exception: bool = False


test_cases = (
    Case(
        'Basic file-to-file rendering',
        argv=[
            'template.jinja2',
            '--data', 'data.json',
            '--output', 'out.txt',
            '--j2_trim_blocks',
            '--j2_lstrip_blocks',
            '--j2_keep_trailing_newline'
        ],
        files=(
            File('data.json', '\n'.join((
                '{',
                '    "title": "test",',
                '    "array": [1, 2, 3]',
                '}',
            ))),
            File('template.jinja2', '\n'.join((
                'Title is {{ title }}',
                '',
                'Array values:',
                '{% for i in array %}',
                ' - {{ i }}',
                '{% endfor %}',
                '',
            ))),
        ),
        expected_files=(
            File('out.txt', '\n'.join((
                'Title is test',
                '',
                'Array values:',
                ' - 1',
                ' - 2',
                ' - 3',
                '',
            ))),
        )
    ),
    Case(
        'Invalid data file extension',
        argv=[
            'template.jinja2',
            '--data', 'data.unknown',
        ],
        files=[
            File('template.jinja2', 'Foo: {{ foo }}\n'),
            File('data.unknown', '{"foo": "bar"}'),
        ],
        expected_exception=True
    ),
    Case(
        'Accessing None should raise exception',
        argv=['template.jinja2', '--data-format', 'json'],
        stdin='{"foo": "bar"}',
        files=[
            File('template.jinja2', 'Foo: {{ fooo }}\n'),
        ],
        expected_exception=True
    ),
    Case(
        'Data from stdin, output to stdout, missing data format override',
        argv=['template.jinja2'],
        stdin='{"foo": "bar"}',
        files=[
            File('template.jinja2', 'Foo: {{ foo }}\n'),
        ],
        expected_exception=True
    ),
    Case(
        'Data from stdin, output to stdout, data format override',
        argv=[
            'template.jinja2',
            '--data', 'data.json',
            '--data-format', 'json',
        ],
        files=[
            File('data.json', '{"x": 42}'),
            File('template.jinja2', '{{ x }}'),
        ],
        expected_stdout='42',
    ),
    Case(
        'Enrich flag',
        argv=[
            'template.jinja2',
            '--data', 'data.json',
            '--enrich',
        ],
        files=[
            File('data.json', '{"foo": {"bar": 1}}'),
            File('template.jinja2',
                 '{{ foo.bar }}{{ foo.parent is mapping }}'),
        ],
        expected_stdout='1True',
    ),
    Case(
        'Depleting the enriched mapping data',
        argv=[
            'template.jinja2',
            '--data', 'data.json',
            '--enrich',
        ],
        files=[
            File('data.json', '{"foo": {"bar": 1}}'),
            File('template.jinja2',
                 '{{ foo.bar }}{{ foo.parent.depleted is mapping }}'),
        ],
        expected_stdout='1True',
    ),
    Case(
        'Depleting the enriched array data',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": [1, 2, 3]}',
        files=[
            File('template.jinja2',
                 '{{ foo.0.depleted }}{{ foo.0.parent.depleted is sequence }}'),
        ],
        expected_stdout='1True',
    ),
    Case(
        'Enriched proxy size',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2',
                 '{{ foo | length }} {{ foo.bar | length }}'),
        ],
        expected_stdout='1 3',
    ),
    Case(
        'Enriched proxy iteration',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2',
                 '{% for i in foo.bar %}{{ i }} {% endfor %}{% for i in foo %}{{ i }} {% endfor %}'),
        ],
        expected_stdout='1 2 3 bar ',
    ),
    Case(
        'Enriched proxy as string',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo}} {{foo.bar}}'),
        ],
        expected_stdout="{'bar': [1, 2, 3]} [1, 2, 3]",
    ),
    Case(
        'Proxy mapping is recognised as mapping',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo is mapping}}'),
        ],
        expected_stdout="True",
    ),
    Case(
        'Proxy iterable is recognised as iterable',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": [1, 2, 3] }',
        files=[
            File('template.jinja2', '{{foo is sequence}}'),
        ],
        expected_stdout="True",
    ),
    Case(
        'Accessing proxy mapping parent',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo.parent}}'),
        ],
        expected_stdout='{\'foo\': {\'bar\': [1, 2, 3]}}',
    ),
    Case(
        'Accessing proxy list parent',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo.bar.parent}}'),
        ],
        expected_stdout='{\'bar\': [1, 2, 3]}',
    ),
    Case(
        'Accessing proxy plain value parent',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo.bar.0.parent}}'),
        ],
        expected_stdout='[1, 2, 3]',
    ),


    Case(
        'Accessing proxy mapping member',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo.bar}}'),
        ],
        expected_stdout='[1, 2, 3]',
    ),
    Case(
        'Accessing proxy list member',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": {"bar": [1, 2, 3]} }',
        files=[
            File('template.jinja2', '{{foo.bar | length}}'),
        ],
        expected_stdout='3',
    ),
    Case(
        'Accessing proxy plain value member',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('template.jinja2', '{{foo | length}}'),
        ],
        expected_stdout='3',
    ),
    Case(
        'Private rich proxy values must not be accessed',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('template.jinja2', '{{foo.value}}'),
        ],
        expected_exception=True
    ),
    Case(
        'Deplete filter should not work on non-proxy values',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('template.jinja2', '{{foo | deplete}}'),
        ],
        expected_exception=True
    ),
    Case(
        'Check rich proxy value equivalence',
        argv=[
            'template.jinja2',
            '--data-format', 'json',
            '--enrich',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('template.jinja2', '{{foo | deplete == foo}}'),
        ],
        expected_stdout="True",
    ),
    Case(
        'Custom template dir',
        argv=[
            'template.jinja2',
            '--template-dir', '/some/non/standard/path/',
            '--data-format', 'json',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('/some/non/standard/path/template.jinja2', '{{foo}}'),
        ],
        expected_stdout="bar",
    ),
    Case(
        'Non-existent custom template dir',
        argv=[
            'template.jinja2',
            '--template-dir', '/some/non/existing/path/',
            '--data-format', 'json',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('/some/non/standard/path/template.jinja2', '{{foo}}'),
        ],
        expected_exception=True
    ),
    Case(
        'Non-dir custom template dir',
        argv=[
            'template.jinja2',
            '--template-dir', '/some/non/existing/path/',
            '--data-format', 'json',
        ],
        stdin='{"foo": "bar"}',
        files=[
            File('/some/non/existing/path', '{{foo}}'),
        ],
        expected_exception=True
    ),

    # Format support tests
    Case(
        'YAML .yaml file input',
        argv=[
            'template.jinja2',
            '--data', 'data.yaml',
        ],
        files=[
            File('data.yaml', 'foo: 123\nbar: [a, b, c]'),
            File('template.jinja2', 'Foo={{ foo }} Bar={{ bar|join(",") }}'),
        ],
        expected_stdout='Foo=123 Bar=a,b,c',
    ),
    Case(
        'YAML .yml file input',
        argv=[
            'template.jinja2',
            '--data', 'data.yaml',
        ],
        files=[
            File('data.yaml', 'foo: 123\nbar: [a, b, c]'),
            File('template.jinja2', 'Foo={{ foo }} Bar={{ bar|join(",") }}'),
        ],
        expected_stdout='Foo=123 Bar=a,b,c',
    ),
    Case(
        'YAML from stdin',
        argv=[
            'template.jinja2',
            '--data', '-',
            '--data-format', 'yaml',
        ],
        stdin='foo: hello\nbar: [1,2]',
        files=[
            File('template.jinja2', '{{ foo }}-{{ bar|sum }}'),
        ],
        expected_stdout='hello-3',
    ),
    Case(
        'YAML from stdin',
        argv=[
            'template.jinja2',
            '--data', '-',
            '--data-format', 'yml',
        ],
        stdin='foo: hello\nbar: [1,2]',
        files=[
            File('template.jinja2', '{{ foo }}-{{ bar|sum }}'),
        ],
        expected_stdout='hello-3',
    ),
    Case(
        'TOML file input',
        argv=[
            'template.jinja2',
            '--data', 'data.toml',
        ],
        files=[
            File('data.toml', 'foo = 123\nbar = ["a", "b", "c"]'),
            File('template.jinja2', 'Foo={{ foo }} Bar={{ bar|join(",") }}'),
        ],
        expected_stdout='Foo=123 Bar=a,b,c',
    ),
    Case(
        'TOML from stdin',
        argv=[
            'template.jinja2',
            '--data', '-',
            '--data-format', 'toml',
        ],
        stdin='foo = "hello"\nbar = [1,2]',
        files=[
            File('template.jinja2', '{{ foo }}-{{ bar|sum }}'),
        ],
        expected_stdout='hello-3',
    ),
)


@pytest.mark.parametrize('case', test_cases, ids=map(lambda c: c.title, test_cases))
def test_format_template(fs: FakeFilesystem, monkeypatch, case: Case) -> None:
    stdout_mock = io.StringIO()
    stderr_mock = io.StringIO()
    stdin_mock = io.StringIO(case.stdin)

    monkeypatch.setattr('sys.stdin', stdin_mock)
    monkeypatch.setattr('sys.stdout', stdout_mock)
    monkeypatch.setattr('sys.stderr', stderr_mock)
    monkeypatch.setattr('sys.argv', list(['jinja2-toolbox', *case.argv]))

    for file in case.files:
        fs.create_file(file.filename, contents=file.content)

    error = None
    try:
        toolbox_main()
    except Exception as e:
        error = e

    if case.expected_exception:
        assert error is not None
    else:
        assert error is None

    for file in case.expected_files:
        with open(file.filename) as f:
            assert f.read() == file.content

    stderr_mock.seek(0)
    assert case.expected_stderr == stderr_mock.read()

    stdout_mock.seek(0)
    assert case.expected_stdout == stdout_mock.read()


def test_data_proxy_repr():
    value_proxy = enrich(123, None)
    assert repr(value_proxy) == '123'

    array_proxy = enrich([1, 2, 3], None)
    assert repr(array_proxy) == '[1, 2, 3]'

    mapping_proxy = enrich({1: 2, 3: 4}, None)
    assert repr(mapping_proxy) == '{1: 2, 3: 4}'


def test_double_proxy():
    value_proxy = enrich(123, None)
    value_proxy = enrich(value_proxy)
    assert type(deplete(value_proxy)) is int


def test_enrich_unsupported_type():
    with pytest.raises(RuntimeError) as e_info:
        enrich(io.StringIO())
    assert e_info.value.args[0] == f'Unsupported data type {type(io.StringIO())} for wrapping'
