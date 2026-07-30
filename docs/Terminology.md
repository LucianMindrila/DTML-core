# DTML Terminology

## Customer

The individual or organisation requesting a manufactured product.

---

## Space

The physical environment into which furniture will be installed.

Includes dimensions, obstacles, services and installation constraints.

---

## Obstruction

A physical constraint in the customer's existing space that a design must accommodate or avoid: a window, door, socket, radiator, sloped ceiling, pipe boxing, etc.

Represented as a structured object (`{type, position, dimensions, clearance_required}`), never as free text.

See `Specifications/ObstructionSpecification.md`.

---

## Requirement

A measurable need that must be satisfied.

Examples include dimensions, storage capacity, accessibility or budget.

---

## Constraint

A limitation that restricts possible solutions.

Examples include ceiling height, material availability, transport limitations or machine capabilities.

---

## Intent

The desired outcome expressed by the customer.

Intent describes *what the customer wishes to achieve*, not *how it should be engineered*.

---

## Function

The purpose performed by a furniture element.

Examples include:

- Storage
- Display
- Seating
- Support
- Hanging
- Lighting

---

## Furniture

A complete manufacturable product composed of one or more modules.

---

## Module

An independently manufacturable section of furniture.

Modules may be combined to form larger assemblies.

---

## Part

A single manufactured component.

A Part may contain multiple Features.

---

## Feature

An individual manufacturing element applied to a Part.

Examples include:

- Hole
- Slot
- Pocket
- Groove
- Chamfer
- Edge Band

---

## Operation

A manufacturing process performed to create one or more Features.

Examples include:

- Drilling
- Routing
- Cutting
- Edgebanding
- Assembly

---

## Rule

An engineering statement describing how decisions should be made.

Rules may depend on constraints, requirements or other rules.

---

## Library

A reusable collection of engineering knowledge.

Libraries may contain Features, Parts, Modules, Materials, Hardware or Rules.

---

## Manufacturing Brain

The complete collection of structured engineering knowledge used by DTML.

The Manufacturing Brain is the authoritative source from which all outputs are generated.

---

## Representation

Any generated view of the Manufacturing Brain.

Examples include:

- Drawings
- Renders
- Quotations
- CNC Programs
- Installation Instructions

Representations are outputs, not authoritative data.

---

## Confidence

A quantified measure of certainty associated with an engineering decision.

Confidence determines whether a decision may be automated or requires human review.

---

## Knowledge Capture

The process of converting manufacturing expertise into structured DTML objects.

Knowledge may originate from experienced engineers, legacy documentation or validated manufacturing processes.
