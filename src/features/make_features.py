"""Create the MVP feature table from processed match data.

Data flow for this step:
1. Read ``data/processed/matches.csv``.
2. Validate that the columns required to describe each match result exist.
3. Create a supervised-learning target and a small set of beginner-friendly
   numeric features.
4. Save the resulting table to ``data/processed/features.csv``.

Note for future modeling work:
``goal_difference`` and ``total_goals`` are useful for data analysis, but they
are calculated from final scores. They should not be used as model inputs for a
pre-match predictor because that would leak the answer into training.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


# Keep repository-relative paths in one place so future pipeline steps can reuse
# or override them easily.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "data" / "processed" / "matches.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"

REQUIRED_COLUMNS = ["date", "home_team", "away_team", "home_score", "away_score"]
DIRECT_LEAKAGE_COLUMNS = ["home_score", "away_score", "goal_difference", "total_goals"]

# Common names used by public international-football datasets. The script checks
# these pairs in order and creates the first available rank difference.
RANKING_COLUMN_PAIRS = [
    ("home_rank", "away_rank"),
    ("home_team_rank", "away_team_rank"),
    ("home_fifa_rank", "away_fifa_rank"),
    ("home_ranking", "away_ranking"),
]


def load_matches(input_path: Path = INPUT_PATH) -> pd.DataFrame:
    """Load processed match rows from disk with a clear error message."""
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}. "
            "Run the data preparation step first or place matches.csv there."
        )

    return pd.read_csv(input_path)


def validate_required_columns(matches: pd.DataFrame) -> None:
    """Ensure the minimum columns needed for feature generation are present."""
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in matches.columns]
    if missing_columns:
        raise ValueError(
            "matches.csv is missing required columns: "
            f"{', '.join(missing_columns)}. Required columns are: "
            f"{', '.join(REQUIRED_COLUMNS)}."
        )


def create_target_result(row: pd.Series) -> str:
    """Convert home/away scores into a classification target label."""
    if row["home_score"] > row["away_score"]:
        return "home_win"
    if row["home_score"] < row["away_score"]:
        return "away_win"
    return "draw"


def add_rank_difference(features: pd.DataFrame) -> None:
    """Add ``rank_difference`` when a supported home/away ranking pair exists.

    The function mutates ``features`` in place to avoid copying the whole table.
    A positive value means the home team's rank number is larger than the away
    team's rank number. In FIFA-style rankings, a larger number often means a
    lower-ranked team, so model interpretation should account for that.
    """
    for home_rank_column, away_rank_column in RANKING_COLUMN_PAIRS:
        if home_rank_column in features.columns and away_rank_column in features.columns:
            home_rank = pd.to_numeric(features[home_rank_column], errors="coerce")
            away_rank = pd.to_numeric(features[away_rank_column], errors="coerce")
            features["rank_difference"] = home_rank - away_rank
            return


def parse_neutral_value(value: object) -> int:
    """Convert common neutral-site values into a safe 0/1 flag."""
    if pd.isna(value):
        return 0

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y"}:
            return 1
        if normalized in {"false", "0", "no", "n", ""}:
            return 0

    return int(bool(value))


def add_neutral_feature(features: pd.DataFrame) -> None:
    """Add a numeric neutral-site flag if neutral-site source data exists."""
    if "neutral" not in features.columns:
        return

    # ``astype(bool)`` alone can turn non-empty strings like "False" into True,
    # so parse each value explicitly before converting to 0/1.
    features["is_neutral"] = features["neutral"].map(parse_neutral_value).astype(int)


def build_features(matches: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Build the MVP feature table and return model-safe feature column names."""
    validate_required_columns(matches)

    features = matches.copy()

    # Coerce score columns to numeric values before doing arithmetic. Invalid
    # values become NaN and are reported clearly instead of producing bad output.
    for score_column in ["home_score", "away_score"]:
        features[score_column] = pd.to_numeric(features[score_column], errors="coerce")

    if features[["home_score", "away_score"]].isna().any().any():
        raise ValueError("home_score and away_score must contain numeric values for every row.")

    features["target_result"] = features.apply(create_target_result, axis=1)
    features["goal_difference"] = features["home_score"] - features["away_score"]
    features["total_goals"] = features["home_score"] + features["away_score"]

    add_neutral_feature(features)
    add_rank_difference(features)

    feature_columns = select_model_feature_columns(features)
    return features, feature_columns


def select_model_feature_columns(features: pd.DataFrame) -> list[str]:
    """Return numeric feature columns that are safe to use as model inputs.

    Direct result-derived columns are intentionally excluded to reduce target
    leakage in downstream training. They remain in the saved table for analysis
    and validation.
    """
    excluded_columns = set(REQUIRED_COLUMNS + DIRECT_LEAKAGE_COLUMNS + ["target_result"])
    numeric_columns = features.select_dtypes(include="number").columns.tolist()
    return [column for column in numeric_columns if column not in excluded_columns]


def save_features(features: pd.DataFrame, output_path: Path = OUTPUT_PATH) -> None:
    """Persist the feature table, creating the output directory if needed."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output_path, index=False)


def main() -> None:
    """Run the feature engineering pipeline as a command-line script."""
    matches = load_matches()
    features, feature_columns = build_features(matches)
    save_features(features)

    print(f"Output path: {OUTPUT_PATH}")
    print(f"Row count: {len(features)}")
    print(f"Feature columns: {', '.join(feature_columns) if feature_columns else '(none)'}")


if __name__ == "__main__":
    main()
