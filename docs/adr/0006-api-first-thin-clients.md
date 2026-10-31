# ADR-0006: Core library first; API next; CLI and web as thin clients

- Status: Proposed
- Date: 2026-10-27
- Related: FR-50, FR-51, FR-52, NFR-06, NFR-10

## Context

Integrators automate and integrate. They will want to script batches, run in CI, call from their own
tools and also use a GUI. A product built UI-first tends to bury logic in the UI; a product built as a
script tends to resist a service. We also must isolate untrusted file parsing in a hosted setting.

## Options considered

1. **Monolithic web app with logic in request handlers:** fast to demo; hard to test, script and reuse.
2. **Library + CLI only:** easy; no GUI, no hosted option.
3. **Pure core library + application layer of use cases; CLI, HTTP API and web UI are thin clients of the use cases; heavy work runs in sandboxed workers:** more structure; one source of truth; scriptable and testable; supports hosted and self-hosted.

## Decision

Adopt option 3 incrementally ([architecture.md](../architecture.md) section 12):

1. Keep `core` pure and importable as a library (already largely true).
2. Extract use cases (`import_site`, `plan`, `validate`, `calibrate`, `export`) as the application layer.
3. Expose an HTTP API (OpenAPI) over the use cases once the core is stable (P4); the web UI uses only this API, no private endpoints.
4. Run import and planning as jobs in sandboxed worker processes with resource limits.

Do not build the web UI or the API before the core exits phases P1-P3, because trustworthy inputs and numbers are what customers buy.

## Consequences

* Customers can script everything the UI can do; the UI cannot drift from the product behaviour.
* Contract tests on the API protect integrators' scripts.
* More up-front design than a monolith, mitigated by staging the work.
* The same code supports a self-hosted container for customers who refuse to upload models.

## Revisit when

Discovery shows that a hosted UI is the only thing buyers want, and no one scripts; then reprioritise UI work, but keep the layering.
