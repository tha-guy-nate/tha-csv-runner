from pathlib import Path

from click.testing import CliRunner

from tha_csv_runner.cli import main


def test_run_basic(simple_csv: Path) -> None:
    result = CliRunner().invoke(main, [
        "run",
        "--input", str(simple_csv),
        "--processor", "tests.fixtures.processors:noop",
        "--header", "name",
        "--header", "email",
    ])
    assert result.exit_code == 0, result.output


def test_run_sample(simple_csv: Path) -> None:
    result = CliRunner().invoke(main, [
        "run",
        "--input", str(simple_csv),
        "--processor", "tests.fixtures.processors:noop",
        "--sample", "1",
    ])
    assert result.exit_code == 0


def test_run_missing_input() -> None:
    result = CliRunner().invoke(main, [
        "run",
        "--input", "nope.csv",
        "--processor", "tests.fixtures.processors:noop",
    ])
    assert result.exit_code != 0


def test_run_bad_processor_spec(simple_csv: Path) -> None:
    result = CliRunner().invoke(main, [
        "run",
        "--input", str(simple_csv),
        "--processor", "no_colon_here",
    ])
    assert result.exit_code != 0


def test_run_missing_header_error(simple_csv: Path) -> None:
    result = CliRunner().invoke(main, [
        "run",
        "--input", str(simple_csv),
        "--processor", "tests.fixtures.processors:noop",
        "--header", "phone",
    ])
    assert result.exit_code != 0
    assert "Missing required headers" in result.output
