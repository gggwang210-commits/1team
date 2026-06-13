"""Third-place ranking utilities for tournament simulation.

This module ranks the twelve third-placed teams and returns the best eight
teams that qualify for the Round of 32.

The implemented criteria follow the FIFA World Cup 26 Regulations Article 13
for the eight best-ranked third-placed teams, with deterministic fallback for
software reproducibility.

Ranking order:
    1. points obtained in all group matches
    2. goal difference from all group matches
    3. goals scored in all group matches
    4. team conduct score, where a higher score ranks higher
    5. FIFA/Coca-Cola Men's World Ranking, where a lower rank number is better
    6. group and team name as deterministic non-regulatory software fallback

Important:
    The final fallback by group/team name is not a FIFA competition rule. It is
    used only to keep tests and simulations deterministic when ranking data is
    incomplete or still equal after all available official criteria.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


UNKNOWN_FIFA_RANK = 10_000


@dataclass(frozen=True)
class ThirdPlaceRecord:
    """Standing record for one third-placed team.

    Args:
        group: Group letter, such as "A" or "L".
        team: Team name.
        points: Points from all group matches.
        goal_difference: Goal difference from all group matches.
        goals_for: Goals scored in all group matches.
        conduct_score: Team conduct score. Higher is better.
        fifa_rank: FIFA ranking number. Lower is better. Use None if unknown.
    """

    group: str
    team: str
    points: int
    goal_difference: int
    goals_for: int
    conduct_score: int = 0
    fifa_rank: int | None = None


def rank_third_place_teams(
    records: Iterable[ThirdPlaceRecord],
) -> list[ThirdPlaceRecord]:
    """Rank third-placed teams using Article 13-compatible criteria.

    Args:
        records: Iterable of third-placed team records.

    Returns:
        Ranked third-placed team records.
    """

    return sorted(
        records,
        key=lambda record: (
            -record.points,
            -record.goal_difference,
            -record.goals_for,
            -record.conduct_score,
            record.fifa_rank if record.fifa_rank is not None else UNKNOWN_FIFA_RANK,
            record.group,
            record.team,
        ),
    )


def get_best_third_place_teams(
    records: Iterable[ThirdPlaceRecord],
    slots: int = 8,
) -> list[ThirdPlaceRecord]:
    """Return the best third-placed teams.

    Args:
        records: Iterable of third-placed team records.
        slots: Number of third-placed teams that qualify.

    Returns:
        Top-ranked third-placed team records.
    """

    ranked = rank_third_place_teams(records)
    return ranked[:slots]


def get_best_third_place_team_names(
    records: Iterable[ThirdPlaceRecord],
    slots: int = 8,
) -> list[str]:
    """Return names of the best third-placed teams.

    Args:
        records: Iterable of third-placed team records.
        slots: Number of third-placed teams that qualify.

    Returns:
        Team names of qualifying third-placed teams.
    """

    return [
        record.team
        for record in get_best_third_place_teams(records, slots=slots)
    ]
