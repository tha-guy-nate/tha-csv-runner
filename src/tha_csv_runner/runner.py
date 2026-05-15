import csv
import functools
import shutil
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from .errors import ConfigError


def tqdm_ncols(max_cols: int = 85) -> int:
    return min(shutil.get_terminal_size(fallback=(max_cols, 24)).columns, max_cols)


def _sort_key(val: object) -> tuple:
    try:
        return (0, float(val))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return (1, str(val))


def _write_chunk(path: Path, rows: list[dict], cols: list[str], label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        if rows:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(
                {c: row[c] for c in cols if c in row}
                for row in tqdm(rows, desc=label, ncols=tqdm_ncols())
            )


class ThaCSV:
    def __init__(self) -> None:
        self.rows: list[dict] = []
        self._read: bool = False
        self._input_path: Path | None = None
        self.status_cb = print

    def read(
        self,
        desc: str | None,
        input_path: str | Path,
        required_headers: list[str],
        validator: Callable[[dict], None] | None = None,
        enrich: bool = True,
    ) -> list[dict]:
        self._input_path = Path(input_path)

        with open(self._input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ConfigError(f"{self._input_path} appears to be empty")
            missing = [h for h in required_headers if h not in reader.fieldnames]
            if missing:
                raise ConfigError(f"Missing required headers: {missing}")
            raw_rows = list(reader)

        self.rows = []
        self._read = True

        label = desc if desc is not None else f"Reading {self._input_path.stem} CSV"
        for i, row in enumerate(tqdm(raw_rows, desc=label, ncols=tqdm_ncols()), start=2):
            if enrich:
                enriched = {**row, "row number": i, "row status": "", "message": ""}
            else:
                enriched = dict(row)
            try:
                if validator is not None:
                    validator(enriched)
            except Exception as exc:
                if enrich:
                    enriched["row status"] = "error"
                    enriched["message"] = str(exc)
                else:
                    raise
            self.rows.append(enriched)

        return self.rows

    def write(
        self,
        desc: str | None,
        output_path: str | Path | None = None,
        rows: list[dict] | None = None,
        sort_by: str | list[str] | None = None,
        ascending: bool | list[bool] = True,
        column_order: list[str] | None = None,
        keep: list[str] | None = None,
        drop: list[str] | None = None,
        chunk_size: int | None = None,
    ) -> Path | list[Path]:
        if rows is None and not self._read:
            raise RuntimeError("No data to write — call read() first or pass rows=")
        if keep and drop:
            raise ValueError("Cannot specify both keep and drop")
        if chunk_size is not None and chunk_size < 1:
            raise ValueError("chunk_size must be >= 1")

        rows = list(rows) if rows is not None else list(self.rows)

        # --- column filtering ---
        all_cols = list(rows[0].keys()) if rows else []

        if keep:
            cols = [c for c in keep if c in all_cols]
        elif drop:
            cols = [c for c in all_cols if c not in drop]
        else:
            cols = all_cols

        # --- column ordering: listed cols first, unlisted follow in original order ---
        if column_order:
            front = [c for c in column_order if c in cols]
            rest = [c for c in cols if c not in column_order]
            cols = front + rest

        # --- sorting ---
        if sort_by is not None:
            sort_cols = [sort_by] if isinstance(sort_by, str) else list(sort_by)
            asc_list = (
                [ascending] * len(sort_cols) if isinstance(ascending, bool) else list(ascending)
            )

            def compare(a: dict, b: dict) -> int:
                for col, asc in zip(sort_cols, asc_list, strict=True):
                    ka, kb = _sort_key(a.get(col, "")), _sort_key(b.get(col, ""))
                    if ka < kb:
                        return -1 if asc else 1
                    if ka > kb:
                        return 1 if asc else -1
                return 0

            rows.sort(key=functools.cmp_to_key(compare))

        # --- output path ---
        if output_path is None:
            stem = self._input_path.stem if self._input_path else "output"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"{stem}_processed_{ts}.csv")

        output_file = Path(output_path)

        # --- chunked write ---
        if chunk_size is not None:
            chunks = [rows[i:i + chunk_size] for i in range(0, max(len(rows), 1), chunk_size)]
            paths = []
            for idx, chunk in enumerate(chunks, start=1):
                chunk_name = f"{output_file.stem}_{idx:03d}{output_file.suffix}"
                chunk_path = output_file.parent / chunk_name
                label = (
                    f"{desc} ({idx}/{len(chunks)})"
                    if desc
                    else f"Writing {output_file.stem} CSV ({idx}/{len(chunks)})"
                )
                _write_chunk(chunk_path, chunk, cols, label)
                paths.append(chunk_path)
            self.status_cb(f":white_check_mark: Done! CSV was written to: {paths}")
            return paths

        write_label = desc if desc is not None else f"Writing {output_file.stem} CSV"
        _write_chunk(output_file, rows, cols, write_label)
        self.status_cb(f":white_check_mark: Done! CSV was written to: {output_file}")
        return output_file
