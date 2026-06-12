"""Provisional group ranking utilities.

This module provides a provisional group ranking implementation for
the tournament simulation pipeline.

Important:
    This implementation does not claim full FIFA regulation compliance.
    It currently ranks teams by:
        1. points
        2. goal_difference
        3. goals_for
        4. team name, as a deterministic fallback

Official FIFA tiebreakers should be verified before using this as the
final competition regulation implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class MatchResult:
    """Single group-stage match result."""

    home_team: str
    away_team: str
    home_score: int
    away_score: int


def _empty_team_record(team: str) -> dict:
    """Create an empty standing record for one team."""

    return {
        "team": team,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0,
        "points": 0,
    }


def build_group_table(matches: Iterable[MatchResult]) -> list[dict]:
    """Build a provisional group table from match results.

    Args:
        matches: Iterable of MatchResult objects.

    Returns:
        A list of team standing records sorted by provisional ranking rules.
    """

    table: dict[str, dict] = {}

    for match in matches:
        if match.home_team not in table:
            table[match.home_team] = _empty_team_record(match.home_team)
        if match.away_team not in table:
            table[match.away_team] = _empty_team_record(match.away_team)

        home = table[match.home_team]
        away = table[match.away_team]

        home["played"] += 1
        away["played"] += 1

        home["goals_for"] += match.home_score
        home["goals_against"] += match.away_score

        away["goals_for"] += match.away_score
        away["goals_against"] += match.home_score

        if match.home_score > match.away_score:
            home["wins"] += 1
            away["losses"] += 1
            home["points"] += 3
        elif match.home_score < match.away_score:
            away["wins"] += 1
            home["losses"] += 1
            away["points"] += 3
        else:
            home["draws"] += 1
            away["draws"] += 1
            home["points"] += 1
            away["points"] += 1

    for record in table.values():
        record["goal_difference"] = (
            record["goals_for"] - record["goals_against"]
        )

    return rank_group_table(table.values())


def rank_group_table(records: Iterable[dict]) -> list[dict]:
    """Sort group standing records by provisional ranking rules.

    Args:
        records: Iterable of standing dictionaries.

    Returns:
        Ranked standing records.
    """

    return sorted(
        records,
        key=lambda record: (
            -record["points"],
            -record["goal_difference"],
            -record["goals_for"],
            record["team"],
        ),
    )


def get_qualified_teams(
    ranked_table: list[dict],
    direct_slots: int = 2,
) -> list[str]:
    """Return directly qualified teams from a ranked group table.

    Args:
        ranked_table: Ranked group table.
        direct_slots: Number of direct qualification slots.

    Returns:
        Team names that qualify directly.
    """

    return [record["team"] for record in ranked_table[:direct_slots]]
