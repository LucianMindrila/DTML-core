# Core Principles

These are the non-negotiable rules DTML is built against. Anything that
conflicts with one of these needs an RFC and an explicit decision to
override, not a quiet exception.

## 1. Equations drive geometry, not the other way round

Every dimension in the library is either an input (bay width, height,
depth, material thickness) or a formula output (shelf pitch, drawer
count, rail position, hardware BOM). Nothing is a hardcoded preset with
some flex bolted on. This is what makes the CNC handoff trustworthy at
scale — see `Specifications/RuleSpecification.md`.

## 2. Standardise one variable per hardware category, let the rest flex

Rather than shrinking every hardware category to a tiny fixed set, fix
the variable that actually drives compatibility/cost and let the rest
vary:

- **Runners**: fix load class and closing type; vary only depth (a small,
  discrete set of options).
- **Hinges**: fix cup diameter and opening angle; vary only overlay type.
- **Lighting**: fix profile/voltage/driver; vary only cut length (a
  formula output, not a SKU choice at all).

## 3. Classification is confidence-scored, never silently deterministic

Matching an AI-generated image region to a Module (bay type) always
produces a confidence score alongside the match. Below a defined
threshold, the match is flagged for human or customer confirmation before
it's committed to a Bill of Materials. Silent misclassification — not low
confidence itself — is the failure mode to design against.

## 4. Fidelity vs. standardisation conflicts are made visible, never hidden

When an AI vision's specific proportions don't fit the standardised
library, the resolution (snap-to-standard vs. flex-the-equation) is shown
to the customer as an explicit, plain-language substitution note — not
silently absorbed into the output. See `Philosophy.md`.

## 5. Narration-first knowledge capture; existing drawings verify, they don't originate

Construction rules come from an explicit human statement of the rule.
Existing CAD drawings are used afterward to check the rule against real
built examples — never used to infer the rule in the first place. See
`KnowledgeCapture.md`.

## 6. The IP gate sits at the dimensioned-drawing boundary

Customer-facing output stops at a proportional render and a confidence/
delta view. Dimensioned drawings, cut lists with real quantities,
hardware BOMs, and nested sheet layouts are manufacturing-only outputs,
enforced architecturally (separate renderer path), not just by policy.
See `Architecture.md`.

## 7. One schema, two renderers

Every resolved design is a single data structure. A manufacturing
renderer turns it into dimensioned DXF; a customer renderer turns the same
data into a proportional 3D view with no dimensions. They read the same
resolved output — nothing is computed twice, and nothing manufacturing-
grade leaks into the customer path by accident.
