"""schemas/resolved/resolved_part.schema.yaml's polymorphic resolved_feature
— see docs/Specifications/ResolvedGeometrySpecification.md.

RESOLVED_GROOVE_PANEL is hand-constructed to match exactly what
dtml.resolver.resolve_part() produces for examples/panel_with_groove.part.yaml
(see tests/test_groove_resolution.py's test_canonical_example, which
asserts the resolver's real output against these same values), proving
the resolved_feature_groove branch added to resolved_part.schema.yaml
validates independent of any one producer. tests/test_dxf_render.py
reuses it to assert the renderer's real groove geometry output.
"""
from jsonschema import Draft202012Validator

from dtml.loader import SCHEMAS_DIR, load_yaml, schema_registry

RESOLVED_GROOVE_PANEL = {
    "schema_version": "0.1",
    "resolution_version": "0.2.0",
    "source_part": {
        "ref": "cuttingedgebespoke.part.panel_with_groove",
        "object_version": "1.0.0",
    },
    "construction": "single_18mm",
    "dimensions": {"width_mm": 500, "height_mm": 300, "thickness_mm": 18},
    "resolved_features": [
        {
            "instance_index": 0,
            "feature_type": "groove",
            "feature": {
                "ref": "cuttingedgebespoke.feature.straight_groove",
                "object_version": "1.0.0",
            },
            "operation": {
                "ref": "cuttingedgebespoke.operation.router_groove",
                "object_version": "1.0.0",
            },
            "reference_face": "front",
            "effective_parameters": {
                "width_mm": 8,
                "depth_mm": 6,
                "length_mm": 350,
                "direction": {"axis": "x", "sense": "positive"},
                "groove_form": "stopped",
            },
            "geometry": {
                "start_mm": {"x": 50, "y": 150, "z": 0},
                "end_mm": {"x": 400, "y": 150, "z": 0},
                "width_mm": 8,
                "depth_mm": 6,
            },
        }
    ],
    "resolved_edges": [
        {
            "edge": "top",
            "treatment_type": "edge_band",
            "band": {
                "material": {
                    "ref": "cuttingedgebespoke.material.white_abs_1mm",
                    "object_version": "1.0.0",
                },
                "thickness_mm": 1,
                "width_mm": 22,
            },
            "length_mm": 500,
            "process_requirements": {"pre_mill": {"required": True, "removal_mm": 1}},
        },
        {
            "edge": "bottom",
            "treatment_type": "edge_band",
            "band": {
                "material": {
                    "ref": "cuttingedgebespoke.material.white_abs_1mm",
                    "object_version": "1.0.0",
                },
                "thickness_mm": 1,
                "width_mm": 22,
            },
            "length_mm": 500,
            "process_requirements": {"pre_mill": {"required": True, "removal_mm": 1}},
        },
    ],
}


def test_resolved_groove_branch_validates():
    resolved_schema = load_yaml(SCHEMAS_DIR / "resolved" / "resolved_part.schema.yaml")
    validator = Draft202012Validator(resolved_schema, registry=schema_registry())
    assert list(validator.iter_errors(RESOLVED_GROOVE_PANEL)) == []


def test_resolved_groove_branch_rejects_a_second_form_value():
    """groove_form's enum permits only "stopped" in the resolved contract
    too, mirroring the source Feature schema's restriction."""
    invalid = {
        **RESOLVED_GROOVE_PANEL,
        "resolved_features": [
            {
                **RESOLVED_GROOVE_PANEL["resolved_features"][0],
                "effective_parameters": {
                    **RESOLVED_GROOVE_PANEL["resolved_features"][0]["effective_parameters"],
                    "groove_form": "through",
                },
            }
        ],
    }
    resolved_schema = load_yaml(SCHEMAS_DIR / "resolved" / "resolved_part.schema.yaml")
    validator = Draft202012Validator(resolved_schema, registry=schema_registry())
    assert list(validator.iter_errors(invalid)) != []
