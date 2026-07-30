# Style Specification (Draft v0.1)

A **Style** is the customer-facing finish/aesthetic layer — door style,
material/colour, handle type — applied on top of a resolved Module
without changing its underlying construction logic (see
`../CorePrinciples.md` §7 and `ModuleSpecification.md`).

## Shape

```yaml
style:
  id: string
  name: string                     # e.g. "Navarra / Walnut"
  door_style: string                # references library/styles/ door options
  material: string                  # references materials library
  finish: string                    # e.g. "chrome illuminated" (from order_form)
  handle: string
  applies_to_slots: [string]        # which Module style_slots this fills
```

## Source material

The initial Style set should be built from what's already visible in
`order_form.pdf`/`order_form.dxf` — e.g. the "Navarra style door" /
"Walnut" / "Chrome illuminated" combinations seen in that library, and
the checkbox-style option groupings in the order form template. These
need to be confirmed and formalised, not assumed, per the same
narration-first principle used elsewhere (`../KnowledgeCapture.md`) —
the order form's actual option text wasn't machine-extractable (no
surviving text layer), so this needs direct confirmation against the
real form rather than a best guess from the visual layout.

## Relationship to Modules

A Style must never alter a Module's Rules or Part dimensions — only the
finish/appearance layer. If a "Style" seems to require a different panel
thickness, hinge type, or hardware, that's actually a different Module
variant or a Rule-level distinction, not a Style — flag it for
reclassification rather than encoding it as a Style exception.

## Open questions

- Whether Style should support partial overrides (e.g. same door style,
  different handle) or must always be selected as a complete named set.
- How Style options map to the confidence-scored classification —
  i.e. can the AI vision image also drive a Style guess, or is Style
  always a separate customer selection? Current assumption: Style is a
  separate, explicit customer choice, not inferred from the vision image,
  since aesthetic finish is far less constrained by real-world
  manufacturability than a Module's underlying construction.

See `../../schemas/style.schema.yaml` for the machine-readable schema.
