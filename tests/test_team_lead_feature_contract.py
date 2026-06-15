import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = PROJECT_ROOT / "data" / "schema" / "team_lead_features.json"

EXPECTED_GENERATED_ARTIFACTS = {
    "results_preprocessed.csv",
    "X_train.csv",
    "X_test.csv",
    "y_train.csv",
    "y_test.csv",
    "w_train.csv",
    "wc2026_matches.csv",
}

EXPECTED_LEAKAGE_COLUMNS = {
    "home_score",
    "away_score",
    "result",
    "target_result",
    "target_result_korea_perspective",
    "y",
    "date",
    "home_team",
    "away_team",
    "tournament",
    "city",
    "country",
    "year",
    "match_id",
    "group",
    "round",
}


def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def feature_names(schema: dict) -> list[str]:
    return [feature["name"] for feature in schema["features"]]


def test_team_lead_feature_schema_file_exists_and_is_valid_json():
    assert SCHEMA_PATH.exists()
    schema = load_schema()

    assert schema["schema_name"] == "team_lead_52_feature_model_input_contract"
    assert schema["source_artifact"] == "features.json from team shared preprocessing output"


def test_feature_count_is_exactly_52():
    schema = load_schema()

    assert schema["feature_count"] == 52
    assert len(schema["features"]) == 52


def test_feature_names_are_unique():
    schema = load_schema()
    names = feature_names(schema)

    assert len(names) == len(set(names))


def test_all_features_are_marked_as_non_leakage_inputs():
    schema = load_schema()

    assert all(feature["leakage_allowed"] is False for feature in schema["features"])


def test_leakage_columns_are_not_in_feature_contract():
    schema = load_schema()
    names = set(feature_names(schema))

    assert names.isdisjoint(EXPECTED_LEAKAGE_COLUMNS)


def test_schema_records_expected_leakage_exclusion_columns():
    schema = load_schema()
    leakage_exclusion = schema["leakage_exclusion"]
    recorded_columns = set()

    for key in ("score_columns", "result_columns", "metadata_columns"):
        recorded_columns.update(leakage_exclusion[key])

    assert EXPECTED_LEAKAGE_COLUMNS.issubset(recorded_columns)


def test_label_encoding_contract_matches_team_lead_baseline():
    schema = load_schema()
    label_contract = schema["label_contract"]

    assert label_contract["column"] == "y"
    assert label_contract["encoding"] == {"A": 0, "D": 1, "H": 2}
    assert label_contract["allowed_values"] == [0, 1, 2]
    assert label_contract["perspective"] == "home_team_result"


def test_train_test_split_date_contract_is_fixed():
    schema = load_schema()
    split_contract = schema["split_contract"]

    assert split_contract["split_date"] == "2022-01-01"
    assert split_contract["train"] == "date < 2022-01-01"
    assert split_contract["test"] == "date >= 2022-01-01"


def test_generated_artifacts_are_listed_as_not_committed_by_default():
    schema = load_schema()
    generated = set(schema["generated_artifacts"]["not_committed_by_default"])

    assert EXPECTED_GENERATED_ARTIFACTS.issubset(generated)
    assert schema["generated_artifacts"]["committed_contract_file"] == (
        "data/schema/team_lead_features.json"
    )


def test_feature_schema_has_required_metadata_fields():
    schema = load_schema()

    for feature in schema["features"]:
        assert set(feature) == {"name", "family", "role", "dtype", "leakage_allowed"}
        assert feature["name"]
        assert feature["family"]
        assert feature["role"]
        assert feature["dtype"] == "numeric_or_boolean_encoded"
