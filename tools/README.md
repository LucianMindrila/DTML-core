# tools

Supporting scripts and utilities that aren't part of the core engine or
the extractor (see `../extractor/` for DXF mining specifically).

## `validate_schema.py`

Minimal Draft 2020-12 conformance checker for the schema layer. Answers
two questions only — see the module docstring and
`../docs/Specifications/SchemaConventions.md` ("Validator scope") for what
it deliberately does not check.

```bash
# Every schemas/*.schema.yaml is a valid Draft 2020-12 schema, with every $ref it contains statically resolved
python tools/validate_schema.py --schemas

# A YAML instance validates against the schema it declares via x-dtml-schema
python tools/validate_schema.py examples/panel_with_shelf_pin_array.part.yaml
```

Requires `jsonschema>=4.18` and `PyYAML` — see `../requirements-dev.txt`.

## `resolve_part.py`

CLI wrapper around `dtml.resolver.resolve_part()` — see
`../docs/Specifications/ResolverSpecification.md`.

```bash
python tools/resolve_part.py examples/panel_with_shelf_pin_array.part.yaml --output resolved.yaml
```

## `render_dxf.py`

CLI wrapper around `dxf.render.render_resolved_part()` — see
`../docs/Specifications/DXFRendererSpecification.md`. Takes a resolved
Part YAML document (the output of `resolve_part.py`, not a raw Part) and
writes it out as a `.dxf` file. Deliberately doesn't resolve or validate
anything itself; the two tools compose as separate steps:

```bash
python tools/resolve_part.py examples/panel_with_shelf_pin_array.part.yaml --output resolved.yaml
python tools/render_dxf.py resolved.yaml --output panel.dxf
```

Requires `ezdxf>=1.3` — see `../requirements-dev.txt`.

Expected future contents: library linting (e.g. flagging any object whose
`provenance.confidence` is `unconfirmed` that's somehow been referenced by
a production Module), and DXF diff/comparison utilities supporting the
verification workflow in `../tests/`.
