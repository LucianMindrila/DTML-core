# Feature Specification (Draft v0.1)

A **Feature** is a structured representation of a physical constraint in
the customer's existing space — never free text, never inferred silently
from a photo without being resolved into this structure first.

## Why structured, not free text

The whole point of capturing constraints is so Module placement and Rule
resolution can query against them programmatically. If a window or socket
stays as an unstructured photo/scan annotation, the ambiguity problem just
moves one step down the pipeline instead of being solved. See
`../CorePrinciples.md` and `../Philosophy.md`.

## Shape

```yaml
feature:
  id: string                     # unique within the project
  type: enum                     # window | door | socket | radiator |
                                  # sloped_ceiling | pipe_boxing | other
  position:
    x: float                     # mm, relative to room origin
    y: float
    z: float
  dimensions:
    width: float                 # mm
    height: float
    depth: float                 # 0 for flush features like sockets
  clearance_required: float      # mm of mandatory clearance around the feature
  notes: string                  # optional, human-readable, non-authoritative
```

## Type-specific notes

- **window / door**: `clearance_required` typically covers door swing or
  opening sash, not just the frame.
- **socket**: `depth` is typically 0 (flush-mount) unless a surface-mount
  unit; `clearance_required` should reflect any accessibility requirement
  (e.g. must remain reachable), not just physical fit.
- **sloped_ceiling**: represented as a constraint on `height` that varies
  by `x`/`y` position rather than a single fixed value — the exact
  parametrisation for this is still open; see `../RFC/` for a proposal
  before implementing.
- **radiator / pipe_boxing**: typically drives a cut-out or notch in a
  Part rather than a placement exclusion zone — this interaction with
  `PartSpecification.md` needs an explicit Rule, not an implicit one.

## Confidence and confirmation

Unlike Module classification, Features derived from a scan/photo (rather
than manually entered) should also carry a confidence score and be
subject to the same "flag below threshold" principle in
`../CorePrinciples.md` §3 — a missed socket or misjudged sloped-ceiling
angle is exactly the kind of silent error this project is designed to
avoid.

## Open questions

- Exact schema for sloped ceilings and other non-rectilinear constraints.
- Whether Features should be versioned per-project or reusable across a
  customer's multiple projects (e.g. a repeat customer's room shape).

See `../../schemas/feature.schema.yaml` for the machine-readable schema
once finalised (currently a draft stub).
