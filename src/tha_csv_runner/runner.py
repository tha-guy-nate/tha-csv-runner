import csv
import functools
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

from .errors import ConfigError


def _sort_key(val: object) -> tuple:
    try:
        return (0, float(val))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return (1, str(val))


class Runner:
    def __init__(
        self,
        input_path: str | Path,
        required_headers: list[str],
        processor: Callable[[dict], None] | None = None,
        sample: int | None = None,
    ) -> None:
        self.input_path = Path(input_path)
        self.processor = processor
        self.required_headers = required_headers
        self.sample = sample
        self.rows: list[dict] | None = None

    def _load(self) -> list[dict]:
        with open(self.input_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ConfigError(f"{self.input_path} appears to be empty")
            missing = [h for h in self.required_headers if h not in reader.fieldnames]
            if missing:
                raise ConfigError(f"Missing required headers: {missing}")
            rows = list(reader)

        if self.sample is not None:
            rows = rows[: self.sample]

        return rows

    def run(self) -> None:
        raw_rows = self._load()
        self.rows = []

        for i, row in enumerate(tqdm(raw_rows, desc=f"Reading {self.input_path.name}"), start=1):
            enriched = {**row, "row_number": i, "row_status": "", "message": ""}
            try:
                if self.processor is not None:
                    self.processor(enriched)
            except Exception as exc:
                enriched["row_status"] = "error"
                enriched["message"] = str(exc)
            self.rows.append(enriched)

    def write(
        self,
        output_path: str | Path | None = None,
        sort_by: str | list[str] | None = None,
        ascending: bool | list[bool] = True,
        column_order: list[str] | None = None,
        keep: list[str] | None = None,
        drop: list[str] | None = None,
    ) -> Path:
        if self.rows is None:
            raise RuntimeError("No data to write — call run() first")
        if keep and drop:
            raise ValueError("Cannot specify both keep and drop")

        rows = list(self.rows)

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
            asc_list = [ascending] * len(sort_cols) if isinstance(ascending, bool) else list(ascending)

            def compare(a: dict, b: dict) -> int:
                for col, asc in zip(sort_cols, asc_list):
                    ka, kb = _sort_key(a.get(col, "")), _sort_key(b.get(col, ""))
                    if ka < kb:
                        return -1 if asc else 1
                    if ka > kb:
                        return 1 if asc else -1
                return 0

            rows.sort(key=functools.cmp_to_key(compare))

        # --- output path ---
        if output_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"{self.input_path.stem}_processed_{ts}.csv")

        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        print(f"Writing {out.name}...")

        with open(out, "w", newline="", encoding="utf-8") as f:
            if rows:
                writer = csv.DictWriter(f, fieldnames=cols)
                writer.writeheader()
                writer.writerows({c: row[c] for c in cols if c in row} for row in rows)

        return out
