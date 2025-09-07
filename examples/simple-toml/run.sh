#!/bin/sh

export export PYTHONPATH="$(pwd)/../../:$PYTHONPATH"
python -m jinja2_toolbox \
    template.jinja2 \
    --data data.toml \
    --output out.txt \
    --j2_trim_blocks \
    --j2_lstrip_blocks \
    --j2_keep_trailing_newline
