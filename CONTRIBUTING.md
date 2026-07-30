# Contributing to DTML

This is a private, proprietary repository. "Contributing" here means
internal collaborators (Cutting Edge Bespoke team, contracted
developers) adding to the manufacturing brain, schemas, or tooling.

## The one rule that matters most: narration-first, not inference-first

DTML's core risk is silent hallucination of construction rules — a wrong
hinge offset or shelf-pin pitch doesn't fail loudly, it fails as a
customer-approved drawing that doesn't match reality. Because of that:

- **Construction rules (hole positions, joinery equations, KD fitting
  specs) must come from an explicit, human-stated rule**, not be inferred
  from a single example drawing or an AI's best guess at pattern-matching.
- **Existing CAD drawings are a verification set, not a source.** Use them
  to check a rule you've already encoded from a narrated spec — if the
  generated output doesn't match the real drawing, that's a signal to
  investigate, not a reason to silently adjust the rule to fit.
- Any extracted geometry (see `extractor/`) that isn't explicitly
  labelled/confirmed by a human must be marked as unconfirmed in the data
  itself — never merged into `library/` as if it were verified.

See `docs/KnowledgeCapture.md` for the full reasoning.

## Adding to the library

1. Confirm the rule/part/module against real production knowledge first
   (narrated by someone who actually knows the construction method).
2. Write it against the relevant schema in `schemas/`.
3. Add it under the correct `library/` subfolder.
4. If it changes or extends an existing schema, open an RFC in `docs/RFC/`
   before merging — schema changes ripple through every consumer
   (manufacturing renderer, customer renderer, nesting).
5. Add a verification case under `tests/` where practical (e.g. diff the
   generated DXF against a real reference drawing).

## Proposing architecture or schema changes

Open an RFC under `docs/RFC/` following the numbering convention
(`RFC-000N-Title.md`). Reference `RFC-0001-DTML.md` for the expected
structure (context, proposal, alternatives considered, open questions).

## Style

- Schemas: YAML, one file per data type, versioned.
- Docs: Markdown, one concern per file — don't let `Architecture.md`
  absorb content that belongs in a spec or RFC.
- Code: Python for the engine and tooling (see `docs/Architecture.md` for
  why), type-hinted where practical.
