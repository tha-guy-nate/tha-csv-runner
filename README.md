# tha-csv-runner

[![CI](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml/badge.svg)](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml)

A small Python library that runs a function against every row of a CSV — with a progress bar, required header validation, and structured error capture per row.

## Install

```bash
pip install tha-csv-runner
```

## Quick start

```python
from tha_csv_runner import Runner

def process(row: dict) -> None:
    """Raise any exception to mark the row as an error. Return value is ignored."""
    if not row["email"].endswith("@example.com"):
        raise ValueError("invalid email domain")

runner = Runner(
    "Step 1 of 1",
    "data.csv",
    ["name", "email"],
    process,
)
runner.run()
runner.write("output.csv")
```

## How it works

1. Opens the CSV and validates that all `required_headers` are present — raises immediately if any are missing
2. Iterates every row with a `tqdm` progress bar labelled with `desc`
3. Calls your `processor(row)` function — if it raises, that row is marked as an error and processing continues
4. Appends three columns to every row: `row number`, `row status`, and `message`
   - On success: `row status` and `message` are blank
   - On error: `row status = "error"`, `message = str(exception)`
5. `write()` writes all rows (success and error) to a CSV

## API

### `Runner`

```python
Runner(
    "Step 2 of 10",          # progress bar label — pass None to use the filename
    "data.csv",              # path to input CSV
    ["a", "b"],              # columns that must exist — raises ConfigError if missing
    processor=my_func,       # optional: callable(row: dict) -> None
    sample=100,              # optional: process only the first N rows
    enrich=True,             # optional: set False to skip row number/status/message columns
)
```

When `enrich=False`, processor exceptions are re-raised instead of captured.

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
    drop=["row number"],               # optional — remove these columns (mutually exclusive with keep)
)
```

Returns the `Path` that was written.

## License

MIT
