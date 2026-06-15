"""Group ranking utilities for tournament simulation.

This module keeps the original provisional ranking functions for backward
compatibility and adds Article 13-oriented helpers for FIFA World Cup 26 group
ranking checks.

Important boundaries:
    - ``rank_group_table`` remains the simple provisional ranking used by the
      existing smoke tests.
    - ``rank_group_table_article_13`` applies the documented FIFA Article 13
      ranking sequence for group-stage ties as far as the provided data allows.
    - If FIFA ranking snapshots are missing or teams remain tied after all
      available official criteria, deterministic team-name fallback is used only
      as a software reproducibility fallback, not as a FIFA competition rule.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


UNKNOWN_FIFA_RANK = 10_000


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


def _normalise_record(record: dict) -> dict:
    """Return a copy of a record with optional official-rule fields present."""

    normalised = dict(record)
    normalised.setdefault("conduct_score", 0)
    normalised.setdefault("fifa_rank", None)
    return normalised


def _record_match(table: dict[str, dict], match: MatchResult) -> None:
    """Apply one match result to a mutable standings table."""

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


def _finalise_goal_difference(table: Iterable[dict]) -> None:
    """Update goal difference for every standing record in-place."""

    for record in table:
        record["goal_difference"] = record["goals_for"] - record["goals_against"]


def build_group_table(matches: Iterable[MatchResult]) -> list[dict]:
    """Build a provisional group table from match results.

    Args:
        matches: Iterable of MatchResult objects.

    Returns:
        A list of team standing records sorted by provisional ranking rules.
    """

    table: dict[str, dict] = {}

    for match in matches:
        _record_match(table, match)

    _finalise_goal_difference(table.values())

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


def _build_head_to_head_table(
    teams: set[str],
    matches: Iterable[MatchResult],
) -> dict[str, dict]:
    """Build a mini table using only matches between the tied teams."""

    table = {team: _empty_team_record(team) for team in teams}

    for match in matches:
        if match.home_team in teams and match.away_team in teams:
            _record_match(table, match)

    _finalise_goal_difference(table.values())
    return table


def _head_to_head_key(record: dict) -> tuple[int, int, int]:
    """Article 13 Step 1 key for tied teams."""

    return (
        -record["points"],
        -record["goal_difference"],
        -record["goals_for"],
    )


def _overall_article_13_key(record: dict) -> tuple[int, int, int, int, int, str]:
    """Article 13 Step 2/3 key plus deterministic software fallback."""

    fifa_rank = record.get("fifa_rank")

    return (
        -record["goal_difference"],
        -record["goals_for"],
        -record.get("conduct_score", 0),
        fifa_rank if fifa_rank is not None else UNKNOWN_FIFA_RANK,
        0 if fifa_rank is not None else 1,
        record["team"],
    )


def _resolve_head_to_head_order(
    teams: list[str],
    matches: list[MatchResult],
) -> list[list[str]] | None:
    """Resolve tied teams by Article 13 Step 1, reapplying if possible.

    Returns a list of ordered team groups. A nested group with more than one
    team means those teams remain tied after head-to-head criteria. ``None``
    means head-to-head criteria did not separate any team.
    """

    if len(teams) <= 1:
        return [teams]

    h2h_table = _build_head_to_head_table(set(teams), matches)
    grouped: dict[tuple[int, int, int], list[str]] = {}

    for team in teams:
        key = _head_to_head_key(h2h_table[team])
        grouped.setdefault(key, []).append(team)

    if len(grouped) == 1:
        return None

    resolved_groups: list[list[str]] = []

    for key in sorted(grouped):
        grouped_teams = grouped[key]
        if len(grouped_teams) == 1:
            resolved_groups.append(grouped_teams)
            continue

        reapplied = _resolve_head_to_head_order(grouped_teams, matches)
        if reapplied is None:
            resolved_groups.append(grouped_teams)
        else:
            resolved_groups.extend(reapplied)

    return resolved_groups


def _resolve_tied_group_article_13(
    tied_records: list[dict],
    matches: list[MatchResult],
) -> list[dict]:
    """Resolve one same-points group with Article 13 criteria."""

    records_by_team = {record["team"]: record for record in tied_records}
    teams = [record["team"] for record in tied_records]
    head_to_head_groups = _resolve_head_to_head_order(teams, matches)

    if head_to_head_groups is None:
        return sorted(tied_records, key=_overall_article_13_key)

    ranked_records: list[dict] = []

    for group in head_to_head_groups:
        group_records = [records_by_team[team] for team in group]
        if len(group_records) == 1:
            ranked_records.extend(group_records)
        else:
            ranked_records.extend(sorted(group_records, key=_overall_article_13_key))

    return ranked_records


def rank_group_table_article_13(
    records: Iterable[dict],
    matches: Iterable[MatchResult],
) -> list[dict]:
    """Rank a group table using Article 13-oriented tiebreakers.

    The official sequence implemented here is:
        1. points in all group matches
        2. head-to-head points among tied teams
        3. head-to-head goal difference among tied teams
        4. head-to-head goals scored among tied teams
        5. reapplication to remaining tied teams when possible
        6. overall group goal difference
        7. overall group goals scored
        8. team conduct score, where a higher score ranks higher
        9. FIFA ranking, where a lower rank number is better
        10. team name as deterministic software fallback only

    Args:
        records: Iterable of standing dictionaries. Optional keys:
            ``conduct_score`` and ``fifa_rank``.
        matches: Group-stage matches used for head-to-head resolution.

    Returns:
        Ranked standing records.
    """

    normalised_records = [_normalise_record(record) for record in records]
    matches_list = list(matches)
    grouped_by_points: dict[int, list[dict]] = {}

    for record in normalised_records:
        grouped_by_points.setdefault(record["points"], []).append(record)

    ranked: list[dict] = []

    for points in sorted(grouped_by_points, reverse=True):
        same_points_records = grouped_by_points[points]
        if len(same_points_records) == 1:
            ranked.extend(same_points_records)
        else:
            ranked.extend(
                _resolve_tied_group_article_13(same_points_records, matches_list)
            )

    return ranked


def build_group_table_article_13(
    matches: Iterable[MatchResult],
    conduct_scores: dict[str, int] | None = None,
    fifa_rankings: dict[str, int] | None = None,
) -> list[dict]:
    """Build and rank a group table using Article 13-oriented tiebreakers.

    Args:
        matches: Iterable of MatchResult objects.
        conduct_scores: Optional team conduct score mapping. Higher is better.
        fifa_rankings: Optional FIFA ranking mapping. Lower rank number is better.

    Returns:
        A list of team standing records sorted by Article 13-oriented rules.
    """

    conduct_scores = conduct_scores or {}
    fifa_rankings = fifa_rankings or {}
    matches_list = list(matches)
    table: dict[str, dict] = {}

    for match in matches_list:
        _record_match(table, match)

    _finalise_goal_difference(table.values())

    for team, record in table.items():
        record["conduct_score"] = conduct_scores.get(team, 0)
        record["fifa_rank"] = fifa_rankings.get(team)

    return rank_group_table_article_13(table.values(), matches_list)


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
