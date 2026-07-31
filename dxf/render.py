"""Translates an already-resolved Part (dtml.resolver.resolve_part()'s
output, valid against schemas/resolved/resolved_part.schema.yaml) into
DXF entities. Does not resolve references, merge defaults, evaluate
Expressions, decide Feature semantics, or re-check engineering rules —
those are the resolver's job. See
docs/Specifications/DXFRendererSpecification.md.
"""
from __future__ import annotations

import math

import ezdxf
from ezdxf.document import Drawing

from .errors import UnsupportedFeatureType
from .layers import ALL_LAYERS, PANEL_OUTLINE, groove_layer_for_face, hole_layer_for_face

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
        feature_type = feature["feature_type"]
        if feature_type == "hole_array":
            layer = hole_layer_for_face(feature["reference_face"])
            for hole in feature["geometry"]["holes"]:
                centre = hole["centre_mm"]
                msp.add_circle(
                    center=(centre["x"], centre["y"]),
                    radius=hole["diameter_mm"] / 2,
                    dxfattribs={"layer": layer},
                )
        elif feature_type == "groove":
            layer = groove_layer_for_face(feature["reference_face"])
            geometry = feature["geometry"]
            start = geometry["start_mm"]
            end = geometry["end_mm"]
            points = _capsule_points(
                (start["x"], start["y"]), (end["x"], end["y"]), geometry["width_mm"] / 2
            )
            msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer})
        else:
            raise UnsupportedFeatureType(feature_type)

    return doc


def _capsule_points(
    start: tuple[float, float], end: tuple[float, float], radius: float
) -> list[tuple[float, float, float, float, float]]:
    """The stadium/capsule outline swept by a stopped groove's cutter —
    two straight sides parallel to the centreline plus a semicircular cap
    at each endpoint, bulging past it along the direction of travel. See
    docs/Specifications/GrooveFeatureSpecification.md, "Geometry model".

    Returns LWPOLYLINE vertices in "xyseb" format (start_width, end_width
    always 0). A bulge of -1 encodes an exact 180-degree arc; the sign is
    fixed by the P1->P2->P3->P4 winding chosen below, verified to trace
    the outline clockwise (hence a negative/clockwise bulge) for either
    axis and either sense.
    """
    sx, sy = start
    ex, ey = end
    length = math.hypot(ex - sx, ey - sy)
    ux, uy = (ex - sx) / length, (ey - sy) / length
    px, py = -uy, ux  # perpendicular to the centreline

    p1 = (sx + radius * px, sy + radius * py)
    p2 = (ex + radius * px, ey + radius * py)
    p3 = (ex - radius * px, ey - radius * py)
    p4 = (sx - radius * px, sy - radius * py)

    return [
        (p1[0], p1[1], 0, 0, 0),
        (p2[0], p2[1], 0, 0, -1),  # arc around `end`, capping past it
        (p3[0], p3[1], 0, 0, 0),
        (p4[0], p4[1], 0, 0, -1),  # arc around `start`, capping past it
    ]


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
