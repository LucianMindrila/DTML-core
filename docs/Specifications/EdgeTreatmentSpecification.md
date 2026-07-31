# Edge Treatment Specification (Draft v0.1)

An edge treatment records that one of a Part's four fixed edges
(`top | bottom | left | right`) is banded — a strip of edge material
bonded to that edge, e.g. 1mm white ABS. It's the third knowledge-object
type this schema foundation resolves end to end (after `hole_array` and
`groove`), and structurally different from both: it is not a placed
Feature instance. There is no `feature.schema.yaml` entry for "edge
band", no `feature_instances` record, no anchor position — it's a
property of one of the Part's own four named edges, declared directly on
the Part.

The schema is the source of truth — the `edge_treatment` shape inside
`../../schemas/part.schema.yaml`, and the `resolved_edges` shape inside
`../../schemas/resolved/resolved_part.schema.yaml`. This document
explains why both are shaped that way. See `ResolvedGeometrySpecification.md`
for why `resolved_edges` is a sibling array on `resolved_part` rather than
a `resolved_feature` branch, and `MaterialSpecification.md` for the
`edge_band`-typed Material an edge treatment's `band.material` resolves
against.

## The governing invariant

**A DTML Part is always defined and machined to finished dimensions.
Edge-banding is a subsequent process whose pre-milling compensation
preserves — never changes — those dimensions.**

`part.dimensions.width` / `part.dimensions.height` (`PartSpecification.md`)
are the Part's finished size, band included, both before and after
resolution. Adding an edge treatment to a Part never changes its
resolved `width_mm`/`height_mm` — the panel is still machined so that,
once banded, it measures exactly what `dimensions` says. Everything the
factory does to make that true (removing material equal to the band's
own thickness before bonding it, so the banded result comes back out to
the same finished size) is a **manufacturing process requirement**,
carried in the resolved output as data for a downstream consumer to act
on — never as a geometric adjustment to the Part's own resolved
dimensions.

This is a specific instance of a general DTML principle, worth stating
plainly because it will recur: **the source and resolved model describe
the required finished result; manufacturing knowledge determines how the
factory preserves that result through each process.** The resolver
computes what the factory must do (`process_requirements.pre_mill`); it
never lets that computation feed back into the numbers that define what
the *Part* is.

## Three-layer ownership split

Three genuinely different concerns are easy to conflate here, so v0.1
keeps them in three separate places:

1. **Edge treatment (source, Part-owned)** — *which* named edge carries
   *what* band: material, thickness, width, and whether it's exposed.
   Lives on the Part, next to the edge it describes. This is the only
   layer a Part author writes.
2. **Manufacturing rule (resolver-owned)** — *how* the factory achieves
   the governing invariant: `pre_mill_removal_mm = band.thickness_mm`.
   This is manufacturing knowledge, not something a Part author decides
   per Part — every banded edge follows the same rule. Resolver v0.1
   implements this rule directly in `dtml/resolver.py`, hardcoded, the
   same way `hole_array`'s `depth < thickness` blind-hole check is
   hardcoded Python in `dtml.semantic_validation` rather than a `Rule`
   object (`docs/Specifications/RuleSpecification.md` has no
   implementation yet — no `rule.schema.yaml`, no expression parser; see
   "Why hardcoded, not a Rule" below). A future Rule engine may become
   responsible for evaluating this rule, but must produce the same
   resolved contract.
3. **Capability resolution (future, machine-owned)** — *which machine*,
   *which cutter*, *what feed speed*, *what glue temperature* actually
   performs the pre-mill and bonding. Entirely out of scope for this
   milestone. This layer must never leak back into a Part's resolved
   dimensions or into `resolved_edges` — a machine substitution can
   change which station does the work, never what the Part is supposed
   to measure afterward.

## Why hardcoded, not a Rule

