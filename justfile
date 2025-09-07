
all: test

dev-deps:
    poetry install --with dev

test: dev-deps
    pytest -vv --cov=jinja2_toolbox --cov-report=term-missing --cov-report=xml

build: test dev-deps
    poetry build