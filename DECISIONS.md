# Decisions Log

A running log of significant architectural decisions made in this project — what changed, why, and what alternatives were considered. For proposals still under discussion, see `docs/RFC/`; once a decision is made, it gets an entry here.

---

## 2026-07-30 — Renamed "Feature" (room obstruction) to "Obstruction"

**What changed:** The term "Feature" previously meant a physical constraint
in the customer's room (window, door, socket, radiator, sloped ceiling —
see `schemas/feature.schema.yaml` and `FeatureSpecification.md`). It has
been renamed to **Obstruction** throughout the schemas, specs, and library
(`schemas/obstruction.schema.yaml`, `ObstructionSpecification.md`,
`library/obstructions/`).

**Why:** The updated `docs/Terminology.md` and `README.md` define
"Feature" as a machining element applied to a Part (hole, slot, pocket,
groove, chamfer, edge band) — the term needed for the
Part → Feature → Operation hierarchy. The two meanings collided, so the
room-obstruction concept was renamed rather than the newer, more central
manufacturing-hierarchy term.

**Alternatives considered:** Keep "Feature" for room obstructions and
invent a new term (e.g. "Machining Feature") for the Part-level concept —
rejected because the Part → Feature → Operation hierarchy is the more
fundamental, frequently-referenced concept going forward.
