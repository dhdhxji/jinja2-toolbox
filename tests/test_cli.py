import io
from pyfakefs.fake_filesystem import FakeFilesystem
from dataclasses import dataclass
from jinja2_toolbox.cli import main as toolbox_main
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
        'Data from stdin, output to stdout, missing data format override',
        argv=[
            'template.jinja2',
            '--data', '-',
        ],
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
            File('template.jinja2', '{{ foo.bar }}{{ foo.parent is mapping }}'),
        ],
        expected_stdout='1True',
    ),
)


@pytest.mark.parametrize('case', test_cases)
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
