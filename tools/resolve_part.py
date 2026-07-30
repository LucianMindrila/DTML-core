#!/usr/bin/env python3
"""CLI wrapper around dtml.resolver.resolve_part() — see
docs/Specifications/ResolverSpecification.md.

Loads a Part, resolves it through the full ten-stage pipeline, and either
prints or writes the resulting schema-valid resolved_part document.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dtml.errors import ResolutionError  # noqa: E402
from dtml.resolver import default_search_roots, resolve_part  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("part", help="Path to a Part YAML document to resolve.")
    parser.add_argument(
        "--search-root", action="append", default=[], dest="search_roots",
        help="Additional directory to search for referenced Feature/Operation "
             "documents by canonical identity. May be repeated. Defaults to "
             "[the Part file's own directory, examples/].",
    )
    parser.add_argument(
        "--output", help="Write the resolved document here instead of stdout.",
    )
    args = parser.parse_args()

    part_path = Path(args.part)
    search_roots = default_search_roots(part_path) + [Path(p) for p in args.search_roots]

    try:
        resolved = resolve_part(part_path, search_roots=search_roots)
    except ResolutionError as exc:
        print(f"Resolution failed at {exc.path}:", file=sys.stderr)
        print(f"  {exc.message}", file=sys.stderr)
        return 1

    output_text = yaml.safe_dump(resolved, sort_keys=False)
    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
        print(f"Resolved Part written to {args.output}")
    else:
        print(output_text, end="")

    return 0


if __name__ == "__main__":
    sys.exit(main())
