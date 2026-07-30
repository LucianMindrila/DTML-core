# DTML Architecture

## Purpose
This document is the **normative**, implementation-independent architecture for DTML Core.

## Scope
It defines:
- logical architecture
- trust boundaries
- canonical objects
- processing pipeline
- conformance

Implementation details belong in `ReferenceImplementation.md`.

## System Overview
Customer World
→ Translation Layer
→ DTML Core
→ Resolved Design
→ Two Trust Paths

### Customer Trust Path
- proposals
- renders
- finishes
- overall dimensions
- approval views

### Protected Manufacturing Trust Path
Contains two output profiles:
- Engineering Representation
- Manufacturing Representation

Both derive from the same Resolved Design.

## Canonical Model
The Resolved Design is the authoritative project instance.

No renderer may add engineering logic.

## Manufacturing Brain
Versioned libraries:
- Materials
- Hardware
- Features
- Parts
- Modules
- Furniture
- Styles
- Rules
- Capability Profiles

## IP Boundary
Manufacturing dimensions, equations, feature locations, cut lists and CNC outputs remain inside the protected trust path.

Relaxation requires an accepted RFC.

## Knowledge Capture
Explicit narration is authoritative.
Legacy DXFs provide evidence only.

## Determinism
After interpretation is approved, identical inputs and versions must produce identical resolved designs.

## Technology Independence
DTML semantics are independent of implementation technology.
This does not determine licensing or commercial openness.

## Conformance
CorePrinciples.md governs this document.
