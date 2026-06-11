"""Phase 3-6 tournament simulation CLI scaffold with match probabilities.

This scaffold intentionally does not run tournament simulation yet.
It validates input paths, parses tournament JSON files, checks minimal schema
contracts, warns about skeleton/TBD values, loads generated probability inputs,
assembles scheduled feature rows when possible, and creates an in-memory match
probability table with model.predict_proba().

No simulation reports are generated in this phase.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARTICIPANTS_PATH = PROJECT_ROOT / "data" / "tournament" / "participants.json"
DEFAULT_SCHEDULE_PATH = PROJECT_ROOT / "data" / "tournament" / "schedule.json"
DEFAULT_BRACKET_PATH = PROJECT_ROOT / "data" / "tournament" / "bracket.json"
DEFAULT_FEATURES_PATH = PROJECT_ROOT / "data" / "processed" / "features_global.csv"
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "global_baseline_calibrated_model.pkl"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_OUTPUT_DIR = DEFAULT_REPORTS_DIR / "simulation_global"
SKELETON_STATUS = "SKELETON_NOT_OFFICIAL"
TBD_VALUE = "TBD"
TARGET_AND_AUDIT_COLUMNS = {
    "target_result",
    "target_result_korea_perspective",
    "source_target_column",
    "source_target_scope",
}


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
        if current == TBD_VALUE:
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
    require_keys(
        data,
        "participants",
        ["data_status", "source_note", "last_updated", "tournament", "participants"],
    )
    warnings: list[str] = []

    if data.get("data_status") == SKELETON_STATUS:
        warnings.append("participants.json is marked SKELETON_NOT_OFFICIAL.")
    if not isinstance(data.get("tournament"), dict):
        raise ValueError("participants.tournament must be an object.")
    participants = data.get("participants")
    if not isinstance(participants, list):
        raise ValueError("participants.participants must be a list.")

    required_participant_keys = [
        "team_id",
        "canonical_name",
        "fifa_code",
        "group",
        "qualification_status",
    ]
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
        [
            "data_status",
            "source_note",
            "last_updated",
            "tournament",
            "group_stage_rules",
            "knockout_rules",
            "rounds",
        ],
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
                key
                for key in ["match_id", "slot_home", "slot_away", "winner_advances_to"]
                if key not in match
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


def load_features_table(features_path: Path, required: bool) -> pd.DataFrame | None:
    """Load features_global.csv when available for future match feature assembly."""
    if not features_path.exists():
        if required:
            raise FileNotFoundError(f"features file not found: {features_path}")
        return None
    return pd.read_csv(features_path)


def load_probability_model(model_path: Path, required: bool):
    """Load calibrated probability model when available for future predictions."""
    if not model_path.exists():
        if required:
            raise FileNotFoundError(f"calibrated model file not found: {model_path}")
        return None
    model = joblib.load(model_path)
    if not hasattr(model, "predict_proba"):
        raise TypeError(
            f"Loaded model from {model_path} does not support predict_proba(). "
            "Tournament simulation requires probability outputs."
        )
    return model


def infer_model_feature_columns(model, features: pd.DataFrame | None) -> list[str]:
    """Infer model input columns for future scheduled-match feature assembly."""
    if model is not None and hasattr(model, "feature_names_in_"):
        return [str(column) for column in model.feature_names_in_]

    preprocessor = getattr(model, "named_steps", {}).get("preprocessor") if model is not None else None
    if preprocessor is not None and hasattr(preprocessor, "feature_names_in_"):
        return [str(column) for column in preprocessor.feature_names_in_]

    if features is not None:
        return [column for column in features.columns if column not in TARGET_AND_AUDIT_COLUMNS]
    return []


def model_class_labels(model) -> list[str]:
    """Return model class labels in predict_proba order when a model is loaded."""
    if model is None or not hasattr(model, "classes_"):
        return []
    return [str(label) for label in model.classes_]


def probability_column_names(class_labels: list[str]) -> list[str]:
    """Return probability output column names based on model class labels."""
    return [f"prob_{label}" for label in class_labels]


def scheduled_match_candidates(schedule: dict) -> tuple[list[dict[str, Any]], list[str]]:
    """Build prediction candidates from schedule matches, excluding TBD teams."""
    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []
    matches = schedule.get("matches", [])

    for index, match in enumerate(matches):
        match_id = match.get("match_id", f"MATCH_{index}")
        home_team = match.get("home_team")
        away_team = match.get("away_team")
        if home_team == TBD_VALUE or away_team == TBD_VALUE:
            warnings.append(f"Skipping {match_id}: home_team or away_team is still TBD.")
            continue
        candidates.append(
            {
                "match_id": match_id,
                "stage": match.get("stage"),
                "group": match.get("group"),
                "home_team": home_team,
                "away_team": away_team,
                "home_fifa_code": match.get("home_fifa_code"),
                "away_fifa_code": match.get("away_fifa_code"),
            }
        )
    return candidates, warnings


def matching_feature_rows(features: pd.DataFrame, candidate: dict[str, Any]) -> pd.DataFrame:
    """Find historical/global feature rows matching a scheduled home-away pair."""
    required_columns = {"home_team", "away_team"}
    if not required_columns.issubset(features.columns):
        return pd.DataFrame()

    home_team = str(candidate["home_team"])
    away_team = str(candidate["away_team"])
    return features[
        (features["home_team"].astype(str) == home_team)
        & (features["away_team"].astype(str) == away_team)
    ]


def select_feature_template(rows: pd.DataFrame) -> pd.Series:
    """Select a single feature template row, preferring the latest dated row."""
    if rows.empty:
        raise ValueError("Cannot select a feature template from an empty DataFrame.")
    if "date" not in rows.columns:
        return rows.iloc[-1]

    dated_rows = rows.copy()
    dated_rows["_parsed_date"] = pd.to_datetime(dated_rows["date"], errors="coerce")
    dated_rows = dated_rows.sort_values("_parsed_date", na_position="first")
    return dated_rows.drop(columns=["_parsed_date"]).iloc[-1]


def assemble_scheduled_feature_rows(
    candidates: list[dict[str, Any]],
    features: pd.DataFrame | None,
    feature_columns: list[str],
) -> tuple[pd.DataFrame, list[dict[str, Any]], list[str]]:
    """Assemble model-ready feature rows for scheduled matches when possible.

    This is still a scaffold: it reuses the latest matching historical/global
    home-away feature row as a temporary template. Later phases should replace
    this with real pre-match feature construction from ranking, form, venue, and
    schedule inputs.
    """
    warnings: list[str] = []
    metadata_rows: list[dict[str, Any]] = []
    assembled_rows: list[dict[str, Any]] = []

    if not candidates:
        warnings.append("No scheduled matches are ready for feature assembly.")
        return pd.DataFrame(columns=feature_columns), metadata_rows, warnings

    if features is None:
        warnings.append("features_global.csv was not loaded, so scheduled feature rows were not assembled.")
        return pd.DataFrame(columns=feature_columns), metadata_rows, warnings

    if not feature_columns:
        warnings.append("No feature columns were inferred, so scheduled feature rows were not assembled.")
        return pd.DataFrame(), metadata_rows, warnings

    missing_feature_columns = [column for column in feature_columns if column not in features.columns]
    if missing_feature_columns:
        warnings.append(
            "features_global.csv is missing model feature columns, examples: "
            f"{missing_feature_columns[:10]}"
        )
        return pd.DataFrame(columns=feature_columns), metadata_rows, warnings

    for candidate in candidates:
        rows = matching_feature_rows(features, candidate)
        if rows.empty:
            warnings.append(
                f"No feature template found for {candidate['match_id']} "
                f"({candidate['home_team']} vs {candidate['away_team']})."
            )
            continue

        template = select_feature_template(rows)
        assembled_rows.append(template[feature_columns].to_dict())
        metadata_rows.append(
            {
                "match_id": candidate["match_id"],
                "home_team": candidate["home_team"],
                "away_team": candidate["away_team"],
                "matched_feature_rows": int(len(rows)),
                "template_strategy": "latest_matching_home_away_row",
            }
        )

    return pd.DataFrame(assembled_rows, columns=feature_columns), metadata_rows, warnings


def build_match_probability_table(
    model,
    feature_frame: pd.DataFrame,
    feature_metadata: list[dict[str, Any]],
    class_labels: list[str],
) -> tuple[pd.DataFrame, list[str]]:
    """Create an in-memory match probability table with model.predict_proba()."""
    warnings: list[str] = []
    probability_columns = probability_column_names(class_labels)

    if model is None:
        warnings.append("No probability model was loaded, so match probabilities were not generated.")
        return pd.DataFrame(columns=["match_id", "home_team", "away_team", *probability_columns]), warnings
    if feature_frame.empty:
        warnings.append("No assembled feature rows are available for model.predict_proba().")
        return pd.DataFrame(columns=["match_id", "home_team", "away_team", *probability_columns]), warnings
    if len(feature_metadata) != len(feature_frame):
        raise ValueError(
            "Feature metadata row count does not match assembled feature row count: "
            f"metadata={len(feature_metadata)}, features={len(feature_frame)}."
        )

    probabilities = model.predict_proba(feature_frame)
    if len(probability_columns) != probabilities.shape[1]:
        raise ValueError(
            "Probability column count does not match predict_proba output width: "
            f"columns={len(probability_columns)}, output={probabilities.shape[1]}."
        )

    rows: list[dict[str, Any]] = []
    for metadata, probability_row in zip(feature_metadata, probabilities):
        row = {
            "match_id": metadata["match_id"],
            "home_team": metadata["home_team"],
            "away_team": metadata["away_team"],
        }
        for column, probability in zip(probability_columns, probability_row):
            row[column] = float(probability)
        rows.append(row)

    return pd.DataFrame(rows), warnings


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

    required_generated_inputs = not args.allow_missing_generated_inputs
    features = load_features_table(args.features_path, required=required_generated_inputs)
    model = load_probability_model(args.model_path, required=required_generated_inputs)
    feature_columns = infer_model_feature_columns(model, features)
    class_labels = model_class_labels(model)
    probability_columns = probability_column_names(class_labels)
    candidates, candidate_warnings = scheduled_match_candidates(schedule)
    feature_frame, feature_metadata, assembly_warnings = assemble_scheduled_feature_rows(
        candidates=candidates,
        features=features,
        feature_columns=feature_columns,
    )
    match_probability_table, probability_warnings = build_match_probability_table(
        model=model,
        feature_frame=feature_frame,
        feature_metadata=feature_metadata,
        class_labels=class_labels,
    )
    warnings.extend(candidate_warnings)
    warnings.extend(assembly_warnings)
    warnings.extend(probability_warnings)

    if args.n_simulations <= 0:
        raise ValueError("--n-simulations must be greater than 0.")

    print("Tournament simulation CLI scaffold ready.")
    print("Tournament JSON schema validation complete.")
    print("Scheduled-match probability scaffold complete.")
    print("Scheduled-match feature row assembly scaffold complete.")
    print("Match probability table scaffold complete.")
    print("No simulation was executed and no report files were generated.")
    print(f"participants_path: {args.participants_path}")
    print(f"schedule_path: {args.schedule_path}")
    print(f"bracket_path: {args.bracket_path}")
    print(f"features_path: {args.features_path}")
    print(f"features_loaded: {features is not None}")
    print(f"features_row_count: {len(features) if features is not None else 0}")
    print(f"model_path: {args.model_path}")
    print(f"model_loaded: {model is not None}")
    print(f"model_type: {type(model).__name__ if model is not None else 'None'}")
    print(f"model_classes: {class_labels}")
    print(f"probability_columns: {probability_columns}")
    print(f"feature_column_count: {len(feature_columns)}")
    print(f"prediction_candidate_count: {len(candidates)}")
    print(f"assembled_feature_row_count: {len(feature_frame)}")
    print(f"unassembled_candidate_count: {len(candidates) - len(feature_frame)}")
    print(f"match_probability_row_count: {len(match_probability_table)}")
    print(f"run_name: {validate_run_name(args.run_name)}")
    print(f"output_dir: {output_dir}")
    print(f"n_simulations: {args.n_simulations}")
    print(f"random_seed: {args.random_seed}")
    print(summarize_json("participants", participants))
    print(summarize_json("schedule", schedule))
    print(summarize_json("bracket", bracket))
    if candidates:
        print("Prediction candidates:")
        for candidate in candidates[:10]:
            print(f"- {candidate}")
    if feature_metadata:
        print("Feature assembly metadata:")
        for metadata in feature_metadata[:10]:
            print(f"- {metadata}")
    if not match_probability_table.empty:
        print("Match probability preview:")
        print(match_probability_table.head(10).to_string(index=False))
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
    print("Next step: save match probabilities to a generated CSV before simulation.")


if __name__ == "__main__":
    main()
