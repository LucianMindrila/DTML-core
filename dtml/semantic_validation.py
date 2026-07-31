"""Stages 6 and 8 — semantic rules the source schemas deliberately leave
open. See ResolverSpecification.md, "Semantic validation rules", and
HoleArrayFeatureSpecification.md, "What's structurally enforced vs.
semantic".
"""
from __future__ import annotations

from .errors import GeometryBoundsError, SemanticValidationError

RECOGNISED_HOLE_ARRAY_KEYS = {
    "diameter", "hole_form", "depth", "pitch", "count", "start_offset", "direction",
}

RECOGNISED_GROOVE_KEYS = {"width", "depth", "length", "direction", "groove_form"}


def validate_part_dimensions(width: float, height: float, thickness: float, path: str) -> None:
    if width <= 0:
        raise SemanticValidationError(f"{path}.dimensions.width", "must be > 0")
    if height <= 0:
        raise SemanticValidationError(f"{path}.dimensions.height", "must be > 0")
    if thickness <= 0:
        raise SemanticValidationError(f"{path}.thickness", "must be > 0")


def validate_material_type(material: dict, expected: str, path: str) -> None:
    """The schema can't check a referenced document's material_type — that's
    cross-document. See EdgeTreatmentSpecification.md, acceptance criteria."""
    actual = material.get("material_type")
    if actual != expected:
        raise SemanticValidationError(
            path, f"referenced Material must be material_type '{expected}', got '{actual}'"
        )


def validate_construction_thickness(
    construction: str, thickness: float, material_thickness_mm: float, path: str
) -> None:
    """v1 scope: stock always stays 18mm MFC — single_18mm resolves to one
    sheet's thickness, bonded_double_18mm to two. See
    MaterialSpecification.md, "Thickness cross-check: now enforced"."""
    expected = material_thickness_mm if construction == "single_18mm" else 2 * material_thickness_mm
    if thickness != expected:
        raise SemanticValidationError(
            f"{path}.thickness",
            f"construction '{construction}' requires thickness={expected} "
            f"(material thickness_mm={material_thickness_mm}) — got {thickness}",
        )


def validate_no_duplicate_edges(edge_treatments: list, path: str) -> None:
    """Schema-valid, resolver-rejected — see EdgeTreatmentSpecification.md,
    "Duplicate-edge rejection"."""
    seen = set()
    for i, treatment in enumerate(edge_treatments):
        edge = treatment["edge"]
        if edge in seen:
            raise SemanticValidationError(
                f"{path}[{i}].edge", f"duplicate edge_treatments entry for edge '{edge}'"
            )
        seen.add(edge)


def validate_edge_band_dimensions(thickness_mm: float, width_mm: float, path: str) -> None:
    if thickness_mm <= 0:
        raise SemanticValidationError(f"{path}.thickness_mm", "must be > 0")
    if width_mm <= 0:
        raise SemanticValidationError(f"{path}.width_mm", "must be > 0")


def validate_edge_band_material_thickness(
    band_thickness_mm: float, material_thickness_mm: float, path: str
) -> None:
    """A Part cannot claim '1mm edging' while pointing at a Material stocked
    at 2mm. See MaterialSpecification.md, "Thickness cross-check: now
    enforced"."""
    if band_thickness_mm != material_thickness_mm:
        raise SemanticValidationError(
            path,
            f"band.thickness_mm ({band_thickness_mm}) must equal the "
            f"referenced Material's thickness_mm ({material_thickness_mm})",
        )


