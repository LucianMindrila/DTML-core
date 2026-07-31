# groove Feature Specification (Draft v0.1)

`groove` is DTML's second typed Feature contract, and the first that
isn't a point-pattern of holes: a single straight, axis-aligned channel
of constant width and depth, cut by a round tool travelling along a
centreline and stopping short of both ends. The worked example
throughout this document is `straight_groove`
(`../../examples/straight_groove.feature.yaml`), placed on a Part in
`../../examples/panel_with_groove.part.yaml`.

The schema is the source of truth —
`../../schemas/features/groove.schema.yaml`. This document explains why
it's shaped that way. See `FeatureSpecification.md` for the generic
typed-schema pattern this follows, and `ResolvedGeometrySpecification.md`
for how a resolved groove fits the polymorphic `resolved_feature`
contract once resolver/renderer support exists.

## Parameter shape

```yaml
feature_type: groove
parameters:
  width: {literal: {value: 8, unit: mm}}
  depth: {literal: {value: 6, unit: mm}}
  length: {literal: {value: 400, unit: mm}}
  direction: {axis: x, sense: positive}
  groove_form: stopped
```

Unlike `hole_geometry`, none of these properties are shared with another
`feature_type` yet, so `groove.schema.yaml` does not introduce a shared
fragment (`FeatureSpecification.md`, "Shared geometry fragments" — a
fragment is only extracted once a second Feature type genuinely needs the
same shape). `direction` reuses the same `axis`/`sense` shape
`hole_array.schema.yaml` already defines, duplicated locally rather than
cross-referenced — the two typed schemas are independent documents, and
this repo's existing precedent (`resolved_part.schema.yaml`'s own
`direction` fragment for the resolved layer) already accepts this
duplication rather than inventing a shared cross-file fragment for a
four-field object.

`feature_instance.position` (`part.schema.yaml`) is the groove's
centreline **start** point — the tool's plunge point, in the same
face-local 2D anchor role `position` plays for `hole_array`. The
resolver computes the centreline **end** point from `position`, `length`,
and `direction`, the same way it already computes each hole's centre
from `position`, `start_offset`, `pitch`, and `direction`
(`HoleArrayFeatureSpecification.md`, "`start_offset`").

## Why `groove_form` is an explicit field, not an unstated assumption

A groove's two centreline endpoints could, in principle, land either
inside the Part face (a **stopped** groove, machined entirely by the
round tool with no exit) or exactly on a Part edge (an **edge-exit**
groove, open at that end). These are geometrically and structurally
different: a stopped end has a semicircular cap; an edge-exit end has
none, and the swept shape simply continues past the panel boundary. v0.1
supports **stopped grooves only** — both endpoints strictly inside the
Part face, both ends round-capped by the cutter.

Rather than leaving that restriction as prose convention, `groove_form`
records it directly in the data, with `stopped` as the only value
`groove.schema.yaml`'s enum permits in v0.1:

```yaml
groove_form: stopped
```

This deliberately does **not** anticipate the future edge-exit value by
naming it `through` — that name risks confusion with a groove cut through
the full panel **thickness**, which is a separate, also-deferred concept
(edge termination and depth condition are independent axes). A future
open-ended form gets its own, differently-named enum member and its own
geometric/bounds rules, added the same way any closed-enum vocabulary
extension is added — without reinterpreting existing `groove_form:
stopped` documents.

## Direction: axis + sense, reused from `hole_array`

```yaml
direction: {axis: x, sense: positive}
```

Same rationale as `HoleArrayFeatureSpecification.md`, "Direction: axis +
sense, not a compound enum" — relative to the Part's own local coordinate
system, not the machine, and an open axis/sense pair rather than a
combinatorial enum. For `groove`, `direction` fixes both the centreline's
orientation (the groove is axis-aligned in v0.1 — no arbitrary angle) and
the sense the resolver walks from `position` to compute the end point.

## Geometry model: a capsule, not a rectangle

The tool that cuts a groove is round. The resulting cavity is the swept
region of a circle of radius `r = width / 2` travelling along the
centreline segment from `start` to `end` — a **stadium** (capsule)
shape, not a rectangle: each end is a semicircular cap centred on that
endpoint, not a square corner.

The critical, easy-to-miss consequence: the cap at each end bulges
**past** the centreline endpoint by `r`, along the direction of travel —
not merely to the sides. A groove whose centreline runs from `x=100` to
`x=500` at `width=8` (`r=4`) occupies `x=96` to `x=504`, not `x=100` to
`x=500`. Treating the centreline endpoints as the physical extremes of
the cut would under-count the groove's true footprint by `r` at each end
and risk validating a groove that actually overruns the panel edge.

## Bounds rule: inset rectangle, not raw endpoint containment

Because both ends are stopped (capped, not edge-exit), the entire capsule
— not just the centreline — must lie within the Part face. For a
rectangular panel of width `W` and height `H`, and a groove of radius
`r = width / 2`, the rule is: **both centreline endpoints must lie within
the panel inset by `r` from every boundary.**

```
r ≤ start.x ≤ W - r        r ≤ end.x ≤ W - r
r ≤ start.y ≤ H - r        r ≤ end.y ≤ H - r
```

Because v0.1 grooves are straight and axis-aligned, checking both
endpoints against this single inset rectangle is sufficient — it needs no
direction-specific logic. For a positive-X groove the occupied X range is
`start.x - r` to `end.x + r`; for a negative-X groove the geometric
minimum and maximum reverse; either way, requiring both endpoints inside
`[r, W-r] × [r, H-r]` guarantees the fully swept capsule stays inside the
panel, regardless of `direction.sense`.

This is a semantic-validation rule (it needs the instantiated Part's
resolved `dimensions`, not just the Feature's own parameters) — see "What's
structurally enforced vs. semantic" below, and the same category
`HoleArrayFeatureSpecification.md` places its own hole-bounds check in.

## Agreed v0.1 contract

- straight, axis-aligned centreline (`direction.axis`/`direction.sense`,
  no arbitrary angle);
- constant `width` and `depth` along the entire length;
- `groove_form: stopped` only — both ends interior to the Part face,
  round-capped, no edge-exit;
- capsule (stadium) footprint, per "Geometry model" above;
- literal Expressions only, for resolver v0.1 (`formula`/`rule_reference`
  remain out of scope, same restriction `hole_array` resolution has
  today);
- rectangular Parts only;
- a single referenced face (`feature_instance.reference_face`) — no
  through-thickness or multi-face groove.

Explicitly **deferred**, not modelled at all in v0.1:

- edge-exit / open-ended grooves (a `groove_form` value other than
  `stopped`);
- square-ended (non-capsule) grooves;
- through-depth grooves (`depth` reaching the Part's full `thickness` —
  a different concept from edge-exit, see "Why `groove_form`..." above);
- curved centrelines;
- angled (non-axis-aligned) centrelines;
- variable width or depth along the length;
- multiple connected segments (a single groove is always one straight
  run).

## What's structurally enforced vs. semantic

JSON Schema (`tools/validate_schema.py`) enforces:

- `width`, `depth`, `length`, `direction`, `groove_form` are all present
  (required — unlike `hole_array`, nothing here is optional, since a
  groove has no analogue to `start_offset`'s "defaults to 0");
- `groove_form` is exactly `stopped` (single-member enum — any other
  value is schema-invalid, not silently accepted);
- `direction.axis` is one of `x | y`; `direction.sense` is one of
  `positive | negative`;
- no unrecognised parameter key is accepted
  (`unevaluatedProperties: false` on the composed shape);
- each of `width`/`depth`/`length` is a well-formed Expression (exactly
  one of `literal`/`formula`/`rule_reference`).

It deliberately does **not** enforce:

- **Positivity** (`width > 0`, `depth > 0`, `length > 0`) — same
  reasoning as `HoleArrayFeatureSpecification.md`: an Expression's
  resolved value isn't known until evaluation, so a literal-only
  conditional check would silently wave through `formula`/
  `rule_reference` instances.
- **The inset-rectangle bounds rule** (see above) — requires the
  instantiated Part's resolved `dimensions`, which this Feature-level
  schema has no access to.
- **`depth < Part thickness`.** Same rule and same reasoning
  `HoleArrayFeatureSpecification.md` already applies to a blind hole's
  depth: this Feature-level schema cannot see the instantiated Part's
  resolved `thickness`.

All of the above are recorded here as the intended semantic-validation
rule set for resolver v0.1, mirroring exactly how
`HoleArrayFeatureSpecification.md` records its own deferred rules:
*effective width, depth and length values must be positive after
expression resolution; effective depth must be less than the
instantiated Part's thickness; both resolved centreline endpoints must
satisfy the inset-rectangle bounds rule above.*

## Acceptance criteria

Structurally enforced (checked directly by `tools/validate_schema.py`):

1. The `straight_groove` Feature definition validates against
   `groove.schema.yaml`.
2. `panel_with_groove.part.yaml`, instantiating it, validates against
   `part.schema.yaml`.
3. Missing any of `width`/`depth`/`length`/`direction`/`groove_form`
   fails (all required).
4. `groove_form` set to anything other than `stopped` fails (enum).
5. An invalid `direction.axis`/`direction.sense` value fails (enum).
6. An unrecognised parameter key fails (`unevaluatedProperties: false`).
7. CI (`schema-validation.yml`) runs every new valid/invalid fixture
   alongside the existing set.

Explicitly **not** structural (see above — semantic validation, at the
resolver layer): positivity of `width`/`depth`/`length`; the
inset-rectangle bounds rule; `depth` vs. Part `thickness`.

## Open questions

- **Whether a future `hole_geometry`-style shared fragment ever covers
  `groove`.** Not today — nothing else needs `width`/`depth`/`length`/
  `direction`/`groove_form` together. Revisit if a second
  centreline-based Feature type (e.g. a routed slot) turns out to need
  the same shape.
- **Naming the eventual edge-exit `groove_form` value.** Deliberately not
  decided now (see "Why `groove_form` is an explicit field" above) —
  needs a name that doesn't collide with through-depth terminology.
- **Whether `direction` should become a shared cross-file fragment**
  once a third Feature type (beyond `hole_array` and `groove`) needs the
  same axis/sense shape, rather than continuing to duplicate it per typed
  schema.

See `../../schemas/features/groove.schema.yaml` for the machine-readable
schema.
