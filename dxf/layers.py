"""Deterministic DXF layer names. See
docs/Specifications/DXFRendererSpecification.md, "Layer conventions".
"""

PANEL_OUTLINE = "PANEL_OUTLINE"
HOLES_FRONT = "HOLES_FRONT"
HOLES_BACK = "HOLES_BACK"

ALL_LAYERS = (PANEL_OUTLINE, HOLES_FRONT, HOLES_BACK)

_HOLE_LAYER_BY_FACE = {
    "front": HOLES_FRONT,
    "back": HOLES_BACK,
}


def hole_layer_for_face(reference_face: str) -> str:
    return _HOLE_LAYER_BY_FACE[reference_face]
