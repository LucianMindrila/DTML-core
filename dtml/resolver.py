"""Orchestrates the full ten-stage pipeline — the only entry point
tools/resolve_part.py calls. See ResolverSpecification.md.
"""
from __future__ import annotations

from pathlib import Path

from jsonschema import Draft202012Validator

from . import coordinate_system, expressions, merge, semantic_validation
from .errors import SemanticValidationError
from .loader import (
    EXAMPLES_DIR,
    SCHEMAS_DIR,
    build_document_index,
    load_and_validate,
    load_yaml,
    schema_registry,
)
from .references import resolve_reference

RESOLUTION_VERSION = "0.1.0"


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

    resolved_features = []
    for i, instance in enumerate(part.get("feature_instances", [])):
        instance_path = f"$.feature_instances[{i}]"

        # Stage 3: resolve the Feature reference, then transitively its
        # Operation — both by canonical identity, never by filename.
        feature = resolve_reference(instance["feature"], index, f"{instance_path}.feature")
        resolve_reference(feature["operation"], index, f"{instance_path}.feature.operation")

        if feature.get("feature_type") != "hole_array":
            raise SemanticValidationError(
                f"{instance_path}.feature",
                f"resolver v0.1 only supports feature_type 'hole_array', "
                f"got '{feature.get('feature_type')}'",
            )

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

        resolved_features.append({
            "instance_index": i,
            "feature": instance["feature"],
            "operation": feature["operation"],
            "reference_face": instance["reference_face"],
            "anchor_mm": {"x": anchor["x"], "y": anchor["y"]},
            "effective_parameters": effective_parameters_out,
            "holes": holes,
        })

    # Stage 9: emit resolved model.
    resolved_part = {
        "schema_version": part["schema_version"],
        "resolution_version": RESOLUTION_VERSION,
        "source_part": {
            "ref": f"{part['namespace']}.{part['id']}",
            "object_version": part["object_version"],
        },
        "dimensions": {
            "width_mm": width,
            "height_mm": height,
            "thickness_mm": thickness,
        },
        "resolved_features": resolved_features,
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
