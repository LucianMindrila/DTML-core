# Part Specification (Draft v0.2)

A **Part** is the atomic manufacturable unit in DTML: a single panel,
rail, or similar component, with everything needed to cut, edge-band, and
machine it.

This document explains the *rationale* behind the shape. The schema
itself — `../../schemas/part.schema.yaml` — is the source of truth; this
spec should never contradict it. See also
`SchemaConventions.md` for the shared conventions (origin, expressions,
references, provenance) a Part relies on but doesn't redefine.

v0.2 supersedes v0.1: inline `holes`/`grooves` arrays and a bare
`source_confidence` field are gone, replaced by Feature instances and the
shared `provenance` block respectively (see "What changed from v0.1"
below).

## Worked example

A side panel with one shelf-pin-array feature (full version in
`../../examples/panel_with_shelf_pin_array.part.yaml`):

```yaml
namespace: cuttingedgebespoke.part
id: panel_with_shelf_pin_array
material:
  ref: cuttingedgebespoke.material.birch_plywood
  object_version: "1.0.0"
thickness:
  literal: {value: 18, unit: mm}
dimensions:
  width: {literal: {value: 600, unit: mm}}
  height: {literal: {value: 720, unit: mm}}
reference_face: front
edge_banding:
  - {edge: top, applied: true}
  - {edge: bottom, applied: true}
  - {edge: left, applied: false}
  - {edge: right, applied: false}
feature_instances:
  - feature:
      ref: cuttingedgebespoke.feature.shelf_pin_array
      object_version: "1.0.0"
    instance_parameters:
      count: {literal: {value: 5, unit: count}}
      start_offset: {literal: {value: 100, unit: mm}}
    position:
      x: {literal: {value: 20, unit: mm}}
      y: {literal: {value: 20, unit: mm}}
    reference_face: front
```

(`namespace`/`id`/`name`/`schema_version`/`object_version`/`status`/
`provenance` are omitted above for brevity — every Part carries them via
`common.schema.yaml#/$defs/knowledge_object`, see SchemaConventions.md.)

## Material: a reference, not an embedded value

A Part points at a Material by `ref` + `object_version`
(`reference.schema.yaml#/$defs/reference`); it does not embed the
material's own properties (density, grain direction, finish, etc.).

This matters for two reasons: a Material is shared across many Parts, so
embedding its properties would let the same logical material drift into
inconsistent copies across the library; and pinning `object_version`
means a Part's meaning doesn't silently change if the Material entry is
later revised — reproducing an old Part always resolves the Material
revision that was actually used.

## Dimensions and thickness are Expressions

`thickness`, `dimensions.width`, `dimensions.height` — and every
Feature-instance `position` coordinate — are
`expression.schema.yaml#/$defs/expression`, not bare numbers. Each is
exactly one of a fixed `literal`, a `formula`, or a `rule_reference` (see
SchemaConventions.md, "Expressions and units").

This resolves the old v0.1 open question of "should dimensions always be
Rule references, or can they be a fixed literal for non-parametric
Parts": both are valid, and the schema makes the choice explicit per
value rather than forcing one convention project-wide. A fixed decorative
end panel uses `literal` throughout; a parametric carcass side panel uses
`rule_reference` or `formula` for whichever dimensions actually vary with
the Module's configuration.

## Feature definitions vs. Feature instances

This is the central change from v0.1. A **Feature definition**
(`feature.schema.yaml`) describes a reusable manufacturing element —
type, default/typical parameters, and which Operation produces it —
independent of any Part. It doesn't know where it will end up, or on
which Part.

A **Feature instance** is a Part's own record of placing one Feature
definition on itself, under `feature_instances`:

```yaml
feature_instances:
  - feature: {ref: ..., object_version: ...}   # which Feature definition
    position: {x: ..., y: ...}                  # where, on this Part
    reference_face: front                       # which face, for this instance
    instance_parameters: {...}                  # overrides, for this instance
```

The split exists so the same Feature definition (e.g.
`shelf_pin_array`) can be reused across many Parts that each place it
differently — different position, different quantity, sometimes a
different reference face — without redefining the hole pattern itself
each time. Concretely: **position, per-instance parameter overrides, and
per-instance reference face belong on the Part's `feature_instance`
record. Type, default parameters, and the producing Operation belong on
the Feature definition.** Neither schema duplicates the other's fields.

## Positioning: relative to the Part's own origin

A `feature_instance.position` is always relative to *this Part's*
origin, not the Module or Furniture it will end up in: bottom-left corner
as viewed from `reference_face`, X increasing right, Y increasing up —
the fixed convention in SchemaConventions.md, "Part geometry conventions".
Translating a Feature instance's position into Module- or
Furniture-level coordinates is later Resolution Engine work, not
something the Part record itself needs to express.

## `instance_parameters`: overriding a Feature's defaults per placement

