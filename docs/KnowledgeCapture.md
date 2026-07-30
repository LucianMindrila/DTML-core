# Knowledge Capture

How real construction knowledge gets encoded into the DTML library safely
— i.e. without introducing the same hallucination risk the whole project
exists to engineer out of the customer-facing side.

## Narration-first, verification-second

The correct order is:

1. **A human who knows the real construction method states the rule
   explicitly.** E.g.: "35mm cup hinges, cup centre 21.5mm from the front
   edge, hinge positions 100mm from top and bottom, third hinge centred
   for door heights over 900mm."
2. **The rule is translated directly into the schema** (`schemas/`) — a
   mechanical translation task, not an inference task, and therefore a
   far lower error surface.
3. **Existing drawings are used afterward to verify** — generate output
   from the encoded rule, diff it against a real historical drawing. A
   match confirms the rule. A mismatch is a signal to investigate: either
   the narration missed a condition (e.g. a different rule for narrow
   doors), or the historical job was a one-off deviation — never
   silently resolved by adjusting the rule to fit the one example.

## Why not extract rules directly from existing drawings

A DXF or DWG file only contains geometry — lines, circles, arcs,
coordinates — with no semantic labels attached. A hole at a given
position and diameter doesn't say what it's for, or whether it reflects a
deliberate rule versus an accidental one-off. Inferring the rule from the
geometry alone stacks inference on inference. That's not a safe way to
generate anything that ends up near a CNC.

This was tested directly against this project's own real drawing library
(`PARTS.dwg`, `modules.dwg`, `order_form.dwg` → later exported as PDF and
DXF). Findings:

- The available DXFs (R12/`AC1009`) contain only `LINE`, `ARC`, and
  `CIRCLE` entities — no `TEXT`, `MTEXT`, `DIMENSION`, or named `BLOCK`
  entities survive. All labels and dimension callouts were exploded to
  raw line geometry at some point, with no recoverable semantic metadata.
- What *is* reliably extractable: real hole positions and diameters
  (via `CIRCLE` entities), which is genuine, exact, low-risk numeric data
  — no OCR or visual guessing involved. See `extractor/README.md`.
- What is **not** reliably extractable: which part a hole cluster belongs
  to, or what the fixing is actually called — there is no label data to
  recover this from. This must come from human confirmation.

## The practical workflow this produces

1. Run the extractor (`extractor/`) against existing DXF/DWG-derived
   files to produce a numeric inventory: hole positions, diameters,
   spacing/pitch per spatial cluster.
2. A human with real production knowledge confirms what each distinct
   diameter/spacing signature actually is (e.g. "the (8mm, 8mm, 15mm)
   cluster is our standard KD cam+dowel fitting").
3. That confirmed identity, plus the narrated rule behind it (positions
   relative to panel edges, conditions under which it varies), gets
   encoded into `schemas/` and `library/`.
4. The encoded rule is used to regenerate the relevant drawing and
   diffed against the original as a sanity check.

## What this means for AI-assisted encoding generally

Any AI system (including this one, working on this repository) must not
treat pattern-matching against known industry standards as confirmation.
Flagging "this looks like a standard Minifix cam+dowel pattern" is a
hypothesis for a human to confirm, not a fact to encode directly — see
the unresolved patterns noted in `Roadmap.md` as a live example of this
distinction being maintained in practice.
