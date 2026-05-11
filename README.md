# tha-csv-runner

[![CI](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml/badge.svg)](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml)

A small Python library that runs a function against every row of a CSV — with a progress bar, required header validation, and structured error capture per row.

## Install

```bash
pip install git+https://github.com/tha-guy-nate/tha-csv-runner.git
```

## Quick start

```python
from tha_csv_runner import Runner

def process(row: dict) -> None:
    """Raise any exception to mark the row as an error. Return value is ignored."""
    if not row["email"].endswith("@example.com"):
        raise ValueError("invalid email domain")

runner = Runner(
    input_path="data.csv",
    required_headers=["name", "email"],
    processor=process,
)
runner.run()
runner.write("output.csv")
```

## How it works

1. Opens the CSV and validates that all `required_headers` are present — raises immediately if any are missing
2. Iterates every row with a `tqdm` progress bar
3. Calls your `processor(row)` function — if it raises, that row is marked as an error and processing continues
4. Appends three columns to every row: `row_number`, `row_status`, and `message`
   - On success: `row_status` and `message` are blank
   - On error: `row_status = "error"`, `message = str(exception)`
5. `write()` writes all rows (success and error) to a CSV

## API

### `Runner`

```python
Runner(
    input_path="data.csv",       # path to input CSV
    required_headers=["a", "b"], # columns that must exist — raises ConfigError if missing
    processor=my_func,           # optional: callable(row: dict) -> None
    sample=100,                  # optional: process only the first N rows
)
```

### `runner.run()`

Reads and processes all rows. Results are stored in `runner.rows` as a list of dicts.

### `runner.write()`

```python
runner.write(
    output_path="output.csv",          # optional — auto-named input_processed_TIMESTAMP.csv if omitted
    sort_by="name",                    # optional — column name, or list of column names
    ascending=True,                    # optional — bool or list of bools matching sort_by
    column_order=["name", "email"],    # optional — listed columns come first, rest follow
    keep=["name", "email"],            # optional — keep only these columns (mutually exclusive with drop)
    drop=["row_number"],               # optional — remove these columns (mutually exclusive with keep)
)
```

Returns the `Path` that was written.

## CLI

```bash
tha-csv-runner run \
    --input data.csv \
    --processor my_module:process_row \
    --header name \
    --header email \
    --sample 100
```

`--processor` uses the `module:function` convention. `--header` is repeatable. All flags are optional except `--input`.

## License

MIT
