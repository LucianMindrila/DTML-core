# tests

Verification for the manufacturing brain. Two categories, per
`../docs/KnowledgeCapture.md`'s narration-first + verification-second
methodology:

1. **Rule/equation unit tests** — given known inputs, does a Rule or
   Module produce the expected dimensions/positions? Standard unit
   testing against `schemas/rule.schema.yaml`-shaped definitions.
2. **DXF round-trip verification** — generate output from an encoded
   Rule/Module and diff it against a real historical drawing (see
   `../extractor/`). A mismatch is a signal to investigate — either the
   narration missed a condition, or the historical job was a genuine
   one-off deviation. Never silently resolved by adjusting the rule to
   fit the one example.

Both categories are empty until Phase 2 (`../docs/Roadmap.md`) produces
the first confirmed Rules/Modules to test against.

## `fixtures/`

Schema-layer conformance fixtures for `../tools/validate_schema.py` —
these test the *schema shape*, not manufacturing correctness, so they
exist now rather than waiting for Phase 2:

- `fixtures/valid/` — specialised validation cases only (e.g. grammar
  edge cases such as `namespace-two-segments.yaml`), not general
  worked examples. A fully-worked valid Part/Feature/Operation belongs in
  `../examples/` instead, which CI validates directly — see
  `../.github/workflows/schema-validation.yml`. Don't duplicate an
  example here just to have a "valid" fixture for it; that copy would
  only drift from the original over time.
- `fixtures/invalid/` — deliberately broken instances, each documenting
  in a comment which single constraint it violates and why, so a fixture
  failing for the wrong reason is easy to spot.

Run the validator against a fixture directly (see `../tools/README.md`).

## `fixtures/resolver/`

Part/Feature documents exercising `dtml.resolver.resolve_part()` (see
`../docs/Specifications/ResolverSpecification.md`), run via
`test_hole_array_resolution.py` — a different layer than
`fixtures/valid|invalid/` above:

- `fixtures/resolver/valid/` — Parts that resolve successfully, each
  proving one resolver behaviour (a direction override, a partial nested
  override, a through hole, a back-face instance, ...). All schema-valid
  by construction; `../tools/validate_schema.py` accepts every one of
  them, same as any other DTML document.
- `fixtures/resolver/invalid/` — Parts that are **schema-valid** but
  **resolver-invalid**: a bad reference, an unsupported `formula`
  Expression, a semantic-validation violation (non-integral count,
  negative pitch, blind depth >= thickness), or a hole landing outside
  the Part's bounds. `validate_schema.py` accepts every one of these too
  — that's the point: the resolver is the only layer that catches them.

Both subdirectories reuse `examples/shelf_pin_array.feature.yaml` and
`examples/vertical_drill.operation.yaml` by reference (found via the
resolver's default search roots) rather than duplicating them — one
exception is `fixtures/resolver/valid/through_dowel_array.feature.yaml`,
a small colocated Feature fixture needed because none of the canonical
`examples/` documents is a through-hole array.

### `pytest` suite

`test_expression_resolution.py`, `test_parameter_merge.py`, and
`test_hole_array_resolution.py` cover the resolver's individual modules
and its full ten-stage pipeline respectively. Run with:

```bash
python -m pytest tests/ -v
```
