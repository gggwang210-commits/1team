"""Train MVP Win/Draw/Loss baseline models from Korea Republic's perspective.

This script reads the model-ready feature table, trains two simple baseline
classifiers, compares them with Accuracy and Macro F1, then saves the best
model and a metrics report.
"""

from __future__ import annotations

from math import ceil
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Project paths are kept in one place so beginners can change them easily.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
METRICS_PATH = PROJECT_ROOT / "reports" / "baseline_metrics.csv"

# The feature pipeline writes this stable column name from
# ``target_result_korea_perspective``. Keeping one explicit target avoids
# accidentally training on the home-team perspective label.
TARGET_COLUMN = "target_result"
SOURCE_TARGET_COLUMN = "target_result_korea_perspective"

# Baseline training is explicitly scoped to three soccer outcome labels.
# Keeping this as a set makes exact membership checks easy to read.
EXPECTED_TARGET_CLASSES = {"Win", "Draw", "Loss"}

# Default split used throughout this script. Validation uses the same value so
# users get a clear dataset-size message before scikit-learn is called.
DEFAULT_TEST_SIZE = 0.2

# If one of these columns exists, we use it to keep older matches in train and
# newer matches in test. This better matches real prediction usage.
DATE_CANDIDATES = ("date", "match_date", "game_date")

# Columns with these names are known result-like fields or targets, so they
# should never be used as model inputs. Keeping this list separate from date
# columns makes the leakage contract easy to audit when feature schemas change.
RESULT_LIKE_COLUMNS = {
    TARGET_COLUMN,
    SOURCE_TARGET_COLUMN,
    "target",
    "result",
    "score",
    "home_score",
    "away_score",
}

# Dates are useful for time-aware splitting but are not fed into the baseline
# models as predictive inputs.
DATE_COLUMNS = {"date", "match_date", "game_date"}

EXCLUDED_FEATURE_COLUMNS = RESULT_LIKE_COLUMNS | DATE_COLUMNS

# Team names are not direct match results, but they are high-cardinality team
# identifiers. On a tiny demo dataset, a model can memorize team-outcome patterns
# instead of learning generalizable ranking/context relationships. We therefore
# evaluate two explicit baseline variants so readers can compare both choices.
TEAM_IDENTIFIER_COLUMNS = {"home_team", "away_team"}
FEATURE_SET_RANKING_CONTEXT_ONLY = "ranking_context_only"
FEATURE_SET_WITH_TEAM_IDENTIFIERS = "with_team_identifiers"
FEATURE_SET_NAMES = (
    FEATURE_SET_RANKING_CONTEXT_ONLY,
    FEATURE_SET_WITH_TEAM_IDENTIFIERS,
)


