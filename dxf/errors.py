"""DXF renderer error types — deliberately separate from dtml.errors, not
a shared base class, because dxf/ must never import from dtml/ (see
DXFRendererSpecification.md, "Module layout": the renderer's only
contract is the resolved dict shape, not the resolver's internals).
"""
from __future__ import annotations


class UnsupportedFeatureType(Exception):
    """A resolved_feature's feature_type is schema-valid but this renderer
    version doesn't know how to draw it — the "known but unsupported"
    case in docs/Specifications/ResolvedGeometrySpecification.md's
    three-way feature_type support rule. Rendering must fail entirely
    rather than silently skip the feature.
    """

    def __init__(self, feature_type: str):
        self.feature_type = feature_type
        super().__init__(
            f"resolved feature_type '{feature_type}' is unsupported by "
            f"this DXF renderer version."
        )
