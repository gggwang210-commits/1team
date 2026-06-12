from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.simulation.ranking import (
    MatchResult,
    build_group_table,
    get_qualified_teams,
    rank_group_table,
)


def test_build_group_table_ranks_by_points():
    matches = [
        MatchResult("Korea Republic", "Mexico", 2, 1),
        MatchResult("Germany", "Sweden", 1, 1),
        MatchResult("Korea Republic", "Germany", 1, 0),
        MatchResult("Mexico", "Sweden", 3, 0),
    ]

    table = build_group_table(matches)

    assert table[0]["team"] == "Korea Republic"
    assert table[0]["points"] == 6
    assert table[1]["team"] == "Mexico"
    assert table[1]["points"] == 3


def test_rank_group_table_uses_goal_difference_tiebreaker():
    records = [
        {
            "team": "Team A",
            "played": 3,
            "wins": 1,
            "draws": 1,
            "losses": 1,
            "goals_for": 4,
            "goals_against": 3,
            "goal_difference": 1,
            "points": 4,
        },
        {
            "team": "Team B",
            "played": 3,
            "wins": 1,
            "draws": 1,
            "losses": 1,
            "goals_for": 5,
            "goals_against": 2,
            "goal_difference": 3,
            "points": 4,
        },
    ]

    ranked = rank_group_table(records)

    assert ranked[0]["team"] == "Team B"


def test_rank_group_table_uses_goals_for_tiebreaker():
    records = [
        {
            "team": "Team A",
            "played": 3,
            "wins": 1,
            "draws": 1,
            "losses": 1,
            "goals_for": 4,
            "goals_against": 3,
            "goal_difference": 1,
            "points": 4,
        },
        {
            "team": "Team B",
            "played": 3,
            "wins": 1,
            "draws": 1,
            "losses": 1,
            "goals_for": 5,
            "goals_against": 4,
            "goal_difference": 1,
            "points": 4,
        },
    ]

    ranked = rank_group_table(records)

    assert ranked[0]["team"] == "Team B"


def test_get_qualified_teams_returns_top_two_by_default():
    ranked_table = [
        {"team": "Korea Republic", "points": 6},
        {"team": "Mexico", "points": 4},
        {"team": "Germany", "points": 3},
        {"team": "Sweden", "points": 1},
    ]

    qualified = get_qualified_teams(ranked_table)

    assert qualified == ["Korea Republic", "Mexico"]


def test_build_group_table_is_deterministic_when_all_tiebreakers_equal():
    matches = [
        MatchResult("Team B", "Team A", 1, 1),
    ]

    table = build_group_table(matches)

    assert [record["team"] for record in table] == ["Team A", "Team B"]
