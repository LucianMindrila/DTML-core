# DTML Specification v0.1 (Draft)

This is the umbrella specification tying together the five core data
types that make up the DTML manufacturing brain. Each type has its own
detailed specification file in this directory; this document defines how
they relate to each other and the overall resolution flow.

## Status

Draft. Versioned independently from the software implementation — schema
changes that break backward compatibility require a new spec version and
an RFC (see `../RFC/`).

## The five core data types

| Type | Spec | Role |
|---|---|---|
| **Obstruction** | `ObstructionSpecification.md` | A physical constraint in the customer's existing space (window, door, socket, radiator, sloped ceiling). Input only — never generated. |
| **Part** | `PartSpecification.md` | An atomic manufacturable component — panel, rail, etc. — with material, thickness, edge-banding, and hole pattern. |
| **Module** | `ModuleSpecification.md` | A standard assembly ("bay type") built from Parts, taking dimensional inputs and producing a concrete cut list + hardware BOM via Rules. |
| **Rule** | `RuleSpecification.md` | An equation/relationship between dimensions, hardware positions, and material thickness. Rules are what make a Module parametric. |
| **Style** | `StyleSpecification.md` | The customer-facing finish/aesthetic layer (door style, material, handle) applied on top of a resolved Module. |

## Resolution flow

```
Input:  Envelope (W×H×D) + Obstructions + Vision image
        │
        ▼
Classification: vision image regions → Module type + confidence score
        │
        ▼
Resolution: Module.equations(inputs) → concrete Parts list + hardware BOM
        │        (Rules referenced by the Module are evaluated here)
        ▼
Styling: Style applied → finish/door/handle overlay on resolved Parts
        │
        ▼
Output: single resolved design object (see below) — consumed by both the
        manufacturing renderer (dimensioned DXF, cut lists, nesting) and
        the customer renderer (proportional 3D view, no dimensions)
```

## Resolved design object (conceptual shape)

```yaml
project_id: string
envelope: {width, height, depth}
obstructions: [Obstruction, ...]
modules:
  - module_type: string
    confidence: float           # 0.0-1.0, from classification
    inputs: {bay_width, bay_height, bay_depth, ...}
    resolved_parts: [Part, ...] # concrete, dimensioned
    hardware_bom: [HardwareItem, ...]
    style: Style
    substitutions: [string]     # plain-language notes for the delta view
```

See `../Architecture.md` for how this object flows through the two
renderers, and `../schemas/` for the authoritative YAML schema of each
referenced type.

## Versioning

- `v0.1`: current draft, covers the five core types above at the level
  needed for Phase 2 of `../Roadmap.md` (parametric Module library).
- Future versions will need to formalise `room.schema.yaml`,
  `project.schema.yaml`, and `furniture.schema.yaml` (see `../schemas/`)
  once multi-Module projects and full-room composition are in scope.
