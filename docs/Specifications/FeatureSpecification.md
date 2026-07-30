# Feature Specification (Draft v0.1)

A **Feature definition** (`feature.schema.yaml`) describes a reusable
manufacturing element — type, default/typical parameters, and which
Operation produces it — independent of any Part. See
`PartSpecification.md` ("Feature definitions vs. Feature instances") for
how a Part places one on itself via `feature_instances`, and
`OperationSpecification.md` for the Feature/Operation ownership boundary
this document assumes throughout.

This document explains the *rationale* behind the generic Feature shape
and the per-`feature_type` typed-schema pattern. `feature.schema.yaml`
itself is the source of truth for the generic shape; a typed schema under
`schemas/features/` is the source of truth for a specific `feature_type`.

## Generic shape vs. typed shape

`feature.schema.yaml` fixes what every Feature has regardless of type:
`feature_type`, an `operation` reference, and a `parameters` object left
open (`additionalProperties: true`) — because a Feature's parameter shape
genuinely differs by type, and the generic schema doesn't know which type
it's looking at.

A **typed Feature schema** narrows that for one specific `feature_type`
by composing `feature.schema.yaml` with a type-specific parameter shape:

```yaml
allOf:
  - $ref: "../feature.schema.yaml#/$defs/feature"
  - type: object
    properties:
      feature_type: {const: hole_array}
      parameters: {$ref: "#/$defs/hole_array_parameters"}
unevaluatedProperties: false
```

These live under `schemas/features/<feature_type>.schema.yaml`, discovered
by `tools/validate_schema.py` via `rglob` alongside the flat top-level
schemas. An instance declares which one it conforms to via
`x-dtml-schema`, same as any other schema:

```yaml
x-dtml-schema: ../schemas/features/hole_array.schema.yaml
```

Not every `feature_type` needs a typed schema immediately — an untyped
`feature_type` (still validated against the generic `feature.schema.yaml`
only) simply hasn't had its parameter shape formalised yet. `hole_array`
is the first (see `HoleArrayFeatureSpecification.md`); `hole`, `slot`,
`pocket`, `groove`, `chamfer`, `edge_band` remain open `parameters`
objects until each gets the same treatment.

## Shared geometry fragments

When two `feature_type`s share real geometric concepts — e.g. a plain
`hole` and `hole_array` both need diameter/hole_form/depth — that shape
belongs in its own reusable `$defs` fragment
(`schemas/features/hole_geometry.schema.yaml`), composed into each typed
schema via `allOf`, rather than duplicated. A fragment is not itself a
valid Feature object (it has no `$id`-rooted standalone use as an
instance schema) — it only exists to be composed into one.

## Composing without accidentally closing too early

A typed schema's own parameter shape and a shared fragment both want to
reject unknown keys, but `additionalProperties: false` on either half of
an `allOf` would reject the *other* half's legitimate properties (each
`allOf` branch is evaluated independently against the same instance).
The pattern used throughout this repo — already established by
`part.schema.yaml`/`feature.schema.yaml`/`operation.schema.yaml`'s own
composition with `common.schema.yaml#/$defs/knowledge_object` — is:
leave each composed branch open, and close the *composed result* with
`unevaluatedProperties: false` one level up. `hole_array.schema.yaml`
applies this twice: once to assemble `hole_array_parameters` from
`hole_geometry` + array-specific properties, and again to assemble the
full Feature object from `feature.schema.yaml` + the `hole_array`
override. See `SchemaConventions.md`, "Known noise: duplicate
'unevaluated properties' errors" for the validator-output side-effect of
this pattern — it still applies here, unchanged.

## Feature definition parameters vs. instance overrides

A typed schema's parameter shape governs the **Feature definition**: it
should require the complete set of values a Feature of that type needs to
be manufacturable, supplied as reusable typical/default values. A Part's
`feature_instance.instance_parameters` (`part.schema.yaml`) may then
override any subset for a specific placement — the schema does not
additionally require the instance to supply anything, since the
definition already guarantees a complete, valid set on its own.

This applies uniformly across parameter keys — there is no fixed rule
that says a given key (count, position, direction, ...) is always
definition-owned or always instance-owned "by nature". Whether a
parameter is typically overridden per-placement is a property of the
specific Feature being modelled, decided when that Feature's typed schema
is designed — see `HoleArrayFeatureSpecification.md` for how this plays
out concretely for `hole_array` (`count` and `direction` both have
Feature-level defaults and are both realistic instance-level overrides).

`instance_parameters` itself remains untyped
(`additionalProperties: true`) in v0.1 — validating that an override
actually matches the referenced Feature's typed parameter shape requires
resolving the `ref` to a live library entry, which is Resolution Engine
work (`SchemaConventions.md`, "Validator scope"), not something
`tools/validate_schema.py`'s static per-document checking can do.

## Structural validation vs. semantic validation

A typed Feature schema can only constrain *shape*: required keys, enums,
conditional requirements between keys, and — for a `literal` Expression —
constraints on that literal's own value. It cannot constrain the
*resolved* value of a `formula` or `rule_reference`, and it cannot check
a Feature instance against the Part it's placed on (e.g. "this hole's
depth must be less than the Part's thickness"). Those are semantic
validation, owned by the future Validation/Resolution Engine
(`Architecture.md`), after expressions are resolved to concrete numbers
in a specific Part's context — not something to fake with a partial,
literal-only JSON Schema constraint that would only ever catch some
cases. See `HoleArrayFeatureSpecification.md` for exactly where this line
falls for `hole_array`'s `pitch`/`count`/`diameter`/`depth`.

## Open questions

- Which `feature_type`s get a typed schema next, and in what order —
  driven by which Features are actually needed for real manufacturing
  examples, not a fixed roadmap.
- Whether `instance_parameters` should eventually get its own validation
  path once the Resolution Engine can resolve a `feature.ref` to a live
  typed schema — deferred, see above.

See `../../schemas/feature.schema.yaml` and
`../../schemas/features/hole_array.schema.yaml` for the machine-readable
schemas.
