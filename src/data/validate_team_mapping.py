"""Validate raw team names against the country alias mapping table.

This script is a Phase 1 data-quality check. It does not train models and does
not change the existing Korea MVP pipeline.

Inputs:
- data/raw/*.csv
- data/mappings/team_name_mapping.csv

Outputs:
- reports/unmapped_teams.csv
- reports/team_mapping_validation.md
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MAPPING_PATH = PROJECT_ROOT / "data" / "mappings" / "team_name_mapping.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
UNMAPPED_TEAMS_PATH = REPORTS_DIR / "unmapped_teams.csv"
VALIDATION_REPORT_PATH = REPORTS_DIR / "team_mapping_validation.md"

REQUIRED_MAPPING_COLUMNS = {
    "canonical_name",
    "fifa_code",
    "aliases",
    "region",
    "notes",
}

COLUMN_ALIASES = {
    "home": "home_team",
    "away": "away_team",
    "home_name": "home_team",
    "away_name": "away_team",
    "home_team_name": "home_team",
    "away_team_name": "away_team",
    "team_home": "home_team",
    "team_away": "away_team",
}

TEAM_COLUMNS = ("home_team", "away_team")


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names used by common international match datasets."""
    standardized = df.copy()
    standardized.columns = [
        column.strip().lower().replace(" ", "_") for column in standardized.columns
    ]
    standardized = standardized.rename(columns=COLUMN_ALIASES)
    return standardized


def _read_csv_with_fallback(path: Path) -> pd.DataFrame:
    """Read a CSV with UTF-8 first, then UTF-8-SIG for spreadsheet exports."""
    try:
        return pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8-sig")


def _find_compatible_raw_files(raw_dir: Path = RAW_DIR) -> list[Path]:
    """Find raw CSV files that contain home and away team columns."""
    if not raw_dir.exists():
        print(f"Raw data directory not found: {raw_dir}")
        return []

    compatible_files: list[Path] = []
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        print(f"No raw CSV files found in: {raw_dir}")
        return []

    for csv_path in csv_files:
        try:
            sample = _standardize_columns(_read_csv_with_fallback(csv_path))
        except Exception as exc:  # pragma: no cover - defensive user message
            print(f"Skipping unreadable CSV {csv_path}: {exc}")
            continue

        if set(TEAM_COLUMNS).issubset(sample.columns):
            compatible_files.append(csv_path)
        else:
            print(
                f"Skipping {csv_path.name}: missing home_team/away_team columns "
                "after column standardization."
            )
    return compatible_files


def _load_team_mapping(mapping_path: Path = MAPPING_PATH) -> pd.DataFrame:
    """Load and validate the country alias mapping table."""
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"Team mapping file not found: {mapping_path}. "
            "Create data/mappings/team_name_mapping.csv first."
        )

    mapping_df = _read_csv_with_fallback(mapping_path)
    missing = REQUIRED_MAPPING_COLUMNS - set(mapping_df.columns)
    if missing:
        raise ValueError(
            "team_name_mapping.csv is missing required columns: "
            + ", ".join(sorted(missing))
        )
    return mapping_df


def _normalize_team_name(value: Any) -> str:
    """Normalize a raw team-name value for lookup comparison."""
    if pd.isna(value):
        return ""
    return str(value).strip()


def _build_alias_lookup(
    mapping_df: pd.DataFrame,
) -> tuple[dict[str, str], dict[str, sorted]]:
    """Build alias lookup and detect aliases mapped to multiple countries."""
    alias_to_canonicals: dict[str, set[str]] = defaultdict(set)

    for _, row in mapping_df.iterrows():
        canonical_name = _normalize_team_name(row["canonical_name"])
        if not canonical_name:
            continue

        raw_aliases = _normalize_team_name(row.get("aliases", ""))
        alias_values = [canonical_name]
        if raw_aliases:
            alias_values.extend(alias.strip() for alias in raw_aliases.split(";"))

        for alias in alias_values:
            normalized_alias = _normalize_team_name(alias)
            if normalized_alias:
                alias_to_canonicals[normalized_alias].add(canonical_name)

    duplicate_aliases = {
        alias: sorted(canonical_names)
        for alias, canonical_names in alias_to_canonicals.items()
        if len(canonical_names) > 1
    }
    alias_lookup = {
        alias: next(iter(canonical_names))
        for alias, canonical_names in alias_to_canonicals.items()
        if len(canonical_names) == 1
    }
    return alias_lookup, duplicate_aliases


def _extract_raw_team_names(raw_files: list[Path]) -> dict[str, set[str]]:
    """Extract unique home/away team names and the files where they appear."""
    team_sources: dict[str, set[str]] = defaultdict(set)

    for raw_file in raw_files:
        matches = _standardize_columns(_read_csv_with_fallback(raw_file))
        for column in TEAM_COLUMNS:
            if column not in matches.columns:
                continue
            for value in matches[column].dropna().unique():
                team_name = _normalize_team_name(value)
                if team_name:
                    team_sources[team_name].add(raw_file.name)
    return team_sources


