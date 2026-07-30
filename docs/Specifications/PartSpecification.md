# Part Specification (Draft v0.1)

A **Part** is the atomic manufacturable unit in DTML: a single panel,
rail, or similar component, with everything needed to cut, edge-band, and
drill it.

## Shape

```yaml
part:
  id: string
  name: string                    # human-readable, e.g. "wardrobe side panel"
  material: string                # references materials library, see
                                   # ../../schemas/material.schema.yaml
  thickness: float                # mm
  dimensions:
    width: float                  # mm, may be a Rule output rather than fixed
    height: float
  edge_banding:
    - edge: enum                  # top | bottom | left | right
      applied: bool
      material: string            # may differ from face material
  holes:
    - type: string                # references hardware library, e.g. "shelf_pin"
      diameter: float              # mm
      position:
        x: float                  # mm, relative to part origin (bottom-left)
        y: float
      depth: float                 # mm, blind vs through
  grooves: []                     # structure TBD — see open questions
  source_confidence: enum          # confirmed | extracted_unconfirmed
```

## `source_confidence` — mandatory field, not decoration

Every Part must declare whether it came from a narrated, human-confirmed
rule (`confirmed`) or was produced by the extractor tooling against real
DXF geometry without a human having confirmed its identity yet
(`extracted_unconfirmed`). Nothing with `extracted_unconfirmed` may be
referenced by a production Module. See `../KnowledgeCapture.md`.

## Hole patterns and the extraction findings

The initial Part hole-pattern data for this library is being populated
against the findings in `../../extractor/README.md`, specifically:

- A repeating `(8mm, 8mm, 15mm)` diameter cluster — high-confidence match
  to a standard KD cam+dowel fitting, but still needs a named entry in
  `../../schemas/hardware.schema.yaml` before being referenced here.
- A `(2mm, 4mm, 11mm)` cluster, the most common 3-hole signature found —
  identity not yet confirmed. **Do not encode a Part referencing this
  pattern until confirmed.**
- Full-height 5mm hole rows at a measured ~70.7mm pitch — tentatively
  shelf-pin holes, but the pitch doesn't match the standard 32mm system.
  Needs confirmation of intended pitch before encoding as a Rule.

## Open questions

- Groove representation (for panel-to-panel slot joints) — not yet
  modelled; needs a proposal before Parts with grooves can be encoded.
- Whether `dimensions` should always be Rule references (per
  `../CorePrinciples.md` §1) or may be a fixed literal for genuinely
  non-parametric Parts (e.g. a fixed decorative end panel).

See `../../schemas/part.schema.yaml` for the machine-readable schema.
