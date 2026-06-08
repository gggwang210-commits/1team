"""Train MVP Win/Draw/Loss baseline models.

This script reads the model-ready feature table, trains two simple baseline
classifiers, compares them with Accuracy and Macro F1, then saves the best
model and a metrics report.
"""

from __future__ import annotations

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

# The target may use either name depending on the feature engineering step.
TARGET_CANDIDATES = ("target_result", "target")

# If one of these columns exists, we use it to keep older matches in train and
# newer matches in test. This better matches real prediction usage.
DATE_CANDIDATES = ("date", "match_date", "game_date")

# Columns with these names are identifiers or known result-like fields, so they
# should not be used as model inputs. Keeping them out reduces leakage risk.
EXCLUDED_FEATURE_COLUMNS = {
    "target_result",
    "target",
    "date",
    "match_date",
    "game_date",
    "result",
    "score",
    "home_score",
    "away_score",
}


def load_features(path: Path = FEATURES_PATH) -> pd.DataFrame:
    """Load the prepared feature table from CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Feature file not found: {path}. Run the feature pipeline first."
        )
    return pd.read_csv(path)


def find_target_column(df: pd.DataFrame) -> str:
    """Return the first supported target column name found in the data."""
    for column in TARGET_CANDIDATES:
        if column in df.columns:
            return column
    raise ValueError(
        "Missing target column. Expected one of: "
        + ", ".join(TARGET_CANDIDATES)
    )


def find_date_column(df: pd.DataFrame) -> Optional[str]:
    """Return a supported date column name if one exists."""
    for column in DATE_CANDIDATES:
        if column in df.columns:
            return column
    return None


def validate_input_data(df: pd.DataFrame) -> str:
    """Check that the dataset has the columns and rows needed for training."""
    target_column = find_target_column(df)

    if df.empty:
        raise ValueError("Feature dataset is empty.")

    if df[target_column].isna().any():
        raise ValueError(f"Target column '{target_column}' contains missing values.")

    feature_columns = get_feature_columns(df)
    if not feature_columns:
        raise ValueError(
            "No usable feature columns found after removing target/date/result columns."
        )

    # Win/Draw/Loss is a multiclass task, so at least two classes are required.
    if df[target_column].nunique() < 2:
        raise ValueError(
            f"Target column '{target_column}' must contain at least two classes."
        )

    return target_column


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Choose model input columns while excluding targets, dates, and leakage."""
    return [
        column
        for column in df.columns
        if column not in EXCLUDED_FEATURE_COLUMNS
    ]


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
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, str]:
    """Create a train/test split, preferring chronological split when possible."""
    feature_columns = get_feature_columns(df)
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
        stratify = df[target_column] if df[target_column].value_counts().min() >= 2 else None
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
    return X_train, X_test, y_train, y_test, split_method


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
    X_train, X_test, y_train, y_test, split_method = split_train_test(df, target_column)

    best_model, metrics_df = train_and_evaluate(X_train, X_test, y_train, y_test)
    metrics_df.insert(1, "split_method", split_method)
    save_outputs(best_model, metrics_df)

    best_row = metrics_df.iloc[0]
    print("Baseline training complete.")
    print(f"Best model: {best_row['model']}")
    print(f"Macro F1: {best_row['macro_f1']:.4f}")
    print(f"Accuracy: {best_row['accuracy']:.4f}")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"Saved metrics to: {METRICS_PATH}")


if __name__ == "__main__":
    main()
