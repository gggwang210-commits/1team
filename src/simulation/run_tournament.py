"""Phase 3-2 tournament simulation CLI scaffold.

This scaffold intentionally does not run tournament simulation yet.
It only validates input paths, parses tournament JSON files, and prints the
selected input/output contract so the next implementation step can safely add
simulation logic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARTICIPANTS_PATH = PROJECT_ROOT / "data" / "tournament" / "participants.json"
DEFAULT_SCHEDULE_PATH = PROJECT_ROOT / "data" / "tournament" / "schedule.json"
DEFAULT_BRACKET_PATH = PROJECT_ROOT / "data" / "tournament" / "bracket.json"
DEFAULT_FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features_global.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "global_baseline_calibrated_model.pkl"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_OUTPUT_DIR = DEFAULT_REPORTS_DIR / "simulation_global"


def validate_run_name(run_name: str) -> str:
    """Validate a run name before using it in generated output paths."""
    cleaned = run_name.strip()
    if not cleaned:
        raise ValueError("--run-name cannot be empty or whitespace.")
    if "/" in cleaned or "\\" in cleaned:
        raise ValueError("--run-name cannot contain path separators '/' or '\\'.")
    return cleaned


def load_json_file(path: Path, label: str) -> dict:
    """Load a JSON file and provide clear beginner-friendly errors."""
    if not path.exists():
        raise FileNotFoundError(f"{label} file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"{label} file is not valid JSON: {path}. "
            f"JSON error: {error.msg} at line {error.lineno}, column {error.colno}."
        ) from error

    if not isinstance(data, dict):
        raise ValueError(f"{label} JSON must contain an object at the top level: {path}")
    return data


def validate_existing_file(path: Path, label: str, required: bool = True) -> None:
    """Validate a file path when the current scaffold requires it."""
    if required and not path.exists():
        raise FileNotFoundError(f"{label} file not found: {path}")


def resolve_output_dir(run_name: str, output_dir: Path | None) -> Path:
    """Resolve output directory without creating generated simulation files yet."""
    safe_run_name = validate_run_name(run_name)
    return output_dir or DEFAULT_REPORTS_DIR / safe_run_name


def summarize_json(label: str, data: dict) -> str:
    """Return a compact summary of top-level JSON keys for CLI output."""
    keys = sorted(data.keys())
    return f"{label}: top_level_keys={keys}"


def parse_args() -> argparse.Namespace:
    """Parse CLI options for the future tournament simulation workflow."""
    parser = argparse.ArgumentParser(
        description="Validate tournament simulation inputs before implementation."
    )
    parser.add_argument(
        "--participants-path",
        type=Path,
        default=DEFAULT_PARTICIPANTS_PATH,
        help="Tournament participants JSON path.",
    )
    parser.add_argument(
        "--schedule-path",
        type=Path,
        default=DEFAULT_SCHEDULE_PATH,
        help="Tournament schedule JSON path.",
    )
    parser.add_argument(
        "--bracket-path",
        type=Path,
        default=DEFAULT_BRACKET_PATH,
        help="Tournament bracket JSON path.",
    )
    parser.add_argument(
        "--features-path",
        type=Path,
        default=DEFAULT_FEATURES_PATH,
        help="Global feature CSV path for future scheduled-match prediction.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help="Calibrated global model path for future match probabilities.",
    )
    parser.add_argument(
        "--run-name",
        default="global_simulation",
        help="Safe run name used to derive output paths. Default: global_simulation.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory for future generated simulation reports.",
    )
    parser.add_argument(
        "--n-simulations",
        type=int,
        default=10_000,
        help="Number of future Monte Carlo simulations. Default: 10000.",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for future reproducible simulations. Default: 42.",
    )
    parser.add_argument(
        "--allow-missing-generated-inputs",
        action="store_true",
        help=(
            "Allow missing generated inputs such as features_global.csv or the "
            "calibrated model while validating only tournament JSON scaffolds."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Validate inputs and print the future simulation contract."""
    args = parse_args()
    output_dir = resolve_output_dir(args.run_name, args.output_dir)

    participants = load_json_file(args.participants_path, "participants")
    schedule = load_json_file(args.schedule_path, "schedule")
    bracket = load_json_file(args.bracket_path, "bracket")

    validate_existing_file(
        args.features_path,
        "features",
        required=not args.allow_missing_generated_inputs,
    )
    validate_existing_file(
        args.model_path,
        "calibrated model",
        required=not args.allow_missing_generated_inputs,
    )

    if args.n_simulations <= 0:
        raise ValueError("--n-simulations must be greater than 0.")

    print("Tournament simulation CLI scaffold ready.")
    print("No simulation was executed and no report files were generated.")
    print(f"participants_path: {args.participants_path}")
    print(f"schedule_path: {args.schedule_path}")
    print(f"bracket_path: {args.bracket_path}")
    print(f"features_path: {args.features_path}")
    print(f"model_path: {args.model_path}")
    print(f"run_name: {validate_run_name(args.run_name)}")
    print(f"output_dir: {output_dir}")
    print(f"n_simulations: {args.n_simulations}")
    print(f"random_seed: {args.random_seed}")
    print(summarize_json("participants", participants))
    print(summarize_json("schedule", schedule))
    print(summarize_json("bracket", bracket))
    print("Next step: add scheduled-match probability generation.")


if __name__ == "__main__":
    main()
