# RFC-0003: Knowledge Capture Methodology

**Status:** Accepted, in active use (see `extractor/` for the resulting
tooling)

## Context

DTML's library needs to be populated from decades of real Cutting Edge
Bespoke production knowledge, currently scattered across DWG/DXF
drawings (`PARTS.dwg`, `modules.dwg`, `order_form.dwg` and their DXF/PDF
exports) with no consistent digital structure. The obvious approach —
point an AI directly at these drawings and have it infer construction
rules — was considered and specifically rejected. See
`../KnowledgeCapture.md` for the full reasoning; this RFC records the
decision and the alternatives considered.

## Proposal

**Narration-first, verification-second**, as detailed in
`../KnowledgeCapture.md`:

1. A human states the construction rule explicitly.
2. The rule is translated mechanically into the schema (low error
   surface — translation, not inference).
3. Existing drawings are used afterward as a verification set — diffing
   generated output against real historical drawings — never as the
   original source of the rule.

Supporting tooling (`extractor/`) mines existing DXF files for real,
exact numeric geometry (hole positions, diameters, spacing) that a human
can then confirm the identity of — this is a legitimate and reliable
extraction (it's just reading coordinates), clearly distinguished from
the rejected approach of inferring semantic meaning from that geometry
automatically.

## Evidence this distinction matters in practice

Direct investigation of this project's own DWG/DXF library found:

- No `TEXT`/`MTEXT`/`DIMENSION`/named-`BLOCK` entities survive in the
  available DXF exports — all labels were exploded to raw line geometry
  at some point. There is no semantic metadata to recover, confirming
  that any "extraction" of meaning (not just geometry) would necessarily
  be inference, not reading.
- Pattern-matching circle diameters against known industry hardware
  standards produced both a high-confidence hit (an (8mm, 8mm, 15mm)
  cluster matching a standard KD cam+dowel fitting almost exactly) and a
  clearly unconfident result (a (2mm, 4mm, 11mm) cluster — the single
  most common 3-hole signature in the library — with no confident
  match). Treating both with equal confidence would have been exactly
  the silent-hallucination failure mode this methodology exists to avoid.
- A tentative "shelf-pin" pattern's measured pitch (~70.7mm) didn't match
  the assumed standard (32mm system), which surfaced a real discrepancy
  needing human confirmation rather than being silently reconciled.

## Alternatives considered

- **Direct DWG parsing via a from-source LibreDWG build**, attempted
  first. Technically promising (DWG contains the same entity types as
  DXF) but impractical in this environment (long, fragile source build)
  and doesn't change the underlying finding — DWG/DXF here carry no
  semantic text regardless of parser.
- **OCR against rasterized PDF exports of the drawings.** Tested and
  found unreliable — the drawings use CAD stroke-font (SHX) text
  rendered as thin open outlines, which standard OCR engines (tested:
  Tesseract) cannot recognise as characters at any resolution tested.
- **Trusting AI pattern-matches against known hardware standards as
  confirmed data.** Rejected — see evidence above. Pattern-matches are
  surfaced as hypotheses for human confirmation, never written into
  `library/` as confirmed.

## Consequence for contributors

See `CONTRIBUTING.md` at the repo root: this is now a binding project
convention, not just documented reasoning.
