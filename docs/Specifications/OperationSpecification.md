# Operation Specification (Draft v0.1)

An **Operation** is a reusable definition of a manufacturing process
family (drill, route, edge band, ...), referenced by a Feature
definition. It must stay machine-independent and must not duplicate the
resulting geometry that the Feature already owns.

This document explains the *rationale* behind the shape. The schema
itself — `../../schemas/operation.schema.yaml` — is the source of truth;
this spec should never contradict it. See also `SchemaConventions.md`
("Feature / Operation scope") for the reference syntax an Operation is
pointed at from.

## Worked example

`vertical_drill` (full version in
`../../examples/vertical_drill.operation.yaml`), referenced by the
`shelf_pin_array` Feature (`../../examples/shelf_pin_array.feature.yaml`):

```yaml
namespace: cuttingedgebespoke.operation
id: vertical_drill
operation_type: drill
parameters: {}
```

`parameters` is empty. That's not a placeholder — it's the expected
shape once diameter, depth, pitch and quantity are correctly recognised
as belonging to the *Feature*, not the Operation. See below.

## The three-tier model

Confusing these three layers is the easiest way to break Operation
reuse, so DTML keeps them strictly separate:

| Layer | Owns | Examples |
|---|---|---|
| **Feature** | resulting geometry / manufacturing condition | `hole_diameter`, `hole_depth`, `pitch`, `quantity`, `hole_form` |
| **Operation** | process family + process-level intent | `drill`, `route`, `edge_band`; a tolerance class; anything genuinely independent of which Feature invokes it |
| **Capability resolution** *(future)* | execution | selected tool ID, spindle speed, feed rate, pass depth, machine cycle |

Capability resolution doesn't have a schema yet (see `Architecture.md`)
— it's listed here so the boundary is clear before it's built, not
because Operation should anticipate its shape.

## Two tests for where a value belongs

1. **Machine test** — *"Could this value change merely because the same
   Part is manufactured on a different capable machine?"* If yes, it's
   capability resolution, not Operation. Feed rate and spindle speed
   fail this test immediately.
2. **Reuse test** — *"Could this value change merely because a different
   Feature reuses the same Operation?"* If yes, it's Feature, not
   Operation. Hole diameter fails this test: `vertical_drill` should be
   equally reusable by a 5mm shelf-pin hole and an 8mm dowel hole.

This is why `vertical_drill.operation.yaml` ships with `parameters: {}`
— diameter and depth live on `shelf_pin_array.feature.yaml` instead,
precisely so the same Operation can be reused by any hole-producing
Feature regardless of size.

## Hole form is Feature-owned

Whether a hole is blind, through, countersunk, or counterbored is a
**Feature** parameter, not an Operation parameter:

```yaml
feature_type: hole
parameters:
  hole_form: blind
  diameter: {literal: {value: 5, unit: mm}}
  depth: {literal: {value: 13, unit: mm}}
```

or, for a compound condition:

```yaml
feature_type: hole
parameters:
  hole_form: countersunk
  diameter: {literal: {value: 5, unit: mm}}
  countersink:
    major_diameter: {literal: {value: 10, unit: mm}}
    angle: {literal: {value: 90, unit: degrees}}
```

This passes the reuse test in reverse: `hole_form` changes the required
*result* (a through-hole and a blind hole are different geometry,
inspected and validated differently — a through-hole can be checked
against panel thickness, a blind hole against remaining material), and
that's true regardless of which capable machine drills it. `drill`
stays a single reusable Operation across all of them.

For `hole_array`, `hole_form` (`blind | through`) is now schema-enforced
— see `schemas/features/hole_geometry.schema.yaml` and
`HoleArrayFeatureSpecification.md`. `countersink` remains a documented
convention only, not schema-enforced anywhere yet: it's out of scope for
`hole_array` v0.1 and there's no typed plain `hole` schema yet either
(`feature.schema.yaml`'s generic `parameters` stays open until one
exists — see `FeatureSpecification.md`).

An Operation may still branch its own internal behaviour on `hole_form`
(e.g. a through-hole implying breakout-control on exit) — but it reads
that fact from the Feature, it does not own it.

## Why countersink isn't its own `operation_type`

A countersunk hole is a *compound* Feature — a cylindrical hole plus a
conical recess — producible more than one way in practice (a combined
countersink bit in one pass, a separate secondary operation, or routing
the recess). Adding `operation_type: countersink` would bake one
specific manufacturing method into what is actually a geometric
requirement of the Feature, and would stop being reusable the moment a
shop machined it a different way.

So for v0.1: `operation_type: drill` stays the Operation, and the
Feature's `parameters` describe the countersink geometry. Whether a
countersunk hole eventually needs *one* Operation reference or a
sequence of two is exactly the kind of case the existing "Feature
definitions support one primary manufacturing operation" limitation
(`SchemaConventions.md`, "Feature / Operation scope") is deferred
pending — a countersunk hole is a good future test case for that
decision, not a reason to generalise `operation_type` now.

## `entry_direction`: flagged, not resolved

An Operation's entry direction (which face/normal a tool approaches
from) plausibly varies by *placement* — the same `vertical_drill`
Operation drilled from `front` on one Part and `back` on another. That
suggests it belongs on the Feature instance's placement record
(`feature_instance.reference_face`, see `PartSpecification.md`) rather
than baked into the reusable Operation definition — unless a future
Operation genuinely means something orientation-invariant by it (e.g.
"always normal to whichever face is referenced"). Left as an open
question below rather than decided speculatively; a real multi-face
example should settle it.

## The v0.1 rule

> An Operation identifies the manufacturing process family requested by
> a Feature. It does not duplicate the Feature's resulting geometry, and
> it does not contain machine-specific execution settings.
>
> Hole form — blind, through, counterbored, or countersunk — is
> Feature-owned, because it describes required resulting geometry, not
> process family or execution.

`operation.schema.yaml`'s `parameters` therefore stays open-ended (no
per-operation-type schema yet — future work, parallel to Feature
parameter typing) but is narrowly scoped in practice: process-level
properties genuinely independent of the invoking Feature. Most v0.1
Operation library entries are expected to have empty `parameters`, as
`vertical_drill` does.

## Open questions

- **`entry_direction` placement.** Feature-instance field vs.
  Operation-level, per above — unresolved until a real multi-face
  example forces the decision.
- **Multi-operation Features.** Deferred; a countersunk hole modelled as
  two sequential Operations is the concrete future test case — see
  `SchemaConventions.md`, "Feature / Operation scope".
- **Per-operation-type parameter typing.** Future work, parallel to
  Feature parameter typing (see `PartSpecification.md`'s open
  questions).

See `../../schemas/operation.schema.yaml` for the machine-readable
schema.
