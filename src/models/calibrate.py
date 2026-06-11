"""Phase 2-2b probability calibration workflow.

Current implementation:
- define CLI options
- resolve MVP/global-style output paths
- load the selected baseline model
- fit a CalibratedClassifierCV model
- save the calibrated model artifact
- write calibration metrics, curve data, and a summary report
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import log_loss

from train_baseline import (
    DEFAULT_TEST_SIZE,
    calculate_multiclass_brier_score,
    get_feature_columns,
    load_features,
    split_train_test,
    validate_input_data,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "baseline_model.pkl"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_CALIBRATED_MODEL_PATH = MODELS_DIR / "calibrated_model.pkl"
DEFAULT_REPORT_DIR = REPORTS_DIR / "calibration_report"
METHOD_CHOICES = ("sigmoid", "isotonic")


def validate_run_name(run_name: str) -> str:
    """Validate a run name before turning it into output paths."""
    cleaned = run_name.strip()
    if not cleaned:
        raise ValueError("--run-name cannot be empty or whitespace.")
    if "/" in cleaned or "\\" in cleaned:
        raise ValueError("--run-name cannot contain path separators '/' or '\\'.")
    return cleaned


def resolve_outputs(
    run_name: str | None,
    calibrated_model_path: Path | None,
    report_dir: Path | None,
) -> tuple[Path, Path]:
    """Resolve output paths from explicit paths, run name, or MVP defaults."""
    if run_name:
        safe_run_name = validate_run_name(run_name)
        calibrated_model_path = (
            calibrated_model_path
            or MODELS_DIR / f"{safe_run_name}_calibrated_model.pkl"
        )
        report_dir = report_dir or REPORTS_DIR / f"{safe_run_name}_calibration_report"

    return (
        calibrated_model_path or DEFAULT_CALIBRATED_MODEL_PATH,
        report_dir or DEFAULT_REPORT_DIR,
    )


def load_baseline_model(model_path: Path):
    """Load the selected baseline model and validate probability support."""
    if not model_path.exists():
        raise FileNotFoundError(
            f"Baseline model not found: {model_path}. "
            "Run src/models/train_baseline.py first."
        )

    model = joblib.load(model_path)
    if not hasattr(model, "predict_proba"):
        raise TypeError(
            f"Loaded model from {model_path} does not support predict_proba(). "
            "Probability calibration requires a probability-capable classifier."
        )
    return model


def expected_feature_columns(model, features: pd.DataFrame) -> list[str]:
    """Infer feature columns from the trained baseline model when possible."""
    if hasattr(model, "feature_names_in_"):
        return [str(column) for column in model.feature_names_in_]

    preprocessor = getattr(model, "named_steps", {}).get("preprocessor")
    if preprocessor is not None and hasattr(preprocessor, "feature_names_in_"):
        return [str(column) for column in preprocessor.feature_names_in_]

    return get_feature_columns(features)


def choose_cv_folds(y_train: pd.Series, requested_cv: int) -> int:
    """Choose a safe CV fold count based on the smallest class count."""
    if requested_cv < 2:
        raise ValueError("--cv must be at least 2 for probability calibration.")

    class_counts = y_train.value_counts()
    cv_folds = min(requested_cv, int(class_counts.min()))
    if cv_folds < 2:
        raise ValueError(
            "Not enough training rows per class for calibration. "
            f"Current training class counts: {class_counts.to_dict()}."
        )
    return cv_folds


def make_calibrator(model, method: str, cv_folds: int):
    """Create CalibratedClassifierCV with sklearn version compatibility."""
    try:
        return CalibratedClassifierCV(estimator=model, method=method, cv=cv_folds)
    except TypeError:
        return CalibratedClassifierCV(base_estimator=model, method=method, cv=cv_folds)


def probability_metrics(model, X_test: pd.DataFrame, y_test: pd.Series) -> dict[str, float]:
    """Return probability-quality metrics for a fitted model."""
    probabilities = model.predict_proba(X_test)
    class_labels = np.asarray(model.classes_)
    return {
        "log_loss": float(log_loss(y_test, probabilities, labels=class_labels)),
        "brier_score": calculate_multiclass_brier_score(
            y_true=y_test,
            probability_matrix=probabilities,
            class_labels=class_labels,
        ),
    }


def calibration_curve_rows(
    model_name: str,
    y_true: pd.Series,
    probabilities: np.ndarray,
    class_labels: np.ndarray,
    n_bins: int,
) -> list[dict[str, object]]:
    """Build one-vs-rest calibration curve rows for each class."""
    if n_bins < 2:
        raise ValueError("--n-bins must be at least 2.")

    rows: list[dict[str, object]] = []
    bin_edges = np.linspace(0.0, 1.0, n_bins + 1)
    y_array = np.asarray(y_true)

    for class_index, class_label in enumerate(class_labels):
        predicted = probabilities[:, class_index]
        observed = (y_array == class_label).astype(float)

        for bin_index in range(n_bins):
            left = bin_edges[bin_index]
            right = bin_edges[bin_index + 1]
            if bin_index == n_bins - 1:
                mask = (predicted >= left) & (predicted <= right)
            else:
                mask = (predicted >= left) & (predicted < right)

            sample_count = int(mask.sum())
            if sample_count == 0:
                continue

            rows.append(
                {
                    "model": model_name,
                    "class_label": class_label,
                    "bin_index": bin_index,
                    "sample_count": sample_count,
                    "mean_predicted_probability": float(predicted[mask].mean()),
                    "observed_frequency": float(observed[mask].mean()),
                }
            )
    return rows


def fit_calibrated_model(
    features_path: Path,
    baseline_model,
    method: str,
    requested_cv: int,
):
    """Fit and return uncalibrated and calibrated models plus test data."""
    features = load_features(features_path)
    target_column = validate_input_data(features)
    feature_columns = expected_feature_columns(baseline_model, features)

    missing_columns = [column for column in feature_columns if column not in features.columns]
    if missing_columns:
        raise ValueError(
            "Selected feature file is missing columns expected by the baseline model: "
            + ", ".join(missing_columns)
        )

    X_train, X_test, y_train, y_test, split_method = split_train_test(
        features,
        target_column,
        feature_columns,
        test_size=DEFAULT_TEST_SIZE,
    )
    cv_folds = choose_cv_folds(y_train, requested_cv=requested_cv)

    uncalibrated_model = clone(baseline_model)
    uncalibrated_model.fit(X_train, y_train)

    calibrator = make_calibrator(
        model=clone(baseline_model),
        method=method,
        cv_folds=cv_folds,
    )
    calibrator.fit(X_train, y_train)
    return (
        uncalibrated_model,
        calibrator,
        X_test,
        y_test,
        split_method,
        cv_folds,
        feature_columns,
    )


def write_calibration_report(
    report_dir: Path,
    metrics_df: pd.DataFrame,
    curve_df: pd.DataFrame,
    summary: dict[str, object],
) -> None:
    """Write calibration metrics, curve data, and markdown summary."""
    report_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = report_dir / "calibration_metrics.csv"
    curve_path = report_dir / "calibration_curve.csv"
    summary_path = report_dir / "summary.md"

    metrics_df.to_csv(metrics_path, index=False)
    curve_df.to_csv(curve_path, index=False)

    lines = [
        "# Calibration Report",
        "",
        "Generated by `python src/models/calibrate.py`.",
        "",
        "## Run Metadata",
        "",
        f"- Features path: `{summary['features_path']}`",
        f"- Baseline model path: `{summary['model_path']}`",
        f"- Calibrated model path: `{summary['calibrated_model_path']}`",
        f"- Method: `{summary['method']}`",
        f"- CV folds: {summary['cv_folds']}",
        f"- Split method: `{summary['split_method']}`",
        f"- Feature column count: {summary['feature_column_count']}",
        "",
        "## Metrics",
        "",
        metrics_df.to_markdown(index=False),
        "",
        "## Notes",
        "",
        "- Lower Log Loss is better.",
        "- Lower Brier Score is better.",
        "- Calibration curve data is saved to `calibration_curve.csv`.",
        "- This step checks probability quality before tournament simulation.",
        "",
    ]
    summary_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse CLI options for MVP and global calibration runs."""
    parser = argparse.ArgumentParser(
        description="Fit a calibrated probability model from a baseline model."
    )
    parser.add_argument(
        "--features-path",
        type=Path,
        default=FEATURES_PATH,
        help="Feature CSV used for calibration. Default: data/processed/features.csv.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=MODEL_PATH,
        help="Baseline model .pkl used for calibration. Default: models/baseline_model.pkl.",
    )
    parser.add_argument(
        "--calibrated-model-path",
        type=Path,
        default=None,
        help="Optional explicit output path for the calibrated model .pkl file.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="Optional explicit output directory for future calibration report files.",
    )
    parser.add_argument(
        "--run-name",
        default=None,
        help=(
            "Optional safe run name. Example: --run-name global_baseline writes "
            "models/global_baseline_calibrated_model.pkl and "
            "reports/global_baseline_calibration_report/."
        ),
    )
    parser.add_argument(
        "--method",
        choices=METHOD_CHOICES,
        default="sigmoid",
        help="Calibration method. Default: sigmoid.",
    )
    parser.add_argument(
        "--cv",
        type=int,
        default=3,
        help="Maximum CV folds to use with CalibratedClassifierCV.",
    )
    parser.add_argument(
        "--n-bins",
        type=int,
        default=10,
        help="Number of bins to use for calibration curve output.",
    )
    return parser.parse_args()


