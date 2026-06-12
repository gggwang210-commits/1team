"""Create model-ready features from standardized match data.

Data flow for beginners:
1. Read the processed match dataset produced by ``src/data/build_dataset.py``.
2. Convert raw match facts into model inputs such as rank difference and neutral
   venue flag.
3. Save a model-ready feature table for ``src/models/train_baseline.py``.

Default behavior preserves the Korea Republic MVP target and file paths.
Expansion work can run this script with ``--target-scope home`` to read
``data/processed/matches_global.csv`` and write
``data/processed/features_global.csv``.

Preprocessing note: final scores are used only to create result labels and are
never saved as model input features.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MATCHES_PATH = PROCESSED_DIR / "matches.csv"
GLOBAL_MATCHES_PATH = PROCESSED_DIR / "matches_global.csv"
FEATURES_PATH = PROCESSED_DIR / "features.csv"
GLOBAL_FEATURES_PATH = PROCESSED_DIR / "features_global.csv"

MODEL_TARGET_COLUMN = "target_result"
KOREA_TARGET_COLUMN = "target_result_korea_perspective"
TARGET_SCOPE_KOREA = "korea"
TARGET_SCOPE_HOME = "home"
TARGET_SCOPE_CHOICES = (TARGET_SCOPE_KOREA, TARGET_SCOPE_HOME)
REQUIRED_BASE_COLUMNS = {"date", "home_team", "away_team"}
SCORE_COLUMNS = {"home_score", "away_score"}


def _target_column_for_scope(target_scope: str) -> str:
    """Return the source target column for the requested feature target scope."""
    if target_scope == TARGET_SCOPE_KOREA:
        return KOREA_TARGET_COLUMN
    if target_scope == TARGET_SCOPE_HOME:
        return MODEL_TARGET_COLUMN
    raise ValueError(
        f"Unknown target_scope '{target_scope}'. Expected one of: "
        f"{', '.join(TARGET_SCOPE_CHOICES)}."
    )


def _default_input_path(target_scope: str) -> Path:
    """Choose the safe default match input path for MVP or global feature mode."""
    if target_scope == TARGET_SCOPE_HOME:
        return GLOBAL_MATCHES_PATH
    return MATCHES_PATH


def _default_output_path(target_scope: str) -> Path:
    """Choose the safe default feature output path for MVP or global feature mode."""
    if target_scope == TARGET_SCOPE_HOME:
        return GLOBAL_FEATURES_PATH
    return FEATURES_PATH


def load_matches(
    path: Path = MATCHES_PATH,
    target_scope: str = TARGET_SCOPE_KOREA,
) -> pd.DataFrame:
    """Load the processed match table created by the data-building step."""
    if not path.exists():
        raise FileNotFoundError(
            f"Match dataset not found: {path}. Run src/data/build_dataset.py first."
        )

    matches = pd.read_csv(path)
    source_target_column = _target_column_for_scope(target_scope)
    required_columns = REQUIRED_BASE_COLUMNS | {source_target_column}
    missing = required_columns - set(matches.columns)
    if missing:
        raise ValueError(
            "Processed match dataset is missing required columns for "
            f"target_scope='{target_scope}': " + ", ".join(sorted(missing))
        )
    return matches


def _safe_numeric(series: pd.Series, default: float = 0.0) -> pd.Series:
    """Convert a column to numeric values and fill missing values safely."""
    return pd.to_numeric(series, errors="coerce").fillna(default)


def _clean_target(series: pd.Series) -> pd.Series:
    """Normalize target labels while preserving real missing values."""
    return series.astype("string").str.strip().replace("", pd.NA)


def make_features(
    matches: pd.DataFrame,
    target_scope: str = TARGET_SCOPE_KOREA,
) -> pd.DataFrame:
    """Transform match rows into a model-ready feature table.

    Target scope contract:
    - ``korea`` uses ``target_result_korea_perspective`` for the Korea MVP.
    - ``home`` uses ``target_result`` for global expansion experiments.

    The saved model target column stays named ``target_result`` so
    ``train_baseline.py`` can continue to read one stable target name.
    """
    source_target_column = _target_column_for_scope(target_scope)
    missing = (REQUIRED_BASE_COLUMNS | {source_target_column}) - set(matches.columns)
    if missing:
        raise ValueError(
            "Cannot create features because matches data is missing required columns: "
            + ", ".join(sorted(missing))
        )

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

    selected_target = _clean_target(matches[source_target_column])

    # TARGET COLUMN CONTRACT:
    # - features.csv.target_result is always the modeling target.
    # - source_target_column and source_target_scope document where it came from.
    # - train_baseline.py excludes these audit columns from model input features.
    features[MODEL_TARGET_COLUMN] = selected_target
    features["source_target_column"] = source_target_column
    features["source_target_scope"] = target_scope

    if KOREA_TARGET_COLUMN in matches.columns:
        # Preserve the Korea audit column when available. In home/global mode,
        # non-Korea rows may be missing here; that is expected and allowed.
        features[KOREA_TARGET_COLUMN] = _clean_target(matches[KOREA_TARGET_COLUMN])

    # Defense-in-depth: final scores must not become model input features even if
    # upstream match data contains them.
    for score_column in SCORE_COLUMNS:
        if score_column in features.columns:
            features = features.drop(columns=[score_column])

    before_drop = len(features)
    features = features.dropna(subset=["date", MODEL_TARGET_COLUMN]).reset_index(
        drop=True
    )
    dropped_rows = before_drop - len(features)
    if dropped_rows:
        print(
            f"Dropped {dropped_rows} rows without a usable target for "
            f"target_scope='{target_scope}'."
        )
    return features


def save_features(features: pd.DataFrame, path: Path = FEATURES_PATH) -> None:
    """Persist the model-ready feature table."""
    path.parent.mkdir(parents=True, exist_ok=True)

    before_dedup = len(features)
    features = features.drop_duplicates().reset_index(drop=True)
    dropped_duplicates = before_dedup - len(features)

    if dropped_duplicates:
        print(f"Dropped duplicate feature rows: {dropped_duplicates}")

    features.to_csv(path, index=False)
    print(f"Saved model-ready features with {len(features)} rows to: {path}")


def _parse_args() -> argparse.Namespace:
    """Parse command-line options for MVP and expansion feature builds."""
    parser = argparse.ArgumentParser(description="Create model-ready feature table.")
    parser.add_argument(
        "--target-scope",
        choices=TARGET_SCOPE_CHOICES,
        default=TARGET_SCOPE_KOREA,
        help=(
            "Choose which match-result target to copy into the output target_result. "
            "Use 'korea' for the MVP and 'home' for global expansion."
        ),
    )
    parser.add_argument(
        "--input-path",
        type=Path,
        default=None,
        help=(
            "Optional processed matches CSV path. If omitted, korea scope reads "
            "data/processed/matches.csv and home scope reads "
            "data/processed/matches_global.csv."
        ),
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        default=None,
        help=(
            "Optional feature output CSV path. If omitted, korea scope writes "
            "data/processed/features.csv and home scope writes "
            "data/processed/features_global.csv."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """CLI entry point for the feature-engineering step."""
    args = _parse_args()
    input_path = args.input_path or _default_input_path(args.target_scope)
    output_path = args.output_path or _default_output_path(args.target_scope)
    matches = load_matches(path=input_path, target_scope=args.target_scope)
    features = make_features(matches, target_scope=args.target_scope)
    save_features(features, path=output_path)


if __name__ == "__main__":
    main()