def validate_hole_array_parameters(params: dict, thickness: float, path: str) -> None:
    # No unrecognised key survives the merge — currently the only
    # enforcement point, since instance_parameters is schema-open. See
    # ResolverSpecification.md.
    unknown = set(params) - RECOGNISED_HOLE_ARRAY_KEYS
    if unknown:
        raise SemanticValidationError(
            path, f"unrecognised parameter key(s): {sorted(unknown)}"
        )

    diameter = params["diameter"]
    if diameter <= 0:
        raise SemanticValidationError(f"{path}.diameter", "must be > 0")

    pitch = params["pitch"]
    if pitch <= 0:
        raise SemanticValidationError(f"{path}.pitch", "must be > 0")

    count = params["count"]
    if count != int(count) or count < 1:
        raise SemanticValidationError(f"{path}.count", "must be a positive integer")

    start_offset = params.get("start_offset", 0)
    if start_offset < 0:
        raise SemanticValidationError(f"{path}.start_offset", "must be >= 0")

    hole_form = params["hole_form"]
    if hole_form == "blind":
        depth = params["depth"]
        if depth <= 0:
            raise SemanticValidationError(f"{path}.depth", "must be > 0")
        if depth >= thickness:
            raise SemanticValidationError(
                f"{path}.depth",
                f"must be less than the Part's thickness (strictly) — "
                f"got depth={depth}, thickness={thickness}",
            )


def validate_groove_parameters(params: dict, thickness: float, path: str) -> None:
    # Mirrors validate_hole_array_parameters — see
    # GrooveFeatureSpecification.md, "What's structurally enforced vs.
    # semantic".
    unknown = set(params) - RECOGNISED_GROOVE_KEYS
    if unknown:
        raise SemanticValidationError(
            path, f"unrecognised parameter key(s): {sorted(unknown)}"
        )

    width = params["width"]
    if width <= 0:
        raise SemanticValidationError(f"{path}.width", "must be > 0")

    length = params["length"]
    if length <= 0:
        raise SemanticValidationError(f"{path}.length", "must be > 0")

    depth = params["depth"]
    if depth <= 0:
        raise SemanticValidationError(f"{path}.depth", "must be > 0")
    if depth >= thickness:
        raise SemanticValidationError(
            f"{path}.depth",
            f"must be less than the Part's thickness (strictly) — "
            f"got depth={depth}, thickness={thickness}",
        )


def validate_groove_bounds(
    start: tuple[float, float],
    end: tuple[float, float],
    groove_width: float,
    part_width: float,
    part_height: float,
    path: str,
) -> None:
    """Inset-rectangle rule for a stopped groove — see
    GrooveFeatureSpecification.md, "Bounds rule: inset rectangle, not raw
    endpoint containment". Both centreline endpoints must lie within the
    Part face inset by radius = groove_width / 2 from every boundary, so
    the fully swept capsule (which bulges past each endpoint by that
    radius, along the direction of travel) stays inside the Part."""
    radius = groove_width / 2
    for label, (x, y) in (("start", start), ("end", end)):
        if not (radius <= x <= part_width - radius):
            raise GeometryBoundsError(
                path,
                f"groove {label} x={x} (radius={radius}) is outside Part "
                f"bounds [{radius}, {part_width - radius}] (width={part_width})",
            )
        if not (radius <= y <= part_height - radius):
            raise GeometryBoundsError(
                path,
                f"groove {label} y={y} (radius={radius}) is outside Part "
                f"bounds [{radius}, {part_height - radius}] (height={part_height})",
            )


def validate_hole_bounds(
    centre: tuple[float, float], diameter: float, width: float, height: float, path: str
) -> None:
    """Radius-aware bounds check: a centre exactly on the edge would
    otherwise produce a partially missing hole."""
    radius = diameter / 2
    x, y = centre
    if not (radius <= x <= width - radius):
        raise GeometryBoundsError(
            path,
            f"hole centre x={x} (radius={radius}) is outside Part bounds "
            f"[{radius}, {width - radius}] (width={width})",
        )
    if not (radius <= y <= height - radius):
        raise GeometryBoundsError(
            path,
            f"hole centre y={y} (radius={radius}) is outside Part bounds "
            f"[{radius}, {height - radius}] (height={height})",
        )
