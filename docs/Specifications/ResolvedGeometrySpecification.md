# Resolved Geometry Specification (Draft v0.1)

`resolved_part.schema.yaml`'s `resolved_feature` is polymorphic: its exact
shape depends on `feature_type`. This document is the contract both
`dtml.resolver` (which produces a `resolved_feature`) and any renderer
(which consumes one — currently `dxf.render`) must follow, so that adding
a second Feature type is a matter of adding a branch, not renegotiating
the envelope every time.

It stands alongside `ResolverSpecification.md` and
`DXFRendererSpecification.md` rather than folding into either, because
both of those consume this contract — it isn't owned by one side of the
resolver/renderer boundary.

## Why polymorphic, not one generic geometry shape

The alternative — a single, universal `geometry` shape every Feature type
reuses, e.g. `geometry: {entities: [{type: circle, ...}, {type: line,
...}]}` — was considered and rejected. It would drift toward a generic
CAD-interchange format and discard manufacturing meaning too early: a
groove's width, depth, and direction are meaningful parameters a
downstream consumer needs to reason about, not incidental properties of
a generic "line" primitive. Keeping each Feature type's resolved geometry
closed and named preserves that meaning all the way to the renderer.

## Common resolved-feature envelope

Every `resolved_feature`, regardless of `feature_type`, carries:

- `instance_index` — position of this Feature instance within the source
  Part's `feature_instances` array. Deliberately not called
  `instance_id`: `feature_instance` has no stable id/name field of its
  own yet (open question, `HoleArrayFeatureSpecification.md`), and
  calling this an "id" would imply a stable identity that doesn't exist.
  See `ResolverSpecification.md` for the same rationale, established when
  this field was first introduced.
- `feature_type` — the discriminator. Common at the envelope level as a
  general string; each branch narrows it to a single `const` value (see
  below).
- `feature` — reference to the source Feature definition.
- `operation` — reference to the source Operation.
- `reference_face` — `front` or `back`. Common because every Feature type
  DTML has considered so far, point-anchored or not, is placed on one
  face of the Part; nothing about edge-banding or a face-independent
  Feature type has yet forced this to move.

`anchor_mm` is **not** common. `hole_array` needs a single point anchor,
but a future edge-banding Feature (a Feature applied to a Part *edge*,
not a face-local point) has no natural single-point anchor to share that
field's meaning with. Point-anchored Feature types (like `hole_array`)
carry their own `anchor_mm` inside their branch instead.

## Polymorphic branches

`resolved_feature` is a `oneOf`, with each branch fixing `feature_type`
via `const`:

```yaml
resolved_feature:
  oneOf:
    - $ref: "#/$defs/resolved_feature_hole_array"
    # future branches (groove, edge_band, ...) added here deliberately,
    # one at a time, each forcing exactly one existing worked example.
```

Each branch combines the common envelope with its own type-specific
`effective_parameters` and `geometry`, closed with `unevaluatedProperties:
false` — the same `allOf` + `const` + closed-schema technique already
used on the *source* side to compose `hole_array.schema.yaml` from
`feature.schema.yaml`. This isn't a new pattern; it's the existing one
applied one layer further downstream.

### `hole_array` (implemented)

```yaml
feature_type: hole_array
anchor_mm: {x, y}
effective_parameters: {diameter_mm, hole_form, depth_mm, pitch_mm, count, start_offset_mm, direction}
geometry:
  holes:
    - index: 0
      centre_mm: {x, y, z}
      diameter_mm: ...
      depth_mm: ...
      hole_form: ...
```

### `groove` (worked example only — not implemented)

Illustrates why the polymorphic model is needed, not a committed schema.
No `schemas/features/groove.schema.yaml`, resolver support, or renderer
support exists yet — this shape is a placeholder for the extension
procedure below to produce for real:

```yaml
feature_type: groove
effective_parameters: {width_mm, depth_mm, ...}
geometry:
  start: {x_mm, y_mm}
  end: {x_mm, y_mm}
  width_mm: ...
  depth_mm: ...
```

A groove has no single point anchor — its geometry is a start/end pair —
which is exactly the case `anchor_mm` being branch-specific rather than
common is designed for.

## Three-way `feature_type` support rule

Normative for every consumer of a `resolved_part` — the resolver
producing one, and any renderer consuming one:

1. **Unknown `feature_type`** (not in `feature.schema.yaml`'s
   `feature_type` enum) — schema-invalid. Caught by JSON Schema
   validation itself; no dedicated code path needed.
2. **Known to the DTML specification, unsupported by this
   implementation's version** (e.g. `feature_type: groove` today) — an
   explicit, dedicated "unsupported feature type" error. Not a schema
   error, not a generic/vague error, and never silent.
3. **Known and supported** — processed/rendered deterministically.

**Silent omission is prohibited.** A resolver or renderer encountering
case 2 must fail the *entire* resolution or render, not produce a
partial, technically-valid-looking artifact missing some of the
Feature's geometry. This is the most dangerous failure mode this rule
exists to prevent: a DXF file that looks complete but is silently
missing a groove because the renderer didn't recognise it.

`dtml.errors.UnsupportedFeatureType` and `dxf.errors.UnsupportedFeatureType`
implement case 2 for the resolver and the DXF renderer respectively — two
separate classes, not one shared type, because `dxf/` must not import
from `dtml/` (`DXFRendererSpecification.md`, "Module layout": the
renderer's only contract is the resolved dict shape, not the resolver's
internals).

## Renderer conformance

Any renderer consuming `resolved_part` must reject a `resolved_feature`
whose `feature_type` it doesn't implement, per the three-way rule above,
rather than skipping it and rendering everything else. `dxf.render`
implements this today for every `feature_type` other than `hole_array`.

## Extension procedure — adding a new Feature type

Adding a new Feature type (e.g. `groove`) requires, in order:

1. A typed source Feature schema (`schemas/features/groove.schema.yaml`),
   following the existing `allOf` + `const` + `unevaluatedProperties:
   false` pattern `hole_array.schema.yaml` already established.
2. A resolved schema branch — a new `oneOf` entry in
   `resolved_part.schema.yaml`, combining the common envelope with the
   new branch's own `effective_parameters` and `geometry`.
3. Resolver support — `dtml/resolver.py` logic computing that branch's
   geometry, replacing the current unconditional "only hole_array"
   rejection with a positive case for the new type, keeping the
   `UnsupportedFeatureType` rejection for every type still not
   implemented.
4. Semantic tests exercising the new branch end to end, mirroring
   `test_hole_array_resolution.py`'s structure.
5. Renderer support for the new branch, or — until that's built — an
   explicit `UnsupportedFeatureType` from the renderer rather than a
   silent skip.
6. Documentation: the new branch's worked example replaces its "not
   implemented" placeholder in this document.

## Migration note

`hole_array`'s resolved output was migrated to this shape (flat `holes:
[...]` wrapped under `geometry: {holes: [...]}`, plus an explicit
`feature_type: hole_array` field) at the same time this document was
written, rather than later — so that when `groove` becomes the second
branch, both branches already share the same structural convention
instead of `hole_array` needing a follow-up migration under time
pressure.

## Status

Implemented: the common envelope and the `hole_array` branch, in
`schemas/resolved/resolved_part.schema.yaml`, `dtml/resolver.py`, and
`dxf/render.py`. Not implemented: `groove` or any other branch — shown
above purely as a worked example this document's extension procedure
will produce for real.
