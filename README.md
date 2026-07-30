# DTML Core

> **Design-to-Manufacture Language**
>
> A manufacturing language that translates customer imagination into engineered, manufacturable furniture.

"From imagination to manufacture."

DTML is an open engineering specification for translating human design intent into manufacturable furniture.

It captures the knowledge that traditionally lives in the heads of experienced furniture makers and makes it available as a structured, reusable manufacturing language.

---

## Vision

Artificial Intelligence has transformed the way people imagine furniture.

Customers can now generate beautiful wardrobes, home offices, media walls and dressing rooms in seconds.

Unfortunately those images rarely consider:

- manufacturing methods
- available materials
- hardware limitations
- structural integrity
- machining constraints
- installation requirements

DTML exists to bridge this gap.

Rather than asking customers to learn CAD software, DTML allows them to communicate in the language they already understand:

**Images.**

The Manufacturing Brain then translates those images into real, manufacturable furniture using engineering knowledge captured from years of practical experience.

---

## The Problem

Today's workflow is fragmented.

```
Customer Idea
      │
      ▼
 AI Generated Image
      │
      ▼
 Interior Designer
      │
      ▼
 CAD Drawing
      │
      ▼
 Manufacturing Drawing
      │
      ▼
 CNC Programming
      │
      ▼
 Production
```

Every stage recreates information that already exists.

Each translation introduces time, cost and the possibility of human error.

---

## Our Vision

DTML creates a single source of truth.

```
Customer Inspiration
        │
        ▼
   Manufacturing Brain
        │
 ┌──────┼─────────────┐
 │      │             │
 ▼      ▼             ▼
Render  Quote      Production
                   Drawings
                        │
                        ▼
                     CNC Output
```

The customer speaks in inspiration.

The factory speaks in manufacturing.

DTML translates between them.

---

## What is DTML?

DTML is not CAD.

DTML is not CAM.

DTML is not a rendering engine.

DTML is a manufacturing language.

It describes:

- engineering intent
- furniture structure
- manufacturing knowledge
- construction rules
- hardware relationships
- machining features

Every output is generated from this knowledge.

---

## Design Philosophy

The Manufacturing Brain is the only source of truth.

Everything else is generated.

- Drawings
- Renders
- Quotations
- CNC Programs
- Installation Instructions

No output should ever become the master.

---

## Core Concepts

DTML describes furniture using a hierarchy.

```
Intent

↓

Function

↓

Furniture

↓

Modules

↓

Parts

↓

Features

↓

Operations

↓

Machine Instructions
```

Each layer adds engineering knowledge without losing the customer's original design intent.

---

## Why DTML?

Traditional CAD systems ask:

> How should this furniture be drawn?

DTML asks:

> How should this furniture be manufactured?

That distinction changes everything.

---

## Long-Term Goals

The project aims to create a platform where customers can:

- Upload photographs of their room
- Upload AI-generated inspiration
- Define dimensions and constraints
- Receive an engineered proposal
- Approve the design
- Automatically generate manufacturing data

without requiring the design to be recreated manually.

---

## Project Status

Current Version

```
v0.1.0
```

Current Focus

> Defining the DTML language and Manufacturing Brain.

Software implementation will begin only after the language has been formally specified.

---

## Repository Structure

```
docs/
    Vision
    Philosophy
    Architecture
    Specifications

library/
    Features
    Parts
    Modules
    Hardware
    Rules
    Styles

schemas/
    Formal DTML object definitions

examples/
    Example furniture projects

extractor/
    Legacy DXF knowledge capture

```

---

## Guiding Principle

> **The customer's vision is the source of truth for appearance.**
>
> **The Manufacturing Brain is the source of truth for construction.**

DTML exists to connect those two worlds.

---

© CuttingEdgeBespoke.
