# Material Specification (Draft v0.3)

A Material is a physical stock item a Part is made from (`panel_stock`)
or bonded to a Part's edge (`edge_band`). Both `part.schema.yaml`'s
`material` field and the edge treatment's `band.material` field
(`EdgeTreatmentSpecification.md`) are `reference.schema.yaml`-shaped
references into this catalogue, resolved by canonical ref +
`object_version` (`ResolverSpecification.md`, stage 3), the same
reference-resolution mechanism already used for `feature` and
`operation` refs.

The schema is the source of truth — `../../schemas/material.schema.yaml`.
This document explains why it's shaped that way.

## Normative statement — v1 material scope

> DTML v1 supports only 18mm Egger MFC decors available in the UK. Parts
> requiring a 36mm finished thickness are manufactured as bonded
> constructions consisting of two 18mm MFC components. Edge banding is
> limited to 1mm and 2mm thicknesses. All other board families,
> thicknesses, and edge-band thicknesses are outside the scope of DTML v1
> and must be rejected explicitly.

This is a deliberate, controlled scope — enough to model carcasses,
doors, shelves, and tops without designing a universal materials system
prematurely. v0.3 supersedes v0.2's open-ended `category` vocabulary
(`mfc, mdf, plywood, veneer, solid_wood, hpl, other` for panel stock;
`abs, pvc, veneer, laminate, other` for edge band) with the single
narrow vocabulary below. 19mm/25mm veneer boards are an explicitly
anticipated *future* extension (see "Extending the scope later"), not
something v0.3 builds room for today.

## Rejection is structural, not semantic

MDF, plywood, solid timber, veneer board, laminates, 19mm board, 25mm
board, non-Egger manufacturers, and non-UK market availability are all
rejected the same way: they are simply not in the relevant field's
`enum`. `tools/validate_schema.py` rejects them at Stage 1-2 (schema
validation), before the resolver ever runs — there is no
`validate_material_family` semantic function to write or maintain,
because JSON Schema's `enum` already is that check:

```yaml
material_family: {type: string, enum: [mfc]}
manufacturer: {type: string, enum: [egger]}
market: {type: string, enum: [UK]}
thickness_mm: {type: number, enum: [18]}          # panel_stock
thickness_mm: {type: number, enum: [1, 2]}        # edge_band
```

The one thing this narrowing does *not* try to enforce structurally is
*which* Egger decors are approved — `decor_code` stays a free-form
string. See "The approved decor list lives in the library, not the
schema" below.

## Why v0.2, not v0.1 patched in place

The v0.1 draft (`{id, name, category, standard_thicknesses,
standard_sheet_size, edge_band_compatible, finish_options,
cost_per_sheet}`) predates the `knowledge_object` convention
(`common.schema.yaml`, `SchemaConventions.md`): no `$id`, no `namespace`,
no `object_version`, no `provenance`. It was never actually referenceable
by `reference.schema.yaml`, even though worked examples already pointed
at one. Rebuilding on `common.schema.yaml#/$defs/knowledge_object` closed
that gap and brought Material in line with `feature.schema.yaml` and
`operation.schema.yaml`. v0.3 (this revision) keeps that envelope and
narrows the content to the v1 scope above.

## `material_type`: panel stock vs. edge band

Edge-banding needs both kinds of material to be resolvable through the
same reference mechanism, but a panel material and an edge-band material
carry different, non-overlapping properties. `material_type` is a
discriminator, split the same way `feature_type` splits
`hole_array`/`groove` on the source side and `resolved_feature` splits
them on the resolved side: `allOf` + `const` +
`unevaluatedProperties: false` per branch, `oneOf` at the top
(`ResolvedGeometrySpecification.md`'s polymorphism pattern, applied here
to a source-side knowledge object rather than a resolved one).

```yaml
material_type: panel_stock
material_family: mfc
manufacturer: egger
market: UK
decor_code: W1000
decor_name: "Premium White ST9"
thickness_mm: 18
```

```yaml
material_type: edge_band
manufacturer: egger
decor_code: W1000
decor_name: "Premium White ST9"
thickness_mm: 1
```

The two branches deliberately look almost identical now — both identify
an Egger decor and a locked thickness. `panel_stock` additionally carries
`market` (a sheet's UK availability matters; a matched edge band is
assumed to ship alongside its decor) and `standard_sheet_size` is gone
entirely — sheet size isn't needed to resolve a Part's own dimensions and
was never used by the resolver.

## The approved decor list lives in the library, not the schema

