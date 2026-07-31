"""End-to-end resolver tests for the groove Feature type — the groove
analogue of test_hole_array_resolution.py. See
docs/Specifications/ResolverSpecification.md and
docs/Specifications/GrooveFeatureSpecification.md, and
tests/fixtures/resolver/.
"""
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from dtml.errors import (
    GeometryBoundsError,
    SemanticValidationError,
    UnsupportedExpressionForm,
)
from dtml.loader import SCHEMAS_DIR, load_yaml, schema_registry
from dtml.resolver import resolve_part

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"
VALID_DIR = REPO_ROOT / "tests" / "fixtures" / "resolver" / "valid"
INVALID_DIR = REPO_ROOT / "tests" / "fixtures" / "resolver" / "invalid"

RESOLVED_PART_SCHEMA = load_yaml(SCHEMAS_DIR / "resolved" / "resolved_part.schema.yaml")


def assert_schema_valid(resolved: dict) -> None:
    validator = Draft202012Validator(RESOLVED_PART_SCHEMA, registry=schema_registry())
    errors = list(validator.iter_errors(resolved))
    assert not errors, f"resolved output is not schema-valid: {errors[0].message}"


def endpoints_of(resolved: dict, instance_index: int = 0):
    geometry = resolved["resolved_features"][instance_index]["geometry"]
    start = geometry["start_mm"]
    end = geometry["end_mm"]
    return (start["x"], start["y"]), (end["x"], end["y"])


# ------------------------------------------------------------------ valid --

def test_canonical_example():
    resolved = resolve_part(EXAMPLES_DIR / "panel_with_groove.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["resolution_version"] == "0.1.0"
    assert resolved["dimensions"] == {"width_mm": 500, "height_mm": 300, "thickness_mm": 18}
    assert endpoints_of(resolved) == ((50, 150), (400, 150))

    feature = resolved["resolved_features"][0]
    assert feature["feature_type"] == "groove"
    assert feature["reference_face"] == "front"
    assert feature["effective_parameters"] == {
        "width_mm": 8,
        "depth_mm": 6,
        "length_mm": 350,  # overridden from the Feature's default 400mm
        "direction": {"axis": "x", "sense": "positive"},
        "groove_form": "stopped",
    }
    assert feature["geometry"]["width_mm"] == 8
    assert feature["geometry"]["depth_mm"] == 6


def test_negative_x_direction_override():
    resolved = resolve_part(VALID_DIR / "part_groove_negative_x.part.yaml")
    assert_schema_valid(resolved)
    assert endpoints_of(resolved) == ((450, 150), (50, 150))
    assert resolved["resolved_features"][0]["effective_parameters"]["direction"] == {
        "axis": "x", "sense": "negative",
    }


def test_instance_override_touches_only_depth():
    resolved = resolve_part(VALID_DIR / "part_groove_override_depth.part.yaml")
    assert_schema_valid(resolved)
    feature = resolved["resolved_features"][0]
    assert feature["effective_parameters"]["depth_mm"] == 10
    assert feature["effective_parameters"]["width_mm"] == 8
    assert feature["effective_parameters"]["length_mm"] == 400
    assert feature["effective_parameters"]["direction"] == {"axis": "x", "sense": "positive"}
    assert endpoints_of(resolved) == ((50, 150), (450, 150))


def test_back_face_resolves_same_as_front():
    resolved = resolve_part(VALID_DIR / "part_groove_back_face.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["resolved_features"][0]["reference_face"] == "back"
    assert endpoints_of(resolved) == ((50, 150), (450, 150))


# ---------------------------------------------------------------- invalid --

def test_formula_expression_is_rejected():
    with pytest.raises(UnsupportedExpressionForm) as exc_info:
        resolve_part(INVALID_DIR / "part_groove_formula_unsupported.part.yaml")
    assert exc_info.value.form == "formula"
    assert "instance_parameters.length" in exc_info.value.path


def test_zero_width_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_groove_width_zero.part.yaml")
    assert "width" in exc_info.value.path


def test_depth_equal_to_thickness_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_groove_depth_equal_thickness.part.yaml")
    assert "depth" in exc_info.value.path


def test_start_outside_bounds_is_rejected():
    with pytest.raises(GeometryBoundsError) as exc_info:
        resolve_part(INVALID_DIR / "part_groove_start_outside_bounds.part.yaml")
    assert "start" in exc_info.value.message


def test_end_outside_bounds_is_rejected():
    with pytest.raises(GeometryBoundsError) as exc_info:
        resolve_part(INVALID_DIR / "part_groove_end_outside_bounds.part.yaml")
    # Proves the end endpoint is checked too, not only the start.
    assert "end" in exc_info.value.message


def test_radius_crossing_edge_is_rejected():
    with pytest.raises(GeometryBoundsError) as exc_info:
        resolve_part(INVALID_DIR / "part_groove_radius_crosses_edge.part.yaml")
    assert "start" in exc_info.value.message
