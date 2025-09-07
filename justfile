
all: test

dev-deps:
    poetry install --with dev

test: dev-deps
    pytest --cov=jinja2_toolbox --cov-report=term-missing 

build: test dev-deps
    poetry build