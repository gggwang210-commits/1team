"""Helpers for the team lead 52-feature schema contract.

This module provides lightweight helpers around `data/schema/team_lead_features.json`.
It is intentionally safe to use before the full preprocessing pipeline is ported.

Current status:
    Contract-loading and validation helpers only. No generated CSV artifacts are
    created or committed by this module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = PROJECT_ROOT / "data" / "schema" / "team_lead_features.json"


def load_team_lead_feature_contract(schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> dict[str, Any]:
    """Load the team lead feature schema contract.

    Args:
        schema_path: Path to the machine-readable feature schema.

    Returns:
        Parsed JSON schema dictionary.
    """

    with Path(schema_path).open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def get_team_lead_feature_names(schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> list[str]:
    """Return the ordered 52-feature list from the schema contract."""

    schema = load_team_lead_feature_contract(schema_path)
    return [feature["name"] for feature in schema["features"]]


def validate_team_lead_feature_contract(schema_path: Path | str = DEFAULT_SCHEMA_PATH) -> None:
    """Validate the minimum invariants of the team lead feature contract.

    This mirrors the pytest gate and can be reused by future preprocessing code.

    Raises:
        ValueError: If the schema violates the basic 52-feature contract.
    """

    schema = load_team_lead_feature_contract(schema_path)
    names = get_team_lead_feature_names(schema_path)

    if schema.get("feature_count") != 52:
        raise ValueError("Team lead feature schema must declare feature_count = 52.")
    if len(names) != 52:
        raise ValueError("Team lead feature schema must contain exactly 52 features.")
    if len(names) != len(set(names)):
        raise ValueError("Team lead feature schema contains duplicate feature names.")
