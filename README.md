# tha-csv-runner

[![CI](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml/badge.svg)](https://github.com/tha-guy-nate/tha-csv-runner/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/tha-guy-nate/tha-csv-runner/graph/badge.svg)](https://codecov.io/gh/tha-guy-nate/tha-csv-runner)
[![PyPI](https://img.shields.io/pypi/v/tha-csv-runner)](https://pypi.org/project/tha-csv-runner/)
[![Python](https://img.shields.io/pypi/pyversions/tha-csv-runner)](https://pypi.org/project/tha-csv-runner/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![wheel size](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpypi.org%2Fpypi%2Ftha-csv-runner%2Fjson&label=wheel%20size&query=%24.urls%5B0%5D.size&suffix=%20B)](https://pypi.org/project/tha-csv-runner/#files)

A Tabular Helper API library that reads and writes CSVs with progress tracking, header validation, and structured per-row errors. Runs a function against every row — with a progress bar, required header validation, and structured error capture per row.

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
2. Iterates every row with a `tqdm` progress bar labelled with `desc` (used as the whole label)
3. Calls your `validator(row)` function — if it raises, that row is marked as an error and processing continues
4. Appends three columns to every row: `row number`, `row status`, and `message`
   - `row number` starts at 2 (row 1 is the header)
   - On success: `row status` and `message` are blank
   - On error: `row status = "error"`, `message = str(exception)`
5. `write()` writes all rows (success and error) to a CSV

## Excel (.xlsx) support

`read()` and `write()` both auto-detect Excel files by extension — pass a path ending in `.xlsx` instead of `.csv` and it's routed through [`openpyxl`](https://openpyxl.readthedocs.io) (a core dependency, no extra install needed) instead of the stdlib `csv` module. Everything else (`required_headers`, `validator`, `column_order`, `sort_by`, `chunk_size`, etc.) works identically across both formats.

```python
runner = ThaCSV()
runner.read("Step 1 of 2", "data.xlsx", ["name", "email"], process)
runner.write("Step 2 of 2", "output.xlsx")
```

Only the modern `.xlsx` (OOXML) format is supported; legacy `.xls` (BIFF) is not, since `openpyxl` itself doesn't read it. Output is plain data only — no cell styling, formulas, or formatting; use `openpyxl` directly if you need that.

### Reading a specific sheet

By default `read()` uses the workbook's active sheet. Pass `sheet=` to target a different one by name or 0-based index — this only applies to `.xlsx` input, passing it for a `.csv` path raises `ValueError`.

```python
runner.read("Step 1 of 2", "data.xlsx", ["name", "email"], process, sheet="Q3 Data")
runner.read("Step 1 of 2", "data.xlsx", ["name", "email"], process, sheet=1)
```

An unknown sheet name or out-of-range index raises `CsvError` listing the available sheets.

### Naming the output sheet

`write()` also takes `sheet=` to name the single tab in a `.xlsx` output file (default is openpyxl's own "Sheet"). Same gating as `read()` — only valid when `output_path` ends in `.xlsx`, raises `ValueError` otherwise. With `chunk_size`, every chunk file gets a sheet with this same name.

```python
runner.write("Step 2 of 2", "output.xlsx", sheet="Q3 Data")
```

## JSON Lines (.jsonl) support

`read()` and `write()` also auto-detect `.jsonl` (newline-delimited JSON) by extension — no extra dependency, it's stdlib `json` under the hood. Each line is one JSON object; everything else (`required_headers`, `validator`, `column_order`, `sort_by`, `chunk_size`, etc.) works the same as CSV/Excel.

```python
runner = ThaCSV()
runner.read("Step 1 of 2", "data.jsonl", ["name", "email"], process)
runner.write("Step 2 of 2", "output.jsonl")
```

`required_headers` is checked against the first line's keys — later lines aren't required to match exactly, so JSONL's per-row schema flexibility isn't lost. Blank lines are skipped on read. `sheet=` doesn't apply here (it's `.xlsx`-only) and raises `ValueError` if passed.

## Suppressing the progress bar

Pass `show_progress=False` to silence the `tqdm` progress bar on both `read()` and `write()` — useful when output is captured to a log file rather than a live terminal, where a redrawing bar just adds noise. `tqdm` is still a hard dependency either way; this only toggles its display.

```python
runner = ThaCSV(show_progress=False)
```

## API

### `ThaCSV`

```python
ThaCSV(
    delimiter=",",        # optional — pass "\t" for TSV, or any single-character separator
    encoding="utf-8",     # optional — pass "cp1252" or "latin-1" for Excel exports
    show_progress=True,   # optional — set False to silence the tqdm progress bar
)
```

### `runner.read()`

```python
runner.read(
    "[1/2]: Reading data",   # progress bar label, used as-is — pass None for "Reading {stem} CSV"
    "data.csv",              # path to input CSV
    ["a", "b"],              # columns that must exist — raises CsvError if missing
    validator=my_func,       # optional: callable(row: dict) -> None
    enrich=True,             # optional: set False to skip row number/status/message columns
    sheet=None,              # optional: .xlsx only — sheet name (str) or 0-based index (int)
)
```

Reads and processes all rows. Returns the rows as a `list[dict]` (same object as `runner.rows`).

The `validator` is designed for **offline, in-memory checks** — field presence, format, business rules. It runs synchronously on each row; don't use it for API calls or database lookups.

When `enrich=False`, validator exceptions are re-raised instead of captured.

### `runner.write()`

```python
runner.write(
    "[2/2]: Writing data",             # progress bar label, used as-is — pass None for "Writing {stem} CSV"
                                       # (with chunk_size, " (i/n)" is appended to it)
    output_path="output.csv",          # optional — auto-named input_processed_TIMESTAMP.csv if omitted
    rows=my_rows,                      # optional — use these rows instead of runner.rows
    sort_by="name",                    # optional — column name, or list of column names
    ascending=True,                    # optional — bool or list of bools matching sort_by
    column_order=["name", "email"],    # optional — listed columns come first, rest follow
    keep=["name", "email"],            # optional — keep only these columns (mutually exclusive with drop)
    drop=["row number"],               # optional — remove these columns (mutually exclusive with keep)
    chunk_size=1000,                   # optional — split output into files of this many rows
    sheet=None,                        # optional: .xlsx only — names the output sheet
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

## Alternatives

This library is intentionally limited in scope — it handles row-by-row processing with error capture and a progress bar, not data analysis or transformation. For heavier workloads:

- [**pandas**](https://pandas.pydata.org) — the standard for CSV processing and in-memory data manipulation; use when you need filtering, grouping, joins, or vectorized operations
- [**polars**](https://pola.rs) — faster alternative to pandas for large files with a cleaner API and lazy evaluation
- [**csv**](https://docs.python.org/3/library/csv.html) (stdlib) — raw CSV reading/writing with no dependencies; sufficient when you don't need progress tracking or structured error capture
- [**openpyxl**](https://openpyxl.readthedocs.io) — use directly when you need cell styling, formulas, multi-sheet output, or other Excel-specific features beyond plain data read/write and single-sheet-by-name/index read
- [**json**](https://docs.python.org/3/library/json.html) (stdlib) — use directly if you need nested/non-tabular JSON structures; this library's `.jsonl` support is flat, one-row-per-line only

Choose this library when you need per-row error capture with `row status` and `message` columns baked in — pandas and polars process data, they don't track individual row failures.

## License

MIT
