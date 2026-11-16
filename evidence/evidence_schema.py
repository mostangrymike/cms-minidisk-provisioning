from __future__ import annotations

from typing import Any, Dict

REQUIRED_KEYS = ["id", "timestamp", "type", "source"]


def validate_evidence(evidence: Dict[str, Any]) -> bool:
    """
    Very lightweight validation: ensure required keys exist and have simple types.
    This is intentionally minimal to avoid pulling extra dependencies.
    """
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be a dict")
    for key in REQUIRED_KEYS:
        if key not in evidence:
            raise ValueError(f"evidence missing required key: {key}")
    # Basic type checks
    if not isinstance(evidence["id"], str):
        raise ValueError("evidence.id must be a string")
    if not isinstance(evidence["timestamp"], str):
        raise ValueError("evidence.timestamp must be a string (ISO8601)")
    if not isinstance(evidence["type"], str):
        raise ValueError("evidence.type must be a string")
    if not isinstance(evidence["source"], str):
        raise ValueError("evidence.source must be a string")
    return True
