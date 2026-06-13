from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.simulation.third_place import (
    ThirdPlaceRecord,
    get_best_third_place_team_names,
    get_best_third_place_teams,
    rank_third_place_teams,
)


def test_rank_third_place_teams_uses_points_first():
    records = [
        ThirdPlaceRecord("A", "Team A", 3, 10, 10),
        ThirdPlaceRecord("B", "Team B", 5, -1, 2),
    ]

    ranked = rank_third_place_teams(records)

    assert ranked[0].team == "Team B"


def test_rank_third_place_teams_uses_goal_difference_tiebreaker():
    records = [
        ThirdPlaceRecord("A", "Team A", 4, 1, 4),
        ThirdPlaceRecord("B", "Team B", 4, 3, 3),
    ]

    ranked = rank_third_place_teams(records)

    assert ranked[0].team == "Team B"


def test_rank_third_place_teams_uses_goals_for_tiebreaker():
    records = [
        ThirdPlaceRecord("A", "Team A", 4, 1, 4),
        ThirdPlaceRecord("B", "Team B", 4, 1, 5),
    ]

    ranked = rank_third_place_teams(records)

    assert ranked[0].team == "Team B"


def test_rank_third_place_teams_uses_conduct_score_tiebreaker():
    records = [
        ThirdPlaceRecord("A", "Team A", 4, 1, 5, conduct_score=-4),
        ThirdPlaceRecord("B", "Team B", 4, 1, 5, conduct_score=-1),
    ]

    ranked = rank_third_place_teams(records)

    assert ranked[0].team == "Team B"


def test_rank_third_place_teams_uses_fifa_rank_tiebreaker():
    records = [
        ThirdPlaceRecord("A", "Team A", 4, 1, 5, conduct_score=-1, fifa_rank=20),
        ThirdPlaceRecord("B", "Team B", 4, 1, 5, conduct_score=-1, fifa_rank=5),
    ]

    ranked = rank_third_place_teams(records)

    assert ranked[0].team == "Team B"


def test_rank_third_place_teams_is_deterministic_when_equal():
    records = [
        ThirdPlaceRecord("B", "Team B", 4, 1, 5, conduct_score=-1, fifa_rank=10),
        ThirdPlaceRecord("A", "Team A", 4, 1, 5, conduct_score=-1, fifa_rank=10),
    ]

    ranked = rank_third_place_teams(records)

    assert [record.team for record in ranked] == ["Team A", "Team B"]


def test_get_best_third_place_teams_returns_top_eight_by_default():
    records = [
        ThirdPlaceRecord("A", "Team A", 9, 5, 8),
        ThirdPlaceRecord("B", "Team B", 8, 4, 7),
        ThirdPlaceRecord("C", "Team C", 7, 3, 6),
        ThirdPlaceRecord("D", "Team D", 6, 2, 5),
        ThirdPlaceRecord("E", "Team E", 5, 1, 4),
        ThirdPlaceRecord("F", "Team F", 4, 0, 3),
        ThirdPlaceRecord("G", "Team G", 3, -1, 2),
        ThirdPlaceRecord("H", "Team H", 2, -2, 1),
        ThirdPlaceRecord("I", "Team I", 1, -3, 1),
        ThirdPlaceRecord("J", "Team J", 0, -4, 0),
        ThirdPlaceRecord("K", "Team K", 0, -5, 0),
        ThirdPlaceRecord("L", "Team L", 0, -6, 0),
    ]

    qualified = get_best_third_place_teams(records)

    assert len(qualified) == 8
    assert [record.team for record in qualified] == [
        "Team A",
        "Team B",
        "Team C",
        "Team D",
        "Team E",
        "Team F",
        "Team G",
        "Team H",
    ]


def test_get_best_third_place_team_names_returns_names_only():
    records = [
        ThirdPlaceRecord("A", "Team A", 4, 1, 5),
        ThirdPlaceRecord("B", "Team B", 3, 0, 4),
        ThirdPlaceRecord("C", "Team C", 2, -1, 3),
    ]

    names = get_best_third_place_team_names(records, slots=2)

    assert names == ["Team A", "Team B"]