def main() -> None:
    """Load baseline model, fit calibrated model, save artifact, and write reports."""
    args = parse_args()
    calibrated_model_path, report_dir = resolve_outputs(
        run_name=args.run_name,
        calibrated_model_path=args.calibrated_model_path,
        report_dir=args.report_dir,
    )
    baseline_model = load_baseline_model(args.model_path)
    (
        uncalibrated_model,
        calibrated_model,
        X_test,
        y_test,
        split_method,
        cv_folds,
        feature_columns,
    ) = fit_calibrated_model(
        features_path=args.features_path,
        baseline_model=baseline_model,
        method=args.method,
        requested_cv=args.cv,
    )

    calibrated_model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrated_model, calibrated_model_path)

    uncalibrated_metrics = probability_metrics(uncalibrated_model, X_test, y_test)
    calibrated_metrics = probability_metrics(calibrated_model, X_test, y_test)
    metrics_df = pd.DataFrame(
        [
            {
                "model": "uncalibrated_baseline",
                "method": "none",
                "split_method": split_method,
                **uncalibrated_metrics,
            },
            {
                "model": "calibrated_baseline",
                "method": args.method,
                "split_method": split_method,
                **calibrated_metrics,
            },
        ]
    )

    curve_df = pd.DataFrame(
        calibration_curve_rows(
            "uncalibrated_baseline",
            y_test,
            uncalibrated_model.predict_proba(X_test),
            np.asarray(uncalibrated_model.classes_),
            args.n_bins,
        )
        + calibration_curve_rows(
            "calibrated_baseline",
            y_test,
            calibrated_model.predict_proba(X_test),
            np.asarray(calibrated_model.classes_),
            args.n_bins,
        )
    )
    write_calibration_report(
        report_dir=report_dir,
        metrics_df=metrics_df,
        curve_df=curve_df,
        summary={
            "features_path": args.features_path.as_posix(),
            "model_path": args.model_path.as_posix(),
            "calibrated_model_path": calibrated_model_path.as_posix(),
            "method": args.method,
            "cv_folds": cv_folds,
            "split_method": split_method,
            "feature_column_count": len(feature_columns),
        },
    )

    print("Calibration workflow complete.")
    print("Baseline model loaded successfully.")
    print("Calibrated model fitted successfully.")
    print(f"baseline_model_type: {type(baseline_model).__name__}")
    print(f"calibrated_model_type: {type(calibrated_model).__name__}")
    print(f"features_path: {args.features_path}")
    print(f"model_path: {args.model_path}")
    print(f"calibrated_model_path: {calibrated_model_path}")
    print(f"report_dir: {report_dir}")
    print(f"method: {args.method}")
    print(f"cv_requested: {args.cv}")
    print(f"cv_used: {cv_folds}")
    print(f"split_method: {split_method}")
    print(f"feature_column_count: {len(feature_columns)}")
    print(f"n_bins: {args.n_bins}")
    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