def load_features(path: Path = FEATURES_PATH) -> pd.DataFrame:
    """Load the prepared feature table from CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Feature file not found: {path}. Run the feature pipeline first."
        )
    return pd.read_csv(path)


def find_target_column(df: pd.DataFrame) -> str:
    """Return the explicit Korea-perspective modeling target column name.

    ``features.csv`` may also retain ``target_result_korea_perspective`` as an
    audit column, but the model target remains ``target_result``. This function
    also guards the leakage contract: every result-like column must be listed in
    ``EXCLUDED_FEATURE_COLUMNS`` before training can proceed.
    """
    unexcluded_result_columns = RESULT_LIKE_COLUMNS - EXCLUDED_FEATURE_COLUMNS
    if unexcluded_result_columns:
        raise RuntimeError(
            "Result-like columns must be excluded from model inputs: "
            f"{sorted(unexcluded_result_columns)}."
        )

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Missing target column '{TARGET_COLUMN}'. Run src/features/make_features.py "
            f"so '{SOURCE_TARGET_COLUMN}' is copied into the model target."
        )

    if SOURCE_TARGET_COLUMN in df.columns:
        target_values = df[TARGET_COLUMN].astype(str).str.strip()
        source_values = df[SOURCE_TARGET_COLUMN].astype(str).str.strip()
        if not target_values.equals(source_values):
            raise ValueError(
                f"Audit column '{SOURCE_TARGET_COLUMN}' must match modeling target "
                f"'{TARGET_COLUMN}'. Regenerate features with src/features/make_features.py."
            )

    return TARGET_COLUMN


def find_date_column(df: pd.DataFrame) -> Optional[str]:
    """Return a supported date column name if one exists."""
    for column in DATE_CANDIDATES:
        if column in df.columns:
            return column
    return None


def validate_input_data(df: pd.DataFrame, test_size: float = DEFAULT_TEST_SIZE) -> str:
    """Check that the dataset has the columns, classes, and rows for training.

    This validation intentionally runs before scikit-learn. MVP datasets are
    often tiny, and clear messages here are much easier to understand than
    downstream errors from ``train_test_split`` or ``LogisticRegression``.
    """
    if df.empty:
        raise ValueError(
            "Feature dataset is empty. Expected data/processed/features.csv to "
            f"contain at least one row, the '{TARGET_COLUMN}' target column, and "
            "feature columns."
        )

    target_column = find_target_column(df)

    if df[target_column].isna().any():
        raise ValueError(
            f"Target column '{target_column}' contains missing values. Remove or "
            "label those rows before training."
        )

    # Validate label names before checking counts so data-quality errors are
    # reported directly instead of surfacing later as split or model errors.
    actual_target_classes = set(df[target_column].dropna().unique())
    missing_target_classes = EXPECTED_TARGET_CLASSES - actual_target_classes
    unexpected_target_classes = actual_target_classes - EXPECTED_TARGET_CLASSES
    if missing_target_classes or unexpected_target_classes:
        raise ValueError(
            f"Target column '{target_column}' must contain exactly these labels: "
            f"{sorted(EXPECTED_TARGET_CLASSES)}. "
            f"Missing labels: {sorted(missing_target_classes)}. "
            f"Unexpected labels: {sorted(unexpected_target_classes)}."
        )

    feature_sets_with_usable_columns = []
    for feature_set in FEATURE_SET_NAMES:
        feature_columns = get_feature_columns(df, feature_set=feature_set)
        usable_feature_columns = [
            column for column in feature_columns if not df[column].isna().all()
        ]
        if usable_feature_columns:
            feature_sets_with_usable_columns.append(feature_set)

    if not feature_sets_with_usable_columns:
        excluded_columns = EXCLUDED_FEATURE_COLUMNS | TEAM_IDENTIFIER_COLUMNS
        raise ValueError(
            "No usable feature columns found for any baseline feature set after "
            "excluding leakage columns "
            f"({', '.join(sorted(excluded_columns))}). Add at least one non-empty "
            "pre-match feature such as rank_diff, is_neutral, or is_korea_home."
        )

    class_counts = df[target_column].value_counts(dropna=False)
    class_count = len(class_counts)
    if class_count < 2:
        raise ValueError(
            f"Target column '{target_column}' must contain at least two classes "
            "before a classifier can be trained. Current class counts: "
            f"{class_counts.to_dict()}. For Win/Draw/Loss modeling, include examples "
            "from the expected Win, Draw, and Loss outcomes."
        )

    if class_counts.min() < 2:
        raise ValueError(
            "Not enough examples per target class for a reliable train/test split. "
            f"Each class needs at least 2 rows; current counts are {class_counts.to_dict()}. "
            "If this MVP dataset is intentionally tiny, add more labeled rows before "
            "running baseline training so every class can appear in both train and test."
        )

    minimum_rows = minimum_rows_for_split(class_count, test_size)
    if len(df) < minimum_rows:
        raise ValueError(
            "Not enough rows for the baseline train/test split. "
            f"With {class_count} target classes and test_size={test_size}, the dataset "
            f"needs at least {minimum_rows} rows so train and test can each contain all "
            f"classes. Current rows: {len(df)}. Current class counts: {class_counts.to_dict()}. "
            "For the default MVP Win/Draw/Loss setup, use at least 15 labeled matches "
            "with at least 2 examples per class."
        )

    return target_column


def minimum_rows_for_split(class_count: int, test_size: float) -> int:
    """Return rows needed so train and test can each include every class."""
    if not 0 < test_size < 1:
        raise ValueError("test_size must be a float between 0 and 1.")

    rows = class_count
    while (
        ceil(rows * test_size) < class_count
        or rows - ceil(rows * test_size) < class_count
    ):
        rows += 1
    return rows


def get_feature_columns(
    df: pd.DataFrame,
    feature_set: str = FEATURE_SET_WITH_TEAM_IDENTIFIERS,
) -> list[str]:
    """Choose model input columns for an explicit baseline feature set.

    Data flow note for beginners:
    - Every feature set excludes targets, dates, scores, and result-like fields.
    - ``ranking_context_only`` also excludes team names to reduce memorization risk.
    - ``with_team_identifiers`` keeps team names so we can measure that baseline
      separately and label its metrics clearly.
    """
    if feature_set not in FEATURE_SET_NAMES:
        raise ValueError(
            f"Unknown feature_set '{feature_set}'. Expected one of: "
            f"{', '.join(FEATURE_SET_NAMES)}."
        )

    excluded_columns = set(EXCLUDED_FEATURE_COLUMNS)
    if feature_set == FEATURE_SET_RANKING_CONTEXT_ONLY:
        excluded_columns.update(TEAM_IDENTIFIER_COLUMNS)

    return [column for column in df.columns if column not in excluded_columns]


def make_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    """Build preprocessing for numeric and categorical columns.

    Numeric values are median-imputed and scaled for Logistic Regression.
    Text/category values are filled with the most common value and one-hot
    encoded so scikit-learn models can read them.
    """
    numeric_columns = X.select_dtypes(include="number").columns.tolist()
    categorical_columns = [
        column for column in X.columns if column not in numeric_columns
    ]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )


def split_train_test(
    df: pd.DataFrame,
    target_column: str,
    feature_columns: list[str],
    test_size: float = DEFAULT_TEST_SIZE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, str]:
    """Create a train/test split, preferring chronological split when possible."""
    if not feature_columns:
        raise ValueError("At least one feature column is required for training.")

    date_column = find_date_column(df)

    # If a date column exists, sort by date and test on the most recent rows.
    if date_column is not None:
        dated_df = df.copy()
        dated_df[date_column] = pd.to_datetime(dated_df[date_column], errors="coerce")
        if dated_df[date_column].isna().any():
            raise ValueError(f"Date column '{date_column}' contains invalid dates.")

        dated_df = dated_df.sort_values(date_column).reset_index(drop=True)
        split_index = int(len(dated_df) * (1 - test_size))
        if split_index <= 0 or split_index >= len(dated_df):
            raise ValueError("Not enough rows to create a date-based train/test split.")

        train_df = dated_df.iloc[:split_index]
        test_df = dated_df.iloc[split_index:]
        split_method = f"date_based:{date_column}"
    else:
        # Without dates, use a reproducible random split. Stratify keeps class
        # proportions similar when each class has enough samples.
        stratify = (
            df[target_column] if df[target_column].value_counts().min() >= 2 else None
        )
        train_df, test_df = train_test_split(
            df,
            test_size=test_size,
            random_state=42,
            stratify=stratify,
        )
        split_method = "random_stratified" if stratify is not None else "random"

    X_train = train_df[feature_columns]
    X_test = test_df[feature_columns]
    y_train = train_df[target_column]
    y_test = test_df[target_column]
    validate_split_data(y_train, y_test, split_method)
    return X_train, X_test, y_train, y_test, split_method


def validate_split_data(
    y_train: pd.Series,
    y_test: pd.Series,
    split_method: str,
) -> None:
    """Confirm the split is trainable before fitting scikit-learn models."""
    if y_train.empty or y_test.empty:
        raise ValueError(
            f"The {split_method} split produced an empty train or test set. "
            "Add more rows to data/processed/features.csv before training."
        )

    if y_train.nunique() < 2:
        raise ValueError(
            f"The {split_method} split left the training set with fewer than two "
            f"target classes: {y_train.value_counts().to_dict()}. LogisticRegression "
            "requires at least two classes in training data. Add more labeled rows "
            "or adjust the date distribution so multiple outcomes appear in train."
        )


def build_models(X_train: pd.DataFrame) -> dict[str, Pipeline]:
    """Create baseline models that share the same preprocessing steps."""
    return {
        "LogisticRegression": Pipeline(
            steps=[
                ("preprocessor", make_preprocessor(X_train)),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1_000,
                        random_state=42,
                    ),
                ),
            ]
        ),
        "RandomForestClassifier": Pipeline(
            steps=[
                ("preprocessor", make_preprocessor(X_train)),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=200,
                        random_state=42,
                        class_weight="balanced",
                    ),
                ),
            ]
        ),
    }


def train_and_evaluate(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    feature_set: str,
) -> tuple[Pipeline, pd.DataFrame]:
    """Train each model and return the best model plus a metrics table."""
    metrics: list[dict[str, float | str]] = []
    trained_models: dict[str, Pipeline] = {}

    for model_name, model in build_models(X_train).items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        accuracy = accuracy_score(y_test, predictions)
        macro_f1 = f1_score(y_test, predictions, average="macro", zero_division=0)

        trained_models[model_name] = model
        metrics.append(
            {
                "model": model_name,
                "feature_set": feature_set,
                "accuracy": accuracy,
                "macro_f1": macro_f1,
            }
        )

    metrics_df = pd.DataFrame(metrics).sort_values(
        by=["macro_f1", "accuracy"], ascending=False
    )
    best_model_name = metrics_df.iloc[0]["model"]
    return trained_models[best_model_name], metrics_df


def save_outputs(best_model: Pipeline, metrics_df: pd.DataFrame) -> None:
    """Save the selected model artifact and evaluation metrics."""
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(best_model, MODEL_PATH)
    metrics_df.to_csv(METRICS_PATH, index=False)


def main() -> None:
    """Run the full MVP baseline training workflow."""
    df = load_features()
    target_column = validate_input_data(df)

    all_metrics: list[pd.DataFrame] = []
    best_models: dict[tuple[str, str], Pipeline] = {}

    for feature_set in FEATURE_SET_NAMES:
        feature_columns = get_feature_columns(df, feature_set=feature_set)
        X_train, X_test, y_train, y_test, split_method = split_train_test(
            df,
            target_column,
            feature_columns,
        )
        best_model, metrics_df = train_and_evaluate(
            X_train,
            X_test,
            y_train,
            y_test,
            feature_set,
        )
        metrics_df.insert(2, "split_method", split_method)
        all_metrics.append(metrics_df)

        best_row_for_feature_set = metrics_df.iloc[0]
        best_models[(feature_set, best_row_for_feature_set["model"])] = best_model

    combined_metrics_df = pd.concat(all_metrics, ignore_index=True).sort_values(
        by=["macro_f1", "accuracy"], ascending=False
    )
    best_row = combined_metrics_df.iloc[0]
    best_model = best_models[(best_row["feature_set"], best_row["model"])]
    save_outputs(best_model, combined_metrics_df)

    print("Baseline training complete.")
    print(f"Best model: {best_row['model']}")
    print(f"Best feature set: {best_row['feature_set']}")
    print(f"Macro F1: {best_row['macro_f1']:.4f}")
    print(f"Accuracy: {best_row['accuracy']:.4f}")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved metrics to: {METRICS_PATH}")


if __name__ == "__main__":
    main()
