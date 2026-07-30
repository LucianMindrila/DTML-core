# RFC-0002: The Manufacturing Brain Architecture

**Status:** Accepted, implementation in progress (Phase 2, `../Roadmap.md`)

## Context

The manufacturing brain — the combination of schemas, populated library,
and rule/equation engine — needs to serve two very different consumers
from a single source of truth: an internal manufacturing pipeline
(dimensioned DXF, cut lists, nested sheets) and an eventual customer-
facing web product (proportional 3D renders, no dimensions). It also
needs to be buildable incrementally against real Cutting Edge production
knowledge scattered across existing DWG/DXF drawings and order forms.

## Proposal

1. **Single schema, two renderers.** See `../Architecture.md`. One
   resolved-design data structure; a manufacturing renderer (ezdxf) and a
   customer renderer (Three.js) both read it, never compute independently.
2. **Python as the implementation language**, for the reasons in
   `../Architecture.md` (panel+hole-pattern domain model, not general
   solid modeling; existing team fluency; `ezdxf` gives both read and
   write DXF access).
3. **YAML as the library storage format**, version-controlled like code,
   one file per Module/Rule/Style/hardware-standard entry.
4. **Equations as the only source of derived dimensions** — see
   `../CorePrinciples.md` §1. No Part or Module may hardcode a value a
   Rule could compute.
5. **The IP boundary is structural**: the manufacturing renderer's code
   path must be architecturally unreachable from the customer-facing
   application, not merely excluded by a data filter that could be
   forgotten or bypassed.

## Alternatives considered

- **A general CAD kernel (CadQuery, FreeCAD, OpenSCAD).** Rejected —
  over-solves a domain that mature industry tools already model as
  panels + hole patterns, not B-rep solids.
- **JSON instead of YAML for the library.** Not rejected on technical
  grounds, but YAML was chosen for human-editability and comment support,
  which matters heavily during the narration-first encoding process
  (`RFC-0003`) where a human is directly authoring these files.
- **A single renderer that customers see a redacted version of.** Rejected
  — a data-filtering approach is a policy, not a structural guarantee,
  and this project's whole premise is not trusting policy alone to hold
  under commercial pressure (a rushed feature, a well-meaning but
  careless integration, etc.).

## Open questions

- Formal expression language/parser for Rule `expression` fields — see
  `../Specifications/RuleSpecification.md` open questions.
- Multi-Module composition (shared panels between adjoining bays) — not
  yet specified; likely needs its own RFC once Phase 2's single-Module
  library is validated.
