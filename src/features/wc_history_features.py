"""World Cup history feature scaffold for the team lead preprocessing pipeline.

The team lead baseline includes World Cup participation and title-count features
for home and away teams, plus home-away gap features.

Current status:
    Scaffold only. Historical source selection and generation logic are follow-up work.
"""

from __future__ import annotations

import pandas as pd


REQUIRED_HISTORY_COLUMNS = {"team", "wc_participations", "wc_titles"}


def add_world_cup_history_features(
    matches: pd.DataFrame,
    history: pd.DataFrame,
) -> pd.DataFrame:
    """Attach World Cup participation/title features to match rows.

    Expected output columns include:
        - `home_wc_participations`
        - `away_wc_participations`
        - `home_wc_titles`
        - `away_wc_titles`
        - `gap_wc_participations`
        - `gap_wc_titles`

    Args:
        matches: Match table with normalized home/away team names.
        history: Team-level World Cup history table.

    Returns:
        Match table with World Cup history features.

    Raises:
        NotImplementedError: Until source mapping and join logic are ported.
    """

    raise NotImplementedError(
        "World Cup history features are scaffolded but not implemented yet."
    )


def validate_world_cup_history(history: pd.DataFrame) -> None:
    """Validate minimum columns for World Cup history input."""

    missing_columns = REQUIRED_HISTORY_COLUMNS - set(history.columns)
    if missing_columns:
        raise ValueError(f"Missing World Cup history columns: {sorted(missing_columns)}")
