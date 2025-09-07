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
    stdin: str = ''
    argv: list[str] = ()
    files: list[File] = ()
    expected_files: list[File] = ()
    expected_stdout: str = ''
    expected_stderr: str = ''


test_cases = (
    Case(
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

    toolbox_main()

    for file in case.expected_files:
        with open(file.filename) as f:
            assert f.read() == file.content

    stdout_mock.seek(0)
    assert case.expected_stdout == stdout_mock.read()
    
    stderr_mock.seek(0)
    assert case.expected_stderr == stderr_mock.read()
