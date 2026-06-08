"""Prediction helpers for Korea Republic match outcomes.

This starter file will load trained models and generate Win/Draw/Loss
probabilities in a later implementation step.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"


def _require_file(path: Path, message: str) -> None:
    """Give a helpful error before Python tries to open a missing file."""

    if not path.exists():
        raise FileNotFoundError(message)


def load_prediction_inputs(
    model_path: str | Path = BASELINE_MODEL_PATH,
    features_path: str | Path = FEATURES_PATH,
) -> tuple[object, pd.DataFrame]:
    """Load the trained baseline model and processed feature table."""

    model_path = Path(model_path)
    features_path = Path(features_path)

    _require_file(
        model_path,
        "Missing models/baseline_model.pkl. "
        "Run the baseline training step first; it should create the trained model file.",
    )
    _require_file(
        features_path,
        "Missing data/processed/features.csv. "
        "Run the feature engineering step first; it should create the model-ready feature table.",
    )

    model = joblib.load(model_path)
    features = pd.read_csv(features_path)
    return model, features


# TODO: Implement model loading and match prediction functions.
