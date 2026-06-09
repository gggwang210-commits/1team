"""Build the MVP processed match dataset.

Data flow for the MVP smoke test:
1. Create a small deterministic in-memory set of match records.
2. Validate that at least one row exists before writing anything to disk.
3. Persist the records to ``data/processed/matches.csv`` for downstream
   feature engineering and model-training experiments.
"""

from pathlib import Path

import pandas as pd


# Keep the MVP schema explicit so downstream feature engineering can rely on it.
MATCH_COLUMNS = [
    "date",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "home_rank",
    "away_rank",
    "neutral",
]


def build_smoke_test_matches() -> pd.DataFrame:
    """Return a deterministic match dataset for MVP pipeline smoke tests.

    The records are intentionally small and static. They are not intended to
    train a production model; they only provide enough realistic structure for
    preprocessing and feature-engineering code to run end-to-end.
    """
    records = [
        {
            "date": "2024-01-10",
            "home_team": "Argentina",
            "away_team": "Brazil",
            "home_score": 2,
            "away_score": 1,
            "home_rank": 1,
            "away_rank": 5,
            "neutral": False,
        },
        {
            "date": "2024-01-17",
            "home_team": "France",
            "away_team": "Germany",
            "home_score": 1,
            "away_score": 1,
            "home_rank": 2,
            "away_rank": 16,
            "neutral": False,
        },
        {
            "date": "2024-01-24",
            "home_team": "Spain",
            "away_team": "Italy",
            "home_score": 3,
            "away_score": 2,
            "home_rank": 8,
            "away_rank": 9,
            "neutral": True,
        },
        {
            "date": "2024-01-31",
            "home_team": "England",
            "away_team": "Netherlands",
            "home_score": 0,
            "away_score": 2,
            "home_rank": 4,
            "away_rank": 7,
            "neutral": False,
        },
        {
            "date": "2024-02-07",
            "home_team": "Portugal",
            "away_team": "Belgium",
            "home_score": 2,
            "away_score": 2,
            "home_rank": 6,
            "away_rank": 3,
            "neutral": True,
        },
    ]

    return pd.DataFrame.from_records(records, columns=MATCH_COLUMNS)


def main() -> None:
    """Create ``data/processed/matches.csv`` from the MVP smoke-test data."""
    project_root = Path(__file__).resolve().parents[2]
    output_dir = project_root / "data" / "processed"
    output_path = output_dir / "matches.csv"

    matches = build_smoke_test_matches()
    if matches.empty:
        raise ValueError("Generated matches dataset is empty; cannot write matches.csv.")

    # Ensure the processed data directory exists before writing the CSV file.
    output_dir.mkdir(parents=True, exist_ok=True)
    matches.to_csv(output_path, index=False)

    print(f"Wrote {output_path} with {len(matches)} rows.")


if __name__ == "__main__":
    main()
