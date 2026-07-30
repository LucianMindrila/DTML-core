"""Resolver error types.

Every resolver-stage failure carries a JSON-path-like string identifying
where in the source (or generated) document it occurred, matching the
error-reporting convention tools/validate_schema.py already uses
(`$.path` then message) — see docs/Specifications/ResolverSpecification.md.
"""
from __future__ import annotations


class ResolutionError(Exception):
    """Base class for every resolver-stage failure."""

    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}")

    def __str__(self) -> str:
        return f"{self.path}\n  {self.message}"


class SchemaValidationError(ResolutionError):
    """A source document fails validation against its declared schema."""


class ReferenceResolutionError(ResolutionError):
    """A `ref`/`object_version` doesn't resolve to a matching document."""


class UnsupportedExpressionForm(ResolutionError):
    """A `formula` or `rule_reference` Expression — valid DTML, but not
    evaluated by resolver v0.1."""

    def __init__(self, path: str, form: str):
        super().__init__(
            path,
            f"Expression form '{form}' is valid DTML but unsupported by "
            f"resolver v0.1.",
        )
        self.form = form


class SemanticValidationError(ResolutionError):
    """A resolved value violates a semantic rule the source schema
    deliberately leaves unstructural (see HoleArrayFeatureSpecification.md,
    "What's structurally enforced vs. semantic")."""


class GeometryBoundsError(ResolutionError):
    """A generated hole centre falls outside the Part's bounds."""
