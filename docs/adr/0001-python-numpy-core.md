# ADR-0001: Python with NumPy and Shapely for the computational core

- Status: Accepted (describes the v0.1 implementation)
- Date: 2026-10-27
- Related: NFR-02, NFR-03, NFR-09, NFR-10

## Context

The product reads BIM files, does geometry, evaluates a radio model on many points and runs an
optimiser. The only mature open-source IFC toolkit with geometry support is ifcopenshell, which has
first-class Python bindings. The numerical work is array-shaped. The maintainer is productive in Python
and the audience values scriptability (CLI, API, notebooks).

## Options considered

1. **Python + NumPy + Shapely (+ ifcopenshell):** fast to develop, best IFC ecosystem, vectorised numerics are adequate for small and medium floors, easy scripting. Slower than compiled code for large problems; the GIL limits threads (processes work).
2. **Rust/C++ core with Python bindings:** best performance and memory control, harder to develop and hire for, IFC library story weaker, premature before a performance need is measured.
3. **Julia or similar:** good numerics, weaker ecosystem for IFC and for integrators to adopt.
4. **JavaScript/TypeScript end to end:** convenient for a web UI, weak scientific and IFC geometry stack for server-side work.

## Decision

Use Python with NumPy for vectorised math, Shapely for 2-D geometry and ifcopenshell for IFC.
Keep the core pure and array-oriented so hot loops can be replaced later (Numba, Cython or a Rust
extension) without changing interfaces.

## Consequences

* Rapid iteration and an easy path to a scriptable CLI and API.
* Performance is bounded; a dense candidates x cells matrix does not scale ([architecture.md](../architecture.md) section 8). We commit to **measure first**, then optimise algorithmically (spatial index, chunking, lazy greedy) before considering a native rewrite.
* Dependency licensing must be checked before choosing a distribution model (risk R9).
* Python version support is a declared promise (3.10-3.13) and must be tested (currently gap).

## Revisit when

Benchmarks show the algorithmic fixes cannot meet NFR-02/03, or a licensing issue blocks the chosen deployment.
