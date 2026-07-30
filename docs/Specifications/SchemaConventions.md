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

`namespace` and `id` both match `^[a-z0-9_]+(\.[a-z0-9_]+)*$` for
`namespace` and `^[a-z0-9_]+$` for `id` (no dots — the namespace carries
the hierarchy).

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
ref: cuttingedgebespoke.material.birch_plywood
object_version: "1.2.0"
```

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

## Validator scope

`tools/validate_schema.py` checks JSON Schema *shape* conformance only: is
this a valid Draft 2020-12 schema, and does an instance document match the
schema it declares. It does not resolve whether a referenced object
(`ref: cuttingedgebespoke.material.birch_plywood`) actually exists in
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
