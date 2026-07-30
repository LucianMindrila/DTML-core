# Rule Specification (Draft v0.1)

A **Rule** is an equation or relationship between dimensions, hardware
positions, and material thickness. Rules are what make a Module
parametric rather than a fixed preset — see `../CorePrinciples.md` §1.

## Shape

```yaml
rule:
  id: string
  description: string              # human-readable, plain-language statement
                                    # of the rule as narrated — see
                                    # ../KnowledgeCapture.md
  inputs: [string]                 # named variables this rule depends on
  expression: string               # the actual formula
  applies_when: string             # optional condition, e.g.
                                    # "door_height > 900"
  source: enum                     # narrated | derived
  verified_against: string         # optional: reference to a real drawing
                                    # used to check this rule, per
                                    # ../KnowledgeCapture.md
```

## Example: hinge positioning rule

```yaml
rule:
  id: hinge_position_standard
  description: >
    35mm cup hinges. Cup centre 21.5mm from the front edge. Hinge
    positions 100mm from top and bottom of the door. A third hinge is
    added, centred, for door heights over 900mm.
  inputs: [door_height]
  expression: >
    positions = [100, door_height - 100] +
                ([door_height / 2] if door_height > 900 else [])
  applies_when: null
  source: narrated
  verified_against: null           # pending: diff against a real door drawing
```

## Non-negotiables

- **`expression` must be the authoritative source of the value it
  computes.** Nothing downstream (a Part, a Module) should hardcode a
  value a Rule could produce — see `../CorePrinciples.md` §1.
- **`source: narrated` is required before a Rule can be referenced by a
  production Module.** A Rule with `source: derived` (i.e. produced by
  pattern-matching against extracted geometry without human confirmation)
  must stay flagged and unreferenced until narrated/confirmed — see
  `../KnowledgeCapture.md`.
- **`verified_against` should be populated once available.** It doesn't
  block encoding the Rule, but a Rule that's been checked against a real
  historical drawing is strictly more trustworthy than one that hasn't.

## Standardisation-axis rules (hardware categories)

Per `../CorePrinciples.md` §2, certain Rules exist specifically to
enforce the "one variable fixed, rest flexible" standardisation pattern:

```yaml
rule:
  id: led_strip_length
  description: >
    LED strip is cut to length, not selected from discrete SKUs. Profile,
    voltage, and driver are fixed; only cut length varies.
  inputs: [bay_width]
  expression: "length = bay_width - (2 * margin)"
  source: narrated
```

## Open questions

- Formal grammar/parser for `expression` — currently illustrative
  pseudo-code; needs to be pinned to an actual expression language
  (e.g. a restricted Python-eval subset, or a dedicated DSL) before
  implementation.
- How `applies_when` conditions compose when multiple Rules could apply
  to the same output.

See `../../schemas/rule.schema.yaml` (note: not yet listed in the top-level
`schemas/` set — add if a dedicated schema file is needed beyond what's
embedded in `module.schema.yaml`).
