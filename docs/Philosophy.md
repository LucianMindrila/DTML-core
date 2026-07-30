# Philosophy

## The gap DTML exists to close

AI image generation has removed the need for a professional designer or
third-party design software to *imagine* a piece of furniture. Anyone can
now generate a photorealistic vision of their dream wardrobe or media wall
in seconds. What AI image generation cannot do — and was never trained to
do — is guarantee that vision is anchored in real construction methods:
real material thicknesses, real hardware, real joinery, real CNC
tolerances.

DTML exists to close that specific gap: **turning an uncontrolled,
externally-generated vision into a standardised, manufacturable reality**,
without pretending the gap doesn't exist.

## The central tension

Every AI-generated image will contain details that don't map cleanly onto
a standardised parts library — an odd shelf spacing, an unusual drawer
proportion, a rail height that doesn't match a fixed KD geometry. At that
point there are exactly two honest choices:

1. **Snap to the nearest standardised equivalent.** Fast, cheap, always
   buildable — but risks quietly editing the customer's vision without
   them fully realising it.
2. **Flex the equations to hit the exact proportion.** True to the
   picture, but breaks standardisation, and every job risks becoming a
   one-off with its own tolerances to verify.

DTML's answer is not to resolve this tension by picking a side — it's to
make the tradeoff **visible and confirmed** rather than hidden. The
product being sold isn't "we will build exactly what the AI showed you."
It's "we will build the most faithful standardised interpretation of what
you showed us, and we will show you exactly where and how we adapted it."

## Why narration-first, not inference-first

The same tension shows up in how DTML itself gets built. It would be
tempting to point an AI at an existing DWG/DXF library and have it infer
the construction rules automatically — hinge offsets, shelf-pin patterns,
KD fixing positions. This is exactly the wrong approach, for the same
reason: geometry alone is ambiguous. A hole at a given position and
diameter doesn't say what it's for, or whether it's a deliberate rule or a
one-off deviation from a specific job. Inferring rules from raw geometry
stacks assumption on assumption — precisely the hallucination risk this
whole project is trying to engineer out of the customer-facing side.

Instead: a human who knows the real construction method states the rule
explicitly. Existing drawings are then used to *verify* that rule against
reality, not to originate it. See `KnowledgeCapture.md` for the full
methodology.

## Trust as the product

The classifier confidence score, the delta/approval view, and the
narration-first library are not separate features bolted onto a
manufacturing pipeline — they are the actual differentiation. The
CAD/CAM/nesting pipeline that turns confirmed geometry into CNC output is
a solved industrial problem (imos, Cyncly, PolyBoard already do it well).
The unsolved, defensible part is the honest reconciliation between an
uncontrolled AI vision and a standardised, buildable interpretation of it
— made visible to the customer rather than silently absorbed.
