# DXF Renderer Specification (Draft v0.1)

The DXF renderer is DTML's first output layer: it takes an already
resolved Part (`schemas/resolved/resolved_part.schema.yaml`, produced by
`dtml.resolver.resolve_part()` — see `ResolverSpecification.md`) and
translates it into DXF geometry a machine or CAM package can read.

It is deliberately thin. Every decision that determines *what* the
geometry is has already been made by the resolver; the renderer's only
job is *how that geometry is expressed as DXF entities and layers*.

## v0.1 scope

The renderer does **not**:

- resolve references;
- merge Feature defaults with instance overrides;
- evaluate Expressions;
- decide Feature semantics (e.g. what `hole_array` means);
- re-check engineering rules already owned by the resolver (positivity,
  bounds, depth-vs-thickness, ...);
- infer any geometry that isn't already explicit in the resolved model.

It only translates resolved geometry into DXF entities and layers. A
`resolved_part` dict that fails its own schema is not this module's
problem — `dtml.resolver.resolve_part()` already refuses to emit one
(`ResolverSpecification.md`, stage 10). `dxf.render.render_resolved_part()`
assumes its input is already valid and does not re-validate it.

Supported in v0.1:

- rectangular panel outline;
- resolved hole circles, at true diameter and centre;
- front/back face separation via layer, in a single DXF file (not
  separate per-face files — see "Layer conventions" below);
- deterministic layer names;
- units in millimetres;
- metadata linking the DXF back to its source Part and resolution
  version.

Explicitly deferred (not this milestone):

- drilling markers/annotations distinct from true-size circles;
- any Feature type other than `hole_array` (the resolver itself doesn't
  support any other type yet either — see `ResolverSpecification.md`);
- multi-Part/assembly layout (nesting several Parts onto one sheet);
- text/dimension annotations, title blocks, or any human-readable layout
  beyond the raw geometry;
- reading a DXF back into DTML (this is one-directional: DTML → DXF).

Acceptance criterion: given the committed resolved shelf-pin panel
example, the renderer generates a valid DXF containing one correct
rectangular outline and the exact expected number, diameter, and
coordinates of holes, without accessing any unresolved DTML source
document.

## Module layout

- `dxf/layers.py` — deterministic layer-name constants and the
  `reference_face → layer` mapping. No geometry, no I/O.
- `dxf/render.py` — `render_resolved_part(resolved: dict) -> ezdxf.document.Drawing`.
  Pure function: takes an already-resolved dict, returns an in-memory
  DXF document. Never opens a file and never imports anything from
  `dtml/` — the input contract is the resolved dict shape alone, not the
  resolver's internals.
- `tools/render_dxf.py` — CLI. Reads a resolved-Part YAML file (the
  output of `tools/resolve_part.py`), calls `render_resolved_part()`,
  writes a `.dxf` file. Composes with `resolve_part.py` as two separate,
  independently testable steps (`resolve_part.py part.yaml --output
  resolved.yaml`, then `render_dxf.py resolved.yaml --output part.dxf`)
  rather than one tool that both resolves and renders.

## Layer conventions

A single DXF file per resolved Part, with face separation expressed as
layers rather than separate files — one file is what most CNC/CAM
software expects per panel, and a machinist toggles layer visibility per
operation rather than juggling multiple files for one physical part.

| Layer            | Contents                                   |
|------------------|---------------------------------------------|
| `PANEL_OUTLINE`  | the rectangular panel boundary               |
| `HOLES_FRONT`    | every hole from a `reference_face: front` Feature instance |
| `HOLES_BACK`     | every hole from a `reference_face: back` Feature instance  |

Layer names are derived purely from `resolved_features[i].reference_face`
— deterministic and independent of Feature type, instance count, or
ordering. All three layers are created on every render, even if a given
Part has no back-face holes, so downstream tooling can rely on the layer
existing.

## Entities

- **Outline** — a closed `LWPOLYLINE` at
  `(0,0) → (width_mm,0) → (width_mm,height_mm) → (0,height_mm)`, on
  `PANEL_OUTLINE`. Coordinates come directly from `resolved.dimensions`;
  the renderer does not re-derive or validate them.
- **Holes** — one `CIRCLE` per resolved hole, `center` = the hole's
  `centre_mm.x`/`centre_mm.y`, `radius` = `diameter_mm / 2`, on the layer
  for that feature instance's `reference_face`. `centre_mm.z` and
  `depth_mm`/`hole_form` are not represented as separate DXF geometry in
  v0.1 (a 2D circle at true diameter is the literal translation the
  acceptance criterion asks for) — depth/form differentiation by layer
  or block attribute is deferred until a real downstream consumer needs
  it.

## Units

DXF header `$INSUNITS = 4` (millimetres) and `$MEASUREMENT = 1` (metric)
are set on every render, since `resolved_part.schema.yaml` values are
always millimetres already — the renderer states the unit, it doesn't
convert anything.

## Metadata

Each render attaches XDATA under a custom `DTML` APPID to the outline
entity, recording:

- the source Part reference (`source_part.ref`) and its
  `object_version`;
- the resolver's `resolution_version`.

XDATA rather than visible `TEXT` entities: it keeps the drawing clean for
a machinist while staying trivially machine-readable
(`entity.get_xdata("DTML")` via `ezdxf`) for traceability — which
resolved model, from which resolver version, produced this specific
`.dxf` file.

## Testing

`tests/test_dxf_render.py` resolves the committed
`examples/panel_with_shelf_pin_array.part.yaml` via
`dtml.resolver.resolve_part()`, passes the resulting dict straight to
`render_resolved_part()`, and inspects the result with `ezdxf`'s
modelspace query API — never re-opening or re-parsing any DTML source
document from within the render path itself. Assertions cover: outline
point coordinates, per-layer circle count/diameter/centre, and the
XDATA metadata round-tripping through a save/reload cycle.

## What's not built yet

- Multi-Part sheet layout/nesting.
- Any annotation beyond raw outline + hole geometry.
- Hole-form-aware layer or block differentiation (through vs. blind).
- Any Feature type other than `hole_array` (blocked on the resolver
  supporting more than one).
