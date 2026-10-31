# ADR-0003: Propagation models behind one interface, versioned

- Status: Proposed
- Date: 2026-10-27
- Related: FR-10, FR-11, FR-13, FR-14, NFR-08

## Context

The radio model is the part customers will challenge and the part most likely to change: a standard
model (3GPP TR 38.901), a calibrated variant, a multi-floor variant, perhaps ray tracing later. In v0.1
`received_power_dbm` calls `path_loss_db` and `wall_loss_db` directly, so changing the model means
editing the planner. Also, a change to the model silently changes results, which is unacceptable if
plans are used for quoting.

## Options considered

1. **Hard-wired formula (status quo):** simple; no extensibility; no traceability of which formula produced a plan.
2. **Configuration flags inside one function:** quick, but flags multiply and obscure behaviour.
3. **Interface (`PropagationModel`) with registered implementations; each has an id, version, declared valid range:** a little more structure; clean substitution, clean testing, traceability.

## Decision

Define a `PropagationModel` protocol: given transmitter(s), receiver points and the Site Model, return
received power (dBm) and an uncertainty estimate (dB). Each implementation declares `id`, `version` and
a valid range, and any behavioural change bumps its version. The existing formula becomes
`simple-wall` v1 with unchanged output (proven by a golden test). The plan artifact records the model id and version.

## Consequences

* Easier: adding `3gpp-inh`, `calibrated-wall`, `multi-wall-floor`; A/B comparison on validation data; clear provenance.
* Harder: designing an interface general enough for ray tracing without over-engineering now. Mitigation: define it from the two models we will actually build in P2, not speculatively.
* Performance-sensitive code (batch evaluation) must stay vectorised behind the interface; the interface takes arrays of points, not one point at a time.
* Models must handle valid-range violations visibly (warn, do not silently extrapolate).

## Revisit when

A third model needs data the interface cannot express (for example, per-ray polarisation), or the vectorised batch contract blocks an optimisation.
