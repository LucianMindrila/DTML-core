# Module Specification (Draft v0.1)

A **Module** (a.k.a. "bay type") is a standard assembly built from Parts,
parametrised by Rules, and the unit that an AI-vision image region is
classified into.

## Shape

```yaml
module:
  module_type: string              # e.g. "shoe_rake_bay", "drawer_bank",
                                    # "hanging_bay", "open_shelf_bay"
  inputs:
    - bay_width
    - bay_height
    - bay_depth
    - material_thickness
  equations:
    # references to Rules — see RuleSpecification.md
    internal_width: "bay_width - (2 * side_panel_thickness)"
    shelf_count: "floor((bay_height - top_clearance) / shelf_pitch)"
    rake_angle: 15                  # fixed per CorePrinciples §2
  parts:
    - part_ref: string              # references library/parts/
      quantity_expr: string         # e.g. "shelf_count"
  hardware:
    - hardware_ref: string          # references library/hardware/
      positions_expr: string        # e.g. "linear_series(pitch=32, count=shelf_count)"
  style_slots:
    - door_front
    - handle
    - finish
  outputs:
    panels: []                      # resolved at runtime, not stored here
    hardware_bom: []
```

## The classification target

Modules are the unit the Phase 3 classifier (`../Roadmap.md`) assigns to
each region of an uploaded AI vision image, each with a confidence score.
A Module definition should therefore be distinguishable from its
siblings by visually identifiable traits (e.g. a shoe-rake bay's angled
shelves vs. an open shelf bay's flat ones) — this is a design constraint
on how Modules are split, not just an engineering one.

## Initial Module set (Phase 2 target)

Per `../Roadmap.md`, the first 6–10 Modules to build, cross-referenced
against what's visible in the existing `modules.dxf`/`modules.pdf`
library:

- Hanging bay (single rail)
- Hanging bay (double rail)
- Drawer bank
- Shelving bay (fixed)
- Shoe-rake bay
- Computer shelf & file drawer bay
- Blanket drawer bay
- TV shelf bay

These names are provisional — confirm against the actual bay types shown
in `modules.pdf`/`modules.dxf` before finalising.

## Relationship to Style

A Module's `style_slots` define where a Style (`StyleSpecification.md`)
attaches — e.g. door front, handle, finish — without touching the
underlying construction logic. Changing a Style must never change a
Module's Rules.

## Open questions

- How a Module signals to the classifier which visual cues distinguish it
  (this may live in a separate classifier-training spec, not here).
- Multi-Module composition rules (e.g. how adjoining Modules share a
  panel) — not yet specified.

See `../../schemas/module.schema.yaml` for the machine-readable schema.
