# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2026-10-02
### Changed
- Dependencies are now pinned to exact versions (`==`) instead of `>=` floors, and updated to the latest releases: `tqdm==4.70.1`, `openpyxl==3.1.5`. Dev dependencies are pinned the same way (`pytest==9.1.1`, `ruff==0.16.10`, `mypy==2.4.0`, `deptry==0.25.1`, `pip-audit==2.10.1`, `pytest-cov==7.1.0`).

## [0.6.0] - 2026-09-26
### Added
- `read()` and `write()` take a keyword-only `label` that replaces the default progress text (`"Reading {stem} CSV"` / `"Writing {stem} CSV"`). `desc="[1/7]", label="Loading people"` renders `"[1/7]: Loading people"`. With `chunk_size`, `" (i/n)"` is appended to the text.

### Changed
- **Reverts part of 0.5.0:** `desc` is a step prefix again, asserted at the front (`desc="[1/7]"` → `"[1/7]: Reading {stem} CSV"`), instead of the whole label. Callers that adopted 0.5.0 by passing full text (`"[1/7]: Reading data"`) will now get the default text appended; pass `"[1/7]"` and, if the wording should differ, `label="Reading data"`. The shorter bar and the blank line before the Done message from 0.5.0 are unchanged.
- Chunked writes render `"<desc>: <text> (i/n)"` (0.5.0 rendered `"<desc> (i/n)"`, dropping the text).
- `__version__` is now read from the installed package metadata (`importlib.metadata`) instead of a hardcoded string, so `pyproject.toml` is the only place the version is bumped.

## [0.5.0] - 2026-09-26
### Changed
- **Breaking:** the `desc` argument to `read()` and `write()` is now the whole progress-bar label, used verbatim, instead of a prefix that had `": Reading {stem} CSV"` / `": Writing {stem} CSV"` appended. Callers that passed a step marker like `"[1/7]"` should now pass the full text (e.g. `"[1/7]: Reading data"`). `desc=None` still gives the default `"Reading {stem} CSV"` / `"Writing {stem} CSV"`. With `chunk_size`, `" (i/n)"` is appended to `desc` so chunks stay distinguishable (previously the chunk index only appeared when `desc` was truthy, and `desc=""` was treated like `None`).
- Progress bars no longer show elapsed time and rate (`[00:00<00:00, 27594.11it/s]`); they now render as `label: 100%|####| 3/3`. On a long label the extra fields pushed the line past the 85-column cap and the terminal cut it off mid-field. Applies to read, write, xlsx, jsonl, and chunked writes.
- The `✅ Done! CSV was written to: ...` message sent to `status_cb` now starts with a blank line (`"\n"`) when a progress bar was shown, separating it from the bar. No blank line is added when `show_progress=False` or there were no rows to write (no bar is printed in that case).

## [0.4.2] - 2026-08-21
### Fixed
- Re-locked transitive `pip` (pulled in via `deptry` -> `pip-api`) from `26.1.2` to `26.2.1`, resolving a known CVE (PYSEC-2026-3721) flagged by `pip-audit`.

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