`RuleSpecification.md` documents an intended future expression/condition
engine (`inputs`, `expression`, `applies_when`), but today has zero
implementation: no `rule.schema.yaml`, no grammar, no parser, both open
questions ("formal grammar for expression", "how `applies_when`
conditions compose") still unresolved. Modelling the pre-mill rule as a
`Rule` object now would mean inventing that engine under pressure from
an unrelated milestone. Hardcoding
`pre_mill_removal_mm = band.thickness_mm` directly in the resolver
matches existing precedent exactly (hole_array's own blind-hole depth
check) and keeps the contract — `resolved_edges[].process_requirements`
— stable regardless of which layer computes it later.

## Source shape: `edge_treatment`

Replaces the earlier, thinner `edge_banding: [{edge, applied, material}]`
draft (`PartSpecification.md` v0.2, "Edge banding") — that shape recorded
only a boolean and an optional material override, with no band
dimensions and no treatment-type discriminator:

```yaml
edge_treatments:
  - edge: left
    treatment_type: edge_band
    band:
      material: {ref: cuttingedgebespoke.material.white_abs_1mm, object_version: "1.0.0"}
      thickness_mm: {literal: {value: 1, unit: mm}}
      width_mm: {literal: {value: 22, unit: mm}}
```

- `edge` — one of the four fixed named edges (`top | bottom | left |
  right`), unchanged vocabulary from the v0.1 draft — no new decision
  needed here.
- `treatment_type` — `edge_band` is the only value in v0.1. Present now,
  rather than assumed, so a future treatment type (e.g. a solid-lipped
  edge) can be added as a new `const` branch later without reinterpreting
  existing documents — the same reason `groove_form` is explicit in
  `GrooveFeatureSpecification.md` rather than an unstated assumption.
- `band.material` — a `reference.schema.yaml`-shaped reference to an
  `edge_band`-typed Material (`MaterialSpecification.md`), resolved by
  ref + `object_version` the same way `part.material` now is
  (`ResolverSpecification.md`, reference resolution stage).
- `band.thickness_mm` / `band.width_mm` — Expressions
  (`expression.schema.yaml`), not bare numbers, consistent with every
  other dimension in `part.schema.yaml`. Deliberately independent of the
  referenced Material's own `thickness`/`width` fields — see
  `MaterialSpecification.md`, "Deliberately not enforced" for why the two
  are not cross-checked in v0.1.

**Sparse by construction, not by convention.** Unlike the old
`edge_banding` array (which documented — but didn't enforce — listing all
four edges with `applied: true/false`), `edge_treatments` simply omits
any edge with no treatment. There is no `applied` flag to set `false`:
an edge not in the list has no treatment, full stop. This is a
deliberate reversal of the old convention, not an oversight — see
"Sparse resolved_edges emission" below for why the *resolved* side
adopts the same rule, for the same reason.

**Duplicate-edge rejection.** The schema does not (and structurally
cannot, without a custom keyword) reject two entries naming the same
`edge`. The resolver does, as a semantic-validation rule — one treatment
per named edge, an unambiguous manufacturing instruction. Two entries for
`edge: left` is caught the same way hole_array's semantic rules catch a
non-integral `count`: schema-valid, resolver-rejected.

## Resolved shape: `resolved_edges`

A new top-level array on `resolved_part`, sibling to `resolved_features`
— not nested inside it, and not a `resolved_feature` branch (see
`ResolvedGeometrySpecification.md`'s "`resolved_edges` — a sibling array,
not a `resolved_feature` branch" for the full reasoning):

```yaml
resolved_edges:
  - edge: left
    treatment_type: edge_band
    band:
      material: {ref: cuttingedgebespoke.material.white_abs_1mm, object_version: "1.0.0"}
      thickness_mm: 1
      width_mm: 22
    length_mm: 720
    process_requirements:
      pre_mill:
        required: true
        removal_mm: 1
```

**Sparse resolved_edges emission.** Only edges that actually carry a
treatment appear here — no `edge: right` / `applied: false` placeholder
entries. This is the resolved-side mirror of the source-side sparseness
above, and it's a deliberate departure from how the *old*
`edge_banding` convention documented the source side (list all four,
flag `applied`): the resolved contract represents actual manufacturing
requirements, not full-coverage bookkeeping. A consumer asking "does this
Part need any edge-banding work" reads `resolved_edges.length` — zero
means no work, not "zero means the resolver forgot to check."

**`length_mm`: computed from finished dimensions, not carried from the
source.** An edge treatment doesn't declare its own length — it's
derived from the Part's own resolved, finished `dimensions`, by which
axis the named edge runs along:

```
top, bottom  -> length_mm = width_mm
left, right  -> length_mm = height_mm
```

This follows directly from the governing invariant: the band runs the
full finished length of the edge it's on, because the Part's dimensions
already are the finished, banded size.

**`process_requirements.pre_mill`** is where the manufacturing rule from
"Three-layer ownership split" surfaces in the resolved output:
`required` is always `true` for a v0.1 `edge_band` treatment (there is no
edge-banding treatment type yet that skips pre-milling), and
`removal_mm` is always exactly `band.thickness_mm` — enforced by the
resolver, not left for a downstream consumer to (re)compute or
potentially get wrong.

## Material reference resolution

Two references now resolve through the same mechanism
(`ResolverSpecification.md`'s reference-resolution stage): `part.material`
(unresolved by any resolver version until now — confirmed, there is no
existing code path touching it) and `edge_treatment.band.material`. Both
resolve by canonical ref + `object_version` against a real Material
document (`MaterialSpecification.md`) — existence only. Neither resolves
`part.thickness` against `material.standard_thicknesses`, nor
`band.thickness_mm` against `material.thickness` — see
`MaterialSpecification.md`, "Deliberately not enforced", for why both
cross-checks are explicitly out of scope pending a family-vs-product
decision for Material.

## What's structurally enforced vs. semantic

JSON Schema (`tools/validate_schema.py`) enforces, on the source side:

- each `edge_treatments` entry has `edge`, `treatment_type`, and `band`;
- `edge` is one of the four fixed names; `treatment_type` is exactly
  `edge_band`;
- `band` has `material` (a well-formed reference), `thickness_mm`, and
  `width_mm` (each a well-formed Expression);
- no unrecognised key survives (`unevaluatedProperties: false`).

It deliberately does **not** enforce:

- **No duplicate `edge` values** — same category of rule as `hole_array`
  count positivity: a structural array-uniqueness constraint can't
  express "unique by one nested key" cleanly, and this is better read as
  a manufacturing-instruction-ambiguity rule than a shape rule anyway.
- **`band.thickness_mm > 0` / `band.width_mm > 0`** — same reasoning as
  every other Expression-typed dimension in this codebase: the resolved
  value isn't known until Expression evaluation.
- **Existence of the referenced Material** — reference resolution is a
  resolver-stage concern, not a schema-shape concern (same as `feature`/
  `operation` refs today).

All of the above are the intended semantic-validation rule set for
resolver v0.1: *no two `edge_treatments` entries name the same edge;
effective `band.thickness_mm` and `band.width_mm` are positive after
resolution; `band.material` resolves to a real, existing `edge_band`
Material.*

## Explicitly deferred

- multiple layers/passes of banding on the same edge;
- corner treatments (mitred vs. butted corners between two banded
  adjacent edges);
- radiused or profiled edges (v0.1 assumes a square, straight edge);
- the Part/Material thickness cross-check (`MaterialSpecification.md`);
- capability resolution — which machine, cutter, feed speed, or glue
  temperature performs the pre-mill and bonding (layer 3 above);
- DXF/geometric representation of the band or the pre-mill allowance —
  `resolved_edges` is explicitly non-geometric; see
  `DXFRendererSpecification.md`.

## Acceptance criteria

1. A Part with one or more `edge_treatments` entries validates against
   `part.schema.yaml`.
2. Two `edge_treatments` entries naming the same `edge` are schema-valid
   but rejected by the resolver.
3. A `band.material` reference to a Material that isn't `material_type:
   edge_band`, or doesn't exist at the referenced `object_version`, is
   rejected by the resolver.
4. Resolving a Part with a `top` edge treatment produces exactly one
   `resolved_edges` entry, with `length_mm` equal to the Part's resolved
   `dimensions.width`, and `process_requirements.pre_mill.removal_mm`
   equal to the resolved `band.thickness_mm`.
5. Resolving a Part with no `edge_treatments` produces `resolved_edges:
   []` — never an entry for an untreated edge.
6. Resolving a Part's `dimensions.width`/`dimensions.height` is
   unaffected by whether any edge carries a treatment — the governing
   invariant, checked directly.

## Open questions

- **Family-vs-product Material decision** (`MaterialSpecification.md`) —
  blocks ever enabling the Part/Material thickness cross-check.
- **Corner treatment model** — not attempted until two adjacent banded
  edges force a real decision.
- **Capability-resolution layer** — entirely unscoped; this document only
  guarantees it must never feed back into `resolved_edges` or a Part's
  own dimensions.

See `../../schemas/part.schema.yaml` and
`../../schemas/resolved/resolved_part.schema.yaml` for the machine-readable
schemas.
