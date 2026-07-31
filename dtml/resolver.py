"""Orchestrates the full ten-stage pipeline — the only entry point
tools/resolve_part.py calls. See ResolverSpecification.md.
"""
from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from . import coordinate_system, expressions, merge, semantic_validation
from .errors import SemanticValidationError, UnsupportedFeatureType
from .loader import (
    EXAMPLES_DIR,
    SCHEMAS_DIR,
    build_document_index,
    load_and_validate,
    load_yaml,
    schema_registry,
)
from .references import resolve_reference

RESOLUTION_VERSION = "0.2.0"


def default_search_roots(part_path: Path) -> list[Path]:
    return [part_path.resolve().parent, EXAMPLES_DIR]


def resolve_part(part_path: Path, search_roots: list[Path] | None = None) -> dict:
    part_path = Path(part_path)
    if search_roots is None:
        search_roots = default_search_roots(part_path)

    # Stages 1-2: load and validate the Part itself.
    part = load_and_validate(part_path)

    # Reference index, built once over every configured search root.
    index = build_document_index(search_roots)

    # Stage 4 (Part-level): resolve thickness/dimensions to plain numbers.
    thickness = expressions.resolve_value(part["thickness"], "$.thickness")
    width = expressions.resolve_value(part["dimensions"]["width"], "$.dimensions.width")
    height = expressions.resolve_value(part["dimensions"]["height"], "$.dimensions.height")

    semantic_validation.validate_part_dimensions(width, height, thickness, "$")

    # Stage 3 (material): resolve part.material, then cross-check
    # construction against its thickness_mm — see MaterialSpecification.md,
    # "Thickness cross-check: now enforced".
    part_material = resolve_reference(part["material"], index, "$.material")
    semantic_validation.validate_material_type(part_material, "panel_stock", "$.material")
    semantic_validation.validate_construction_thickness(
        part["construction"], thickness, part_material["thickness_mm"], "$"
    )

    resolved_features = []
    for i, instance in enumerate(part.get("feature_instances", [])):
        instance_path = f"$.feature_instances[{i}]"

        # Stage 3: resolve the Feature reference, then transitively its
        # Operation — both by canonical identity, never by filename.
        feature = resolve_reference(instance["feature"], index, f"{instance_path}.feature")
        resolve_reference(feature["operation"], index, f"{instance_path}.feature.operation")

        feature_type = feature.get("feature_type")
        if feature_type not in ("hole_array", "groove"):
            raise UnsupportedFeatureType(f"{instance_path}.feature", feature_type)

        # Stage 4 (Feature-level): resolve defaults and overrides
        # independently, before merging — see ResolverSpecification.md.
        default_params = expressions.resolve_value(
            feature["parameters"], f"{instance_path}.feature.parameters"
        )
        override_params = expressions.resolve_value(
            instance.get("instance_parameters", {}), f"{instance_path}.instance_parameters"
        )
        anchor = expressions.resolve_value(instance["position"], f"{instance_path}.position")

        # Stage 5: merge.
        effective_params = merge.deep_merge(default_params, override_params)

        if feature_type == "hole_array":
            resolved_features.append(_resolve_hole_array(
                instance, feature, effective_params, anchor, thickness, width, height,
                i, instance_path,
            ))
        else:
            resolved_features.append(_resolve_groove(
                instance, feature, effective_params, anchor, thickness, width, height,
                i, instance_path,
            ))

    resolved_edges = _resolve_edge_treatments(part, index, width, height)

    # Stage 9: emit resolved model.
    resolved_part = {
        "schema_version": part["schema_version"],
        "resolution_version": RESOLUTION_VERSION,
        "source_part": {
            "ref": f"{part['namespace']}.{part['id']}",
            "object_version": part["object_version"],
        },
        "construction": part["construction"],
        "dimensions": {
            "width_mm": width,
            "height_mm": height,
            "thickness_mm": thickness,
        },
        "resolved_features": resolved_features,
        "resolved_edges": resolved_edges,
    }

    # Stage 10: validate the assembled output against its own contract, as
    # a regression safety net — see ResolverSpecification.md, "Why the
    # resolved schema can be stricter than the source schemas".
    resolved_schema = load_yaml(SCHEMAS_DIR / "resolved" / "resolved_part.schema.yaml")
    validator = Draft202012Validator(resolved_schema, registry=schema_registry())
    output_errors = list(validator.iter_errors(resolved_part))
    if output_errors:
        raise SemanticValidationError(
            "$", f"resolved output failed its own schema: {output_errors[0].message}"
        )

    return resolved_part


