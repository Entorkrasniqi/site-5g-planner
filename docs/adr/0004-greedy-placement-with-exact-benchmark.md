# ADR-0004: Greedy placement as the default; exact solver as a benchmark

- Status: Accepted (greedy, as implemented in v0.1); exact-solver benchmark Proposed
- Date: 2026-10-27
- Related: FR-20, FR-25, NFR-01, NFR-02

## Context

Choosing the fewest AP positions that cover the required cells is a set-cover / maximum-coverage
problem, NP-hard in general. v0.1 uses greedy selection over a grid of candidate positions: repeatedly
pick the candidate that newly covers the most cells until overall and per-room goals are met. Greedy
has a known approximation guarantee for coverage objectives and is fast and simple. Integrators care
about AP count (cost), so how far greedy is from optimal matters commercially.

## Options considered

1. **Greedy (current):** fast, deterministic, explainable; no optimality guarantee for the minimum-cardinality version, which can use more APs than necessary.
2. **Exact integer program (for example `scipy.optimize.milp` or an open-source solver):** optimal for small and medium instances; slow or intractable for large ones; solver dependency.
3. **Local search / metaheuristics on top of greedy (swap, remove-redundant):** typically closes most of the gap cheaply; less explainable; needs deterministic seeding.
4. **Learned placement (ML):** no validated baseline to learn from or compare to; opaque.

## Decision

Keep greedy as the default planner. Add (a) a **redundancy-removal pass** after greedy (remove any AP whose
removal still meets the goals) and (b) an **exact solver used as a benchmark** on small cases to measure and publish the
greedy gap. Offer the exact or local-search planner as an optional mode if the measured gap justifies it.
Do not pursue ML placement until a validated model exists as a baseline.

## Consequences

* Deterministic and explainable results (NFR-01) with a documented limitation instead of an unmeasured assumption.
* We learn from data whether the AP-count error from greedy is material compared with model error (which is likely larger, see [validation-and-calibration.md](../validation-and-calibration.md)). If model error dominates, optimiser polish is low priority.
* Candidate grid resolution and spacing affect results; they are part of the recorded configuration.
* Lazy greedy evaluation is a valid speedup because coverage gain is submodular; it must preserve the same tie-breaking.

## Revisit when

The benchmark shows a gap that changes quotes by more than one AP on typical sites, or large instances make greedy too slow even with lazy evaluation.
