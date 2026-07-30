# DTML — Design-to-Manufacturing Language

**DTML** is an AI-driven manufacturing language that transforms customer
inspiration (an existing-space photo, an AI-generated vision image, and a
set of room constraints) into fully engineered, manufacturable furniture —
using a standardised library of components, engineering rules, and
production knowledge.

DTML is not a rendering tool. Photorealistic visualisation of a customer's
idea is a solved, commoditised problem. DTML exists to solve the harder,
unsolved problem behind it: turning that vision into a **dimensioned,
buildable, CNC-ready production drawing** without silently guessing at
construction details that don't actually exist in an AI-generated image.

## The core idea

1. A customer uploads a photo of their existing space (with constraints —
   windows, doors, sloped ceilings, sockets, radiators) and an AI-generated
   image of their vision, plus the target envelope (width × height × depth).
2. DTML classifies the vision into a set of known **Modules** (bay types —
   hanging, drawer bank, shelving, shoe-rake, etc.), each built from
   standardised **Parts**, governed by **Rules** (the equations relating
   dimensions, hardware, and material thickness to each other), and dressed
   in a chosen **Style** (finish, door style, handle, etc.).
3. Every classification carries a confidence score. Low-confidence matches
   are flagged for human/customer confirmation rather than silently
   resolved.
4. The customer sees a side-by-side **delta view**: their original AI image
   next to the standardised interpretation, with any substitutions called
   out in plain language. This is the approval gate.
5. Only after approval does DTML generate the real manufacturing output —
   dimensioned drawings, cut lists, hardware BOMs, and nested sheet
   layouts — which stay internal to the manufacturer. The customer-facing
   side of the product never receives dimensioned or nest-ready data; see
   [`docs/Architecture.md`](docs/Architecture.md) for why that boundary is
   structural, not just policy.

## Where to start reading

| If you want to understand... | Read... |
|---|---|
| Why this project exists and the philosophy behind it | [`docs/Philosophy.md`](docs/Philosophy.md) |
| The end-state product vision | [`docs/Vision.md`](docs/Vision.md) |
| The non-negotiable design principles | [`docs/CorePrinciples.md`](docs/CorePrinciples.md) |
| What terms like "Module", "Feature", "Bay" mean here | [`docs/Terminology.md`](docs/Terminology.md) |
| The build plan and current phase | [`docs/Roadmap.md`](docs/Roadmap.md) |
| The technical architecture (engine, schema, renderers) | [`docs/Architecture.md`](docs/Architecture.md) |
| How real construction knowledge gets encoded safely | [`docs/KnowledgeCapture.md`](docs/KnowledgeCapture.md) |
| The formal data specifications | [`docs/Specifications/`](docs/Specifications/) |
| Design decisions and their rationale | [`docs/RFC/`](docs/RFC/) |

## Repository layout

```
docs/            Philosophy, vision, specs, and RFCs — read these first
schemas/         YAML schema definitions for every core data type
library/         The actual populated component/rule/style library (data, not docs)
examples/        Worked example projects (wardrobe, media wall, office, dressing room)
extractor/       Tooling to mine real dimensions/hole patterns out of existing DXF drawings
tests/           Verification: equation checks, DXF round-trip diffing
tools/           Supporting scripts and utilities
```

## Status

Early-stage. The manufacturing brain (schemas + library encoding) is the
current focus, ahead of any customer-facing interface. See
[`CHANGELOG.md`](CHANGELOG.md) and [`docs/Roadmap.md`](docs/Roadmap.md).

## License

Proprietary — see [`LICENSE`](LICENSE). This is not an open-source project.
