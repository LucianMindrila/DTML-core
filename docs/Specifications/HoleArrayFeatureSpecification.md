# hole_array Feature Specification (Draft v0.1)

`hole_array` is DTML's first typed Feature contract — a repeating line of
identical holes, sharing one hole geometry, evenly pitched along one
axis. The worked example throughout this document is `shelf_pin_array`
(`../../examples/shelf_pin_array.feature.yaml`), placed on a Part in
`../../examples/panel_with_shelf_pin_array.part.yaml`.

The schemas are the source of truth — `../../schemas/features/
hole_geometry.schema.yaml` (the shared fragment) and `../../schemas/
features/hole_array.schema.yaml` (the `hole_array`-specific composition).
This document explains why they're shaped that way. See
`FeatureSpecification.md` for the generic typed-schema pattern this
follows, and `OperationSpecification.md` for why `diameter`/`depth`/
`hole_form` live here rather than on the `vertical_drill` Operation.

## Parameter shape

```yaml
feature_type: hole_array
parameters:
  diameter: {literal: {value: 5, unit: mm}}
  hole_form: blind
  depth: {literal: {value: 13, unit: mm}}
  pitch: {literal: {value: 32, unit: mm}}
  count: {literal: {value: 5, unit: count}}
  start_offset: {literal: {value: 100, unit: mm}}
  direction: {axis: y, sense: positive}
```

`diameter`, `hole_form`, `depth` come from the shared `hole_geometry`
fragment (reusable by a future plain `hole`, hinge drilling, dowel
patterns, etc. — see `FeatureSpecification.md`, "Shared geometry
fragments"). `pitch`, `count`, `start_offset`, `direction` are
`hole_array`-specific.

The Feature definition's `parameters` requires the complete set above —
it supplies reusable *typical* values. A Part's `instance_parameters` may
override any subset for a specific placement:

```yaml
instance_parameters:
  count: {literal: {value: 5, unit: count}}
  start_offset: {literal: {value: 100, unit: mm}}
```

Both `count` and `direction` have Feature-level defaults *and* are
realistic instance-level overrides (a taller cabinet side overrides only
`count`; a mirrored placement overrides only `direction`) — there is no
fixed rule classifying a key as definition-owned or instance-owned. The
resolver rule is: **instance parameters replace matching Feature
parameters by key; unspecified parameters retain the Feature's default.**
Actually computing that merge is Resolution Engine work, not encoded in
either schema.

## Termination model: `pitch` × `count`, not an end offset

v0.1 array length is `pitch × (count - 1)` — deterministic, no
conflicting-input case to resolve. A `fill available space` or
`end_offset` termination mode is deferred until the resolver exists:
`count: 20` alongside `end_offset: 37` has no defined precedence, and
inventing one now would be guessing ahead of a real example that needs
it.

## Direction: axis + sense, not a compound enum

```yaml
direction: {axis: y, sense: positive}
```

relative to the Part's own origin/axes (`SchemaConventions.md`, "Part
geometry conventions"), not the machine. This avoids a combinatorial enum
(`positive_x`, `negative_x`, `positive_y`, `negative_y`, ...) that would
need new members for every future axis or reversed convention.

`direction` only ever names the in-plane (X/Y) axis an array runs
along — it says nothing about `depth`, which has its own, independent
convention: always positive, always measured inward from whichever face
the `feature_instance` references (`SchemaConventions.md`, "Face-local
coordinates and depth"). A `hole_array` on the back face uses the same
`depth` sign and the same `direction` enum as one on the front face; the
two faces' coordinate frames are mirrored (front/back X don't align
physically), but nothing about that mirroring is visible in a Feature's
own `parameters` — it only matters once a resolver correlates features
across faces.

## `start_offset`: an offset from the anchor, not an absolute coordinate

`direction` says which in-plane axis and sense an array runs along, but
not *where* it starts. That's split across two fields at two different
levels:

- `feature_instance.position` (`part.schema.yaml`) — the 2D face-local
  anchor point, e.g. `{x: 20, y: 20}`. Placed by the Part, since it's
  about where *this Part* puts the Feature, not a property of the
  Feature itself.
- `hole_array.parameters.start_offset` — an optional non-negative scalar
  distance, along `direction`'s axis and in `direction`'s sense, from
  that anchor to the array's first hole. Defaults to `0` (first hole
  exactly at the anchor) when absent.

The first hole's centre is therefore:

```
distance = start_offset + (index × pitch)
if direction.axis == x:
    centre = (position.x + direction.sense × distance, position.y)
else:
    centre = (position.x, position.y + direction.sense × distance)
```

where `direction.sense` is `+1` for `positive`, `-1` for `negative`, and
`index` runs `0` to `count - 1`. `depth`/`z` is unaffected — see the
`hole_form` section above.

Splitting the anchor (Part-level, 2D, "where") from the offset
(Feature-level, 1D, "how far along the run before the first hole") means
neither field is redundant: `position` alone would force every array to
start exactly at its anchor with no clearance from whatever edge or
datum the anchor represents; folding the offset into a second, absolute
`position`-like coordinate would make one of `position`'s two components
meaningless depending on `direction.axis`. Concretely, `position` doubles
as a directional datum: a positive-sense array's anchor is naturally the
edge it counts up from (e.g. the bottom), a negative-sense array's anchor
is the opposite edge (e.g. the top) — `start_offset` is clearance from
whichever edge that is, not a second position.

