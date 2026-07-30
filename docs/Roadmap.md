# Roadmap

Phased build plan. Each phase should be validated before significant
investment in the next — the manufacturing brain (Phases 1–2) is
deliberately sequenced ahead of anything customer-facing.

## Phase 0 — Define the moat (in progress)

Decide, on paper, exactly what stays behind the paywall before writing
product code — this shapes every downstream decision (e.g. if the nested
DXF is the protected asset, customer-facing output must never carry real
dimensions). See `Vision.md` and `Architecture.md`.

## Phase 1 — MVP intake flow

Simple web upload: existing-space photos + AI vision image + manually
entered constraints (envelope, door/window positions typed in — not
scanned yet). A human maps the image to Modules manually at this stage,
to validate the concept before any classifier is built.

## Phase 2 — Parametric Module library v1

Build 6–10 Module types (hanging, drawer bank, shoe-rake, open shelf,
etc.) as coded equation modules per `Specifications/ModuleSpecification.md`
and `Specifications/RuleSpecification.md`. Validate against real historical
jobs before any AI matching is introduced. **Current focus.**

## Phase 3 — AI-to-Module classifier

Vision model segments an uploaded AI image into regions, assigns each a
Module type + confidence score. Start human-in-the-loop (AI proposes, a
person confirms) before attempting full automation — de-risks the
highest-uncertainty part of the whole project.

## Phase 4 — The approval/delta view

The customer-facing centrepiece: AI image vs. standardised interpretation,
substitutions flagged in plain language, confidence badges per Module.
Also the natural pricing and IP gate (see `Vision.md`).

## Phase 5 — Nesting/CNC handoff

Wire confirmed BOM into nesting logic. Output: sheet layouts, cut lists,
CNC files — internal only, never customer-facing.

## Phase 6 — Commercial launch

Start with DT Solutions / Cutting Edge as the only fulfilment path, prove
unit economics, then decide whether to license the front-end tool to
other manufacturers.

## Immediately actionable, in parallel with Phase 2

- Populate `schemas/` and `library/` using the narration-first
  methodology (`KnowledgeCapture.md`) — starting with the joinery rules
  found in the `parts.dxf` hole-cluster extraction (see `extractor/`).
- Confirm the unresolved patterns flagged during extraction (the
  `(2.0, 4.0, 11.0)mm` hole signature, the ~70.7mm shelf-pin pitch, and
  the scarcity of true 35mm hinge-cup clusters) against real production
  knowledge before encoding any Rule that depends on them.
