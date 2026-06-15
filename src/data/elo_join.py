"""Elo merge-as-of scaffold for the team lead preprocessing pipeline.

This module reserves the contract for joining match rows with the latest known
pre-match Elo ratings for both teams.

Current status:
    Scaffold only. The exact merge-as-of logic from the team lead notebook will
    be ported in a follow-up implementation PR.
"""

from __future__ import annotations

import pandas as pd


REQUIRED_MATCH_COLUMNS = {"date", "home_team", "away_team"}
REQUIRED_ELO_COLUMNS = {"date", "team", "elo"}


def add_pre_match_elo_features(
    matches: pd.DataFrame,
    elo_history: pd.DataFrame,
    date_column: str = "date",
) -> pd.DataFrame:
    """Attach home/away Elo and delta Elo features to match rows.

    Args:
        matches: Normalized match table.
        elo_history: Historical Elo table.
        date_column: Match date column used for merge-as-of joins.

    Returns:
        Match table with `home_elo`, `away_elo`, and `delta_elo` columns.

    Raises:
        NotImplementedError: Until the merge-as-of implementation is ported.
    """

    raise NotImplementedError(
        "Elo merge-as-of logic is scaffolded but not implemented yet."
    )


def validate_elo_join_inputs(matches: pd.DataFrame, elo_history: pd.DataFrame) -> None:
    """Validate the minimum input columns for Elo feature generation.

    Args:
        matches: Match table to enrich.
        elo_history: Historical Elo table.

    Raises:
        ValueError: If required input columns are missing.
    """

    missing_match_columns = REQUIRED_MATCH_COLUMNS - set(matches.columns)
    missing_elo_columns = REQUIRED_ELO_COLUMNS - set(elo_history.columns)

    if missing_match_columns:
        raise ValueError(f"Missing match columns: {sorted(missing_match_columns)}")
    if missing_elo_columns:
        raise ValueError(f"Missing Elo columns: {sorted(missing_elo_columns)}")
