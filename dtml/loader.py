"""Stages 1-2 — load YAML documents and validate them against their
declared x-dtml-schema.

Reuses the same jsonschema/referencing machinery as
tools/validate_schema.py so the resolver and the schema validator can
never disagree about what "valid" means.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from .errors import SchemaValidationError

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
EXAMPLES_DIR = REPO_ROOT / "examples"


def load_yaml(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_path(error) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


@lru_cache(maxsize=1)
def schema_registry() -> Registry:
    """Build a Registry over every schemas/**/*.schema.yaml file, including
    schemas/resolved/ — the resolved-output contract needs to be
    resolvable too, for stage 10."""
    resources = []
    for schema_path in SCHEMAS_DIR.rglob("*.schema.yaml"):
        contents = load_yaml(schema_path)
        if "$id" in contents:
            resources.append((contents["$id"], Resource.from_contents(contents)))
    return Registry().with_resources(resources)


def resolve_schema_ref(document_path: Path, schema_ref: str) -> Path:
    candidate = (document_path.parent / schema_ref).resolve()
    if candidate.is_file():
        return candidate
    # Fallback: schema_ref given relative to schemas/ itself.
    candidate = SCHEMAS_DIR / Path(schema_ref)
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(schema_ref)


def load_and_validate(path: Path) -> dict:
    """Load a YAML document and validate it against its declared
    x-dtml-schema. Returns the document with x-dtml-schema stripped.
    Raises SchemaValidationError rather than a bare jsonschema exception,
    so every resolver stage raises from the same error hierarchy."""
    document = load_yaml(path)
    schema_ref = document.get("x-dtml-schema")
    if not schema_ref:
        raise SchemaValidationError(str(path), "missing 'x-dtml-schema' field")

    schema_path = resolve_schema_ref(path, schema_ref)
    schema = load_yaml(schema_path)
    validator = Draft202012Validator(schema, registry=schema_registry())

    data = {k: v for k, v in document.items() if k != "x-dtml-schema"}
    errors = sorted(validator.iter_errors(data), key=format_path)
    if errors:
        first = errors[0]
        raise SchemaValidationError(f"{path}:{format_path(first)}", first.message)
    return data


def build_document_index(search_roots: list[Path]) -> dict[tuple[str, str], Path]:
    """Scan every *.yaml file under the given search roots and index it by
    (canonical_ref, object_version) — the identity it actually *declares*,
    not its filename. A same-named file that happens to sit in the search
    path is not enough — see ResolverSpecification.md, "Reference
    resolution"."""
    index: dict[tuple[str, str], Path] = {}
    for root in search_roots:
        if not root.is_dir():
            continue
        for candidate_path in root.rglob("*.yaml"):
            try:
                document = load_yaml(candidate_path)
            except yaml.YAMLError:
                continue
            if not isinstance(document, dict):
                continue
            namespace = document.get("namespace")
            id_ = document.get("id")
            object_version = document.get("object_version")
            if not (namespace and id_ and object_version):
                continue
            canonical_ref = f"{namespace}.{id_}"
            index[(canonical_ref, object_version)] = candidate_path
    return index
