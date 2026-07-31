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
  negative pitch, blind depth >= thickness, zero-or-negative groove
  width, groove depth >= thickness), a hole or groove landing outside
  the Part's bounds (including the groove-specific inset-rectangle
  radius check), or a `feature_type` valid DTML but not implemented
  by resolver v0.1 (`pocket_feature.feature.yaml` +
  `part_unsupported_feature_type.part.yaml` — see
  `../docs/Specifications/ResolvedGeometrySpecification.md`'s three-way
  `feature_type` support rule). `validate_schema.py` accepts every one
  of these too — that's the point: the resolver is the only layer that
  catches them.

Both subdirectories reuse `examples/shelf_pin_array.feature.yaml`,
`examples/vertical_drill.operation.yaml`, `examples/straight_groove.feature.yaml`,
and `examples/router_groove.operation.yaml` by reference (found via the
resolver's default search roots) rather than duplicating them — one
exception is `fixtures/resolver/valid/through_dowel_array.feature.yaml`,
a small colocated Feature fixture needed because none of the canonical
`examples/` documents is a through-hole array.

### `pytest` suite

`test_expression_resolution.py`, `test_parameter_merge.py`,
`test_hole_array_resolution.py`, and `test_groove_resolution.py` cover
the resolver's individual modules and its full pipeline for each
`feature_type` respectively. Run with:

```bash
python -m pytest tests/ -v
```

## `test_dxf_render.py`

Covers `dxf.render.render_resolved_part()` (see
`../docs/Specifications/DXFRendererSpecification.md`) — the thin DXF
renderer one layer downstream of the resolver. Resolves the committed
`examples/panel_with_shelf_pin_array.part.yaml` once via
`dtml.resolver.resolve_part()`, then only ever inspects the rendered
result through `ezdxf`'s modelspace query API: outline coordinates,
per-layer hole count/diameter/centre, unit header variables, and the
`DTML` XDATA metadata round-tripping through a save/reload cycle. One
test asserts the acceptance criterion directly — that the renderer never
touches the filesystem, i.e. never re-opens or re-parses a DTML source
document from within the render path itself.

Groove rendering is asserted against `RESOLVED_GROOVE_PANEL` (defined in
`test_resolved_geometry_schema.py`, reused here): the true-size capsule
outline lands on `GROOVES_FRONT` as a single closed `LWPOLYLINE` with the
exact vertex/bulge values `dxf.render._capsule_points()` computes,
independently cross-checked via `LWPolyline.virtual_entities()`
decomposing it into two `LINE`s and two 180-degree `ARC`s of the correct
radius, centred on each resolved endpoint. A separate test proves the
renderer's `feature_type` conformance rule (see
`../docs/Specifications/ResolvedGeometrySpecification.md`): since both
implemented feature_types now render successfully, this uses a synthetic
`RESOLVED_UNSUPPORTED_FEATURE_PANEL` dict (a `feature_type` no
`resolved_part.schema.yaml` branch currently permits) rather than a
schema-valid fixture — the renderer never re-validates its input, so this
is enough to exercise the dispatch's own defensive fallback and confirm
`dxf.errors.UnsupportedFeatureType` aborts the whole render rather than
silently skipping the feature.

## `test_resolved_geometry_schema.py`

Validates `schemas/resolved/resolved_part.schema.yaml`'s polymorphic
`resolved_feature` directly against hand-constructed dicts, independent
of whether `dtml.resolver.resolve_part()` can actually produce that
shape yet. `RESOLVED_GROOVE_PANEL` is a schema-valid
`resolved_feature_groove` example — proves the branch added for groove
validates, and is reused by `test_dxf_render.py` as the renderer's
"known and schema-valid, but unsupported" conformance case.
