from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.simulation.ranking import (  # noqa: E402
    MatchResult,
    build_group_table,
    build_group_table_article_13,
    rank_group_table_article_13,
)


def team_order(table: list[dict]) -> list[str]:
    return [record["team"] for record in table]


def test_article_13_head_to_head_points_beat_overall_goal_difference():
    matches = [
        MatchResult("Team A", "Team B", 1, 0),
        MatchResult("Team A", "Team C", 0, 3),
        MatchResult("Team A", "Team D", 3, 0),
        MatchResult("Team B", "Team C", 5, 0),
        MatchResult("Team B", "Team D", 5, 0),
        MatchResult("Team C", "Team D", 1, 0),
    ]

    provisional = build_group_table(matches)
    article_13 = build_group_table_article_13(matches)

    assert team_order(provisional)[:2] == ["Team B", "Team A"]
    assert team_order(article_13)[:2] == ["Team A", "Team B"]


def test_article_13_head_to_head_goal_difference_resolves_three_way_tie():
    matches = [
        MatchResult("Team A", "Team B", 1, 0),
        MatchResult("Team B", "Team C", 3, 0),
        MatchResult("Team C", "Team A", 2, 0),
        MatchResult("Team A", "Team D", 1, 0),
        MatchResult("Team B", "Team D", 1, 0),
        MatchResult("Team C", "Team D", 1, 0),
    ]

    ranked = build_group_table_article_13(matches)

    assert team_order(ranked)[0] == "Team B"


def test_article_13_uses_overall_goal_difference_after_equal_head_to_head():
    matches = [
        MatchResult("Team A", "Team B", 0, 0),
        MatchResult("Team A", "Team C", 3, 0),
        MatchResult("Team B", "Team C", 1, 0),
    ]

    ranked = build_group_table_article_13(matches)

    assert team_order(ranked)[:2] == ["Team A", "Team B"]


def test_article_13_uses_conduct_score_after_goals_criteria():
    records = [
        {
            "team": "Team A",
            "played": 3,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 5,
            "conduct_score": -5,
            "fifa_rank": 10,
        },
        {
            "team": "Team B",
            "played": 3,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 5,
            "conduct_score": -1,
            "fifa_rank": 20,
        },
    ]

    ranked = rank_group_table_article_13(records, matches=[])

    assert team_order(ranked) == ["Team B", "Team A"]


def test_article_13_uses_fifa_rank_after_conduct_score():
    records = [
        {
            "team": "Team A",
            "played": 3,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 5,
            "conduct_score": -1,
            "fifa_rank": 30,
        },
        {
            "team": "Team B",
            "played": 3,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 5,
            "conduct_score": -1,
            "fifa_rank": 5,
        },
    ]

    ranked = rank_group_table_article_13(records, matches=[])

    assert team_order(ranked) == ["Team B", "Team A"]


def test_missing_fifa_rank_uses_deterministic_software_fallback_only():
    records = [
        {
            "team": "Team B",
            "played": 3,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 5,
            "conduct_score": -1,
            "fifa_rank": None,
        },
        {
            "team": "Team A",
            "played": 3,
            "goals_for": 3,
            "goals_against": 2,
            "goal_difference": 1,
            "points": 5,
            "conduct_score": -1,
            "fifa_rank": None,
        },
    ]

    ranked = rank_group_table_article_13(records, matches=[])

    assert team_order(ranked) == ["Team A", "Team B"]
