#!/bin/sh

export export PYTHONPATH="$(pwd)/../../:$PYTHONPATH"
python -m jinja2-toolbox \
    data.json \
    template.jinja2 \
    out.txt \
    --enrich \
    --j2_trim_blocks \
    --j2_lstrip_blocks \
    --j2_keep_trailing_newline
