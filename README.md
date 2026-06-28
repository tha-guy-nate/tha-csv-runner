# tha-csv-runner

[![CI](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml/badge.svg)](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/tha-csv-runner)](https://pypi.org/project/tha-csv-runner/)
[![Python](https://img.shields.io/pypi/pyversions/tha-csv-runner)](https://pypi.org/project/tha-csv-runner/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

A small Python library that runs a function against every row of a CSV — with a progress bar, required header validation, and structured error capture per row.

## Install

```bash
pip install tha-csv-runner
```

## Quick start

```python
from tha_csv_runner import ThaCSV

def process(row: dict) -> None:
    """Raise any exception to mark the row as an error. Return value is ignored."""
    if not row["email"].endswith("@example.com"):
        raise ValueError("invalid email domain")

runner = ThaCSV()

rows = runner.read("Step 1 of 2", "data.csv", ["name", "email"], process)
runner.write("Step 2 of 2", "output.csv")
```

## How it works

1. Opens the CSV and validates that all `required_headers` are present — raises immediately if any are missing
2. Iterates every row with a `tqdm` progress bar labelled with `desc`
3. Calls your `validator(row)` function — if it raises, that row is marked as an error and processing continues
4. Appends three columns to every row: `row number`, `row status`, and `message`
   - `row number` starts at 2 (row 1 is the header)
   - On success: `row status` and `message` are blank
   - On error: `row status = "error"`, `message = str(exception)`
5. `write()` writes all rows (success and error) to a CSV

## API

### `ThaCSV`

```python
ThaCSV(
    delimiter=",",   # optional — pass "\t" for TSV, or any single-character separator
)
```

### `runner.read()`

```python
runner.read(
    "Step 1 of 2",           # progress bar label — pass None to use the filename
    "data.csv",              # path to input CSV
    ["a", "b"],              # columns that must exist — raises CsvError if missing
    validator=my_func,       # optional: callable(row: dict) -> None
    enrich=True,             # optional: set False to skip row number/status/message columns
)
```

Reads and processes all rows. Returns the rows as a `list[dict]` (same object as `runner.rows`).

The `validator` is designed for **offline, in-memory checks** — field presence, format, business rules. It runs synchronously on each row; don't use it for API calls or database lookups.

When `enrich=False`, validator exceptions are re-raised instead of captured.

### `runner.write()`

```python
runner.write(
    "Step 2 of 2",                     # progress bar label — pass None for "Writing {stem} CSV"
    output_path="output.csv",          # optional — auto-named input_processed_TIMESTAMP.csv if omitted
    rows=my_rows,                      # optional — use these rows instead of runner.rows
    sort_by="name",                    # optional — column name, or list of column names
    ascending=True,                    # optional — bool or list of bools matching sort_by
    column_order=["name", "email"],    # optional — listed columns come first, rest follow
    keep=["name", "email"],            # optional — keep only these columns (mutually exclusive with drop)
    drop=["row number"],               # optional — remove these columns (mutually exclusive with keep)
    chunk_size=1000,                   # optional — split output into files of this many rows
)
```

Prints `✅ Done! CSV was written to: {path}` on completion. Override by setting `runner.status_cb = my_fn`.

Returns the `Path` that was written, or a `list[Path]` when `chunk_size` is set.

#### `chunk_size`

When provided, `write()` splits the output into multiple files named `output_001.csv`, `output_002.csv`, etc. and returns a `list[Path]`.

```python
paths = runner.write("Step 2 of 2", "output.csv", chunk_size=1000)
# ["output_001.csv", "output_002.csv", ...]
```

## Planned

- **Encoding support** — `read()` and `write()` currently assume UTF-8; a future release will add an `encoding=` parameter for files exported from Excel (`cp1252`, `latin-1`, etc.)

## Alternatives

This library is intentionally limited in scope — it handles row-by-row processing with error capture and a progress bar, not data analysis or transformation. For heavier workloads:

- [**pandas**](https://pandas.pydata.org) — the standard for CSV processing and in-memory data manipulation; use when you need filtering, grouping, joins, or vectorized operations
- [**polars**](https://pola.rs) — faster alternative to pandas for large files with a cleaner API and lazy evaluation
- [**csv**](https://docs.python.org/3/library/csv.html) (stdlib) — raw CSV reading/writing with no dependencies; sufficient when you don't need progress tracking or structured error capture

Choose this library when you need per-row error capture with `row status` and `message` columns baked in — pandas and polars process data, they don't track individual row failures.

## License

MIT