def _format_markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Return a small dependency-free Markdown table."""
    header_row = "| " + " | ".join(headers) + " |"
    separator_row = "| " + " | ".join("---" for _ in headers) + " |"
    data_rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in rows]
    return "\n".join([header_row, separator_row, *data_rows])


def _write_unmapped_teams(unmapped_df: pd.DataFrame) -> None:
    """Write unmapped raw team names for later mapping-table updates."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    unmapped_df.to_csv(UNMAPPED_TEAMS_PATH, index=False)
    print(f"Saved unmapped team report to: {UNMAPPED_TEAMS_PATH}")


def _write_validation_report(summary: dict[str, Any]) -> None:
    """Write a human-readable mapping validation summary."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    raw_file_rows = [[file_name] for file_name in summary["raw_files"]]
    duplicate_rows = [
        [alias, "; ".join(canonical_names)]
        for alias, canonical_names in summary["duplicate_aliases"].items()
    ]
    unmapped_rows = [
        [row["raw_team_name"], row["source_files"], row["suggested_action"]]
        for row in summary["unmapped_preview"]
    ]

    sections = [
        "# Team Mapping Validation",
        "",
        "This file is generated by `python src/data/validate_team_mapping.py`.",
        "It is a Phase 1 data-quality report, not a model result.",
        "",
        "## Run Metadata",
        "",
        f"- Run timestamp: {summary['run_timestamp']}",
        f"- Mapping file: `{summary['mapping_path']}`",
        "",
        "## Raw CSV Files Used",
        "",
        _format_markdown_table(["File"], raw_file_rows)
        if raw_file_rows
        else "- No compatible raw CSV files were found.",
        "",
        "## Summary",
        "",
        _format_markdown_table(
            ["Metric", "Value"],
            [
                ["Extracted unique raw team names", summary["total_team_count"]],
                ["Mapped team names", summary["mapped_team_count"]],
                ["Unmapped team names", summary["unmapped_team_count"]],
                ["Duplicate aliases", summary["duplicate_alias_count"]],
            ],
        ),
        "",
        "## Duplicate Aliases",
        "",
        _format_markdown_table(["Alias", "Canonical names"], duplicate_rows)
        if duplicate_rows
        else "- No duplicate aliases found.",
        "",
        "## Unmapped Team Preview",
        "",
        _format_markdown_table(
            ["Raw team name", "Source files", "Suggested action"], unmapped_rows
        )
        if unmapped_rows
        else "- No unmapped team names found.",
        "",
        "## Next Actions",
        "",
        "1. Review `reports/unmapped_teams.csv`.",
        "2. Add confirmed aliases to `data/mappings/team_name_mapping.csv`.",
        "3. Resolve duplicate aliases before using the mapping in production code.",
        "4. Re-run this validation script after updating the mapping table.",
        "",
    ]

    VALIDATION_REPORT_PATH.write_text("\n".join(sections), encoding="utf-8")
    print(f"Saved team mapping validation report to: {VALIDATION_REPORT_PATH}")


def validate_team_mapping(
    raw_dir: Path = RAW_DIR,
    mapping_path: Path = MAPPING_PATH,
) -> dict[str, Any]:
    """Validate raw team names against canonical names and aliases."""
    mapping_df = _load_team_mapping(mapping_path)
    alias_lookup, duplicate_aliases = _build_alias_lookup(mapping_df)
    raw_files = _find_compatible_raw_files(raw_dir)
    team_sources = _extract_raw_team_names(raw_files) if raw_files else {}

    unmapped_rows = []
    mapped_count = 0
    for raw_team_name in sorted(team_sources):
        if raw_team_name in alias_lookup:
            mapped_count += 1
            continue
        unmapped_rows.append(
            {
                "raw_team_name": raw_team_name,
                "source_files": "; ".join(sorted(team_sources[raw_team_name])),
                "suggested_action": "Add canonical_name or alias after verification.",
            }
        )

    unmapped_df = pd.DataFrame(
        unmapped_rows,
        columns=["raw_team_name", "source_files", "suggested_action"],
    )
    _write_unmapped_teams(unmapped_df)

    summary = {
        "run_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "mapping_path": mapping_path.as_posix(),
        "raw_files": [path.name for path in raw_files],
        "total_team_count": len(team_sources),
        "mapped_team_count": mapped_count,
        "unmapped_team_count": len(unmapped_rows),
        "duplicate_alias_count": len(duplicate_aliases),
        "duplicate_aliases": duplicate_aliases,
        "unmapped_preview": unmapped_rows[:20],
    }
    _write_validation_report(summary)

    if not raw_files:
        print(
            "No compatible raw match CSV files were found. Add CSV files with "
            "home_team and away_team columns to data/raw/ and run this script again."
        )
    if duplicate_aliases:
        print("Duplicate aliases found. Review reports/team_mapping_validation.md.")
    if unmapped_rows:
        print(f"Found {len(unmapped_rows)} unmapped team names. Review reports/unmapped_teams.csv.")
    else:
        print("All extracted raw team names are covered by the mapping table.")

    return summary


def main() -> None:
    """CLI entry point for team-name mapping validation."""
    validate_team_mapping()


if __name__ == "__main__":
    main()