A Feature definition's own `parameters` describe its typical/default
shape (e.g. a shelf-pin-array's usual pitch). `instance_parameters` on
the Part's `feature_instance` record supplies or overrides values that
are specific to *this* placement — e.g. `count: 5` and a
`start_offset` for a shelf-pin array that happens to need only 5 pins
on this particular panel instead of the Feature's typical count. Only
the keys that differ need to be present; resolving the *effective*
parameter set (Feature defaults overridden by instance values) is
Resolution Engine work, not encoded in the schema itself.

## `reference_face`: appears at two levels, deliberately

Both the Part itself and each `feature_instance` declare `reference_face`
(`front | back`). The Part-level value is which face is generally being
machined or faces the room. The instance-level value can differ — e.g. a
Part whose primary `reference_face` is `front` can still carry a Feature
instance (a hole, say) drilled from the `back`. Neither value is
redundant; don't assume a Part's `reference_face` implies the same for
every Feature placed on it.

## Edge banding

`edge_banding` is optional at the Part level — a Part with no edge
banding at all simply omits it. When present, each entry is one edge
(`top | bottom | left | right`), whether banding is `applied`, and
optionally a `material` reference that may differ from the Part's own
material (a different finish/edge material than the panel face).

**Convention (not schema-enforced):** list all four edges explicitly,
with `applied: false` for the ones that aren't banded, as in the worked
example above — an explicit `false` is a recorded fact; an omitted edge
is just missing data, and the two shouldn't be conflated. The schema
doesn't require all four edges or forbid duplicates (there's no
`minItems`/`uniqueItems` constraint on the array); this is a documented
convention, enforceable later by the Validation Engine, not by JSON
Schema itself — the same pattern SchemaConventions.md uses for the
`confidence: unconfirmed` production-reference rule.

## Is an empty `feature_instances` array valid?

**Yes, deliberately.** `feature_instances` is a required field (the key
must be present), but the schema does not require at least one entry.
A plain panel with no drilling, slotting, or other machining — a fixed
decorative end panel, for instance — is `feature_instances: []`. This is
the intended v0.2 replacement for what would have been an absent/empty
`holes` array in v0.1: every Part still declares the field, so its
absence is never ambiguous between "not yet encoded" and "genuinely has
no features," but a Part is not forced to invent a Feature instance it
doesn't have.

## Hole patterns and the extraction findings

The DXF extraction findings in `../../extractor/README.md` are candidate
**Feature definitions** now, not raw Part-level hole records — under v0.2
a confirmed hole cluster becomes a `feature.schema.yaml` entry (e.g.
`feature_type: hole` or `hole_array`) that Parts then reference via
`feature_instances`, rather than data embedded directly in the Part:

- A repeating `(8mm, 8mm, 15mm)` diameter cluster — high-confidence match
  to a standard KD cam+dowel fitting, but still needs a named entry in
  `../../schemas/hardware.schema.yaml` before a corresponding Feature can
  reference it.
- A `(2mm, 4mm, 11mm)` cluster, the most common 3-hole signature found —
  identity not yet confirmed. **Do not encode a Feature referencing this
  pattern until confirmed** — per `provenance.confidence`, nothing
  `unconfirmed` may be referenced by a production Module (see
  SchemaConventions.md, "Provenance owns confidence").
- Full-height 5mm hole rows at a measured ~70.7mm pitch — tentatively
  shelf-pin holes, but the pitch doesn't match the standard 32mm system.
  Needs confirmation of intended pitch before encoding as a Feature.

## Open questions

- **Feature parameter typing.** `hole_array` is now typed
  (`schemas/features/hole_array.schema.yaml` — see
  `FeatureSpecification.md` and `HoleArrayFeatureSpecification.md`), but
  every other `feature_type`'s `parameters` remains open-ended
  (`additionalProperties: true`), and a Part's `instance_parameters` is
  untyped regardless of `feature_type` — nothing yet rejects
  `instance_parameters: {banana_count: twelve}` (see
  `FeatureSpecification.md`, "Feature definition parameters vs. instance
  overrides").
- **`groove` parameter shape.** `groove` is a valid `feature_type`, but
  what a groove-shaped panel-to-panel slot joint actually needs
  (run direction, width, depth) isn't modelled yet beyond the generic
  open `parameters` object — needs a proposal once a real groove example
  is encoded.
- **Multi-operation Features.** A Feature definition currently references
  exactly one Operation; deferred until a real manufacturing example
  needs more than one — see SchemaConventions.md, "Feature / Operation
  scope".

## What changed from v0.1

- `holes` / `grooves` inline arrays → `feature_instances`, referencing
  reusable `feature.schema.yaml` definitions instead of embedding
  geometry directly on the Part.
- `material: string` → `material: {ref, object_version}`, a versioned
  reference instead of a bare name.
- Bare `float` dimensions/thickness → Expressions (`literal` / `formula`
  / `rule_reference`).
- `source_confidence: confirmed | extracted_unconfirmed` → the shared
  `provenance` block (`source_type` + `confidence` + review metadata),
  same rule (nothing unconfirmed referenced by a production Module),
  single place it lives across every knowledge object — see
  SchemaConventions.md, "Provenance owns confidence".

See `../../schemas/part.schema.yaml` for the machine-readable schema.