This was originally named `start_position`, which implied an absolute
coordinate it never was — renamed before the resolver made that
confusion permanent. See `../../schemas/features/hole_array.schema.yaml`
and `ResolverSpecification.md` for the implementation.

## `hole_form`: `blind` and `through` only, for now

`countersunk` and `counterbored` are deferred until the multi-operation
Feature model is resolved (`SchemaConventions.md`, "Feature / Operation
scope"; `OperationSpecification.md`, "Why countersink isn't its own
`operation_type`") — a countersunk hole is a compound geometry, and
`shelf_pin_array` (this milestone's driving example) is a plain blind
hole, so compound hole geometry isn't needed to type `hole_array` itself.

`hole_geometry.schema.yaml` enforces the coherence rule structurally:
`blind` requires `depth`; `through` forbids it (via `if`/`then`, not
`if`/`then`/`else`, so a hole_form outside the enum — impossible, since
it's already a closed `enum` — can't silently skip both branches).

## What's structurally enforced vs. semantic

JSON Schema (`tools/validate_schema.py`) enforces:

- `diameter`, `hole_form`, `pitch`, `count`, `direction` are present
  (required); `depth`, `start_offset` are optional
- `hole_form` is one of `blind | through`
- `blind` requires `depth` present; `through` forbids it
- `direction.axis` is one of `x | y`; `direction.sense` is one of
  `positive | negative`
- no unrecognised parameter key is accepted (`unevaluatedProperties:
  false` on the composed shape)
- each of `diameter`/`depth`/`pitch`/`count` is a well-formed Expression
  (exactly one of `literal`/`formula`/`rule_reference`)

It deliberately does **not** enforce:

- **Positivity** (`diameter > 0`, `pitch > 0`, `depth > 0`,
  `count > 0`, `start_offset >= 0`). An Expression can be a `formula` or `rule_reference`
  whose resolved value isn't known until evaluation — a literal-only
  conditional constraint would check some instances and silently wave
  through others, misleadingly implying a guarantee the schema doesn't
  actually give. Skipped entirely for v0.1 rather than half-enforced.
- **`count`'s integer-ness.** Same reasoning — `count`'s unit is `count`
  (`expression.schema.yaml`'s unit enum), but whether its *resolved*
  value is a whole number is a property of the expression, checked after
  resolution, likely by whatever gains authority over unit semantics
  (a future expression/unit validator) rather than duplicated here.
- **`depth < Part thickness`.** In the face-local frame
  (`SchemaConventions.md`, "Face-local coordinates and depth"), a blind
  hole's endpoint is at `z = depth` and the opposing face is at
  `z = thickness`; the rule is `depth < thickness` for a `blind` hole.
  Checking it requires the instantiated Part's own resolved `thickness`,
  which this Feature-level schema has no access to.

All of the above are recorded here as the intended semantic-validation
rule set for whenever that layer exists — not a `TBD` inside the schema,
per the same principle `SchemaConventions.md` already applies to
`confidence: unconfirmed` and the edge-banding convention: *effective
diameter, depth, pitch and count values must be positive after expression
resolution; effective start_offset must be non-negative; effective count
must be an integer; effective depth must be less than the instantiated
Part's thickness for a `blind` hole.*

This is no longer purely aspirational — `ResolverSpecification.md` and
`dtml/semantic_validation.py` implement exactly this rule set as
resolver v0.1's stage 6 ("Validate effective parameters"). The schemas
above remain deliberately unchanged (still open on positivity/integer
constraints, for the reasons given above); the resolver is the layer
that now actually enforces them, on resolved literal values only.

## Acceptance criteria

Structurally enforced (checked directly by `tools/validate_schema.py`):

1. The `shelf_pin_array` Feature definition validates against
   `hole_array.schema.yaml`.
2. `panel_with_shelf_pin_array.part.yaml`, instantiating it with a
   partial `instance_parameters` override, validates against
   `part.schema.yaml`.
3. Missing `diameter` fails (required, `hole_geometry` fragment).
4. Missing `hole_form` fails (required, `hole_geometry` fragment).
5. `hole_form: blind` without `depth` fails (conditional requirement).
6. `hole_form: through` with `depth` present fails (conditional
   prohibition).
7. Missing `count` or `direction` fails (required, array-specific).
8. An invalid `direction.axis`/`direction.sense` value fails (enum).
9. An unrecognised parameter key fails (`unevaluatedProperties: false`).
10. CI (`schema-validation.yml`) runs every new valid/invalid fixture
    alongside the existing set.

Explicitly **not** structural (see above — semantic validation, future):
positivity of `diameter`/`depth`/`pitch`/`count`; `count` integer-ness;
`depth` vs. Part `thickness`.

## Open questions

- **Reuse of `hole_geometry` by future Feature types** — a plain `hole`,
  hinge drilling, dowel patterns, connector drilling — is expected but
  not yet built; each would compose the same fragment the way
  `hole_array` does, adding its own non-array-specific properties.
- **Whether `feature_instance` ever needs its own stable id.** The
  resolver (`ResolverSpecification.md`) currently identifies a resolved
  Feature instance by its index within `feature_instances`, since no
  `id`/`name` field exists on `feature_instance` today. Fine for a single
  Part with few instances; may need revisiting if that turns out to be
  too fragile (e.g. instances reordered between Part revisions) once
  more real Parts exist.

See `../../schemas/features/hole_geometry.schema.yaml` and
`../../schemas/features/hole_array.schema.yaml` for the machine-readable
schemas.
