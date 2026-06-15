"""Tournament sample-weight scaffold for the team lead preprocessing pipeline.

The team lead baseline uses tournament importance to create training sample
weights. This module reserves the interface for that weighting policy.

Current status:
    Scaffold only. The exact tournament-weight mapping is follow-up work.
"""

from __future__ import annotations

import pandas as pd


DEFAULT_TOURNAMENT_WEIGHT = 1.0


def add_tournament_sample_weights(
    matches: pd.DataFrame,
    tournament_column: str = "tournament",
) -> pd.DataFrame:
    """Add a sample-weight column based on tournament importance.

    Args:
        matches: Match table that includes tournament metadata.
        tournament_column: Column containing tournament names or categories.

    Returns:
        Match table with a `sample_weight` or equivalent training-weight column.

    Raises:
        NotImplementedError: Until the team lead weighting policy is ported.
    """

    raise NotImplementedError(
        "Tournament sample-weight generation is scaffolded but not implemented yet."
    )


def build_weight_vector(matches: pd.DataFrame, weight_column: str = "sample_weight") -> pd.Series:
    """Return the training weight vector for model fitting.

    Args:
        matches: Feature table containing a sample-weight column.
        weight_column: Name of the sample-weight column.

    Returns:
        A pandas Series of training weights.

    Raises:
        ValueError: If the weight column is missing.
    """

    if weight_column not in matches.columns:
        raise ValueError(f"Missing sample-weight column: {weight_column}")
    return matches[weight_column]
