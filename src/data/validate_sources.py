"""Minimal raw data source validation before preprocessing."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MANIFEST_PATH = RAW_DIR / "source_manifest.csv"

REQUIRED_COLUMNS = {
    "raw_file_name",
    "dataset_name",
    "expected_columns",
    "verification_status",
}


def parse_expected_columns(value: object) -> list[str]:
    return [column.strip() for column in str(value).split(";") if column.strip()]


def main() -> None:
    failures: list[str] = []

    if not MANIFEST_PATH.exists():
        print(f"FAIL manifest_exists: {MANIFEST_PATH} not found")
        raise SystemExit(1)

    print(f"PASS manifest_exists: {MANIFEST_PATH}")

    manifest = pd.read_csv(MANIFEST_PATH)
    missing_manifest_columns = sorted(REQUIRED_COLUMNS - set(manifest.columns))
    if missing_manifest_columns:
        failures.append(f"manifest missing columns: {missing_manifest_columns}")
        print(f"FAIL manifest_required_columns: {missing_manifest_columns}")
    else:
        print("PASS manifest_required_columns")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        raise SystemExit(1)

    for _, row in manifest.iterrows():
        raw_file_name = str(row["raw_file_name"]).strip()
        raw_path = RAW_DIR / raw_file_name
        expected_columns = parse_expected_columns(row["expected_columns"])

        if not raw_path.exists():
            failures.append(f"{raw_file_name}: raw file not found")
            print(f"FAIL raw_file_exists: {raw_path}")
            continue

        print(f"PASS raw_file_exists: {raw_path}")

        try:
            raw_df = pd.read_csv(raw_path)
        except Exception as exc:
            failures.append(f"{raw_file_name}: could not read CSV: {exc}")
            print(f"FAIL raw_file_readable: {raw_file_name}: {exc}")
            continue

        if raw_df.empty:
            failures.append(f"{raw_file_name}: raw file is empty")
            print(f"FAIL raw_file_non_empty: {raw_file_name}")
        else:
            print(f"PASS raw_file_non_empty: {raw_file_name}: rows={len(raw_df)}")

        actual_columns = {str(column).strip() for column in raw_df.columns}
        missing_expected_columns = sorted(set(expected_columns) - actual_columns)
        if missing_expected_columns:
            failures.append(
                f"{raw_file_name}: missing expected columns {missing_expected_columns}"
            )
            print(
                f"FAIL expected_columns_present: {raw_file_name}: "
                f"{missing_expected_columns}"
            )
        else:
            print(f"PASS expected_columns_present: {raw_file_name}")

    if failures:
        print("Source validation failed.")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("Source validation passed.")


if __name__ == "__main__":
    main()
