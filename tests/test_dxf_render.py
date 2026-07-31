"""dxf.render.render_resolved_part() — the thin DXF renderer. See
docs/Specifications/DXFRendererSpecification.md.

Resolves the committed shelf-pin panel example once via
dtml.resolver.resolve_part(), then only ever inspects the rendered DXF
through ezdxf — never re-opening or re-parsing any DTML source document
from within the render path itself.
"""
from pathlib import Path

import ezdxf
import pytest

from dtml.resolver import resolve_part
from dxf.errors import UnsupportedFeatureType
from dxf.layers import HOLES_BACK, HOLES_FRONT, PANEL_OUTLINE
from dxf.render import render_resolved_part

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = REPO_ROOT / "examples"

EXPECTED_HOLE_CENTRES = [(20, 120), (20, 152), (20, 184), (20, 216), (20, 248)]


def _resolved_shelf_pin_panel() -> dict:
    return resolve_part(EXAMPLES_DIR / "panel_with_shelf_pin_array.part.yaml")


def test_outline_matches_resolved_dimensions():
    doc = render_resolved_part(_resolved_shelf_pin_panel())
    msp = doc.modelspace()

    outlines = list(msp.query(f'LWPOLYLINE[layer=="{PANEL_OUTLINE}"]'))
    assert len(outlines) == 1
    outline = outlines[0]
    assert outline.closed
    assert list(outline.get_points("xy")) == [(0, 0), (600, 0), (600, 720), (0, 720)]


def test_holes_land_on_front_layer_with_correct_geometry():
    doc = render_resolved_part(_resolved_shelf_pin_panel())
    msp = doc.modelspace()

    front_circles = list(msp.query(f'CIRCLE[layer=="{HOLES_FRONT}"]'))
    assert len(front_circles) == 5
    centres = sorted((c.dxf.center.x, c.dxf.center.y) for c in front_circles)
    assert centres == EXPECTED_HOLE_CENTRES
    assert all(c.dxf.radius == 2.5 for c in front_circles)


def test_back_layer_exists_but_is_empty_for_a_front_only_part():
    doc = render_resolved_part(_resolved_shelf_pin_panel())
    msp = doc.modelspace()

    assert HOLES_BACK in doc.layers
    assert list(msp.query(f'CIRCLE[layer=="{HOLES_BACK}"]')) == []


def test_units_are_millimetres():
    doc = render_resolved_part(_resolved_shelf_pin_panel())
    assert doc.header["$INSUNITS"] == 4
    assert doc.header["$MEASUREMENT"] == 1


def test_metadata_round_trips_through_save_and_reload(tmp_path):
    resolved = _resolved_shelf_pin_panel()
    doc = render_resolved_part(resolved)
    dxf_path = tmp_path / "panel.dxf"
    doc.saveas(dxf_path)

    reloaded = ezdxf.readfile(dxf_path)
    outline = list(reloaded.modelspace().query(f'LWPOLYLINE[layer=="{PANEL_OUTLINE}"]'))[0]
    xdata = {tag.value for tag in outline.get_xdata("DTML")}
    assert resolved["source_part"]["ref"] in xdata
    assert resolved["source_part"]["object_version"] in xdata
    assert resolved["resolution_version"] in xdata


def test_unsupported_feature_type_is_rejected_not_skipped():
    """Per ResolvedGeometrySpecification.md's three-way support rule: a
    resolved_feature the renderer doesn't recognise must fail the whole
    render, never be silently omitted. The resolver itself never produces
    a feature_type other than hole_array today, so this mutates an
    otherwise-valid resolved dict to simulate a future branch this
    renderer version doesn't yet implement.
    """
    resolved = _resolved_shelf_pin_panel()
    resolved["resolved_features"][0]["feature_type"] = "groove"

    with pytest.raises(UnsupportedFeatureType) as exc_info:
        render_resolved_part(resolved)
    assert exc_info.value.feature_type == "groove"


def test_renderer_never_touches_unresolved_source_documents(monkeypatch):
    """The acceptance criterion: rendering must not access any DTML source
    document. Simulated by making file reads explode and confirming the
    renderer still succeeds against an already-resolved dict held in memory.
    """
    resolved = _resolved_shelf_pin_panel()

    def _forbidden_read(*_args, **_kwargs):
        raise AssertionError("render_resolved_part() must not read files")

    monkeypatch.setattr(Path, "read_text", _forbidden_read)
    monkeypatch.setattr(Path, "open", _forbidden_read)

    doc = render_resolved_part(resolved)
    msp = doc.modelspace()
    assert len(list(msp.query(f'CIRCLE[layer=="{HOLES_FRONT}"]'))) == 5
