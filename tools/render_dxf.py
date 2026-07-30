#!/usr/bin/env python3
"""CLI wrapper around dxf.render.render_resolved_part() — see
docs/Specifications/DXFRendererSpecification.md.

Reads a resolved-Part YAML document (the output of tools/resolve_part.py)
and writes it out as a DXF file. Does not resolve or validate anything
itself — it assumes its input is already a valid resolved_part document.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from dxf.render import render_resolved_part  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("resolved", help="Path to a resolved-Part YAML document.")
    parser.add_argument("--output", required=True, help="Path to write the .dxf file to.")
    args = parser.parse_args()

    resolved = yaml.safe_load(Path(args.resolved).read_text(encoding="utf-8"))
    doc = render_resolved_part(resolved)
    doc.saveas(args.output)
    print(f"DXF written to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
