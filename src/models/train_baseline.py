"""Train a baseline Win/Draw/Loss classifier.

Data flow for the MVP:
1. ``src/features/make_features.py`` creates ``data/processed/features.csv``.
2. This script reads that feature table and uses ``team_result`` as the label.
3. A multinomial Logistic Regression pipeline is trained on numeric feature
   columns and saved to ``models/baseline_model.pkl``.
4. Basic evaluation metrics are saved to ``reports/baseline_metrics.csv``.
"""

from __future__ import annotations

from pathlib import Path
import pickle

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
METRICS_PATH = PROJECT_ROOT / "reports" / "baseline_metrics.csv"

# The feature list intentionally excludes identifiers, raw scores, and target
# labels.  Keeping the input schema explicit prevents accidental data leakage.
FEATURE_COLUMNS = [
    "win_rate_last_5",
    "win_rate_last_10",
    "avg_goals_for_last_5",
    "avg_goals_against_last_5",
    "goal_difference_last_5",
    "rank_difference",
    "neutral_flag",
]

# ``team_result`` is the row-level target: it is always from the current row's
# team perspective, even when the source match row was home-team oriented.
TARGET_COLUMN = "team_result"
CLASS_ORDER = ["Loss", "Draw", "Win"]
DEFAULT_TEST_SIZE = 0.25
RANDOM_STATE = 42


def load_features(path: str | Path = FEATURES_PATH) -> pd.DataFrame:
    """Load the model-ready feature table."""

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Feature file not found: {path}. Run "
            "python src/features/make_features.py before training."
        )
    return pd.read_csv(path)


def _normalize_target_label(value: object) -> object:
    """Normalize common result spellings to the project's three labels."""

    if pd.isna(value):
        return pd.NA

    normalized = str(value).strip().lower()
    if normalized in {"win", "w", "won", "team_win", "home_win", "2"}:
        return "Win"
    if normalized in {"draw", "d", "tie", "tied", "1"}:
        return "Draw"
    if normalized in {"loss", "lose", "lost", "l", "team_loss", "away_win", "0"}:
        return "Loss"

    raise ValueError(
        f"Unsupported target label: {value!r}. Expected one of Win, Draw, Loss "
        "or a known alias."
    )


def prepare_training_data(
    features_df: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
) -> tuple[pd.DataFrame, pd.Series]:
    """Validate columns, clean labels, and return ``X``/``y`` for training."""

    missing_features = [col for col in FEATURE_COLUMNS if col not in features_df.columns]
    if missing_features:
        raise ValueError(
            "features.csv is missing required model feature column(s): "
            f"{', '.join(missing_features)}. Recreate features.csv with "
            "python src/features/make_features.py."
        )
    if target_column not in features_df.columns:
        raise ValueError(
            f"features.csv must include '{target_column}' for 3-class training."
        )

    training_df = features_df.copy()
    training_df[target_column] = training_df[target_column].map(_normalize_target_label)
    training_df = training_df.dropna(subset=[target_column])

    if training_df.empty:
        raise ValueError(f"No rows with a non-empty '{target_column}' target were found.")

    observed_classes = set(training_df[target_column])
    missing_classes = set(CLASS_ORDER) - observed_classes
    if missing_classes:
        raise ValueError(
            "The baseline is a 3-class classifier, but the training data is "
            f"missing class(es): {', '.join(sorted(missing_classes))}."
        )

    X = training_df[FEATURE_COLUMNS]
    y = training_df[target_column]
    return X, y


def build_model() -> Pipeline:
    """Create a readable, reproducible baseline classification pipeline."""

    return Pipeline(
        steps=[
            # Rolling features are NaN for a team's first known match.  Median
            # imputation keeps those rows usable without leaking future results.
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1_000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def _split_train_test(
    X: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, str]:
    """Create a safe train/test split, with an in-sample fallback for tiny data."""

    class_counts = y.value_counts()
    can_stratify = len(y) >= 2 * len(class_counts) and class_counts.min() >= 2
    if not can_stratify:
        return X, X, y, y, "in_sample_tiny_dataset"

    # Stratified splits need at least one row per class in both train and test.
    test_size = max(DEFAULT_TEST_SIZE, len(class_counts) / len(y))
    test_size = min(test_size, 0.5)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    return X_train, X_test, y_train, y_test, "stratified_holdout"


def _multiclass_brier_score(
    y_true: pd.Series,
    probabilities: np.ndarray,
    classes: list[str],
) -> float:
    """Calculate multiclass Brier score as mean squared probability error."""

    class_to_index = {class_label: index for index, class_label in enumerate(classes)}
    one_hot = np.zeros_like(probabilities, dtype=float)
    for row_index, label in enumerate(y_true):
        one_hot[row_index, class_to_index[label]] = 1.0
    return float(np.mean(np.sum((probabilities - one_hot) ** 2, axis=1)))


def evaluate_model(
    model: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    split_strategy: str,
) -> pd.DataFrame:
    """Return beginner-friendly baseline metrics as a one-row DataFrame."""

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    classes = list(model.classes_)

    metrics = {
        "Target Column": TARGET_COLUMN,
        "Classes": ",".join(classes),
        "Split Strategy": split_strategy,
        "Rows Evaluated": len(y_test),
        "Accuracy": accuracy_score(y_test, predictions),
        "Macro F1": f1_score(y_test, predictions, average="macro", zero_division=0),
        "Log Loss": log_loss(y_test, probabilities, labels=classes),
        "Brier Score": _multiclass_brier_score(y_test, probabilities, classes),
    }
    return pd.DataFrame([metrics])


def save_model(model: Pipeline, path: str | Path = MODEL_PATH) -> None:
    """Persist the trained model artifact for prediction scripts."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as model_file:
        pickle.dump(model, model_file)


def save_metrics(metrics_df: pd.DataFrame, path: str | Path = METRICS_PATH) -> None:
    """Persist evaluation metrics for reports and project review."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(path, index=False)


def main(
    features_path: str | Path = FEATURES_PATH,
    model_path: str | Path = MODEL_PATH,
    metrics_path: str | Path = METRICS_PATH,
) -> Pipeline:
    """Train, evaluate, save, and return the baseline classifier."""

    features_df = load_features(features_path)
    X, y = prepare_training_data(features_df)
    X_train, X_test, y_train, y_test, split_strategy = _split_train_test(X, y)

    model = build_model()
    model.fit(X_train, y_train)

    metrics_df = evaluate_model(model, X_test, y_test, split_strategy)
    save_model(model, model_path)
    save_metrics(metrics_df, metrics_path)

    print(f"Trained baseline model on {len(X_train):,} rows using {TARGET_COLUMN}.")
    print(f"Saved model to {Path(model_path)}")
    print(f"Saved metrics to {Path(metrics_path)}")
    return model


if __name__ == "__main__":
    main()
