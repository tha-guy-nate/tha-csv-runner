import csv
from pathlib import Path

import pytest

from tha_csv_runner import Runner
from tha_csv_runner.errors import ConfigError


def noop(row: dict) -> None:
    pass


def fail_on_bob(row: dict) -> None:
    if row["name"] == "Bob":
        raise ValueError("Bob is not allowed")


def test_happy_path(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["id", "name", "email"], processor=noop)
    runner.run()
    assert len(runner.rows) == 3
    assert all(r["row_status"] == "" for r in runner.rows)


def test_row_number_injected(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    assert runner.rows[0]["row_number"] == 1
    assert runner.rows[2]["row_number"] == 3


def test_message_and_status_columns_present(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    for row in runner.rows:
        assert "row_number" in row
        assert "row_status" in row
        assert "message" in row


def test_error_row_captured(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, processor=fail_on_bob, required_headers=["name"])
    runner.run()

    errors = [r for r in runner.rows if r["row_status"] == "error"]
    success = [r for r in runner.rows if r["row_status"] == ""]

    assert len(errors) == 1
    assert errors[0]["name"] == "Bob"
    assert "Bob is not allowed" in errors[0]["message"]
    assert len(success) == 2


def test_missing_required_header_raises(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["id", "phone"])
    with pytest.raises(ConfigError, match="Missing required headers"):
        runner.run()


def test_sample_limits_rows(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["name"], sample=2)
    runner.run()
    assert len(runner.rows) == 2


def test_original_columns_preserved(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["name", "email"])
    runner.run()
    assert runner.rows[0]["name"] == "Alice"
    assert runner.rows[0]["email"] == "alice@example.com"


def test_write_creates_file(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out)
    assert out.exists()


def test_write_contains_all_rows(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out)
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 3


def test_write_includes_enriched_columns(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out)
    rows = list(csv.DictReader(out.open()))
    assert "row_number" in rows[0]
    assert "row_status" in rows[0]
    assert "message" in rows[0]


def test_write_auto_names_file(
    simple_csv: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    out = runner.write()
    assert out.name.startswith("simple_processed_")
    assert out.exists()


def test_write_before_run_raises(simple_csv: Path) -> None:
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    with pytest.raises(RuntimeError, match=r"call run\(\)"):
        runner.write()


def test_write_sort_by_single(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out, sort_by="name", ascending=False)
    rows = list(csv.DictReader(out.open()))
    names = [r["name"] for r in rows]
    assert names == sorted(names, reverse=True)


def test_write_sort_by_multiple(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out, sort_by=["name", "email"], ascending=[True, False])
    rows = list(csv.DictReader(out.open()))
    assert len(rows) == 3


def test_write_keep(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out, keep=["name", "email"])
    rows = list(csv.DictReader(out.open()))
    assert list(rows[0].keys()) == ["name", "email"]


def test_write_drop(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out, drop=["row_number", "row_status", "message"])
    rows = list(csv.DictReader(out.open()))
    assert "row_number" not in rows[0]
    assert "name" in rows[0]


def test_write_keep_and_drop_raises(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    with pytest.raises(ValueError, match="Cannot specify both"):
        runner.write(out, keep=["name"], drop=["email"])


def test_write_column_order(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out, column_order=["email", "name"])
    rows = list(csv.DictReader(out.open()))
    keys = list(rows[0].keys())
    assert keys[0] == "email"
    assert keys[1] == "name"
    assert "id" in keys  # unlisted columns still present


def test_write_column_order_unlisted_follow(simple_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    runner = Runner(input_path=simple_csv, required_headers=["name"])
    runner.run()
    runner.write(out, column_order=["row_number"])
    keys = next(iter(csv.DictReader(out.open()))).keys()
    assert next(iter(keys)) == "row_number"


def test_sort_numeric_aware(tmp_path: Path) -> None:
    csv_path = tmp_path / "mixed.csv"
    csv_path.write_text("id,val\n1,10\n2,5\n3,abc\n")
    out = tmp_path / "out.csv"
    runner = Runner(input_path=csv_path, required_headers=["val"])
    runner.run()
    runner.write(out, sort_by="val")
    rows = list(csv.DictReader(out.open()))
    vals = [r["val"] for r in rows]
    # numeric sort: 5 < 10, then strings after all numerics
    assert vals == ["5", "10", "abc"]
