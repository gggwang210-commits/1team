"""Rolling four-year performance feature scaffold.

The team lead preprocessing baseline uses rolling four-year team statistics for
home and away teams. This module reserves the public API for those features.

Current status:
    Scaffold only. Implementation and generated output checks are follow-up work.
"""

from __future__ import annotations

import pandas as pd


DEFAULT_LOOKBACK_YEARS = 4


def add_rolling_team_performance_features(
    matches: pd.DataFrame,
    lookback_years: int = DEFAULT_LOOKBACK_YEARS,
) -> pd.DataFrame:
    """Add rolling team-performance features for home and away teams.

    Expected output families include goals scored/received, wins, draws, losses,
    match counts, goal difference, win rate, goals per match, and related gaps.

    Args:
        matches: Chronologically ordered match table.
        lookback_years: Rolling lookback window in years.

    Returns:
        Match table with rolling performance features.

    Raises:
        NotImplementedError: Until the team lead notebook logic is ported.
    """

    raise NotImplementedError(
        "Rolling four-year performance features are scaffolded but not "
        "implemented yet."
    )
