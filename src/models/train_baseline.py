"""Train a baseline classifier and save evaluation metrics.

This script creates a small, reproducible baseline for the project:
1. Load model-ready features from ``data/processed/features.csv``.
2. Train a scikit-learn classifier to predict the binary ``win`` target.
3. Evaluate predictions on a held-out test set.
4. Save metrics to ``reports/baseline_metrics.csv`` so ``evaluate.py`` can build
   the human-readable model evaluation report.

The current feature pipeline creates a binary target:
- ``1`` means the team won the match.
- ``0`` means the team drew or lost the match.

If the project later expands to a three-class Win/Draw/Loss target, the Brier
Score section below should be updated to use a clearly documented multiclass
variant, such as the mean squared distance between one-hot labels and predicted
class probabilities.
"""

from __future__ import annotations

from pathlib import Path
import pickle
import sys

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.make_features import (
    DEFAULT_OUTPUT_PATH as FEATURES_PATH,
    FEATURE_COLUMNS,
    main as build_features,
)
from src.models.evaluate import BASELINE_METRICS_PATH


MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
RANDOM_STATE = 42
TEST_SIZE = 0.25
TARGET_COLUMN = "win"


def _project_path(path: Path) -> Path:
    """Return an absolute project-root path for project-relative constants."""

    path = Path(path)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def load_or_create_features(features_path: Path = FEATURES_PATH) -> pd.DataFrame:
    """Load ``features.csv`` and create it first when it is missing.

    Keeping this fallback in the training script makes the beginner workflow more
    forgiving: after ``python src/data/build_dataset.py``, teammates can run this
    script directly without remembering the separate feature-engineering command.
    """

    features_path = Path(features_path)
    if not features_path.exists():
        print(
            f"Feature file not found at {features_path}. "
            "Creating it from the processed matches dataset first."
        )
        build_features(output_path=features_path)

    return pd.read_csv(features_path)


def prepare_training_data(features_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Select numeric feature columns and the binary target used for training."""

    missing_features = [column for column in FEATURE_COLUMNS if column not in features_df]
    if missing_features:
        raise ValueError(
            "features.csv is missing required model feature column(s): "
            f"{', '.join(missing_features)}. Recreate features.csv with "
            "python src/features/make_features.py."
        )
    if TARGET_COLUMN not in features_df:
        raise ValueError(
            f"features.csv is missing the required target column '{TARGET_COLUMN}'. "
            "The current baseline expects the binary win target produced by "
            "src/features/make_features.py."
        )

    # Coerce features and target to numeric values. Invalid values become NaN and
    # are handled explicitly below or by the model pipeline's SimpleImputer.
    X = features_df[FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(features_df[TARGET_COLUMN], errors="coerce")

    valid_target_rows = y.notna()
    X = X.loc[valid_target_rows]
    y = y.loc[valid_target_rows].astype(int)

    if X.empty:
        raise ValueError("No rows with a valid target were found for baseline training.")
    if y.nunique() < 2:
        raise ValueError(
            "Baseline training needs at least two target classes. The current "
            f"'{TARGET_COLUMN}' column contains only: {sorted(y.unique().tolist())}."
        )

    return X, y


def split_train_test(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = TEST_SIZE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Create a deterministic test split, using stratification when safe."""

    class_counts = y.value_counts()
    test_row_count = max(1, round(len(y) * test_size))
    train_row_count = len(y) - test_row_count
    class_count = y.nunique()

    # Stratification keeps the class ratio similar in train and test sets.  It is
    # only valid when both splits can contain every class at least once.
    can_stratify = (
        class_counts.min() >= 2
        and test_row_count >= class_count
        and train_row_count >= class_count
    )
    stratify = y if can_stratify else None

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )


def build_classifier(y_train: pd.Series) -> Pipeline | DummyClassifier:
    """Build a probability-capable baseline classifier.

    Logistic Regression is the preferred baseline because it is simple and
    provides ``predict_proba()``.  If a very small split leaves only one class in
    training data, we fall back to DummyClassifier so the script can still create
    metrics instead of crashing with a confusing scikit-learn error.
    """

    if y_train.nunique() < 2:
        return DummyClassifier(strategy="most_frequent")

    return Pipeline(
        steps=[
            # Missing rolling-history values are expected for a team's first few
            # matches. Median imputation lets the model train without dropping
            # those rows.
            ("imputer", SimpleImputer(strategy="median")),
            # Scaling helps Logistic Regression treat features with different
            # numeric ranges more evenly.
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(max_iter=1_000, random_state=RANDOM_STATE),
            ),
        ]
    )


def _positive_class_probability(classifier: object, probabilities) -> pd.Series:
    """Return the predicted probability for the positive binary class ``1``."""

    classes = list(getattr(classifier, "classes_", []))
    if 1 not in classes:
        raise ValueError(
            "Cannot compute binary Brier Score because the fitted classifier "
            "does not expose class label 1 in classes_."
        )

    positive_class_index = classes.index(1)
    return pd.Series(probabilities[:, positive_class_index])


def calculate_metrics(
    classifier: object,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, float | str | None]:
    """Calculate evaluation metrics with names expected by ``evaluate.py``."""

    predictions = classifier.predict(X_test)
    metrics: dict[str, float | str | None] = {
        "Model": "Logistic Regression Baseline"
        if not isinstance(classifier, DummyClassifier)
        else "Dummy Classifier Baseline",
        "Target Type": "Binary win target: 1=Win, 0=Draw/Loss",
        "Accuracy": accuracy_score(y_test, predictions),
        "Log Loss": None,
        "Brier Score": None,
    }

    if hasattr(classifier, "predict_proba"):
        probabilities = classifier.predict_proba(X_test)
        classes = list(getattr(classifier, "classes_", []))

        # Log Loss supports binary and multiclass probabilities when the labels
        # are supplied in the same order as the probability columns.
        metrics["Log Loss"] = log_loss(y_test, probabilities, labels=classes)

        # The current project target is binary.  Brier Score is therefore the
        # mean squared error between the true 0/1 outcome and P(class=1).
        if set(classes).issubset({0, 1}) and set(y_test.unique()).issubset({0, 1}):
            positive_probability = _positive_class_probability(classifier, probabilities)
            metrics["Brier Score"] = brier_score_loss(
                y_test.reset_index(drop=True), positive_probability
            )

    return metrics


def save_metrics(metrics: dict[str, float | str | None], path: Path) -> None:
    """Save one row of baseline metrics to ``reports/baseline_metrics.csv``."""

    path = _project_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    metrics_df = pd.DataFrame([metrics])
    metrics_df.to_csv(path, index=False)


def save_model(classifier: object, path: Path = MODEL_PATH) -> None:
    """Persist the fitted classifier for prediction workflows."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as model_file:
        pickle.dump(classifier, model_file)


def main() -> pd.DataFrame:
    """Run the complete baseline training and metric-generation workflow."""

    features_df = load_or_create_features()
    X, y = prepare_training_data(features_df)
    X_train, X_test, y_train, y_test = split_train_test(X, y)

    classifier = build_classifier(y_train)
    classifier.fit(X_train, y_train)

    metrics = calculate_metrics(classifier, X_test, y_test)
    save_metrics(metrics, BASELINE_METRICS_PATH)
    save_model(classifier)

    metrics_df = pd.DataFrame([metrics])
    print(f"Saved baseline metrics to {_project_path(BASELINE_METRICS_PATH)}")
    print(f"Saved fitted baseline model to {MODEL_PATH}")
    return metrics_df


if __name__ == "__main__":
    main()
