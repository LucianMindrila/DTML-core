# Resolver Specification (Draft v0.1)

The resolver is DTML's first executable-semantics layer: it takes
validated source documents (a Part, its Feature instances, the Feature
definitions and Operations they reference) and produces a fully
resolved, deterministic description of the actual generated geometry —
no unresolved Expressions, no unmerged defaults, no implicit conventions
left for a downstream renderer to reinterpret.

It is a narrow, Part-local slice of the "Resolved Design" concept in
`Architecture.md` — not the full multi-Part/Module/Furniture/Room
composition, which is out of scope until later phases (`Roadmap.md`).

## v0.1 scope

Supports:

- flat, rectangular Parts only;
- exactly one Feature type: `hole_array`;
- literal Expressions only (`formula`/`rule_reference` are valid DTML,
  rejected by this resolver version with a precise "unsupported by
  resolver v0.1" error, not a schema error);
- Feature defaults merged with `feature_instance.instance_parameters`
  overrides;
- front/back face-local coordinates (`SchemaConventions.md`, "Face-local
  coordinates and depth");
- semantic validation (positivity, integer-ness, bounds — see below);
- deterministic resolved output, schema-validated against
  `schemas/resolved/resolved_part.schema.yaml`.

Explicitly deferred:

- non-rectangular Parts (rejected, per `SchemaConventions.md`'s "v0.1
  resolver scope");
- rotational placement;
- assembly/world (Module/Furniture/Room) coordinates;
- `formula`/`rule_reference` Expression evaluation;
- multiple Feature types per resolution run;
- capability/manufacturing resolution (machine setup, post-processor
  coordinates);
- DXF or any other rendered output.

Acceptance criterion: the resolver deterministically converts the
`panel_with_shelf_pin_array`/`shelf_pin_array` example into a
schema-valid resolved Part with explicit, face-local hole coordinates,
and rejects each known semantic failure with a precise path.

## Pipeline stages

Implemented as explicit, separately testable phases (`dtml/` package),
not one large function — this is deliberately over-structured for what
`hole_array` alone needs, because every later Feature type and the
eventual `formula`/`rule_reference` evaluator plugs into the same
pipeline rather than forcing a rewrite:

1. **Load** — read the Part YAML document (`dtml.loader`).
2. **Validate source documents** — the Part, and every Feature/Operation
   it references, against their declared `x-dtml-schema`
   (`dtml.loader`, reusing the same `jsonschema`/`referencing` machinery
   as `tools/validate_schema.py`).
3. **Resolve references** — `feature_instance.feature` and, transitively,
   the Feature definition's `operation`, resolved by canonical identity
   (`dtml.references`; see "Reference resolution" below).
4. **Resolve Expressions** — every `literal` Expression in the Part
   (`thickness`, `dimensions`, `feature_instance.position`) and in the
   Feature definition's `parameters` / instance's `instance_parameters`,
   independently, to plain numbers (`dtml.expressions`). A `formula` or
   `rule_reference` anywhere raises `UnsupportedExpressionForm` with the
   exact document path.
5. **Merge Feature defaults and instance overrides** — a plain recursive
   deep-merge of the two already-resolved parameter dicts from stage 4
   (`dtml.merge`). Because both sides are already plain values (numbers,
   strings, nested plain objects) by this point, merge doesn't need to
   distinguish "Expression-shaped" from "plain nested object" — it only
   ever asks "are both sides dicts? recurse. otherwise, override wins."
   This is why Expression resolution happens *before* merge, not after.
6. **Validate effective parameters** — the semantic rules
   `HoleArrayFeatureSpecification.md` documents but the schema
   deliberately doesn't enforce (`dtml.semantic_validation`; see below).
7. **Generate coordinates** — the anchor + offset + direction formula
   (`dtml.coordinate_system`; see below).
8. **Validate geometry against Part bounds** — every hole centre,
   accounting for radius, must lie within the Part's resolved
   `width`/`height` (`dtml.semantic_validation`).
9. **Emit resolved model** — assemble the `resolved_part` structure.
10. **Validate resolved output** — the assembled structure against
    `schemas/resolved/resolved_part.schema.yaml`, as a safety net (see
    "Why the resolved schema can be stricter" below).

`dtml.resolver.resolve_part()` orchestrates all ten stages and is the
only entry point `tools/resolve_part.py` calls.

## Coordinate generation: anchor + offset + direction

`feature_instance.position` is the 2D face-local anchor. `hole_array`'s
own `start_offset` (renamed from `start_position` — see
`HoleArrayFeatureSpecification.md`) is a non-negative scalar offset from
that anchor, along `direction`'s axis, in `direction`'s sense. Given:

```
anchor = (ax, ay)                  # feature_instance.position, resolved
start_offset = s                   # effective_parameters.start_offset, default 0
pitch = p
count = n
index i = 0 .. n-1
```

the direction vector is:

```
axis=x, sense=positive  → ( 1,  0)
axis=x, sense=negative  → (-1,  0)
axis=y, sense=positive  → ( 0,  1)
axis=y, sense=negative  → ( 0, -1)
```

and every hole centre is:

```
distance_i = s + i * p
centre_i = anchor + direction_vector * distance_i
z_i = 0   # every generated hole's z-coordinate is 0 in this face-local
          # frame; depth is reported separately (see below), not folded
          # into centre.z
```

`depth` is independent of this calculation entirely: always positive,
always measured inward from the referenced face
(`SchemaConventions.md`, "Face-local coordinates and depth"). A `blind`
hole's effective depth is its resolved `depth` parameter; a `through`
hole's effective depth is the Part's resolved `thickness` (there is no
source `depth` to resolve — `hole_geometry.schema.yaml` forbids it).

Front and back faces are **not** mirrored during coordinate generation.
Both use the same viewer-relative formula above — mirroring is a
property of how front-face and back-face *frames* relate to each other
physically (`SchemaConventions.md`), not something this stage needs to
account for. A face-local → machine/physical transform is capability
resolution, out of scope here.

## Semantic validation rules (stage 6 and 8)

Structural (schema) validation deliberately leaves these open — see
`HoleArrayFeatureSpecification.md`, "What's structurally enforced vs.
semantic". The resolver is the layer that actually enforces them, on
resolved literal values only (never on unresolved `formula`/
`rule_reference` — those are rejected earlier, at stage 4):

Part:

- `width > 0`, `height > 0`, `thickness > 0`.
- Rectangular geometry only — automatically satisfied, since
  `part.schema.yaml` has no way to express a non-rectangular Part yet.

`hole_array` effective parameters:

- `diameter > 0`.
- `pitch > 0`.
- `count` is a positive integer (checked on the resolved numeric value:
  `count >= 1` and `count` has no fractional part).
- `start_offset >= 0` (defaults to `0` when absent — never negative;
  `direction.sense` supplies the only sign in the calculation).
- `blind` hole: `depth > 0` and `depth < thickness` (strictly less —
  `depth == thickness` is rejected, since that's a through hole
  mis-described as blind).
- `through` hole: no source `depth` (already schema-enforced); effective
  depth is the full resolved `thickness`.
- No unrecognised key survives the merge. (Today's
  `feature_instance.instance_parameters` is schema-open —
  `additionalProperties: true`, see `PartSpecification.md`'s "Feature
  parameter typing" open question — so this is currently the only place
  an unknown override key like `banana_count` gets rejected. Tightening
  `instance_parameters` itself is separate, deferred schema work.)

Geometry bounds (stage 8), using each hole's `diameter / 2` as radius:

```
radius <= x <= width - radius
radius <= y <= height - radius
```

enforced as the stronger radius-aware rule rather than a bare
`0 <= x <= width`, per the earlier discussion: a centre exactly on the
edge would otherwise produce a partially missing hole. Violations report
the resolved centre, radius, and Part bounds, plus the generated hole's
index — e.g. `resolved_features[0].holes[4]`.

## Reference resolution

References (`feature_instance.feature`, and a Feature definition's own
`operation`) are resolved by canonical identity — `namespace + "." + id`
plus `object_version` — never by filename. `dtml.loader` builds an index
of every document under a set of **search roots**, keyed by
`(ref, object_version)`, and `dtml.references` looks up against that
index. Loading a candidate match verifies it actually *declares* the
requested `namespace`/`id`/`object_version` — a same-named file that
happens to sit in the search path is not enough (this is the same
determinism guarantee `reference.schema.yaml` and `Architecture.md`
already require of the format; the resolver is the first thing that
actually checks it at run time).

Search roots default to `[the input file's own directory, examples/]`,
so `tests/fixtures/resolver/` fixtures can reference the canonical
`examples/shelf_pin_array.feature.yaml` and
`examples/vertical_drill.operation.yaml` without duplicating them —
consistent with `tests/README.md`'s "don't duplicate an example" rule.
`tools/resolve_part.py --search-root <dir>` adds further roots.

A reference that resolves to no matching document, or to a document
whose declared `object_version` doesn't match the one requested, is a
stage-3 error (`ReferenceResolutionError`) — not a schema error, since
the referencing document is itself perfectly schema-valid.

## Resolved output contract

`schemas/resolved/resolved_part.schema.yaml` is the output contract. See
that file for the authoritative shape; in outline:

```yaml
schema_version: "0.1"
resolution_version: "0.1.0"
source_part: {ref: ..., object_version: ...}
dimensions: {width_mm, height_mm, thickness_mm}
resolved_features:
  - instance_index: 0
    feature: {ref: ..., object_version: ...}
    operation: {ref: ..., object_version: ...}
    reference_face: front
    anchor_mm: {x, y}
    effective_parameters: {diameter_mm, hole_form, depth_mm, pitch_mm, count, start_offset_mm, direction}
    holes:
      - index: 0
        centre_mm: {x, y, z}
        diameter_mm: ...
        depth_mm: ...
        hole_form: ...
```

`resolution_version` versions the resolver's own output contract and
algorithm, independently of `schema_version` (the source DTML schema
revision) — the same distinction `SchemaConventions.md` already draws
between `object_version` and `schema_version`, one level up.

`instance_index` (not `instance_id`) is deliberately named for what it
actually is: the position of this Feature instance within the Part's
`feature_instances` array. `feature_instance` has no `id`/`name` field
of its own yet (open question, `HoleArrayFeatureSpecification.md`), so
an index is what's honestly available — calling it an "id" would imply a
stable identity that doesn't exist yet.

`effective_parameters` is kept alongside `holes` deliberately, even
though every value it contains is already reflected per-hole: it lets an
engineering reviewer see exactly which merged values produced the array,
without having to reverse-engineer them from the generated points.

### Why the resolved schema can be stricter than the source schemas

Every source-schema decision to leave positivity/integer-ness
unstructural (`hole_array.schema.yaml`, `hole_geometry.schema.yaml`) was
driven by Expressions potentially being `formula`/`rule_reference` —
checking only the literal case would misleadingly imply a guarantee for
values that aren't actually known yet. That reasoning doesn't apply to
*resolved* output: by the time a value is written into
`resolved_part.schema.yaml`, the resolver has already evaluated it to a
concrete number and run stage 6/8 validation against it. So the resolved
schema *does* structurally enforce `exclusiveMinimum: 0` on every
`_mm` dimension, `type: integer` + `minimum: 1` on `count`, and
`minimum: 0` on `start_offset_mm` — as a regression safety net, not as a
relaxation of the earlier structural-vs-semantic principle.

## What's not built yet

- `formula`/`rule_reference` evaluation.
- Any Feature type other than `hole_array`.
- Non-rectangular Parts, rotation, assembly/world coordinates (see
  `SchemaConventions.md`, "v0.1 resolver scope").
- Capability/manufacturing resolution and DXF generation — the next
  milestone after this one is green in CI, expected to be a small,
  low-risk follow-on consuming `resolved_part.schema.yaml` rather than
  another architecture exercise.

## Status: implemented and tested

`dtml/` (loader, references, expressions, merge, semantic_validation,
coordinate_system, resolver) and `tools/resolve_part.py` implement all
ten stages above. `tools/resolve_part.py
examples/panel_with_shelf_pin_array.part.yaml` deterministically produces
a schema-valid resolved Part with the expected five hole coordinates.

`tests/test_expression_resolution.py`, `tests/test_parameter_merge.py`,
and `tests/test_hole_array_resolution.py` (32 tests, all passing) cover
the individual modules and the full pipeline end to end, including every
case in the acceptance criterion above plus the semantic-validation and
geometry-bounds failure modes — see `tests/README.md`, "`fixtures/resolver/`"
for what each fixture proves and why the invalid ones are schema-valid but
resolver-rejected.
