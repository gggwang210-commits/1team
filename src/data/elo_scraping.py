"""Elo scraping scaffold for the team lead preprocessing pipeline.

The team lead preprocessing baseline uses historical Elo data as a primary
strength source. This module reserves the interface for scraping or refreshing
Elo history without committing generated artifacts by default.

Current status:
    Scaffold only. Network scraping and persistence logic are intentionally not
    implemented in this PR.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


DEFAULT_ELO_SOURCE_URL = "https://www.eloratings.net/"


def fetch_elo_history(source_url: str = DEFAULT_ELO_SOURCE_URL) -> pd.DataFrame:
    """Fetch historical Elo rows from the configured source.

    Args:
        source_url: Elo source URL. The team baseline references eloratings.net.

    Returns:
        A DataFrame with historical Elo records.

    Raises:
        NotImplementedError: Until scraping behavior and caching policy are set.
    """

    raise NotImplementedError(
        "Elo scraping is scaffolded only. Add source-specific scraping, rate "
        "limit, cache, and reproducibility policy in a follow-up PR."
    )


def save_elo_history(elo_history: pd.DataFrame, output_path: Path | str) -> None:
    """Persist fetched Elo history to a local generated artifact path.

    Args:
        elo_history: Historical Elo table.
        output_path: Local path for generated Elo output.

    Raises:
        NotImplementedError: Until generated artifact policy is implemented.
    """

    raise NotImplementedError(
        "Generated Elo artifacts should not be committed by default; persistence "
        "logic will be implemented after the artifact policy is finalized."
    )
