"""Generate Win/Draw/Loss prediction tables from a saved baseline model.

This module is intentionally written in a beginner-friendly style:
1. Load the trained model from ``models/baseline_model.pkl``.
2. Load model-ready features from ``data/processed/features.csv``.
3. Ask the model for class probabilities with ``predict_proba``.
4. Save a readable CSV report to ``reports/prediction_table.csv``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import pickle

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"
PREDICTION_TABLE_PATH = PROJECT_ROOT / "reports" / "prediction_table.csv"

# These columns help humans identify which match each probability row belongs to.
# They are copied into the output table when they exist in features.csv, but they
# are not required because different datasets may use different identifiers.
IDENTIFIER_COLUMNS = [
    "date",
    "match_date",
    "team",
    "opponent",
    "home_team",
    "away_team",
    "venue_side",
    "source_row",
]

# These columns are labels/results from historical matches, not future prediction
# inputs.  If the saved model does not advertise its own feature names, we remove
# them before prediction to avoid accidentally giving answers to the model.
TARGET_LIKE_COLUMNS = [
    "win",
    "result",
    "outcome",
    "label",
    "target",
    "target_result",
    "team_result",
]

# Project convention if a future training pipeline saves labels as integers.
# The current baseline trains directly on text labels: Loss, Draw, Win.
NUMERIC_CLASS_LABELS = {0: "Loss", 1: "Draw", 2: "Win"}

# User-facing probability column order expected by reports and simulations.
PROBABILITY_COLUMNS = ["Win", "Draw", "Loss"]


def load_model(path: Path = MODEL_PATH) -> Any:
    """Load the saved pickle model.

    Parameters
    ----------
    path:
        Path to the trained model artifact.  By default this is
        ``models/baseline_model.pkl`` from the project root.

    Returns
    -------
    Any
        A fitted model object.  For this project it should usually be a
        scikit-learn compatible estimator or pipeline with ``predict_proba``.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "Required model file was not found: "
            f"{path}. Train and save the baseline model to exactly this path "
            "before running predictions."
        )

    # ``pickle.load`` rebuilds the Python object that was saved after training.
    # For safety, only open pickle files created by your own trusted training
    # code because pickle can execute code during loading.
    with path.open("rb") as model_file:
        return pickle.load(model_file)


