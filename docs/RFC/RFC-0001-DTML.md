# RFC-0001: DTML — Founding Proposal

**Status:** Accepted (foundational — supersedes nothing, everything else
builds on this)

## Context

AI image generation now lets any customer produce a photorealistic vision
of their desired furniture without a professional designer. This removes
one bottleneck (imaginative visualisation) but exposes another, previously
hidden one: the gap between "a picture of something that looks like
furniture" and "a dimensioned, buildable, CNC-ready production drawing."
No existing product closes this specific gap — see the market research
summarised below.

Existing players fall into three camps, none of which solve the problem:

1. **Consumer AI visualisation tools** (Freedom Kitchens, Armox AI) —
   render a vision, then explicitly hand off to a human designer/installer
   for measurement and construction. No manufacturing link.
2. **Mature CAD/CAM suites** (imos iX, Cyncly/2020/Mozaik/PolyBoard,
   Cabinet Vision) — full parametric design → nesting → CNC pipelines
   already exist and are mature, but built around skilled human design
   input or catalogue-matching against manufacturer parts, not free-form
   bespoke carcass generation from an arbitrary AI image.
3. **AI-native concepting tools** (Prompt2CAD) — closest analog, explicitly
   positions itself as a concepting layer only, handing off to a
   production suite for the real manufacturing pass. Openly acknowledges
   the gap between "looks like an object" and "is manufacturable."

## Proposal

Build DTML: a standardised library of Parts, Modules, Rules, and Styles,
plus a classification layer that maps an AI-generated vision image onto
that library with confidence scoring, plus a customer-facing approval
view that makes any standardisation/fidelity tradeoff explicit rather
than hidden. See `../Vision.md` and `../Philosophy.md` for full detail.

## Alternatives considered

- **Fully automated vision-to-CAD with no human confirmation loop.**
  Rejected — the classification and knowledge-capture problems are both
  high-hallucination-risk; a human-in-the-loop confirmation step is
  required at both the library-encoding stage and (initially) the
  customer classification stage. See `RFC-0003-KnowledgeCapture.md`.
- **License an existing CAD/CAM suite's AI layer (e.g. Cyncly AI) rather
  than build the classifier in-house.** Not rejected outright — worth
  revisiting once the Module library (Phase 2) is mature — but existing
  offerings match against manufacturer catalogue parts, not a bespoke,
  narration-verified library, so they don't yet solve the specific
  problem DTML targets.
- **General-purpose CAD kernel (CadQuery/FreeCAD) instead of a
  panel+hole-pattern data model.** Rejected — over-solves the problem;
  see `../Architecture.md`.

## Open questions

- Long-term: does DTML stay internal to DT Solutions/Cutting Edge, or
  become a licensable front-end for other manufacturers? Deferred to
  Phase 6 (`../Roadmap.md`).
