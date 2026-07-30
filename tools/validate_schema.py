#!/usr/bin/env python3
"""Minimal Draft 2020-12 conformance checker for DTML schemas and instances.

This is the first executable conformance check for the schema layer — it
is deliberately not the expression engine, resolver, or DXF generator. It
answers two questions only:

1. Is every schemas/*.schema.yaml file a well-formed Draft 2020-12 JSON
   Schema, with every $ref it contains (however deeply nested) resolving
   to a real target?
2. Does a given instance document validate against the schema it declares
   (via its `x-dtml-schema` field)?

It does not check whether a `ref:` in an instance actually resolves to an
existing library/ entry — see docs/Specifications/SchemaConventions.md,
"Validator scope".
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def schema_paths() -> list[Path]:
    return sorted(SCHEMAS_DIR.rglob("*.schema.yaml"))


def build_registry(contents_by_path: dict[Path, dict]) -> Registry:
    resources = [
        (contents["$id"], Resource.from_contents(contents))
        for contents in contents_by_path.values()
        if "$id" in contents
    ]
    return Registry().with_resources(resources)


def walk_refs(node, path="$"):
    """Yield (ref, json-path) for every {"$ref": ...} anywhere in a schema,
    however deeply nested — including under properties/items/allOf branches
    that validating a single instance would never visit."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            yield ref, path
        for key, value in node.items():
            yield from walk_refs(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk_refs(value, f"{path}[{i}]")


def check_refs_resolve(contents: dict, registry: Registry) -> list[str]:
    resolver = registry.resolver(base_uri=contents["$id"])
    messages = []
    for ref, loc in walk_refs(contents):
        try:
            resolver.lookup(ref)
        except Unresolvable as exc:
            messages.append(f"  {loc}: $ref '{ref}' does not resolve ({exc})")
    return messages


def check_schemas() -> int:
    paths = schema_paths()
    contents_by_path = {path: load_yaml(path) for path in paths}
    errors = 0

    for path, contents in contents_by_path.items():
        try:
            Draft202012Validator.check_schema(contents)
        except Exception as exc:
            errors += 1
            print(f"INVALID SCHEMA: {path.name}")
            print(f"  {exc}\n")

    if errors:
        print(f"{errors} schema(s) failed Draft 2020-12 validation.")
        return 1

    registry = build_registry(contents_by_path)
    checked_for_refs = 0
    for path, contents in contents_by_path.items():
        if "$id" not in contents:
            # Not yet migrated to the $id/$ref convention — see
            # docs/Specifications/SchemaConventions.md. Structurally valid
            # per the check above, but not part of the cross-file
            # reference graph, so there is nothing to resolve.
            continue
        checked_for_refs += 1
        # Statically walk every $ref in the document and resolve it against
        # the registry — deliberately not "validate against {} and see what
        # gets touched", since a $ref nested under an optional property
        # (e.g. properties.material.$ref) is never visited by validating an
        # empty instance and a break there would go unnoticed.
        problems = check_refs_resolve(contents, registry)
        if problems:
            errors += 1
            print(f"UNRESOLVABLE REFERENCE in {path.name}")
            print("\n".join(problems) + "\n")

    if errors:
        print(f"{errors} schema(s) have unresolvable $ref targets.")
        return 1

    not_migrated = len(paths) - checked_for_refs
    print(f"All {len(paths)} schemas are valid Draft 2020-12 "
          f"({checked_for_refs} with every $ref statically resolved, "
          f"{not_migrated} not yet on the $id/$ref convention).")
    return 0


def format_path(error) -> str:
    path = "$"
    for part in error.absolute_path:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def resolve_declared_schema(instance_path: Path, schema_ref: str) -> Path:
    candidate = (instance_path.parent / schema_ref).resolve()
    if candidate.is_file():
        return candidate
    # Fallback: schema_ref given relative to schemas/ itself (e.g.
    # "features/hole_array.schema.yaml") rather than relative to the
    # instance file. Preserve the full relative path here — collapsing to
    # Path(schema_ref).name would silently flatten subdirectories like
    # schemas/features/ and fail to find the real file.
    candidate = SCHEMAS_DIR / Path(schema_ref)
    if candidate.is_file():
        return candidate
    raise FileNotFoundError(schema_ref)


def check_instance(instance_path: Path) -> int:
    instance = load_yaml(instance_path)
    schema_ref = instance.get("x-dtml-schema")
    if not schema_ref:
        print(f"Validation failed: {instance_path} has no 'x-dtml-schema' "
              f"field declaring which schema it conforms to.")
        return 1

    try:
        schema_path = resolve_declared_schema(instance_path, schema_ref)
    except FileNotFoundError:
        print(f"Validation failed: declared schema '{schema_ref}' not found.")
        return 1

    contents_by_path = {path: load_yaml(path) for path in schema_paths()}
    registry = build_registry(contents_by_path)
    schema = contents_by_path.get(schema_path, load_yaml(schema_path))
    validator = Draft202012Validator(schema, registry=registry)

    # x-dtml-schema is tooling metadata, not part of the DTML data model.
    instance_data = {k: v for k, v in instance.items() if k != "x-dtml-schema"}

    errors = list(validator.iter_errors(instance_data))
    errors.sort(key=format_path)

    if errors:
        print(f"Validation failed: {len(errors)} error(s)\n")
        for error in errors:
            print(format_path(error))
            print(f"  {error.message}\n")
        return 1

    print(f"Valid: {instance_path}")
    print(f"Schema: {schema_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schemas", action="store_true",
        help="Validate every schemas/*.schema.yaml file is a valid Draft 2020-12 schema with every $ref statically resolved.",
    )
    parser.add_argument(
        "instance", nargs="?",
        help="Path to a YAML instance document to validate against its declared x-dtml-schema.",
    )
    args = parser.parse_args()

    if args.schemas:
        return check_schemas()
    if args.instance:
        return check_instance(Path(args.instance))

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
