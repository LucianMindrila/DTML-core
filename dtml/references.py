"""Stage 3 — resolve {ref, object_version} objects to loaded, validated
documents, by canonical identity (never by filename).

See ResolverSpecification.md, "Reference resolution".
"""
from __future__ import annotations

from pathlib import Path

from .errors import ReferenceResolutionError
from .loader import load_and_validate


def resolve_reference(reference: dict, index: dict[tuple[str, str], Path], path: str) -> dict:
    """`reference` is an already-loaded {"ref": ..., "object_version": ...}
    object (reference objects are never Expressions, so no expression
    resolution applies here). `index` maps (ref, object_version) to the
    file that actually declares that identity — see
    dtml.loader.build_document_index — so a successful lookup already
    guarantees the identity match; no further check is needed here."""
    ref = reference["ref"]
    object_version = reference["object_version"]
    candidate_path = index.get((ref, object_version))
    if candidate_path is None:
        raise ReferenceResolutionError(
            path,
            f"no document declares namespace+id '{ref}' at object_version "
            f"'{object_version}' under the configured search roots.",
        )
    return load_and_validate(candidate_path)
