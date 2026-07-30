"""Translates an already-resolved Part (dtml.resolver.resolve_part()'s
output, valid against schemas/resolved/resolved_part.schema.yaml) into
DXF entities. Does not resolve references, merge defaults, evaluate
Expressions, decide Feature semantics, or re-check engineering rules —
those are the resolver's job. See
docs/Specifications/DXFRendererSpecification.md.
"""
from __future__ import annotations

import ezdxf
from ezdxf.document import Drawing

from .layers import ALL_LAYERS, PANEL_OUTLINE, hole_layer_for_face

DTML_APPID = "DTML"

_INSUNITS_MILLIMETERS = 4
_MEASUREMENT_METRIC = 1


def render_resolved_part(resolved: dict) -> Drawing:
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = _INSUNITS_MILLIMETERS
    doc.header["$MEASUREMENT"] = _MEASUREMENT_METRIC
    doc.appids.add(DTML_APPID)
    for layer in ALL_LAYERS:
        doc.layers.add(layer)

    msp = doc.modelspace()

    width = resolved["dimensions"]["width_mm"]
    height = resolved["dimensions"]["height_mm"]
    outline = msp.add_lwpolyline(
        [(0, 0), (width, 0), (width, height), (0, height)],
        format="xy",
        close=True,
        dxfattribs={"layer": PANEL_OUTLINE},
    )
    outline.set_xdata(DTML_APPID, _source_xdata(resolved))

    for feature in resolved["resolved_features"]:
        layer = hole_layer_for_face(feature["reference_face"])
        for hole in feature["holes"]:
            centre = hole["centre_mm"]
            msp.add_circle(
                center=(centre["x"], centre["y"]),
                radius=hole["diameter_mm"] / 2,
                dxfattribs={"layer": layer},
            )

    return doc


def _source_xdata(resolved: dict) -> list[tuple[int, str]]:
    source_part = resolved["source_part"]
    return [
        (1000, "source_part_ref"),
        (1000, source_part["ref"]),
        (1000, "source_part_object_version"),
        (1000, source_part["object_version"]),
        (1000, "resolution_version"),
        (1000, resolved["resolution_version"]),
    ]
