# Changelog

All notable changes to DTML are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — Repository scaffold

### Added
- Initial repository structure: `docs/`, `schemas/`, `library/`, `examples/`,
  `extractor/`, `tests/`, `tools/`.
- Founding documentation: Philosophy, Vision, Core Principles, Terminology,
  Roadmap, Architecture, Knowledge Capture methodology.
- Draft specifications for Feature, Part, Module, Rule, and Style data
  types, plus the umbrella `DTML-Spec-v0.1`.
- Three founding RFCs: overall DTML proposal, the Manufacturing Brain
  architecture, and the Knowledge Capture (narration-first) methodology.
- Draft YAML schema stubs for all nine core data types.
- `extractor/` seeded with a working DXF hole-cluster extraction script,
  used to mine real geometry (hole positions, diameters, spacing) out of
  existing scattered CAD drawings without relying on text/label data that
  doesn't survive in exploded-text DXF exports.

### Notes
- No customer-facing interface yet. Current focus is the manufacturing
  brain (schema + library encoding) — see `docs/Roadmap.md` Phase 1–2.
