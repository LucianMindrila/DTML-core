# Terminology

A glossary of terms as used specifically within DTML. Where a term also
has a general woodworking/CAD meaning, the DTML usage is noted.

**Feature**
A physical constraint in the customer's existing space that the design
must accommodate or avoid: a window, door, socket, radiator, sloped
ceiling, pipe boxing, etc. Represented as a structured obstruction object
(`{type, position, dimensions, clearance_required}`), never as free text.
See `Specifications/FeatureSpecification.md`.

**Part**
An atomic manufacturable component: a single panel, rail, or similar —
with material, thickness, edge-banding spec, and hole/drilling pattern.
The lowest level of the library; Parts are combined into Modules.
See `Specifications/PartSpecification.md`.

**Module** (a.k.a. "Bay type")
A standard assembly built from Parts: a hanging bay, a drawer bank, a
shoe-rake bay, an open shelving bay, etc. Takes bay width/height/depth and
material thickness as inputs, and via Rules produces a concrete cut list
and hardware BOM. This is the unit an AI-vision image gets classified
into. See `Specifications/ModuleSpecification.md`.

**Rule**
An equation or relationship between dimensions, hardware positions, and
material thickness — e.g. "internal width = bay width − (2 × side panel
thickness)". Rules are what make a Module parametric rather than a fixed
preset. See `Specifications/RuleSpecification.md`.

**Style**
The customer-facing finish/aesthetic layer: door style (e.g. "Navarra"),
material/colour (e.g. "Walnut"), handle type, that get applied on top of
a resolved Module without changing its underlying construction logic.
See `Specifications/StyleSpecification.md`.

**Envelope**
The overall available space for a piece of furniture: width × height ×
depth, as constrained by the room and any Features within it.

**KD fitting**
"Knock-down" fitting — a mechanical fixing (e.g. cam + dowel, of the type
identified in the `parts.dxf` extraction as an (8mm, 8mm, 15mm) hole
signature) used to join panels without permanent adhesive, allowing
flat-pack assembly/disassembly.

**Confidence score**
A per-Module classification score produced when matching a region of an
AI-generated vision image to a known Module. Below a defined threshold,
the match is flagged for human/customer confirmation rather than
committed automatically. See `CorePrinciples.md` §3.

**Delta view / Approval view**
The customer-facing side-by-side comparison of their original AI vision
image and DTML's standardised interpretation, with substitutions
explicitly called out. This is the customer approval gate before any
manufacturing output is generated. See `Vision.md`.

**Manufacturing brain**
The combination of the schemas, the populated library, and the rule/
equation engine — everything needed to resolve a classified design into
a concrete, dimensioned, buildable output. See `RFC/RFC-0002-ManufacturingBrain.md`.

**Bay** — see **Module**.
