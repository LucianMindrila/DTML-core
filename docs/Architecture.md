# Architecture

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

## One schema, two renderers

```
                    ┌─────────────────────┐
  constraints  ────▶│                     │
  (Features,        │   Equation Engine   │────▶ Resolved design
  envelope)         │ (schemas + library) │      (single JSON/dict,
                    │                     │       fully dimensioned)
  Module selection ▶│                     │
  (+ confidence)     └─────────────────────┘
                                │
                 ┌──────────────┴──────────────┐
                 ▼                              ▼
        Manufacturing renderer          Customer renderer
        (ezdxf → dimensioned DXF,       (Three.js → proportional
         cut lists, hardware BOM,        3D view, no dimensions,
         nested sheets)                  no part numbers)
                 │                              │
          INTERNAL ONLY                  customer-facing
```

The equation engine is the **only** place Rules/equations live. Everything
downstream — both renderers — just reads already-resolved numbers. This
is what makes the IP boundary structural rather than a policy that could
be forgotten: the manufacturing renderer's code path is never reachable
from anything the browser calls.

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

## Verification, not blind trust, for anything mined from existing drawings

Data extracted from existing DXF files (`extractor/`) is never merged
directly into `library/` as if it were confirmed. See
`KnowledgeCapture.md` for the narration-first methodology and why
existing drawings are a verification set rather than a source.

## Front end (later phases)

The customer-facing web app (Phase 1/4 in `Roadmap.md`) consumes the same
resolved-design JSON via the customer renderer. No dimensioned data, cut
lists, or nested layouts are ever included in what's served to the
browser — this is enforced by the renderer split above, not by filtering
data after the fact.
