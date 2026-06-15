import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRACKET_PATH = PROJECT_ROOT / "data" / "tournament" / "bracket.json"


EXPECTED_ROUND_OF_32 = {
    "M73": ("2A", "2B", None),
    "M74": ("1E", "Best 3rd A/B/C/D/F", ["A", "B", "C", "D", "F"]),
    "M75": ("1F", "2C", None),
    "M76": ("1C", "2F", None),
    "M77": ("1I", "Best 3rd C/D/F/G/H", ["C", "D", "F", "G", "H"]),
    "M78": ("2E", "2I", None),
    "M79": ("1A", "Best 3rd C/E/F/H/I", ["C", "E", "F", "H", "I"]),
    "M80": ("1L", "Best 3rd E/H/I/J/K", ["E", "H", "I", "J", "K"]),
    "M81": ("1D", "Best 3rd B/E/F/I/J", ["B", "E", "F", "I", "J"]),
    "M82": ("1G", "Best 3rd A/E/H/I/J", ["A", "E", "H", "I", "J"]),
    "M83": ("2K", "2L", None),
    "M84": ("1H", "2J", None),
    "M85": ("1B", "Best 3rd E/F/G/I/J", ["E", "F", "G", "I", "J"]),
    "M86": ("1J", "2H", None),
    "M87": ("1K", "Best 3rd D/E/I/J/L", ["D", "E", "I", "J", "L"]),
    "M88": ("2D", "2G", None),
}


def load_bracket() -> dict:
    with BRACKET_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def get_round_of_32_matches(bracket: dict) -> dict:
    round_of_32 = next(
        item for item in bracket["rounds"] if item["round"] == "round_of_32"
    )
    return {match["match_id"]: match for match in round_of_32["matches"]}


def test_round_of_32_has_official_match_ids_m73_to_m88():
    bracket = load_bracket()
    matches = get_round_of_32_matches(bracket)

    assert list(matches.keys()) == list(EXPECTED_ROUND_OF_32.keys())
    assert len(matches) == 16


def test_round_of_32_slot_labels_match_official_mapping():
    bracket = load_bracket()
    matches = get_round_of_32_matches(bracket)

    for match_id, (expected_slot_a, expected_slot_b, _) in EXPECTED_ROUND_OF_32.items():
        match = matches[match_id]

        assert match["slot_a"]["label"] == expected_slot_a
        assert match["slot_b"]["label"] == expected_slot_b


def test_best_third_place_candidate_pools_are_machine_readable():
    bracket = load_bracket()
    matches = get_round_of_32_matches(bracket)

    for match_id, (_, _, expected_candidate_groups) in EXPECTED_ROUND_OF_32.items():
        slot_b = matches[match_id]["slot_b"]

        if expected_candidate_groups is None:
            assert slot_b["type"] == "group_runner_up"
            assert "candidate_groups" not in slot_b
            continue

        assert slot_b["type"] == "best_third_place"
        assert slot_b["candidate_groups"] == expected_candidate_groups
        assert slot_b["allocation_status"] == "requires_annexe_c"


def test_annexe_c_boundary_is_explicit():
    bracket = load_bracket()

    assert (
        bracket["implementation_boundary"]["third_place_qualifier_combinations"]
        == "pending_annexe_c_machine_readable_conversion"
    )
    assert bracket["implementation_boundary"]["complete_tournament_simulation_claim"] is False
    assert bracket["implementation_boundary"]["champion_probability_claim"] is False


def test_round_of_32_status_is_official_source_aligned_but_not_complete_simulation():
    bracket = load_bracket()
    round_of_32 = next(
        item for item in bracket["rounds"] if item["round"] == "round_of_32"
    )

    assert bracket["data_status"] == (
        "ROUND_OF_32_MAPPING_OFFICIAL_SOURCE_ALIGNED__ANNEXE_C_PENDING"
    )
    assert round_of_32["official_source_status"] == "ARTICLE_12_6_ALIGNED"
    assert bracket["third_place_allocation"]["status"] == (
        "ANNEXE_C_PENDING_MACHINE_READABLE_CONVERSION"
    )
