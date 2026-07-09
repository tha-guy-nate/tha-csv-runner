# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.1] - 2026-07-09
### Fixed
- `write()` built the output column header from `rows[0]` only, so a narrow first row (e.g. an errored/no-match row from an upstream fan-out step) silently dropped columns that later rows carried, for every row in the file. `keep=` was affected even more sharply, discarding a keep-listed column outright if it was absent from `rows[0]`. The header is now built from the union of all rows' keys, preserving first-seen order; missing values still write blank per row, matching the existing per-row write behavior. Applies to `.csv`, `.xlsx`, and `.jsonl` output alike since they share the same column-resolution step.

## [0.4.0] - 2026-07-05
### Added
- `.xlsx` read/write support, auto-detected by file extension on `read()`/`write()`, powered by `openpyxl` (core dependency, no extra install needed). Legacy `.xls` is not supported since `openpyxl` itself doesn't read that format.
- `sheet=` parameter on `read()` (name or 0-based index) to target a specific worksheet in a `.xlsx` file; defaults to the active sheet. Raises `CsvError` for an unknown name or out-of-range index, and `ValueError` if passed while reading a `.csv` path.
- `sheet=` parameter on `write()` to name the single output sheet in a `.xlsx` file (applies per-file when `chunk_size` is set). Raises `ValueError` if passed while writing a `.csv` path.
- `.jsonl` read/write support, auto-detected by file extension on `read()`/`write()`. No new dependency (stdlib `json`). Blank lines are skipped on read; `required_headers` is checked against the first line's keys only. `sheet=` raises `ValueError` if passed for a `.jsonl` path.
- `show_progress` parameter on `ThaCSV(show_progress=True)` to silence the `tqdm` progress bar on `read()`/`write()`. `tqdm` remains a hard dependency either way — this only toggles display, useful when output is captured to a log file rather than a live terminal.
### Fixed
- Version drift: `__init__.py`'s `__version__` had been stuck at 0.3.4 while `pyproject.toml` had already moved to 0.3.5.

## [0.3.5] - 2026-07-04
### Fixed
- Added missing `keywords` to `pyproject.toml` (PyPI search had none) and fixed the README's opening line to lead with the family-standard "A Tabular Helper API library that..." description instead of a divergent one-off wording.

## [0.3.4] - 2026-07-04
### Fixed
- Test coverage gaps: added tests for the empty-file `CsvError` and for a sort-key tie (`compare` returning `0`). Excluded `__main__.py` from coverage (CLI entrypoint, not exercised by pytest). Coverage is now 100%.

## [0.3.3] - 2026-06-28
### Added
- `encoding` parameter on `ThaCSV(encoding="utf-8")` — pass `"cp1252"` or `"latin-1"` for files exported from Excel; defaults to `"utf-8"` for full backwards compatibility.

## [0.3.2] - 2026-06-28
### Added
- `delimiter` parameter on `ThaCSV(delimiter=",")` — pass `"\t"` for TSV or any single-character separator; defaults to `","` for full backwards compatibility.

## [0.3.1] - 2026-06-27
### Removed
- `ConfigError` back-compat alias — use `CsvError` directly.

## [0.3.0] - 2026-06-27
### Added
- `CsvError` as the new canonical exception class; `ConfigError` kept as a back-compat alias.
### Changed
- Enabled mypy strict mode for comprehensive type checking.

## [0.2.7] - 2026-06-16
### Added
- Python 3.13 and 3.14 classifier and CI support.
- Alternatives section to README.
### Changed
- Standardized CI and publish workflows; switched to `uv publish`.
- Bumped minimum dev dependency floors (pytest ≥ 9.1.0, ruff ≥ 0.15.17, mypy ≥ 2.1.0).
- Added Dependabot for automated dependency and action updates.

## [0.2.6] - 2026-05-16
### Added
- `py.typed` marker for PEP 561 typed package support.

## [0.2.5] - 2026-05-15
### Changed
- Combined step description with Reading/Writing tqdm label for cleaner output.
- Fixed `status_cb` emoji rendering.

## [0.2.4] - 2026-05-15
### Added
- `rows=` parameter to `write()` to pass data without a prior `read()`.
- `status_cb` hook for customizing completion messages.
- Default tqdm labels when `desc` is `None`.

## [0.2.3] - 2026-05-15
### Added
- `chunk_size` parameter to `write()` for splitting output into multiple files.
- Terminal width cap for tqdm progress bars.
### Fixed
- Row number off-by-one in enriched rows.

## [0.2.2] - 2026-05-15
### Changed
- `read()` now returns the list of rows.
- Renamed `processor` parameter to `validator` in `read()`.

## [0.2.1] - 2026-05-12
### Removed
- `sample` parameter from `read()`.

## [0.2.0] - 2026-05-11
### Added
- `ThaCSV` class replacing the old function-based API.
- `write()` method with tqdm progress bar and sort/filter/column-order support.
- `enrich` parameter to `read()` to control row metadata injection.
### Removed
- CLI entry point — library is script-usage only.

## [0.1.0] - 2026-05-11
### Added
- Initial release with CSV reading, header validation, and per-row error handling.
