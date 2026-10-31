# ADR-0005: The plan is a versioned, provenance-carrying artifact

- Status: Proposed
- Date: 2026-10-27
- Related: FR-30, FR-42, NFR-01, NFR-08, NFR-13, NFR-14

## Context

Integrators will hand plans to customers, compare versions, archive them with a quote and sometimes
defend them after the network is built. v0.1 writes `plan.json` with the configuration and results but
without tool version, model version, input hash or a statement of how much the numbers can be trusted. A
screenshot or a JSON without provenance cannot be reproduced or audited.

## Options considered

1. **Ad hoc JSON (status quo):** trivial; no guarantees, no reproducibility.
2. **Versioned JSON with a published JSON Schema and a provenance block:** modest effort; reproducible, validatable, diffable, language-neutral.
3. **Binary or database-only storage:** efficient; opaque to scripts and customers; poor interchange.

## Decision

`plan.json` is a first-class **contract**: a versioned JSON document validated by a published JSON
Schema, with a `provenance` block (tool version, model id/version, input SHA-256, material table hash and
provenance, parameters, validation status) and structured `warnings`. The identity hash excludes
wall-clock fields so identical inputs yield identical bytes. Readers ignore unknown fields; breaking
changes bump the major schema version and ship a migration.

## Consequences

* Reproducibility and auditability become testable (golden test, schema validation in CI).
* Every output format (PDF, CSV, images) shows the same provenance and validation status (NFR-13).
* Slight overhead: schema maintenance and migrations. Accepted: it is the integration surface with customer tools.
* Enables caching and result diffing in the service layer.

## Revisit when

A partner needs a different interchange (for example, a BIM-native property set) that cannot be derived from this JSON; then add an exporter, not a second source of truth.
