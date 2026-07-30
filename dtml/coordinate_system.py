"""Stage 7 — anchor + offset + direction coordinate generation.

See ResolverSpecification.md, "Coordinate generation: anchor + offset +
direction".
"""
from __future__ import annotations

_DIRECTION_VECTORS = {
    ("x", "positive"): (1, 0),
    ("x", "negative"): (-1, 0),
    ("y", "positive"): (0, 1),
    ("y", "negative"): (0, -1),
}


def direction_vector(axis: str, sense: str) -> tuple[int, int]:
    return _DIRECTION_VECTORS[(axis, sense)]


def generate_hole_centres(
    anchor: tuple[float, float],
    start_offset: float,
    pitch: float,
    count: int,
    axis: str,
    sense: str,
) -> list[tuple[float, float, float]]:
    """Returns `count` (x, y, z) centres. z is always 0 in this face-local
    frame — depth is reported separately, never folded into z (front/back
    mirroring is a downstream capability-resolution concern, not this
    stage's — see ResolverSpecification.md)."""
    dx, dy = direction_vector(axis, sense)
    ax, ay = anchor
    centres = []
    for i in range(count):
        distance = start_offset + i * pitch
        centres.append((ax + dx * distance, ay + dy * distance, 0.0))
    return centres
