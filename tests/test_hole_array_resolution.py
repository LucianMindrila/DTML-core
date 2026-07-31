"""End-to-end resolver tests — dtml.resolver.resolve_part() against real
Part documents, exercising every pipeline stage together. See
docs/Specifications/ResolverSpecification.md and tests/fixtures/resolver/.
"""
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from dtml.errors import (
    GeometryBoundsError,
    ReferenceResolutionError,
    SemanticValidationError,
    UnsupportedExpressionForm,
    UnsupportedFeatureType,
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


def centres_of(resolved: dict, instance_index: int = 0):
    holes = resolved["resolved_features"][instance_index]["geometry"]["holes"]
    return [(h["centre_mm"]["x"], h["centre_mm"]["y"]) for h in holes]


# ------------------------------------------------------------------ valid --

def test_canonical_example_positive_y():
    resolved = resolve_part(EXAMPLES_DIR / "panel_with_shelf_pin_array.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["resolution_version"] == "0.2.0"
    assert resolved["construction"] == "single_18mm"
    assert resolved["dimensions"] == {"width_mm": 600, "height_mm": 720, "thickness_mm": 18}
    assert [edge["edge"] for edge in resolved["resolved_edges"]] == ["top", "bottom"]
    assert all(edge["length_mm"] == 600 for edge in resolved["resolved_edges"])
    assert all(
        edge["process_requirements"]["pre_mill"] == {"required": True, "removal_mm": 1}
        for edge in resolved["resolved_edges"]
    )
    assert centres_of(resolved) == [
        (20, 120), (20, 152), (20, 184), (20, 216), (20, 248),
    ]
    feature = resolved["resolved_features"][0]
    assert feature["feature_type"] == "hole_array"
    assert feature["reference_face"] == "front"
    assert feature["effective_parameters"]["direction"] == {"axis": "y", "sense": "positive"}
    for hole in feature["geometry"]["holes"]:
        assert hole["hole_form"] == "blind"
        assert hole["depth_mm"] == 13


def test_negative_y_direction_override():
    resolved = resolve_part(VALID_DIR / "part_negative_y.part.yaml")
    assert_schema_valid(resolved)
    assert centres_of(resolved) == [
        (20, 650), (20, 618), (20, 586), (20, 554), (20, 522),
    ]
    assert resolved["resolved_features"][0]["effective_parameters"]["direction"] == {
        "axis": "y", "sense": "negative",
    }


def test_positive_x_direction_override():
    resolved = resolve_part(VALID_DIR / "part_positive_x.part.yaml")
    assert_schema_valid(resolved)
    assert centres_of(resolved) == [(70, 360), (102, 360), (134, 360)]
    assert resolved["resolved_features"][0]["effective_parameters"]["direction"] == {
        "axis": "x", "sense": "positive",
    }


def test_through_hole_depth_resolves_to_part_thickness():
    resolved = resolve_part(VALID_DIR / "part_through_hole.part.yaml")
    assert_schema_valid(resolved)
    feature = resolved["resolved_features"][0]
    assert "depth_mm" not in feature["effective_parameters"]
    assert centres_of(resolved) == [(300, 70), (300, 110), (300, 150)]
    for hole in feature["geometry"]["holes"]:
        assert hole["hole_form"] == "through"
        assert hole["depth_mm"] == 18  # the Part's own thickness


def test_instance_override_touches_only_count():
    resolved = resolve_part(VALID_DIR / "part_instance_override_count.part.yaml")
    assert_schema_valid(resolved)
    feature = resolved["resolved_features"][0]
    assert feature["effective_parameters"]["count"] == 3
    assert feature["effective_parameters"]["pitch_mm"] == 32
    assert feature["effective_parameters"]["start_offset_mm"] == 100
    assert centres_of(resolved) == [(20, 120), (20, 152), (20, 184)]


def test_nested_partial_override_keeps_default_axis():
    resolved = resolve_part(VALID_DIR / "part_nested_partial_override_direction.part.yaml")
    assert_schema_valid(resolved)
    direction = resolved["resolved_features"][0]["effective_parameters"]["direction"]
    assert direction == {"axis": "y", "sense": "negative"}
    assert centres_of(resolved) == [
        (20, 650), (20, 618), (20, 586), (20, 554), (20, 522),
    ]


def test_back_face_resolves_same_as_front():
    resolved = resolve_part(VALID_DIR / "part_back_face.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["resolved_features"][0]["reference_face"] == "back"
    assert centres_of(resolved) == [
        (20, 120), (20, 152), (20, 184), (20, 216), (20, 248),
    ]


# ---------------------------------------------------------------- invalid --

def test_formula_expression_is_rejected():
    with pytest.raises(UnsupportedExpressionForm) as exc_info:
        resolve_part(INVALID_DIR / "part_formula_unsupported.part.yaml")
    assert exc_info.value.form == "formula"
    assert "instance_parameters.count" in exc_info.value.path


def test_unsupported_feature_type_is_rejected():
    with pytest.raises(UnsupportedFeatureType) as exc_info:
        resolve_part(INVALID_DIR / "part_unsupported_feature_type.part.yaml")
    assert exc_info.value.feature_type == "pocket"
    assert "feature_instances[0].feature" in exc_info.value.path


def test_missing_referenced_feature_is_rejected():
    with pytest.raises(ReferenceResolutionError):
        resolve_part(INVALID_DIR / "part_missing_referenced_feature.part.yaml")


def test_wrong_object_version_is_rejected():
    with pytest.raises(ReferenceResolutionError):
        resolve_part(INVALID_DIR / "part_wrong_object_version.part.yaml")


def test_non_integral_count_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_count_not_integral.part.yaml")
    assert "count" in exc_info.value.path


def test_zero_count_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_count_zero.part.yaml")
    assert "count" in exc_info.value.path


def test_negative_pitch_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_pitch_negative.part.yaml")
    assert "pitch" in exc_info.value.path


def test_blind_depth_equal_to_thickness_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_blind_depth_equal_thickness.part.yaml")
    assert "depth" in exc_info.value.path


def test_blind_depth_greater_than_thickness_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_blind_depth_greater_thickness.part.yaml")
    assert "depth" in exc_info.value.path


def test_first_hole_outside_bounds_is_rejected():
    with pytest.raises(GeometryBoundsError) as exc_info:
        resolve_part(INVALID_DIR / "part_first_hole_outside_bounds.part.yaml")
    assert "holes[0]" in exc_info.value.path


def test_final_hole_outside_bounds_is_rejected():
    with pytest.raises(GeometryBoundsError) as exc_info:
        resolve_part(INVALID_DIR / "part_final_hole_outside_bounds.part.yaml")
    # Proves later holes are checked too, not only the first.
    assert "holes[0]" not in exc_info.value.path


def test_hole_radius_crossing_edge_is_rejected():
    with pytest.raises(GeometryBoundsError) as exc_info:
        resolve_part(INVALID_DIR / "part_hole_radius_crosses_edge.part.yaml")
    assert "holes[0]" in exc_info.value.path
