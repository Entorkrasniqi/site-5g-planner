# Testing strategy

Status: v0.1 has 29 passing tests in `tests/` (CLI, IFC loader, planner, propagation) and a CI job that
runs `pytest` and plans the sample floor. This document defines the strategy needed for the target
product, where a wrong number has commercial consequences.

## 1. What makes this software hard to test

| Property | Consequence |
|---|---|
| Numerical output | Exact equality is wrong; need tolerances and independent oracles |
| Geometry | Edge cases (touching, parallel, collinear, zero-length) hide bugs |
| Messy file input | Real IFC varies by authoring tool; one sample file proves little |
| Optimisation | "Is the answer good?" differs from "is the answer deterministic and valid?" |
| Model accuracy | Correctness against reality needs measurements, not unit tests |

So tests are layered by what they can and cannot prove.

## 2. Test layers

```
              /\
             /  \    5. Validation vs measurements   (statistical, slow, on a frozen benchmark)
            /----\
           /      \  4. System / end-to-end           (IFC in -> plan.json + report out)
          /--------\
         /          \ 3. Integration / contract        (importers, API, exporters, schema)
        /------------\
       /              \ 2. Property-based & invariants   (hypothesis)
      /----------------\
     /                  \ 1. Unit tests, golden values      (pure functions)
    /--------------------\
```

### 2.1 Unit tests and golden values (layer 1)

* Pure functions only; no files, no network.
* **Independent oracles:** values computed by hand or from a standard, not by re-running the code under test. Examples: `FSPL(1 m)` at 3.5 GHz is 43.3 dB; at 1 GHz, 32.4 + 20 log10(f_MHz) style checks; log-distance doubling adds `10 n log10(2)` dB (3.01 dB for n=1, 9.03 dB for n=3).
* Geometry: crossing, miss, touching endpoint, parallel, collinear overlap, zero-length wall, ray starting on a wall.
* Material lookup: layered walls, no match -> unknown value, case insensitivity, user override.
* Tests are named after the requirement they protect: `test_fr02_...` ([requirements.md](requirements.md) section 3).

### 2.2 Property-based tests and invariants (layer 2)

Use Hypothesis to generate random but valid sites. Properties that must always hold:

| Property | Statement |
|---|---|
| Monotone coverage | Adding an AP never reduces the coverage fraction; `coverage_after_each_ap` is non-decreasing |
| Wall monotonicity | Increasing any wall's attenuation never increases received power at any point |
| Distance monotonicity | In free space (no walls), received power is non-increasing with distance |
| Symmetry | Mirroring the site and the AP mirrors the coverage map |
| Translation invariance | Shifting the whole site leaves the AP count and coverage fractions unchanged |
| Determinism | Two runs with identical input give identical `plan.json` (excluding nothing; timestamps are not in the identity) |
| Budget | `len(access_points) <= max_aps` |
| Constraint respect | No AP in a forbidden or non-mountable area |
| Goal consistency | `goals_met` is true iff the recomputed coverage and per-room coverage satisfy the thresholds |
| Best-server | Power at a cell equals the max over APs |

### 2.3 Integration and contract tests (layer 3)

* **Importer contract:** every importer returns a `SiteModel` satisfying domain invariants plus an `ImportReport`; the same suite runs against IFC, DXF and manual inputs.
* **IFC regression corpus:** at least 3 public models per supported schema (IFC2x3, IFC4), from different authoring tools, with committed expected wall/room counts verified once by eye in a viewer, and expected import-report entries. Licences of corpus files must permit redistribution, otherwise store only checksums and download in CI.
* **Schema contract:** every emitted `plan.json` validates against the JSON Schema; old schema versions still load (NFR-14).
* **API contract:** OpenAPI-driven tests once the API exists (schemathesis-style).
* **Exporters:** golden-file tests for BOM CSV; IFC write-back re-read and compared by position; PDF checked for presence of every assumption string.

### 2.4 System tests (layer 4)

* CLI end to end on the sample building and on corpus models: exit codes, files produced, goals met.
* A `site5g plan` run in CI on every change (already present for the sample).
* Golden `plan.json` snapshot for the sample with a documented tolerance policy: AP positions exact (deterministic), floating-point coverage within `1e-9`.

### 2.5 Validation against measurements (layer 5)

Defined in [validation-and-calibration.md](validation-and-calibration.md). Runs on a frozen benchmark
dataset; reports RMSE/bias; **fails the build** on regression beyond tolerance. Kept separate from fast
tests (nightly or on release), but versioned and reproducible.

## 3. Non-functional testing

| Area | Method |
|---|---|
| Performance | Benchmark suite with fixed synthetic sites of increasing size (e.g. 500 / 2,000 / 10,000 m2); record time and peak memory per stage; compare to budgets (NFR-02, 03); trend in CI; run on dedicated, stable hardware or relative to a baseline calibration job |
| Robustness | Fuzz the IFC importer: truncated files, random byte flips, huge entity counts, missing storeys, zero-thickness walls; expect structured errors, never crashes or hangs (NFR-05) |
| Security | Abuse tests for upload limits, path handling, tenant isolation; dependency and licence scanning |
| Determinism across platforms | CI matrix runs the golden test on Linux, macOS, Windows and on every declared Python version; differences are investigated, not ignored |
| Compatibility | Python 3.10-3.13 matrix (today CI covers 3.12 and 3.13 only) |

## 4. Test data management

* **Synthetic generators** (extend `sample_ifc.py`) produce parametrised buildings: corridors, open plan, multi-storey, thick walls, glass fronts, a doorway at a known position. Tests assert on known geometry.
* **Real models** live in a corpus with provenance and licence in a manifest; large files fetched by checksum.
* **Measurement data** is confidential by default; tests use synthetic measurements with known ground truth, and the real benchmark is accessible only to maintainers.
* No test depends on the current time, network, or random seed without fixing it.

## 5. CI gates

Every PR must pass: unit + property + integration + system tests on the full Python/OS matrix,
linting and formatting, type checking, import-boundary check (core must not import adapters),
coverage threshold on core packages (NFR-10), schema validation, and the sample plan run. Nightly:
performance benchmarks, fuzzing, validation suite, dependency audit. Details in [contributing.md](contributing.md).

## 6. Defect policy

* Every bug fix starts with a failing test that reproduces it.
* A defect that produced a wrong design (not a crash) is treated as high severity and adds a case to the validation or corpus set.
* Flaky tests are fixed or removed within a week; never retried silently.

## 7. Current gaps against this strategy

1. No property-based tests, no golden `plan.json`.
2. No fuzz or corpus tests; the importer has been tested only on its own generated file.
3. CI does not cover the Python versions declared in `pyproject.toml`.
4. No benchmark, no coverage measurement, no type checking.
5. No validation layer (no data yet).
