# jinja2-toolbox

A flexible command-line tool for rendering [Jinja2](https://jinja.palletsprojects.com/) templates with data from various file formats. Supports custom filters, data enrichment, and exposes most Jinja2 environment options via the CLI.

## Features

| Feature                                        | Supported |
| ---------------------------------------------- | --------- |
| json data files                                | ✅         |
| yaml data files                                | ✅         |
| toml data files                                | 🔜         |
| ini data files                                 | 🔜         |
| Data from the file                             | ✅         |
| Data from stdin                                | ✅         |
| Output to file                                 | ✅         |
| Output to stdout                               | ✅         |
| Majority of jinja2 configs exposed to the CLI  | ✅         |
| CLI autocompletion                             | 🔜         |
| Custom filters (extensions)                    | ✅         |
| Data access helpers (`.parent`, etc.)          | ✅         |
| Human-readable CLI output errors               | 🔜         |
| Examples                                       | 🔜         |


## Quick Install

Heads up: This isn't on PyPI yet, but you can grab it straight from GitHub. Just run:

```bash
pip install git+https://github.com/dhdhxji/jinja2-toolbox.git
```

## How to Use It

Render a template with a JSON data file:

```bash
python -m jinja2-toolbox <template.jinja2> --data <data.json> [--output <out.txt>]
```

You can tweak most Jinja2 options by adding `--j2_<option>` flags (like `--j2_trim_blocks`). See the help for more details:

```bash
python -m jinja2-toolbox --help
```

### Example

```bash
python -m jinja2-toolbox \
    examples/simple-json/template.jinja2 \
    --data examples/simple-json/data.json \
    --output result.txt \
    --j2_trim_blocks \
    --j2_lstrip_blocks \
    --j2_keep_trailing_newline
```


## Data Enrichment

The toolbox provides a data enrichment feature that adds convenient helpers to your data, such as `.parent` references for traversing nested structures. This is useful for advanced Jinja2 templates that need to access parent or sibling data.

- Enable enrichment by passing the `--enrich` flag:

    ```bash
    python -m jinja2-toolbox <template.jinja2> --data <data.json> --enrich
    ```

- You can also use the `enrich` filter in your Jinja2 templates to enrich any value on demand:

    ```jinja2
    {{ some_value | enrich }}
    ```

### Corner Case: Data with a "parent" Member

If your input data already contains a key or attribute named `parent`, enabling enrichment will overwrite it with the enrichment helper. You can still access the original value in templates with `enriched_data.deplete.parent` or just `enriched_data['parent']`.

## Custom Filters & Extensions

You can add your own filters or extensions by placing Python files in your project and using the `--j2_extensions` argument.

See `examples/custom-extensions/` for a sample.
