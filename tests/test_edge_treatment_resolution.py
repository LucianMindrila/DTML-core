"""End-to-end resolver tests for edge treatments and material
references — the third knowledge-object type this schema foundation
resolves. See docs/Specifications/EdgeTreatmentSpecification.md and
docs/Specifications/MaterialSpecification.md.
"""
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from dtml.errors import SemanticValidationError
from dtml.loader import SCHEMAS_DIR, load_yaml, schema_registry
from dtml.resolver import resolve_part

REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_DIR = REPO_ROOT / "tests" / "fixtures" / "resolver" / "valid"
INVALID_DIR = REPO_ROOT / "tests" / "fixtures" / "resolver" / "invalid"

RESOLVED_PART_SCHEMA = load_yaml(SCHEMAS_DIR / "resolved" / "resolved_part.schema.yaml")


def assert_schema_valid(resolved: dict) -> None:
    validator = Draft202012Validator(RESOLVED_PART_SCHEMA, registry=schema_registry())
    errors = list(validator.iter_errors(resolved))
    assert not errors, f"resolved output is not schema-valid: {errors[0].message}"


# ------------------------------------------------------------------ valid --

def test_single_edge_band_resolves():
    resolved = resolve_part(VALID_DIR / "part_with_edge_band.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["resolved_edges"] == [
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
            "length_mm": 600,
            "process_requirements": {"pre_mill": {"required": True, "removal_mm": 1}},
        }
    ]


def test_no_edge_treatments_resolves_to_empty_list():
    resolved = resolve_part(VALID_DIR / "part_back_face.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["resolved_edges"] == []


def test_bonded_double_18mm_construction_resolves():
    resolved = resolve_part(VALID_DIR / "part_bonded_double_18mm.part.yaml")
    assert_schema_valid(resolved)
    assert resolved["construction"] == "bonded_double_18mm"
    assert resolved["dimensions"]["thickness_mm"] == 36


# ---------------------------------------------------------------- invalid --

def test_construction_thickness_mismatch_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_construction_thickness_mismatch.part.yaml")
    assert "thickness" in exc_info.value.path


def test_duplicate_edge_treatment_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_duplicate_edge_treatment.part.yaml")
    assert "edge_treatments" in exc_info.value.path


def test_edge_band_wrong_material_type_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_edge_band_wrong_material_type.part.yaml")
    assert "band.material" in exc_info.value.path


def test_edge_band_thickness_mismatch_is_rejected():
    with pytest.raises(SemanticValidationError) as exc_info:
        resolve_part(INVALID_DIR / "part_edge_band_thickness_mismatch.part.yaml")
    assert "thickness_mm" in exc_info.value.path
