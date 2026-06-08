"""Train and save the MVP baseline classification model.

Data flow for beginners:
1. Read ``data/processed/features.csv`` created by ``src/features/make_features.py``.
2. Use the binary ``win`` column as the first MVP target label.
3. Remove identifiers and target/result columns so the model cannot memorize answers.
4. Train a scikit-learn Pipeline that imputes missing values and fits Logistic Regression.
5. Save the trained model and a small metrics table for downstream scripts.
"""

from __future__ import annotations

from pathlib import Path
import pickle

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
METRICS_PATH = PROJECT_ROOT / "reports" / "baseline_metrics.csv"

# MVP decision: make_features.py currently guarantees a binary ``win`` label.
# A future three-class Win/Draw/Loss model can be added once feature generation
# consistently provides a non-leaky result column such as ``target_result``.
TARGET_COLUMN = "win"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Human-readable columns that identify a row but should not be model inputs.
IDENTIFIER_COLUMNS = {
    "date",
    "match_date",
    "team",
    "opponent",
    "home_team",
    "away_team",
    "venue_side",
    "source_row",
}

# Columns that directly describe the answer or final score.  Keeping these out
# prevents target leakage, where the model sees information unavailable before a
# future match is played.
TARGET_LIKE_COLUMNS = {
    TARGET_COLUMN,
    "target",
    "label",
    "result",
    "outcome",
    "target_result",
    "goals_for",
    "goals_against",
    "home_goals",
    "away_goals",
    "score",
}


def load_features(path: str | Path = FEATURES_PATH) -> pd.DataFrame:
    """Load the model-ready feature table from CSV.

    Raises a clear beginner-friendly error when the feature file is missing or
    empty, because pandas/scikit-learn stack traces can be difficult to parse.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "Feature file was not found at "
            f"'{path}'. Run `python src/features/make_features.py` first to "
            "create data/processed/features.csv."
        )

    features = pd.read_csv(path)
    if features.empty:
        raise ValueError(
            f"Feature file '{path}' is empty. Add processed match rows before training."
        )

    return features


def build_target(features: pd.DataFrame, target_column: str = TARGET_COLUMN) -> pd.Series:
    """Return the MVP target label used for training.

    For this project iteration we intentionally choose binary ``win`` because
    it is created by ``make_features.py`` and is already compatible with the
    downstream prediction code.  The values must contain both classes (0 and 1)
    so that a classifier can learn a decision boundary.
    """

    if target_column not in features.columns:
        raise ValueError(
            f"Missing required target column '{target_column}' in features.csv. "
            "Regenerate features with `python src/features/make_features.py`, "
            "or update train_baseline.py if you intentionally changed the target."
        )

    target = pd.to_numeric(features[target_column], errors="coerce")
    if target.isna().any():
        bad_count = int(target.isna().sum())
        raise ValueError(
            f"Target column '{target_column}' contains {bad_count} non-numeric or "
            "missing value(s). Clean the target before training."
        )

    target = target.astype(int)
    unexpected_values = sorted(set(target.unique()) - {0, 1})
    if unexpected_values:
        raise ValueError(
            f"Target column '{target_column}' must be binary 0/1 for the MVP, "
            f"but found unexpected value(s): {unexpected_values}."
        )

    if target.nunique() < 2:
        raise ValueError(
            f"Target column '{target_column}' has only one class. A classifier "
            "needs both wins and non-wins to train a useful baseline."
        )

    return target


def select_numeric_feature_columns(features: pd.DataFrame) -> list[str]:
    """Choose numeric model inputs after excluding identifiers and labels."""

    blocked_columns = IDENTIFIER_COLUMNS | TARGET_LIKE_COLUMNS
    candidate_columns = [
        column for column in features.columns if column not in blocked_columns
    ]

    # Logistic Regression can only consume numeric values in this simple MVP.
    # Non-numeric categorical fields should be encoded in a future iteration.
    numeric_columns = (
        features[candidate_columns]
        .select_dtypes(include=["number", "bool"])
        .columns.tolist()
    )

    if not numeric_columns:
        excluded = ", ".join(sorted(blocked_columns & set(features.columns)))
        raise ValueError(
            "No numeric feature columns were available after excluding "
            f"identifier/target-like columns ({excluded}). Add numeric features "
            "in src/features/make_features.py before training."
        )

    return numeric_columns


def split_train_test(
    x: pd.DataFrame,
    y: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split rows into train/test sets with safe stratification when possible."""

    class_counts = y.value_counts()
    stratify = y if class_counts.min() >= 2 else None

    if len(y) < 5:
        raise ValueError(
            "Not enough rows to create a reliable train/test split. Need at "
            "least 5 feature rows for this MVP training script."
        )

    return train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )


