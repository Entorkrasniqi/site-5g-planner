# ADR-0002: A canonical Site Model decouples importers from the planner

- Status: Proposed
- Date: 2026-10-27
- Related: FR-01 to FR-08, NFR-05, risk R3, R8

## Context

In v0.1 the loader returns `Storey`/`Wall`/`Space`, and the planner consumes those directly. That works
for one generated file. For integrators two facts matter:

* Real IFC varies widely (authoring tool, units, schema version, modelling style), so import logic will grow and churn.
* Some customers will not provide BIM at all (risk R3). They will send PDFs, DWGs or nothing, and the engineer will draw walls.

If the planner depends on IFC details, every new input format and every IFC quirk touches the planning code.

## Options considered

1. **Keep loader output as the planner input (status quo):** least work now; IFC concerns leak into the core; adding formats means touching the planner.
2. **Canonical Site Model owned by the core; importers are adapters that produce it plus an ImportReport:** extra type definitions and a mapping layer; isolates change; enables non-BIM input and manual edits.
3. **Plan directly on raw IFC with ifcopenshell queries at planning time:** couples performance and correctness to the IFC file, no manual edits, hard to test.

## Decision

Adopt option 2. The Site Model is a small, validated, immutable data model (storeys, walls, openings,
floors, spaces, materials, with units and invariants, see [domain-model.md](../domain-model.md)). Every
importer returns `(SiteModel, ImportReport)`. User edits are stored as a patch applied on top of the import,
never as mutations of the source.

## Consequences

* Easier: new input formats; testing the planner with synthetic sites; manual correction (FR-08); caching by content hash.
* Harder: a mapping layer to maintain; Site Model schema needs versioning (NFR-14).
* The loader's silent skipping must become reported warnings (FR-02) as part of this change.
* Migration is a rename-and-wrap: v0.1 types become the first version of the Site Model, with no behaviour change, covered by the golden test.

## Revisit when

Discovery shows every partner supplies clean IFC and never needs edits, in which case the edit/patch layer can be deferred (the type boundary itself stays).