def load_features(path: Path = FEATURES_PATH) -> pd.DataFrame:
    """Read the model-ready feature CSV into a pandas DataFrame."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "Required feature file was not found: "
            f"{path}. Create data/processed/features.csv first, for example by "
            "running python src/features/make_features.py."
        )

    # pandas turns the CSV into a table where rows are matches and columns are
    # identifiers/features that the model can use for prediction.
    return pd.read_csv(path)


def _normalize_text_class_label(label: str) -> str:
    """Convert text class labels into user-facing report labels."""

    normalized = label.strip().lower()
    if normalized in {"win", "w", "won", "home_win", "team_win", "2"}:
        return "Win"
    if normalized in {"draw", "d", "tie", "tied", "1"}:
        return "Draw"
    if normalized in {"loss", "lose", "lost", "l", "away_win", "team_loss", "0"}:
        return "Loss"
    return label.strip().replace(" ", "_")


def _normalize_class_labels(labels: list[object]) -> list[str]:
    """Convert raw model class labels into report column names."""

    # Only apply the 0=Loss, 1=Draw, 2=Win convention when the fitted model
    # actually contains all three numeric classes.  This avoids pretending that
    # a binary helper target such as ``win`` is a full Win/Draw/Loss model.
    if set(labels) == set(NUMERIC_CLASS_LABELS):
        return [NUMERIC_CLASS_LABELS[label] for label in labels]

    normalized_labels: list[str] = []
    for label in labels:
        if isinstance(label, str):
            normalized_labels.append(_normalize_text_class_label(label))
        else:
            # Keep unexpected numeric classes visible instead of silently
            # dropping them.  This makes label-encoding mistakes easier to debug.
            normalized_labels.append(f"class_{label}")
    return normalized_labels


def _feature_input_for_model(model: Any, features_df: pd.DataFrame) -> pd.DataFrame:
    """Return the columns that should be passed into ``model.predict_proba``."""

    # Many scikit-learn estimators remember the exact columns used during fit.
    # When that information exists, using it is the safest way to avoid column
    # order mistakes and accidental identifier columns.
    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is not None:
        required_columns = list(feature_names)
        missing_columns = [
            col for col in required_columns if col not in features_df.columns
        ]
        if missing_columns:
            raise ValueError(
                "features.csv is missing column(s) required by the model: "
                f"{', '.join(missing_columns)}. Recreate features.csv with the "
                "same feature pipeline used during training."
            )
        return features_df[required_columns]

    # Fallback for models that do not store feature names: remove obvious human
    # identifier columns and target/result columns, then pass the remaining table.
    columns_to_remove = set(IDENTIFIER_COLUMNS) | set(TARGET_LIKE_COLUMNS)
    model_columns = [col for col in features_df.columns if col not in columns_to_remove]
    return features_df[model_columns]


def generate_probabilities(model: Any, features_df: pd.DataFrame) -> pd.DataFrame:
    """Create a readable table with match identifiers and Win/Draw/Loss odds.

    The model is expected to follow the scikit-learn API: ``predict_proba``
    returns one probability column per class, and ``classes_`` tells us which
    class label each probability column represents.
    """

    if not hasattr(model, "predict_proba"):
        raise TypeError(
            "The loaded model does not have predict_proba(). Save a classifier "
            "that supports probability prediction, such as LogisticRegression "
            "or RandomForestClassifier."
        )
    if not hasattr(model, "classes_"):
        raise TypeError(
            "The loaded model does not have classes_. A scikit-learn classifier "
            "usually adds classes_ after fitting. Please retrain and save a "
            "fitted classifier."
        )

    model_input = _feature_input_for_model(model, features_df)

    # ``predict_proba`` returns rows like [0.10, 0.20, 0.70].  The meaning of
    # each column comes from ``model.classes_`` in the same order.
    probabilities = model.predict_proba(model_input)
    class_labels = list(model.classes_)
    probability_df = pd.DataFrame(probabilities, index=features_df.index)

    if probability_df.shape[1] != len(class_labels):
        raise ValueError(
            "Model probability output does not match model.classes_. Expected "
            f"{len(class_labels)} probability columns but received "
            f"{probability_df.shape[1]}."
        )

    probability_df.columns = _normalize_class_labels(class_labels)

    # If two raw labels normalize to the same friendly name, add them together so
    # the final report still has one column per outcome.
    probability_df = probability_df.T.groupby(level=0).sum().T

    # Always provide the three expected report columns.  Missing classes are set
    # to 0.0 so downstream code can depend on a stable schema.
    for column in PROBABILITY_COLUMNS:
        if column not in probability_df.columns:
            probability_df[column] = 0.0

    # Keep useful match identifiers beside the probabilities when the columns are
    # available.  This makes reports easier to read and join with simulations.
    available_identifier_columns = [
        column for column in IDENTIFIER_COLUMNS if column in features_df.columns
    ]
    unexpected_probability_columns = [
        column for column in probability_df.columns if column not in PROBABILITY_COLUMNS
    ]
    output_probability_columns = PROBABILITY_COLUMNS + unexpected_probability_columns

    output_parts = [
        features_df[available_identifier_columns],
        probability_df[output_probability_columns],
    ]
    output_df = pd.concat(output_parts, axis=1)

    return output_df


def save_prediction_table(
    prediction_df: pd.DataFrame, path: Path = PREDICTION_TABLE_PATH
) -> None:
    """Save the final prediction table as a CSV report."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # ``index=False`` avoids writing pandas' internal row numbers into the CSV.
    prediction_df.to_csv(path, index=False)


def main(
    model_path: Path = MODEL_PATH,
    features_path: Path = FEATURES_PATH,
    output_path: Path = PREDICTION_TABLE_PATH,
) -> pd.DataFrame:
    """Run the full prediction workflow and return the output table."""

    model = load_model(model_path)
    features_df = load_features(features_path)
    prediction_df = generate_probabilities(model, features_df)
    save_prediction_table(prediction_df, output_path)
    print(f"Saved {len(prediction_df):,} prediction rows to {Path(output_path)}")
    return prediction_df


if __name__ == "__main__":
    main()
