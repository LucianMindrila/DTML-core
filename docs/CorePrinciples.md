# DTML Core Principles

This document has two parts: the guiding principles (the philosophy DTML
is built on) and the technical principles (the specific, numbered
engineering rules referenced by section throughout the schemas and specs
— e.g. `CorePrinciples.md §2`). The technical principles are the
non-negotiable rules; anything that conflicts with one of them needs an
RFC and an explicit decision to override, not a quiet exception.

---

## Guiding Principles

### Principle 1 — The Manufacturing Brain is the Source of Truth

All representations are generated from manufacturing knowledge.

Geometry is never authoritative.

### Principle 2 — Knowledge Must Be Explicit

Engineering decisions should be recorded intentionally.

DTML prefers explicit knowledge over inferred assumptions.

### Principle 3 — Geometry is an Output

Drawings, renders, CNC programs and quotations are generated artefacts.

Knowledge is permanent.

Representations are disposable.

### Principle 4 — Every Decision Must Be Explainable

Every engineering decision should be traceable to:

- a rule
- a constraint
- a requirement
- or a human decision

The system must never produce unexplained behaviour.

### Principle 5 — Human Expertise Remains Authoritative

Automation accelerates engineering.

It does not replace engineering judgement.

Whenever confidence is insufficient, human expertise takes precedence.

### Principle 6 — Manufacturing Before Appearance

Visual intent should be preserved whenever possible.

Manufacturability is mandatory.

### Principle 7 — Standardisation Enables Creativity

Customers should experience unlimited design freedom.

Manufacturing should rely on a controlled set of proven engineering methods.

### Principle 8 — Everything is Parametric

Every object exists as relationships rather than fixed dimensions.

Changing one value should propagate consistently throughout the model.

### Principle 9 — Reuse Before Reinvention

Features form Parts.

Parts form Modules.

Modules form Furniture.

Knowledge should be reused wherever possible.

### Principle 10 — The System Must Learn

Every validated engineering decision strengthens the Manufacturing Brain.

Knowledge accumulates over time.

### Principle 11 — Confidence Determines Automation

High confidence permits automation.

Low confidence requires review.

DTML should never hide uncertainty.

### Principle 12 — Open by Design

The specification should remain implementation-independent.

Any compliant software should be capable of reading and writing DTML.

---

## Technical Principles

These are cited elsewhere as `CorePrinciples.md §N` — the numbering is
load-bearing (schemas, specs, and RFCs reference these sections directly)
and must not be renumbered without updating every citing file.

### 1. Equations drive geometry, not the other way round

Every dimension in the library is either an input (bay width, height,
depth, material thickness) or a formula output (shelf pitch, drawer
count, rail position, hardware BOM). Nothing is a hardcoded preset with
some flex bolted on. This is what makes the CNC handoff trustworthy at
scale — see `Specifications/RuleSpecification.md`.

### 2. Standardise one variable per hardware category, let the rest flex

Rather than shrinking every hardware category to a tiny fixed set, fix
the variable that actually drives compatibility/cost and let the rest
vary:

- **Runners**: fix load class and closing type; vary only depth (a small,
  discrete set of options).
- **Hinges**: fix cup diameter and opening angle; vary only overlay type.
- **Lighting**: fix profile/voltage/driver; vary only cut length (a
  formula output, not a SKU choice at all).

### 3. Classification is confidence-scored, never silently deterministic

Matching an AI-generated image region to a Module (bay type) always
produces a confidence score alongside the match. Below a defined
threshold, the match is flagged for human or customer confirmation before
it's committed to a Bill of Materials. Silent misclassification — not low
confidence itself — is the failure mode to design against.

### 4. Fidelity vs. standardisation conflicts are made visible, never hidden

When an AI vision's specific proportions don't fit the standardised
library, the resolution (snap-to-standard vs. flex-the-equation) is shown
to the customer as an explicit, plain-language substitution note — not
silently absorbed into the output. See `Philosophy.md`.

### 5. Narration-first knowledge capture; existing drawings verify, they don't originate

Construction rules come from an explicit human statement of the rule.
Existing CAD drawings are used afterward to check the rule against real
built examples — never used to infer the rule in the first place. See
`KnowledgeCapture.md`.

### 6. The IP gate sits at the dimensioned-drawing boundary

Customer-facing output stops at a proportional render and a confidence/
delta view. Dimensioned drawings, cut lists with real quantities,
hardware BOMs, and nested sheet layouts are manufacturing-only outputs,
enforced architecturally (separate renderer path), not just by policy.
See `Architecture.md`.

### 7. One schema, two renderers

Every resolved design is a single data structure. A manufacturing
renderer turns it into dimensioned DXF; a customer renderer turns the same
data into a proportional 3D view with no dimensions. They read the same
resolved output — nothing is computed twice, and nothing manufacturing-
grade leaks into the customer path by accident.
