"""Load raw CSV data for the FIFA World Cup prediction MVP.

The functions in this file intentionally stay small and explicit so that new
team members can understand the first step of the data pipeline: read the raw
files, check that they exist, and parse date columns when they are available.
"""

from pathlib import Path

import pandas as pd

# Default raw-data locations used by the project.
RAW_DATA_DIR = Path("data/raw")
MATCHES_PATH = RAW_DATA_DIR / "matches.csv"
RANKINGS_PATH = RAW_DATA_DIR / "fifa_rankings.csv"

# Common date-like column names seen in football match/ranking CSV files.
DATE_COLUMN_CANDIDATES = ("date", "rank_date", "ranking_date", "updated_at")


def _read_csv_with_dates(path: Path | str, *, dataset_name: str) -> pd.DataFrame:
    """Read a CSV file and convert any known date columns to datetime.

    Parameters
    ----------
    path:
        File path supplied by the caller. It can be either a ``Path`` object or
        a string because both are common in beginner Python code.
    dataset_name:
        Human-readable name used in the error message.
    """

    csv_path = Path(path)

    # A clear error helps the next developer know exactly which raw data file
    # must be downloaded or copied into the project before running the pipeline.
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Missing required {dataset_name} CSV file: {csv_path}. "
            f"Please place the file at this path or pass a custom path."
        )

    data = pd.read_csv(csv_path)

    # Convert date columns only when they exist. errors='coerce' keeps the
    # pipeline running by turning unparseable date strings into NaT values.
    for column in DATE_COLUMN_CANDIDATES:
        if column in data.columns:
            data[column] = pd.to_datetime(data[column], errors="coerce")

    return data


def load_matches(path: Path | str = MATCHES_PATH) -> pd.DataFrame:
    """Load raw international match results from CSV."""

    return _read_csv_with_dates(path, dataset_name="matches")


def load_rankings(path: Path | str = RANKINGS_PATH) -> pd.DataFrame:
    """Load raw FIFA ranking data from CSV."""

    return _read_csv_with_dates(path, dataset_name="rankings")