def _resolve_edge_treatments(
    part: dict, index: dict, width: float, height: float
) -> list[dict]:
    """Sparse by construction — only edges that actually carry a treatment
    produce an entry. See EdgeTreatmentSpecification.md."""
    edge_treatments = part.get("edge_treatments", [])
    semantic_validation.validate_no_duplicate_edges(edge_treatments, "$.edge_treatments")

    resolved_edges = []
    for i, treatment in enumerate(edge_treatments):
        treatment_path = f"$.edge_treatments[{i}]"
        band = treatment["band"]

        band_material = resolve_reference(
            band["material"], index, f"{treatment_path}.band.material"
        )
        semantic_validation.validate_material_type(
            band_material, "edge_band", f"{treatment_path}.band.material"
        )

        band_thickness = expressions.resolve_value(
            band["thickness_mm"], f"{treatment_path}.band.thickness_mm"
        )
        band_width = expressions.resolve_value(
            band["width_mm"], f"{treatment_path}.band.width_mm"
        )
        semantic_validation.validate_edge_band_dimensions(
            band_thickness, band_width, f"{treatment_path}.band"
        )
        semantic_validation.validate_edge_band_material_thickness(
            band_thickness, band_material["thickness_mm"], f"{treatment_path}.band.thickness_mm"
        )

        # length_mm is derived from the Part's own finished dimensions, not
        # carried from the source — see EdgeTreatmentSpecification.md,
        # "length_mm: computed from finished dimensions".
        edge = treatment["edge"]
        length = width if edge in ("top", "bottom") else height

        resolved_edges.append({
            "edge": edge,
            "treatment_type": treatment["treatment_type"],
            "band": {
                "material": band["material"],
                "thickness_mm": band_thickness,
                "width_mm": band_width,
            },
            "length_mm": length,
            "process_requirements": {
                "pre_mill": {
                    "required": True,
                    "removal_mm": band_thickness,
                },
            },
        })

    return resolved_edges


def _resolve_hole_array(
    instance: dict, feature: dict, effective_params: dict, anchor: dict,
    thickness: float, width: float, height: float, i: int, instance_path: str,
) -> dict:
    # Stage 6: semantic validation of effective parameters.
    semantic_validation.validate_hole_array_parameters(
        effective_params, thickness, f"{instance_path}.effective_parameters"
    )

    # Stage 7: generate coordinates.
    start_offset = effective_params.get("start_offset", 0)
    direction = effective_params["direction"]
    count = int(effective_params["count"])
    centres = coordinate_system.generate_hole_centres(
        anchor=(anchor["x"], anchor["y"]),
        start_offset=start_offset,
        pitch=effective_params["pitch"],
        count=count,
        axis=direction["axis"],
        sense=direction["sense"],
    )

    hole_form = effective_params["hole_form"]
    depth = effective_params["depth"] if hole_form == "blind" else thickness

    holes = []
    for hole_index, (x, y, z) in enumerate(centres):
        # Stage 8: geometry bounds, radius-aware.
        semantic_validation.validate_hole_bounds(
            (x, y), effective_params["diameter"], width, height,
            f"{instance_path}.holes[{hole_index}]",
        )
        holes.append({
            "index": hole_index,
            "centre_mm": {"x": x, "y": y, "z": z},
            "diameter_mm": effective_params["diameter"],
            "depth_mm": depth,
            "hole_form": hole_form,
        })

    effective_parameters_out = {
        "diameter_mm": effective_params["diameter"],
        "hole_form": hole_form,
        "pitch_mm": effective_params["pitch"],
        "count": count,
        "start_offset_mm": start_offset,
        "direction": direction,
    }
    if hole_form == "blind":
        effective_parameters_out["depth_mm"] = depth

    return {
        "instance_index": i,
        "feature_type": "hole_array",
        "feature": instance["feature"],
        "operation": feature["operation"],
        "reference_face": instance["reference_face"],
        "anchor_mm": {"x": anchor["x"], "y": anchor["y"]},
        "effective_parameters": effective_parameters_out,
        "geometry": {"holes": holes},
    }


def _resolve_groove(
    instance: dict, feature: dict, effective_params: dict, anchor: dict,
    thickness: float, width: float, height: float, i: int, instance_path: str,
) -> dict:
    # Stage 6: semantic validation of effective parameters.
    semantic_validation.validate_groove_parameters(
        effective_params, thickness, f"{instance_path}.effective_parameters"
    )

    # Stage 7: generate coordinates — the centreline start is the anchor
    # itself (see GrooveFeatureSpecification.md, "Parameter shape"); the
    # end is computed from length and direction.
    direction = effective_params["direction"]
    start = (anchor["x"], anchor["y"], 0.0)
    end = coordinate_system.generate_groove_endpoint(
        anchor=(anchor["x"], anchor["y"]),
        length=effective_params["length"],
        axis=direction["axis"],
        sense=direction["sense"],
    )

    # Stage 8: geometry bounds — inset-rectangle rule, both endpoints.
    semantic_validation.validate_groove_bounds(
        (start[0], start[1]), (end[0], end[1]), effective_params["width"],
        width, height, f"{instance_path}.geometry",
    )

    return {
        "instance_index": i,
        "feature_type": "groove",
        "feature": instance["feature"],
        "operation": feature["operation"],
        "reference_face": instance["reference_face"],
        "effective_parameters": {
            "width_mm": effective_params["width"],
            "depth_mm": effective_params["depth"],
            "length_mm": effective_params["length"],
            "direction": direction,
            "groove_form": effective_params["groove_form"],
        },
        "geometry": {
            "start_mm": {"x": start[0], "y": start[1], "z": start[2]},
            "end_mm": {"x": end[0], "y": end[1], "z": end[2]},
            "width_mm": effective_params["width"],
            "depth_mm": effective_params["depth"],
        },
    }
