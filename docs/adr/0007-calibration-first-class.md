# ADR-0007: Calibration and validation are first-class features

- Status: Proposed
- Date: 2026-10-27
- Related: FR-13, FR-14, FR-40 to FR-42, NFR-04, NFR-13, risk R2, R14, R15

## Context

Indoor propagation depends strongly on the specific building: wall composition, reinforcement, glazing,
furniture and equipment. A generic material table cannot be accurate everywhere. Integrators are
experienced engineers who already measure on site; many will trust a tool only if it can learn from
those measurements and show its error. The v0.1 attenuation values are placeholders and unvalidated.

## Options considered

1. **Ship a better generic table and hope:** cheapest; accuracy limited and unprovable.
2. **Calibration as an advanced, optional add-on:** can be skipped; weakens the trust story.
3. **Calibration and validation central to the workflow and the data model:** every plan carries a validation status; measurements are first-class inputs; error reports are standard outputs.

## Decision

Adopt option 3. Specifically:

* Measurements are imported with explicit quantity, device and position provenance.
* Calibration fits a small number of parameters (path-loss exponent, offset, per-material losses) by regularised, constrained least squares and produces a **new versioned material table**.
* Validation uses held-out splits by space or by site, never by random point, and reports bias, RMSE, spread, and decision accuracy.
* Plans, reports and UI state the validation level reached ("not validated" is a valid and prominent state).
* Releases are gated on regressions in a frozen benchmark.

Details in [validation-and-calibration.md](../validation-and-calibration.md).

## Consequences

* Directly addresses the largest technical risk (accuracy, R2) and creates a defensible differentiator vs black-box tools.
* Requires measurement data, so we depend on design partners or our own campaigns (R14).
* Adds product surface (data import, reports) and data-handling responsibilities (measurement confidentiality).
* Honesty cost: reported errors may be large at first. We accept this; hiding it would destroy trust.

## Revisit when

A different approach (for example, a physics-based solver with accurate material data) achieves target accuracy without per-site calibration on real benchmarks.
