# DTML Reference Implementation

## Status
Informative document describing the current CuttingEdgeBespoke implementation.

## Current Stack
- Python
- Pydantic
- YAML
- JSON
- ezdxf
- FastAPI
- pytest

## Components
- Schema layer
- Library loader
- Expression engine
- Rule engine
- Validation engine
- DXF extractor
- Customer renderer
- Protected renderer

## Why Python, and why not a full 3D CAD kernel

Case-good furniture (wardrobes, kitchens, media units) is fundamentally a
*panel + drilling pattern* problem, not a solid-modeling problem — every
Part is a rectangle with thickness, edge-banding spec, and a set of
parametrically-positioned holes/grooves. This is exactly what mature
industry CAD/CAM (imos iX, Cabinet Vision, PolyBoard) models internally
too — none of them use general-purpose CAD kernels (CadQuery, FreeCAD,
OpenSCAD) for this, because that would be solving a harder problem than
the domain requires.

Python fits because:

- `ezdxf` reads **and** writes real DXF — letting the system both mine
  existing scattered DXF drawings (see `extractor/`) and generate real
  manufacturing output.
- `pydantic` gives clean schema validation matching the YAML definitions
  in `schemas/`.
- It's the existing business stack (ReportLab, openpyxl/BOM tooling) —
  one language across design, manufacturing, and reporting.
- Trivially served via FastAPI for the eventual web front end.

## Data model

Component library entries (Parts, Modules, Rules, Styles) are stored as
version-controlled YAML files — one file per Module type, one per
hardware/fitting standard, one per Style set — following the schemas in
`schemas/`. Git gives change history on the manufacturing brain itself,
which matters once tolerances and rules are being iterated on across real
jobs.

Example shape (illustrative, see `Specifications/ModuleSpecification.md`
for the authoritative structure):

```yaml
module_type: shoe_rake_bay
inputs: [bay_width, bay_height, bay_depth, material_thickness]
equations:
  internal_width: "bay_width - (2 * side_panel_thickness)"
  shelf_count: "floor((bay_height - top_clearance) / shelf_pitch)"
  rake_angle: 15   # fixed per CorePrinciples §2 standardisation rule
hardware:
  - type: shelf_pin
    positions: "linear_series(...)"
outputs:
  panels: []       # concrete list once inputs are resolved
  hardware_bom: []
```

## Phases
Phase 0: Documentation and schemas

Phase 1:
- Feature library
- Part library
- First generated DXF

Phase 2:
- Modules
- Rule engine
- Validation

Phase 3:
- Customer intent
- Room model

Phase 4:
- First Compilable Furniture

The reference implementation may evolve without changing the DTML specification.
