# Extractor

Tooling to mine real geometry out of existing DXF drawings, in support of
the narration-first knowledge capture methodology
(`../docs/KnowledgeCapture.md`, `../docs/RFC/RFC-0003-KnowledgeCapture.md`).

## What this does and doesn't do

**Does:** read `CIRCLE` entities directly from a DXF file (real center
coordinates and radii — no OCR, no visual estimation), cluster them
spatially into per-part hole groups, and report diameter distribution and
detected spacing/pitch per group. This is exact, low-risk numeric
extraction — it's just reading coordinates.

**Doesn't:** identify what any hole cluster actually *is* (which part,
which hardware). There is no surviving semantic/label data in the source
files to recover that from — see the findings below. Identity
confirmation is a required human step; see `CONTRIBUTING.md` and
`../docs/KnowledgeCapture.md`.

## Usage

```bash
python3 dxf_hole_extractor.py path/to/drawing.dxf [gap_threshold_mm]
```

`gap_threshold_mm` (default 150mm) controls the spatial clustering —
circles within this distance of each other (chained) are grouped as
belonging to the same physical part. Tune per drawing density.

Output is a per-group report: hole count, bounding box, diameter
breakdown, and any detected repeating spacing pattern. Route to a file
and work through it — see `samples/` and `extracted/` below.

## Directory convention

- **`samples/`** — small representative source DXF excerpts used to
  develop/test the extractor itself. Not the full production library
  (which lives outside this repo — see `.gitignore`, real `.dwg`/working
  files are deliberately excluded from version control).
- **`extracted/`** — regenerated extraction output (reports, CSVs).
  Gitignored — this is scratch output, not a source of truth. Anything
  worth keeping permanently belongs in `library/` after human
  confirmation, following the schema in `../schemas/`.

## Findings from the initial library extraction

Run against the real `parts.dxf`/`modules.dxf`/`order_form.dxf` library
(1,641 / 23 / 61 circles respectively). Full method and reasoning in
`../docs/KnowledgeCapture.md`; summary here:

- **No text/label metadata survives in any of these files.** DXF entity
  inventory is `LINE`, `ARC`, `CIRCLE` only — no `TEXT`, `MTEXT`,
  `DIMENSION`, or named `BLOCK` entities. All labels were exploded to raw
  line geometry at some point prior to these exports.
- **`parts.dxf`, high-confidence pattern:** an `(8.0, 8.0, 15.0)mm`
  3-hole cluster, 18 occurrences — matches a standard KD cam+dowel
  fitting (15mm cam housing + 2× 8mm dowel/bolt holes).
- **`parts.dxf`, unresolved pattern:** `(2.0, 4.0, 11.0)mm`, 42
  occurrences — the single most common 3-hole signature in the file, no
  confident match. **Needs direct confirmation before being encoded
  anywhere in `library/`.**
- **`parts.dxf`, needs confirmation:** full-height (~1980mm) rows of
  5.0mm holes at a measured ~70.7mm pitch (5 occurrences, one per carcass
  width variant) — tentatively shelf-pin lines, but the pitch doesn't
  match the standard 32mm system. Could be a genuinely different pitch
  in use, or two interleaved rows not being separated correctly by this
  tool's clustering — needs a human check either way.
- **`parts.dxf`, notable rarity:** true 35.0mm hinge-cup clusters paired
  with 8mm holes — only 2 occurrences. Much rarer than expected if this
  were the primary door-hinging method across the library; worth checking
  whether hinges are drawn/grouped differently than assumed here.
- **`modules.dxf`:** only 23 circles total, all identical 4.44mm
  diameter, none clustering above 2-per-group — consistent with this
  file being whole-assembly elevations rather than joinery detail
  drawings (no drilling data expected here).
- **`order_form.dxf`:** 10 groups, consistent with an order-form template
  carrying a handful of illustrative example holes rather than a real
  parts library.

See the full per-group data (all 226 groups from `parts.dxf`) in the
`DXF_Hole_Cluster_Report.xlsx` workbook produced during the initial
investigation (not committed here — regenerate via the script above
against the real source files, which live outside this repo).

## Things that were tried and rejected

- **Direct DWG parsing (building LibreDWG from source).** Technically
  sound in principle but impractical to build reliably in a sandboxed
  environment; also doesn't change the underlying text-metadata finding
  above, since DWG and DXF share the same entity model.
- **OCR against rasterized PDF exports.** Tested with Tesseract at
  multiple resolutions — returns nothing. The drawings use CAD stroke-
  font (SHX) text rendered as thin open outlines, not solid glyphs, which
  OCR engines can't recognise as characters.

Both of these are recorded so they aren't re-attempted without reason —
see `../docs/RFC/RFC-0003-KnowledgeCapture.md`.
