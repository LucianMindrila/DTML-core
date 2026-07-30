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
python tools/validate_schema.py tests/fixtures/valid/panel-with-shelf-pin-array.yaml
```

Requires `jsonschema>=4.18` and `PyYAML` — see `../requirements-dev.txt`.

Expected future contents: library linting (e.g. flagging any object whose
`provenance.confidence` is `unconfirmed` that's somehow been referenced by
a production Module), and DXF diff/comparison utilities supporting the
verification workflow in `../tests/`.
