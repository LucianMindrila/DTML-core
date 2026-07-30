"""Stage 5 — merge Feature default parameters with instance overrides.

Both inputs are already fully resolved to plain values by this point
(stage 4 runs before merge), so this is a plain recursive dict merge —
no Expression-shape detection needed. This is why Expression resolution
happens before merge, not after — see ResolverSpecification.md.
"""
from __future__ import annotations


def deep_merge(base: dict, override: dict) -> dict:
    """Keys present in both: recurse if both sides are dicts, otherwise
    override wins outright (covers scalars and arrays)."""
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged
