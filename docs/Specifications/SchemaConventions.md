# Schema Conventions (Draft v0.1)

This document fixes the conventions every DTML schema follows, so they
don't get reinvented per-file. It exists specifically to avoid re-deciding
naming, IDs, versions, units, and reference syntax inside each of the nine
schemas in `../../schemas/`.

## Schema language: Draft 2020-12 JSON Schema, written as YAML

Schemas are standard [JSON Schema Draft
2020-12](https://json-schema.org/draft/2020-12), stored as YAML for
readability. This was chosen over a custom DTML schema language because it
gives us recognised validators, editor tooling, and a path to Pydantic
model generation in the reference implementation — without losing DTML-
specific meaning, which is carried in `x-dtml-*` extension keywords (e.g.
`x-dtml-unit`) rather than undeclared custom keys.

Every schema file:

- declares `$schema: https://json-schema.org/draft/2020-12/schema`
- declares `$id: <filename>` (e.g. `$id: common.schema.yaml`) — this is
  the identifier other schemas use to `$ref` into it
- defines its real content under `$defs`, with the document root set to
  `$ref: "#/$defs/<name>"` — this lets other files reference just the
  object shape (`common.schema.yaml#/$defs/knowledge_object`) while the
  same file also validates standalone as a full document

Cross-file references use the bare filename as the base, e.g.:

```yaml
material:
  $ref: "reference.schema.yaml#/$defs/reference"
```

## Common object fields

Every DTML knowledge object (a Part, Feature, Operation, Material,
Hardware, Module, etc. — anything stored as a `library/` entry) shares the
fields defined in `common.schema.yaml#/$defs/knowledge_object`:

| Field | Purpose |
|---|---|
| `namespace` | The owning domain and object category, dot-separated lowercase segments, e.g. `cuttingedgebespoke.feature`. |
| `id` | The object's local identifier within that namespace, e.g. `shelf_pin_array`. |
| `name` | Human-readable name. |
| `description` | Optional prose description. |
| `schema_version` | Which version of the *schema structure* this object conforms to. |
| `object_version` | Which revision of *this specific knowledge object* is being described — semver string. |
| `status` | `draft \| active \| deprecated \| superseded`. |
| `provenance` | A `provenance.schema.yaml#/$defs/provenance` block — see below. |
| `tags` | Optional free-text labels. |

### `namespace` + `id`, not a stored `canonical_id`

The canonical identifier used in references is derived, never stored
independently:

```
canonical_id = namespace + "." + id
```

e.g. `namespace: cuttingedgebespoke.feature` + `id: shelf_pin_array` →
`cuttingedgebespoke.feature.shelf_pin_array`. Storing `canonical_id` as its
own field would let it drift out of sync with `namespace`/`id`; deriving it
means there's exactly one place the identity is defined.

`namespace` matches `^[a-z0-9_]+(\.[a-z0-9_]+)+$` — **at least two
segments** (owner.category, e.g. `cuttingedgebespoke.feature`). A single
token such as `namespace: feature` is rejected: it carries no owning
domain, which defeats the point of namespacing before libraries even
start proliferating. `id` matches `^[a-z0-9_]+$` (no dots — the namespace
carries the hierarchy), and a full canonical `ref`
(`reference.schema.yaml#/$defs/reference`) is therefore at least three
segments — namespace (2+) + `.` + `id` (1) — enforced by the same
tightened pattern in `reference.schema.yaml` so the two can't drift apart.
See `tests/fixtures/valid/namespace-*.yaml` and
`tests/fixtures/invalid/namespace-*.yaml` / `ref-missing-id-segment.yaml`.

### `schema_version` vs. `object_version`

These are separate version axes and must not be conflated:

- **`schema_version`** answers *"which schema structure does this object
  conform to?"* — it changes when the shape of the schema changes.
- **`object_version`** answers *"which revision of this knowledge object is
  being referenced?"* — it changes when the Part/Feature/Material/etc.
  itself is revised.

A `reference.schema.yaml#/$defs/reference` therefore pins `object_version`
explicitly, never a bare `version`, so it's unambiguous which axis is being
pinned:

```yaml
ref: cuttingedgebespoke.material.egger_w1000_18mm
object_version: "1.2.0"
```

`object_version` is validated as a semver.org string
(`common.schema.yaml#/$defs/semantic_version`), both on the object itself
and everywhere a `reference` pins one — `object_version: banana` or
`object_version: latest` are schema errors. `schema_version` is
deliberately **not** constrained to semver: it's a free-form structure
identifier (this document's own schemas currently use `"0.1"`, which
isn't valid semver), tracking the shape of the schema rather than a
released revision of a specific object. Revisit this if schema versioning
ever needs the same ordering/comparison guarantees object versioning
does.

## Provenance owns confidence

There is exactly one place confidence lives: the `provenance` block
(`provenance.schema.yaml#/$defs/provenance`), not a separate
`source_confidence` field on the object itself. Two competing confidence
values on the same object was the failure mode being avoided here.

`provenance` fields:

| Field | Purpose |
|---|---|
| `source_type` | `narrated \| extracted \| pattern_matched \| derived` — how the data was captured, per `../KnowledgeCapture.md`. |
| `source_reference` | e.g. a DXF filename, drawing number, or narration session reference. |
| `captured_by` | Who captured it. |
| `captured_at` | Timestamp. |
| `confidence` | `confirmed \| unconfirmed` — the controlled vocabulary. `source_type` explains *why* something is unconfirmed (extracted vs. pattern-matched vs. not-yet-reviewed narration); `confidence` is the single binary gate. |
| `review_status` | `pending \| approved \| rejected`. |
| `reviewed_by` | Who reviewed it. |
| `evidence` | References to supporting evidence (extractor output paths, drawing numbers, photos). |

Nothing with `confidence: unconfirmed` may be referenced by a production
object — this is a business rule enforced by the future Validation Engine
(see `../Architecture.md`), not something JSON Schema itself can check, so
it isn't expressed as a schema constraint here.

This is object-level provenance — uncertainty about *the object itself*.
Confidence in a specific interpretation or design decision (e.g. an AI
vision classification's confidence) is a different thing and belongs on
the interpretation/decision record, not duplicated onto object provenance.

## Expressions and units

A dimension or parameter value is exactly one of three shapes
(`expression.schema.yaml#/$defs/expression`), distinguished by which single
key is present:

```yaml
# a fixed value
thickness:
  literal:
    value: 18
    unit: mm

# a parametric formula (grammar not yet fixed — see RuleSpecification.md
# open questions; this schema only defines the container shape)
width:
  formula:
    formula: "module.width - (2 * material.thickness)"
    unit: mm

# a reference to a named Rule
internal_width:
  rule_reference:
    ref: cuttingedgebespoke.rule.internal_width
    object_version: "1.0.0"
```

Exactly one of `literal` / `formula` / `rule_reference` must be present.
(Note: the formula variant's wrapper key is `formula`, not `expression` —
naming it `expression` would collide with the container type's own name.)

`unit` is a controlled vocabulary: `mm | degrees | count`, extended as new
kinds of quantity are needed.

## Part geometry conventions

- **Origin**: the bottom-left corner of the panel as viewed from the
  `reference_face`. X increases right, Y increases up. This is a fixed
  project-wide convention, not a per-instance field.
- **`reference_face`**: `front | back` — which face is being machined or
  faces the room.
- **Edge naming**: `top | bottom | left | right`, relative to the part as
  oriented at its origin.

## Face-local coordinates and depth (resolver v0.1 scope)

This extends the origin/X/Y convention above with the Z axis and the
front/back relationship, settled now (rather than left implicit) because
the first Feature-coordinate resolver's output — resolved hole
coordinates for a per-panel DXF — would otherwise be ambiguous the
moment a `feature_instance`'s `reference_face` is `back`.

### Face-local frame

Each rectangular Part face defines an independent face-local coordinate
frame. When the referenced face (`feature_instance.reference_face`,
`part.schema.yaml`) is viewed from outside the Part, the origin is at
its bottom-left corner, positive X extends to the right, positive Y
extends upward, and positive Z extends inward into the material. (This
is a face-local convention, not a claim of 3D right-handedness — with X
right and Y up, "Z inward" is left-handed under the conventional
cross-product definition, but handedness isn't a meaningful claim to
make before a shared 3D model exists.)

### Depth

Feature depth is measured positively from the referenced face inward.
The referenced surface is `z = 0`; the opposing surface is `z =` the
Part's resolved `thickness` (`part.schema.yaml`'s `thickness` field). A
blind hole's endpoint is `z = depth`. A through hole has no `depth`
parameter at all (`hole_geometry.schema.yaml` forbids it); its effective
depth is the full resolved `thickness`.

### Opposing faces are mirrored, not shared

Front and back each use the same viewer-relative X/Y convention
independently — the bottom-left/X-right/Y-up rule applies separately to
whichever face is being viewed. Because viewing the back face means
looking at the Part from the opposite side, front and back face-local
frames are mirrored in physical space: **equal X/Y coordinates on
opposing faces are not the same physical through-thickness point.**

For a rectangular Part, the physical relationship between a front-face
point and the back-face point at the same physical through-thickness
location is:

```
x_back = part.dimensions.width - x_front
y_back = y_front
z_back = part.thickness - z_front
```

(equivalent to notionally flipping the Part around its vertical Y axis
to change viewing face.) This is recorded for future semantic rules or
helper functions that need to correlate features across faces — it is
*not* needed to resolve a single `feature_instance`'s own coordinates,
since every `feature_instance` already carries its own `reference_face`
and resolves entirely within that face's frame.

Face-local mirroring is a deliberate choice, not the only possible one —
the alternative (a single shared material-coordinate frame spanning both
faces) was considered and rejected because it doesn't match the
"viewed from reference_face" wording above, and because face-local
frames are what a per-face engineering drawing, DXF export, or machine
operator actually expects. The face-local → machine/post-processor
coordinate transform (which depends on physical setup/loading, not just
geometry) is a capability/manufacturing-resolution concern — see
`OperationSpecification.md` — not something the source Feature model or
this resolver needs to know about.

### v0.1 resolver scope

The first Feature-coordinate resolver supports:

- **flat, rectangular Parts only** — non-rectangular Parts are rejected
  as unsupported. Shaped-panel datums raise questions (bounding-box vs.
  design datum, negative coordinates, concave profiles, orientation
  after nesting) that are deferred until a real shaped-panel example
  forces the decision.
- **Part-local, face-local coordinates only** — one `reference_face` at
  a time, per `feature_instance`.
- **no rotational placement** — `degrees` already exists as an
  Expression `unit`, but no positive-angle (clockwise/counterclockwise)
  convention is defined yet, and won't be until a Feature schema
  actually introduces angular placement.
- **no assembly/world transforms** — Part → Module → Furniture → Room
  composition is out of scope for this resolver.

Resolved output is therefore always:

```
Part-local → face-local → Feature coordinates
```

nothing further up or down that chain.

## Feature / Operation scope (v0.1)

A Feature definition references exactly one Operation:

```yaml
operation:
  ref: cuttingedgebespoke.operation.vertical_drill
  object_version: "1.0.0"
```

**DTML v0.1 feature definitions support one primary manufacturing
operation. Multi-operation features are deferred until validated by a
real manufacturing example.** This limitation lives here and in
`FeatureSpecification.md`, not as a `TBD` inside the schema itself — a
schema should describe current valid behaviour, not future uncertainty.
A countersunk hole (cylindrical hole + conical recess, producible as
either one combined operation or two sequential ones) is the concrete
future example expected to force this decision — see
`OperationSpecification.md`, "Why countersink isn't its own
`operation_type`".

See `OperationSpecification.md` for the fuller Feature / Operation /
capability-resolution ownership boundary (which values belong on which
side of this reference, and why).

### Typed Feature schemas: `schemas/features/`

`feature.schema.yaml` fixes the generic Feature shape, but leaves
`parameters` open (`additionalProperties: true`) since the actual
parameter shape differs per `feature_type`. A specific `feature_type` can
be typed by adding `schemas/features/<feature_type>.schema.yaml`,
composing `../feature.schema.yaml#/$defs/feature` with a type-specific
`parameters` shape via `allOf`, closed with `unevaluatedProperties: false`
— the same allOf-then-close-one-level-up pattern this document already
uses for `common.schema.yaml#/$defs/knowledge_object`. Shared geometry
that multiple `feature_type`s need (e.g. a hole's diameter/hole_form/
depth) belongs in its own reusable `$defs` fragment file, composed into
each typed schema the same way, rather than duplicated per type.
`hole_array.schema.yaml` + `hole_geometry.schema.yaml` are the worked
example — see `FeatureSpecification.md` and
`HoleArrayFeatureSpecification.md`.

`tools/validate_schema.py`'s schema discovery walks `schemas/`
recursively (`rglob`, not `glob`) specifically so this subdirectory is
picked up automatically; an instance still declares which schema it
conforms to via a normal `x-dtml-schema: ../schemas/features/
<feature_type>.schema.yaml` reference.

## Validator scope

`tools/validate_schema.py` checks JSON Schema *shape* conformance only: is
this a valid Draft 2020-12 schema, and does an instance document match the
schema it declares. It does not resolve whether a referenced object
(`ref: cuttingedgebespoke.material.egger_w1000_18mm`) actually exists in
`library/`, or whether its `object_version` is current — that's a semantic
check belonging to the future Validation Engine, not this conformance
tool.

### Known noise: duplicate "unevaluated properties" errors

Schemas that compose `common.schema.yaml`'s knowledge-object fields with
their own via `allOf` + `unevaluatedProperties: false` (the pattern used
by `part.schema.yaml`, `feature.schema.yaml`, `operation.schema.yaml`) can
report a property twice when it fails validation: once with the specific
error, and once as `Unevaluated properties are not allowed (...)`.

This is Draft 2020-12's defined behaviour, not a validator bug: a
`properties` keyword only marks a key "evaluated" if the subschema at that
key validates successfully. When it fails (e.g. `material` is missing
`object_version`), that key's annotation is dropped, so
`unevaluatedProperties` reports it again as unexpected — even though
nothing is actually additional. The specific, actionable error is always
present alongside the noise; no error is hidden by this. This holds
regardless of `allOf`, and reproduces with a bare `properties` +
`unevaluatedProperties: false` schema, so there is no library-level fix
to chase here.
