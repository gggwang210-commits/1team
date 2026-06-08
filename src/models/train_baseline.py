"""Train and save the baseline match-result classifier.

Data flow
---------
1. Read ``data/processed/features.csv`` created by ``src/features/make_features.py``.
2. Select the same model-ready feature columns that prediction will later pass
   through ``model.feature_names_in_``.
3. Fit a scikit-learn ``Pipeline`` on a pandas DataFrame so feature names are
   preserved in the saved model artifact.
4. Save the fitted pipeline to ``models/baseline_model.pkl`` for
   ``src/models/predict.py``.
"""

from __future__ import annotations

from pathlib import Path
import pickle
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features.make_features import FEATURE_COLUMNS
from src.models.predict import FEATURES_PATH, MODEL_PATH

RANDOM_STATE = 42
TARGET_COLUMN = "win"


def load_training_features(path: Path = FEATURES_PATH) -> pd.DataFrame:
    """Load the engineered feature table used for baseline training.

    Args:
        path: CSV path created by ``src/features/make_features.py``.

    Returns:
        A pandas DataFrame containing identifiers, target columns, and numeric
        model features.

    Raises:
        FileNotFoundError: If the engineered feature CSV does not exist yet.
    """

    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            "Required training feature file was not found: "
            f"{path}. Run python src/features/make_features.py first."
        )

    return pd.read_csv(path)


def select_training_data(features_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """Split the feature table into model inputs ``X`` and target ``y``.

    Keeping ``X`` as a pandas DataFrame is intentional: scikit-learn stores
    ``feature_names_in_`` when fitting with named DataFrame columns.  The
    prediction script then reads that attribute and selects columns in the same
    order before calling ``predict_proba``.
    """

    missing_feature_columns = [
        column for column in FEATURE_COLUMNS if column not in features_df.columns
    ]
    if missing_feature_columns:
        raise ValueError(
            "features.csv is missing required model feature column(s): "
            f"{', '.join(missing_feature_columns)}. Recreate it with "
            "python src/features/make_features.py."
        )

    if TARGET_COLUMN not in features_df.columns:
        raise ValueError(
            "features.csv must include a 'win' target column for baseline "
            "training. Recreate it with python src/features/make_features.py."
        )

    # Copy only the stable feature contract used by feature engineering.  Avoid
    # identifiers (team/date) and result columns (goals/win) to reduce leakage.
    X = features_df[FEATURE_COLUMNS].copy()
    y = pd.to_numeric(features_df[TARGET_COLUMN], errors="coerce")

    valid_target_rows = y.notna()
    if not valid_target_rows.all():
        dropped_rows = int((~valid_target_rows).sum())
        print(
            "Dropping "
            f"{dropped_rows} row(s) because the training target is missing."
        )
        X = X.loc[valid_target_rows].copy()
        y = y.loc[valid_target_rows]

    y = y.astype(int)
    if X.empty:
        raise ValueError("No training rows are available after target validation.")
    if y.nunique() < 2:
        raise ValueError(
            "Baseline training needs at least two target classes in the 'win' "
            "column. Add more processed match data before training."
        )

    return X, y


def build_baseline_model() -> Pipeline:
    """Create a simple, readable scikit-learn baseline classifier pipeline.

    The pipeline handles missing feature values with median imputation, scales
    numeric features for Logistic Regression, and then estimates win
    probabilities with ``predict_proba``.
    """

    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1_000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def train_model(X: pd.DataFrame, y: pd.Series) -> Pipeline:
    """Fit the baseline model using the selected pandas feature DataFrame."""

    model = build_baseline_model()

    # Fitting with a DataFrame preserves feature_names_in_ on the Pipeline.  This
    # makes prediction safer because predict.py can select the exact same columns.
    model.fit(X, y)
    return model


def save_model(model: Pipeline, path: Path = MODEL_PATH) -> None:
    """Persist the fitted model artifact for the prediction workflow."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Only load this pickle in trusted project environments.  Pickle is suitable
    # for local scikit-learn artifacts but is not a secure interchange format.
    with path.open("wb") as model_file:
        pickle.dump(model, model_file)


def main(
    features_path: Path = FEATURES_PATH,
    model_path: Path = MODEL_PATH,
) -> Pipeline:
    """Run baseline training and save ``models/baseline_model.pkl``."""

    features_df = load_training_features(features_path)
    X, y = select_training_data(features_df)
    model = train_model(X, y)
    save_model(model, model_path)

    print(
        "Saved baseline model trained on "
        f"{len(X):,} rows and {len(X.columns):,} features to {Path(model_path)}"
    )
    return model


if __name__ == "__main__":
    main()
