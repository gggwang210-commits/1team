"""Short-term form feature scaffold for the team lead preprocessing pipeline.

The team lead baseline uses EWMA-style recent form features and missing flags.
This module reserves the public interface for those features.

Current status:
    Scaffold only. No generated CSV artifacts are written by this module.
"""

from __future__ import annotations

import pandas as pd


DEFAULT_EWMA_ALPHA = 0.35


def add_ewma_form_features(
    matches: pd.DataFrame,
    alpha: float = DEFAULT_EWMA_ALPHA,
) -> pd.DataFrame:
    """Add home/away EWMA form and missing-flag features.

    Expected output columns include:
        - `home_form`
        - `away_form`
        - `home_form_missing`
        - `away_form_missing`
        - `gap_form`

    Args:
        matches: Chronologically ordered match table.
        alpha: EWMA smoothing parameter.

    Returns:
        Match table with short-term form features.

    Raises:
        NotImplementedError: Until the team lead notebook logic is ported.
    """

    raise NotImplementedError(
        "EWMA form feature generation is scaffolded but not implemented yet."
    )