`decor_code` and `decor_name` are free-form strings, not an `enum`. The
set of Egger UK decors DT Solutions actually stocks changes over time and
belongs in the Material library as data — one Material document per
approved decor (and, for panel stock, one per decor since v1 only has one
thickness anyway) — not hard-coded into `material.schema.yaml`. A decor
that isn't in the library simply has no Material document to reference,
so `dtml.references.resolve_reference` rejects it with
`ReferenceResolutionError` the same way an unknown Feature or Operation
ref would — no separate decor-list validation step is needed.

## 36mm slabs are bonded constructions, not a Material

A 36mm finished Part (most tops, some shelving) is never modelled as a
`thickness_mm: 36` Material. Egger doesn't stock 36mm MFC in this range;
the 36mm slab is DT Solutions' own bonded construction — two 18mm sheets
glued together (`../../schemas/dtsolutionsltd.co.uk` lists "flat bonding
of laminates and veneers" as a service). Modelling it as its own Material
would silently lose that manufacturing truth (stock stays 18mm; the third
dimension is an assembly step) and reintroduce the "does a Material
represent a family or a specific stocked product" ambiguity this v0.3
revision was written to close.

Instead, `part.schema.yaml` carries a new `construction` field —
`single_18mm` or `bonded_double_18mm` — and `part.material` keeps
pointing at the 18mm stock item either way:

```yaml
material: {ref: cuttingedgebespoke.material.egger_w1000_18mm, object_version: "1.0.0"}
thickness: {literal: {value: 36, unit: mm}}
construction: bonded_double_18mm
```

v1 keeps this vocabulary to exactly two values — no generic
multilayer-composite framework, no per-layer geometry in the resolved
output (`resolved_part.construction` is a straight passthrough of the
source value, see `PartSpecification.md` and
`ResolverSpecification.md`). A future thicker single-sheet product, or a
three-layer construction, is a new enum value when it's actually needed,
not something this revision builds room for speculatively.

## Thickness cross-check: now enforced

The earlier v0.2 draft deliberately did *not* compare a Part's resolved
thickness against its Material's thickness, because a Material's
`standard_thicknesses` was a list — it was genuinely ambiguous whether a
Material represented a generic family or one specific stocked product.
v0.3 answers that: every Material is now pinned to exactly one
`thickness_mm`, so the resolver enforces:

- **panel stock** — `construction: single_18mm` requires
  `part.thickness == material.thickness_mm`; `construction:
  bonded_double_18mm` requires `part.thickness == 2 * material.thickness_mm`.
  In v1 both sides of these equations are locked to 18/36 by the schema's
  own enums, but the check is written generally rather than hard-coded to
  those literals, so it keeps meaning the same thing if the 18mm enum
  value is ever joined by another.
- **edge band** — `edge_treatment.band.thickness_mm` (the Part's own
  Expression, resolved) must equal the referenced Material's
  `thickness_mm`. A Part cannot claim "1mm edging" while pointing at a
  Material stocked at 2mm.

Both are semantic checks (`dtml/semantic_validation.py`), not schema
ones — JSON Schema can't compare two sibling values across two separate
documents without `$data`, which this codebase doesn't use. See
`ResolverSpecification.md`.

## What's still not cross-checked

Colour/finish matching between a Part's own `material` decor and the
`band.material` decor on its edge treatments is not validated — a Part
can reference `egger_w1000_18mm` panel stock with an edge band whose
decor doesn't actually match. Catching that is a data-quality concern,
not a structural one, and is left for the Material library's own
curation (or a later lint step) rather than the resolver.

## Explicitly deferred

Scoped out of v1 entirely, not modelled at all:

- pricing / stock codes / supplier references;
- material substitution rules;
- 19mm/25mm veneer boards (planned next material milestone — extend the
  `material_family`/`thickness_mm` enums when it's actually built, not
  before);
- any board family, manufacturer, or market beyond MFC/Egger/UK.

## What's structurally enforced vs. semantic

JSON Schema (`tools/validate_schema.py`) enforces:

- every Material carries the full `knowledge_object` envelope
  (`namespace`, `id`, `object_version`, `provenance`, ...);
- `material_type` is exactly `panel_stock` or `edge_band`;
- `panel_stock` requires `material_family: mfc`, `manufacturer: egger`,
  `market: UK`, `decor_code`, `decor_name`, `thickness_mm: 18`;
- `edge_band` requires `manufacturer: egger`, `decor_code`,
  `decor_name`, `thickness_mm: 1 | 2`;
- no unrecognised property on either branch
  (`unevaluatedProperties: false`).

The resolver (`dtml/semantic_validation.py`) additionally enforces:

- `part.material` resolves and is `material_type: panel_stock`;
- `edge_treatment.band.material` resolves and is `material_type:
  edge_band`;
- the construction/thickness cross-check and the band/material thickness
  equality above.

See `../../schemas/material.schema.yaml` for the machine-readable schema.
