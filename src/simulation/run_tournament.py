"""Phase 3-3 tournament simulation CLI scaffold with schema checks.

This scaffold intentionally does not run tournament simulation yet.
It validates input paths, parses tournament JSON files, checks minimal schema
contracts, warns about skeleton/TBD values, and prints the selected input/output
contract so the next implementation step can safely add simulation logic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARTICIPANTS_PATH = PROJECT_ROOT / "data" / "tournament" / "participants.json"
DEFAULT_SCHEDULE_PATH = PROJECT_ROOT / "data" / "tournament" / "schedule.json"
DEFAULT_BRACKET_PATH = PROJECT_ROOT / "data" / "tournament" / "bracket.json"
DEFAULT_FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features_global.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "global_baseline_calibrated_model.pkl"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_OUTPUT_DIR = DEFAULT_REPORTS_DIR / "simulation_global"
SKELETON_STATUS = "SKELETON_NOT_OFFICIAL"


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


def require_keys(data: dict, label: str, required_keys: list[str]) -> None:
    """Raise a clear error when required top-level JSON keys are missing."""
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValueError(
            f"{label} JSON is missing required top-level keys: {missing_keys}. "
            f"Current keys: {sorted(data.keys())}."
        )


def find_tbd_values(value: Any, path: str = "$", limit: int = 20) -> list[str]:
    """Find paths that still contain TBD placeholders, capped for readable output."""
    found: list[str] = []

    def walk(current: Any, current_path: str) -> None:
        if len(found) >= limit:
            return
        if current == "TBD":
            found.append(current_path)
            return
        if isinstance(current, dict):
            for key, nested_value in current.items():
                walk(nested_value, f"{current_path}.{key}")
                if len(found) >= limit:
                    return
        elif isinstance(current, list):
            for index, nested_value in enumerate(current):
                walk(nested_value, f"{current_path}[{index}]")
                if len(found) >= limit:
                    return

    walk(value, path)
    return found


def validate_participants_schema(data: dict) -> list[str]:
    """Validate minimal participants.json schema and return warnings."""
    require_keys(data, "participants", ["data_status", "source_note", "last_updated", "tournament", "participants"])
    warnings: list[str] = []

    if data.get("data_status") == SKELETON_STATUS:
        warnings.append("participants.json is marked SKELETON_NOT_OFFICIAL.")
    if not isinstance(data.get("tournament"), dict):
        raise ValueError("participants.tournament must be an object.")
    participants = data.get("participants")
    if not isinstance(participants, list):
        raise ValueError("participants.participants must be a list.")

    required_participant_keys = ["team_id", "canonical_name", "fifa_code", "group", "qualification_status"]
    for index, participant in enumerate(participants):
        if not isinstance(participant, dict):
            raise ValueError(f"participants.participants[{index}] must be an object.")
        missing = [key for key in required_participant_keys if key not in participant]
        if missing:
            raise ValueError(f"participants.participants[{index}] is missing keys: {missing}.")

    tbd_paths = find_tbd_values(data, path="participants")
    if tbd_paths:
        warnings.append(f"participants.json still contains TBD placeholders, examples: {tbd_paths}")
    return warnings


def validate_schedule_schema(data: dict) -> list[str]:
    """Validate minimal schedule.json schema and return warnings."""
    require_keys(data, "schedule", ["data_status", "source_note", "last_updated", "tournament", "matches"])
    warnings: list[str] = []

    if data.get("data_status") == SKELETON_STATUS:
        warnings.append("schedule.json is marked SKELETON_NOT_OFFICIAL.")
    if not isinstance(data.get("tournament"), dict):
        raise ValueError("schedule.tournament must be an object.")
    matches = data.get("matches")
    if not isinstance(matches, list):
        raise ValueError("schedule.matches must be a list.")

    required_match_keys = ["match_id", "stage", "date", "home_team", "away_team"]
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            raise ValueError(f"schedule.matches[{index}] must be an object.")
        missing = [key for key in required_match_keys if key not in match]
        if missing:
            raise ValueError(f"schedule.matches[{index}] is missing keys: {missing}.")

    tbd_paths = find_tbd_values(data, path="schedule")
    if tbd_paths:
        warnings.append(f"schedule.json still contains TBD placeholders, examples: {tbd_paths}")
    return warnings


def validate_bracket_schema(data: dict) -> list[str]:
    """Validate minimal bracket.json schema and return warnings."""
    require_keys(
        data,
        "bracket",
        ["data_status", "source_note", "last_updated", "tournament", "group_stage_rules", "knockout_rules", "rounds"],
    )
    warnings: list[str] = []

    if data.get("data_status") == SKELETON_STATUS:
        warnings.append("bracket.json is marked SKELETON_NOT_OFFICIAL.")
    if not isinstance(data.get("tournament"), dict):
        raise ValueError("bracket.tournament must be an object.")
    if not isinstance(data.get("group_stage_rules"), dict):
        raise ValueError("bracket.group_stage_rules must be an object.")
    if not isinstance(data.get("knockout_rules"), dict):
        raise ValueError("bracket.knockout_rules must be an object.")
    rounds = data.get("rounds")
    if not isinstance(rounds, list):
        raise ValueError("bracket.rounds must be a list.")

    for round_index, round_data in enumerate(rounds):
        if not isinstance(round_data, dict):
            raise ValueError(f"bracket.rounds[{round_index}] must be an object.")
        missing_round_keys = [key for key in ["round", "matches"] if key not in round_data]
        if missing_round_keys:
            raise ValueError(f"bracket.rounds[{round_index}] is missing keys: {missing_round_keys}.")
        if not isinstance(round_data["matches"], list):
            raise ValueError(f"bracket.rounds[{round_index}].matches must be a list.")
        for match_index, match in enumerate(round_data["matches"]):
            if not isinstance(match, dict):
                raise ValueError(
                    f"bracket.rounds[{round_index}].matches[{match_index}] must be an object."
                )
            missing_match_keys = [
                key for key in ["match_id", "slot_home", "slot_away", "winner_advances_to"] if key not in match
            ]
            if missing_match_keys:
                raise ValueError(
                    f"bracket.rounds[{round_index}].matches[{match_index}] is missing keys: "
                    f"{missing_match_keys}."
                )

    tbd_paths = find_tbd_values(data, path="bracket")
    if tbd_paths:
        warnings.append(f"bracket.json still contains TBD placeholders, examples: {tbd_paths}")
    return warnings


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

    warnings: list[str] = []
    warnings.extend(validate_participants_schema(participants))
    warnings.extend(validate_schedule_schema(schedule))
    warnings.extend(validate_bracket_schema(bracket))

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
    print("Tournament JSON schema validation complete.")
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
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    print("Next step: add scheduled-match probability generation.")


if __name__ == "__main__":
    main()
