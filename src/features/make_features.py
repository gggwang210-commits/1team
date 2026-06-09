"""Create model-ready MVP features from standardized match data.

Data flow for beginners:
1. Read ``data/interim/matches.csv`` produced by ``src/data/build_dataset.py``.
2. Convert raw match facts into model inputs such as rank difference and neutral
   venue flag.
3. Save ``data/processed/features.csv`` for ``src/models/train_baseline.py``.

Preprocessing note: final scores are used only to create ``target_result`` and
are deliberately excluded from the saved feature table to reduce leakage.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MATCHES_PATH = PROJECT_ROOT / "data" / "interim" / "matches.csv"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"

REQUIRED_COLUMNS = {"date", "home_team", "away_team", "target_result"}


def load_matches(path: Path = MATCHES_PATH) -> pd.DataFrame:
    """Load the interim match table created by the data-building step."""
    if not path.exists():
        raise FileNotFoundError(
            f"Match dataset not found: {path}. Run src/data/build_dataset.py first."
        )

    matches = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(matches.columns)
    if missing:
        raise ValueError(
            "Interim match dataset is missing required columns: "
            + ", ".join(sorted(missing))
        )
    return matches


def _safe_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    """Convert a column to numeric values and fill missing values safely."""
    return pd.to_numeric(series, errors="coerce").fillna(default)


def make_features(matches: pd.DataFrame) -> pd.DataFrame:
    """Transform match rows into a model-ready feature table."""
    features = pd.DataFrame()
    features["date"] = pd.to_datetime(matches["date"], errors="coerce").dt.strftime(
        "%Y-%m-%d"
    )
    features["home_team"] = matches["home_team"].astype(str).str.strip()
    features["away_team"] = matches["away_team"].astype(str).str.strip()

    if {"home_rank", "away_rank"}.issubset(matches.columns):
        home_rank = _safe_numeric(matches["home_rank"])
        away_rank = _safe_numeric(matches["away_rank"])
        # Lower FIFA rank is better, so away_rank - home_rank is positive when
        # the home team is stronger on paper.
        features["rank_diff"] = away_rank - home_rank
        features["home_rank"] = home_rank
        features["away_rank"] = away_rank
    else:
        # Keep the pipeline runnable before rankings are added. This feature is
        # neutral and can be replaced by real ranking data later.
        features["rank_diff"] = 0.0

    if "neutral" in matches.columns:
        neutral_text = matches["neutral"].astype(str).str.lower().str.strip()
        features["is_neutral"] = neutral_text.isin({"true", "1", "yes", "y"}).astype(
            int
        )
    else:
        features["is_neutral"] = 0

    # Simple categorical context features. OneHotEncoder in train_baseline.py
    # will convert these strings into numeric columns for the models.
    features["is_korea_home"] = (features["home_team"] == "Korea Republic").astype(int)
    features["target_result"] = matches["target_result"].astype(str).str.strip()

    features = features.dropna(subset=["date", "target_result"]).reset_index(drop=True)
    return features


def save_features(features: pd.DataFrame, path: Path = FEATURES_PATH) -> None:
    """Persist the model-ready feature table."""
    path.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(path, index=False)
    print(f"Saved model-ready features with {len(features)} rows to: {path}")


def main() -> None:
    """CLI entry point for the feature-engineering step."""
    matches = load_matches()
    features = make_features(matches)
    save_features(features)


if __name__ == "__main__":
    main()
