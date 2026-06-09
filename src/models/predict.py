"""Generate prediction tables for Korea Republic match outcomes.

This script is the inference counterpart to ``train_baseline.py``. It loads the
saved baseline model, applies the same non-leakage feature column selection used
for training, and writes a human-readable CSV with predicted classes and any
available class probabilities.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

# Add this directory to the import path so the script works both as
# ``python -m src.models.predict`` and ``python src/models/predict.py``.
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from train_baseline import get_feature_columns


# Keep project paths explicit so the script can be run from any working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"
PREDICTION_TABLE_PATH = PROJECT_ROOT / "reports" / "prediction_table.csv"

# These metadata columns make the report useful to humans, but they are not all
# guaranteed to exist in every feature table.
REPORT_METADATA_COLUMNS = ("date", "home_team", "away_team")


def load_model(path: Path = MODEL_PATH) -> Any:
    """Load the trained model artifact from disk.

    A clear error message helps beginners understand which upstream pipeline step
    is missing when prediction is run before training.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found: {path}. Run src/models/train_baseline.py first."
        )
    return joblib.load(path)


def load_features(path: Path = FEATURES_PATH) -> pd.DataFrame:
    """Load the model-ready feature table from CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Feature file not found: {path}. Run the feature pipeline first."
        )
    return pd.read_csv(path)


def build_prediction_table(df: pd.DataFrame, model: Any) -> pd.DataFrame:
    """Create a report table containing match metadata and model predictions.

    The model was trained on columns returned by ``get_feature_columns``. Reusing
    the same helper prevents target/date/result leakage and avoids train/predict
    schema drift.
    """
    feature_columns = get_feature_columns(df)
    if not feature_columns:
        raise ValueError(
            "No usable feature columns found after removing target/date/result columns."
        )

    X = df[feature_columns]
    prediction_table = df[
        [column for column in REPORT_METADATA_COLUMNS if column in df.columns]
    ].copy()

    prediction_table["predicted_result"] = model.predict(X)

    # Not every scikit-learn estimator supports probabilities. When available,
    # map each probability column to the matching class label from model.classes_.
    if hasattr(model, "predict_proba"):
        probabilities = np.asarray(model.predict_proba(X))
        classes = getattr(model, "classes_", range(probabilities.shape[1]))

        for index, class_label in enumerate(classes):
            prediction_table[f"probability_{class_label}"] = probabilities[:, index]

    return prediction_table


def save_prediction_table(
    prediction_table: pd.DataFrame,
    path: Path = PREDICTION_TABLE_PATH,
) -> None:
    """Write the prediction report, creating ``reports/`` when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    prediction_table.to_csv(path, index=False)


def main() -> None:
    """Run the baseline prediction workflow and save the prediction table."""
    model = load_model()
    features_df = load_features()
    prediction_table = build_prediction_table(features_df, model)
    save_prediction_table(prediction_table)

    print("Prediction table complete.")
    print(f"Rows predicted: {len(prediction_table)}")
    print(f"Saved predictions to: {PREDICTION_TABLE_PATH}")


if __name__ == "__main__":
    main()
