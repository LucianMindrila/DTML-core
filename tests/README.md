# tests

Verification for the manufacturing brain. Two categories, per
`../docs/KnowledgeCapture.md`'s narration-first + verification-second
methodology:

1. **Rule/equation unit tests** — given known inputs, does a Rule or
   Module produce the expected dimensions/positions? Standard unit
   testing against `schemas/rule.schema.yaml`-shaped definitions.
2. **DXF round-trip verification** — generate output from an encoded
   Rule/Module and diff it against a real historical drawing (see
   `../extractor/`). A mismatch is a signal to investigate — either the
   narration missed a condition, or the historical job was a genuine
   one-off deviation. Never silently resolved by adjusting the rule to
   fit the one example.

Both categories are empty until Phase 2 (`../docs/Roadmap.md`) produces
the first confirmed Rules/Modules to test against.

## `fixtures/`

Schema-layer conformance fixtures for `../tools/validate_schema.py` —
these test the *schema shape*, not manufacturing correctness, so they
exist now rather than waiting for Phase 2:

- `fixtures/valid/` — instances expected to pass validation against their
  declared `x-dtml-schema`.
- `fixtures/invalid/` — deliberately broken instances, each documenting
  in a comment which single constraint it violates and why, so a fixture
  failing for the wrong reason is easy to spot.

Run the validator against a fixture directly (see `../tools/README.md`).
