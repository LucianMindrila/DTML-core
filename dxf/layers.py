"""Deterministic DXF layer names. See
docs/Specifications/DXFRendererSpecification.md, "Layer conventions".
"""

PANEL_OUTLINE = "PANEL_OUTLINE"
HOLES_FRONT = "HOLES_FRONT"
HOLES_BACK = "HOLES_BACK"
GROOVES_FRONT = "GROOVES_FRONT"
GROOVES_BACK = "GROOVES_BACK"

ALL_LAYERS = (PANEL_OUTLINE, HOLES_FRONT, HOLES_BACK, GROOVES_FRONT, GROOVES_BACK)

_HOLE_LAYER_BY_FACE = {
    "front": HOLES_FRONT,
    "back": HOLES_BACK,
}

_GROOVE_LAYER_BY_FACE = {
    "front": GROOVES_FRONT,
    "back": GROOVES_BACK,
}


def hole_layer_for_face(reference_face: str) -> str:
    return _HOLE_LAYER_BY_FACE[reference_face]


def groove_layer_for_face(reference_face: str) -> str:
    return _GROOVE_LAYER_BY_FACE[reference_face]
