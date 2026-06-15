"""Team-name normalization scaffold for the team lead preprocessing pipeline.

This module will eventually reproduce the team lead workflow that normalizes
historical national-team names before merging match results with Elo, FIFA
ranking, and derived feature sources.

Current status:
    Scaffold only. No generated CSV artifacts are written by this module.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


FORMER_NAMES_COLUMNS = {"current", "former"}


def load_former_names(path: Path | str) -> pd.DataFrame:
    """Load the team-name alias table used for normalization.

    Args:
        path: Path to the team-name alias file, expected to contain former and
            current team-name fields.

    Returns:
        A DataFrame containing team-name mapping rows.

    Raises:
        NotImplementedError: Until the shared team notebook logic is ported.
    """

    raise NotImplementedError(
        "Team-name alias loading will be implemented from the team lead "
        "preprocessing notebook."
    )


def normalize_team_names(
    matches: pd.DataFrame,
    former_names: pd.DataFrame,
    home_column: str = "home_team",
    away_column: str = "away_team",
) -> pd.DataFrame:
    """Normalize home/away team names using the team lead alias contract.

    Args:
        matches: Match-result table with home and away team columns.
        former_names: Team-name alias mapping table.
        home_column: Home-team column name.
        away_column: Away-team column name.

    Returns:
        A copy of ``matches`` with normalized team names.

    Raises:
        NotImplementedError: Until the exact normalization rules are ported.
    """

    raise NotImplementedError(
        "Team-name normalization rules are scaffolded but not implemented yet."
    )
