# Vision

## The end product

A website where a customer can, in an intuitive, mobile-first flow:

1. **Upload photos/scan of their existing space** — capturing constraints:
   windows, doors, sloped ceilings, sockets, radiators, and any other
   physical obstruction relevant to the build.
2. **Specify the target envelope** — width × height × depth of the
   available space for the piece.
3. **Upload an AI-generated (or any inspiration) image** of their desired
   furniture.

DTML then:

4. Classifies the vision image into a set of known Modules (bay types),
   each with a confidence score.
5. Resolves every Module's equations against the real envelope and
   constraints to produce a standardised interpretation.
6. Presents an **approval view**: the customer's original image side by
   side with the standardised render, with any substitutions/adaptations
   called out in plain language, and confidence badges per bay.
7. On approval (backed by a refundable design deposit — see
   `Philosophy.md` and the IP notes below), generates the real
   manufacturing package internally: dimensioned drawings, cut lists,
   hardware BOMs, and nested sheet layouts ready for CNC.

## What the customer never sees

Dimensioned production drawings, cut lists with real quantities, hardware
part numbers, or nested sheet layouts are never exposed through the
customer-facing product, at any tier. This is both a commercial boundary
(the design is the sales tool; the manufacturing package is what's sold
as part of the order) and, per `Architecture.md`, a structural one — the
manufacturing renderer is architecturally separate from anything the
browser can call.

## What "done" looks like, directionally

- A manufacturer (starting with Cutting Edge Bespoke) can take a
  customer's two photos and constraints, and within minutes produce an
  approval-ready standardised design with an honest confidence/delta view
  — without a human designer manually re-drawing the vision from scratch.
- The manufacturing brain (library + rules) is populated deeply enough
  that most common wardrobe/media-wall/office/dressing-room requests
  resolve with high classifier confidence.
- The system's dimensioned output is trustworthy enough to nest and cut
  directly, with no manual re-checking of every job.

## What DTML is deliberately not trying to be

- Not a general-purpose AI image generator or interior design tool — the
  vision image is an input, not something DTML produces.
- Not a room-scanning/LiDAR product — that's a solved, licensable problem
  (Matterport, Cyncly Scan, etc.), not a differentiator worth building
  in-house at this stage.
- Not a general CAD/CAM/nesting suite — the industrial pipeline
  (imos, Cyncly, PolyBoard, Mozaik) is mature and not worth
  re-inventing. DTML's value sits specifically in the reconciliation
  layer between an uncontrolled AI image and that pipeline's inputs.

See `Roadmap.md` for how this gets built in phases, starting with the
manufacturing brain rather than the customer-facing interface.