def build_pipeline() -> Pipeline:
    """Create the baseline preprocessing + model pipeline."""

    return Pipeline(
        steps=[
            # Missing rolling-history values are common for a team's first few
            # matches.  Median imputation is simple and robust for numeric data.
            ("imputer", SimpleImputer(strategy="median")),
            # Logistic Regression is a readable first baseline with probability
            # estimates for accuracy, log loss, and Brier score evaluation.
            (
                "classifier",
                LogisticRegression(max_iter=1_000, random_state=RANDOM_STATE),
            ),
        ]
    )


def evaluate_model(
    model: Pipeline,
    x_test: pd.DataFrame,
    y_test: pd.Series,
) -> dict[str, float]:
    """Calculate MVP metrics on the held-out test set."""

    predictions = model.predict(x_test)
    probabilities = model.predict_proba(x_test)
    positive_class_index = list(model.classes_).index(1)
    win_probabilities = probabilities[:, positive_class_index]

    return {
        "Accuracy": accuracy_score(y_test, predictions),
        "Log Loss": log_loss(y_test, probabilities, labels=model.classes_),
        "Brier Score": brier_score_loss(y_test, win_probabilities),
    }


def save_model(model: Pipeline, path: str | Path = MODEL_PATH) -> None:
    """Save the fitted model for predict.py.

    The downstream script uses pickle.load, so this training script writes the
    model with pickle.dump for a matching read/write pair.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as model_file:
        pickle.dump(model, model_file)


def save_metrics(
    metrics: dict[str, float],
    feature_columns: list[str],
    train_rows: int,
    test_rows: int,
    path: str | Path = METRICS_PATH,
) -> None:
    """Save one-row metrics CSV for reports/evaluate.py."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    metrics_row = {
        "Target": TARGET_COLUMN,
        "Model": "LogisticRegression",
        "Train Rows": train_rows,
        "Test Rows": test_rows,
        "Feature Count": len(feature_columns),
        **metrics,
    }
    pd.DataFrame([metrics_row]).to_csv(path, index=False)


def train_baseline(
    features_path: str | Path = FEATURES_PATH,
    model_path: str | Path = MODEL_PATH,
    metrics_path: str | Path = METRICS_PATH,
) -> Pipeline:
    """Run the complete baseline training pipeline and return the fitted model."""

    # Step 1: Load the prepared data table.
    features = load_features(features_path)

    # Step 2: Build the binary MVP target from the guaranteed ``win`` column.
    target = build_target(features)

    # Step 3: Keep only safe numeric feature columns for model input.
    feature_columns = select_numeric_feature_columns(features)
    x = features[feature_columns]

    # Step 4: Hold out test rows so metrics estimate performance on unseen data.
    x_train, x_test, y_train, y_test = split_train_test(x, target)

    # Step 5: Build and fit the preprocessing + classifier pipeline.
    model = build_pipeline()
    model.fit(x_train, y_train)

    # Step 6: Evaluate before saving so broken probability outputs fail early.
    metrics = evaluate_model(model, x_test, y_test)

    # Step 7: Save artifacts for downstream prediction and reporting scripts.
    save_model(model, model_path)
    save_metrics(metrics, feature_columns, len(x_train), len(x_test), metrics_path)

    print(f"Trained baseline model with {len(feature_columns)} numeric feature(s).")
    print(f"Saved model to {Path(model_path)}")
    print(f"Saved metrics to {Path(metrics_path)}")
    return model


def main() -> Pipeline:
    """Command-line entry point."""

    return train_baseline()


if __name__ == "__main__":
    main()
