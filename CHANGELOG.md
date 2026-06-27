# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
