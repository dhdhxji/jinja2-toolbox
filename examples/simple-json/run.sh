#!/bin/sh

export export PYTHONPATH="$(pwd)/../../:$PYTHONPATH"
python -m jinja2-toolbox data.json template.jinja2 out.txt
