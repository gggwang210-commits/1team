"""Phase 2-2b probability calibration CLI scaffold.

This file starts with a safe minimum implementation:
- define CLI options
- resolve MVP/global-style output paths
- print selected input and output paths

Later steps will add model loading, CalibratedClassifierCV, and report outputs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

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


def parse_args() -> argparse.Namespace:
    """Parse CLI options for MVP and global calibration runs."""
    parser = argparse.ArgumentParser(
        description="Prepare probability calibration paths for baseline models."
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
        help="Optional explicit output directory for calibration report files.",
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
        help="Calibration method to use later. Default: sigmoid.",
    )
    parser.add_argument(
        "--cv",
        type=int,
        default=3,
        help="Maximum CV folds to use later with CalibratedClassifierCV.",
    )
    parser.add_argument(
        "--n-bins",
        type=int,
        default=10,
        help="Number of bins to use later for calibration curve output.",
    )
    return parser.parse_args()


def main() -> None:
    """Print the selected calibration inputs and outputs."""
    args = parse_args()
    calibrated_model_path, report_dir = resolve_outputs(
        run_name=args.run_name,
        calibrated_model_path=args.calibrated_model_path,
        report_dir=args.report_dir,
    )

    print("Calibration CLI scaffold ready.")
    print(f"features_path: {args.features_path}")
    print(f"model_path: {args.model_path}")
    print(f"calibrated_model_path: {calibrated_model_path}")
    print(f"report_dir: {report_dir}")
    print(f"method: {args.method}")
    print(f"cv: {args.cv}")
    print(f"n_bins: {args.n_bins}")


if __name__ == "__main__":
    main()
