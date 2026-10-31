# Requirements

Status: draft for review. IDs are stable; tests, ADRs and the roadmap cite them.

* **Priority** (MoSCoW): M = must, S = should, C = could, W = won't (for now).
* **Phase**: see [roadmap.md](roadmap.md). **State**: `done` = implemented in v0.1, `part` = partly, `-` = not started.
* Every requirement has a **verification** method so it can be closed objectively.

## 1. Functional requirements

### 1.1 Input and site model

| ID | Requirement | Pri | Phase | State | Verification |
|---|---|---|---|---|---|
| FR-01 | Load IFC4 and IFC2x3 files and extract walls and rooms per storey in metres | M | P1 | part (IFC4, own sample only) | Regression corpus of >= 3 public models per schema; counts checked against a viewer |
| FR-02 | Produce an **import report** listing every element skipped or approximated, with reason; never fail silently | M | P1 | - (loader skips silently) | Unit test: corrupt element appears in report; CLI exit code reflects severity |
| FR-03 | Model doors and windows as openings with their own attenuation instead of ignoring them | M | P1 | - | Plan around a doorway differs predictably; test with synthetic wall+door |
| FR-04 | Handle IFC unit conversions (mm, ft, m) and storey elevation correctly | M | P1 | part | Fixture files in each unit give identical geometry in metres |
| FR-05 | Curtain walls, curved walls, sloped/stacked walls are imported or reported as approximated | S | P1 | - | Corpus models; entries appear in import report |
| FR-06 | Per-project editable material-to-attenuation table, versioned with the project, with provenance (source: placeholder / literature / measured) | M | P1 | part (JSON override, no provenance) | Table schema validated; provenance appears in plan |
| FR-07 | Accept a non-BIM site model (scaled floor plan image/PDF/DXF plus manual wall and room drawing) via the canonical site model | S | P4 | - | Round-trip: draw -> plan equals equivalent IFC-derived plan |
| FR-08 | Let the user correct the imported model (move/add/delete wall, change material) without editing the source IFC | S | P4 | - | Edits recorded as a patch on top of the import |

### 1.2 Radio modelling

| ID | Requirement | Pri | Phase | State | Verification |
|---|---|---|---|---|---|
| FR-10 | Propagation models are interchangeable behind one interface | M | P2 | - (hard-wired) | Two models run the same scenario via the same call |
| FR-11 | Provide the 3GPP TR 38.901 Indoor-Office model (LOS/NLOS) as a selectable model | S | P2 | - | Reproduces tabulated spec values within 0.5 dB |
| FR-12 | Multi-storey planning with floor/ceiling attenuation between levels and 3-D distance | M | P3 | - (single storey) | AP on level n gives attenuated coverage on n+/-1 in a synthetic two-floor model |
| FR-13 | Calibrate model parameters (path-loss exponent, per-material loss) from measurement CSV by constrained least squares | M | P2 | - | Held-out RMSE reported; improves over uncalibrated on a benchmark |
| FR-14 | Report prediction uncertainty: show a confidence margin / fade margin and its source, not just a point value | S | P2 | - | Output contains margin; documented derivation |
| FR-15 | Model antenna patterns (at least omni vs directional with azimuth/tilt) from the equipment catalogue | S | P3 | - | Pattern lookup test; directional AP shows expected lobe |
| FR-16 | Model uplink budget (UE transmit power, AP receive sensitivity), not only downlink | M | P3 | - | Plan flags uplink-limited cells in a synthetic case |
| FR-17 | Estimate SINR from co-channel interference and map to indicative throughput | S | P3 | - | Closed-form two-AP case matches hand calculation |

### 1.3 Planning

| ID | Requirement | Pri | Phase | State | Verification |
|---|---|---|---|---|---|
| FR-20 | Select AP positions to meet overall and per-room coverage goals with a minimum number of APs | M | P0 | done (greedy) | Existing planner tests |
| FR-21 | Equipment catalogue: vendor-neutral radio entries (band, EIRP, antenna, mounting, cost) editable by the user | M | P3 | - | Schema validation; BOM uses catalogue |
| FR-22 | Planning constraints: no-go zones, mountable surfaces and ceiling height, pre-existing fixed APs, max AP count/budget | M | P3 | part (`exclude_ap_rooms`, `max_aps`) | Constraint tests: no AP in a forbidden area |
| FR-23 | User can place/move/lock an AP and the tool re-evaluates coverage only | M | P4 | - | Re-evaluation matches full recompute for that AP set |
| FR-24 | Compare scenarios side by side (band, AP count, constraints) | S | P3 | - | Scenario diff output |
| FR-25 | Benchmark greedy against an exact solver on small cases and report the gap | S | P2 | - | Table of gap on random layouts |
| FR-26 | Plan a sequence of models (construction phases) and report cumulative AP rollout | C | P5 | - | CSV per phase |

### 1.4 Output and integration

| ID | Requirement | Pri | Phase | State | Verification |
|---|---|---|---|---|---|
| FR-30 | `plan.json` is a **versioned, schema-validated artifact** with full provenance (tool version, model id and version, input SHA-256, all parameters, material table, timestamps excluded from the identity hash) | M | P0 | part (config only) | JSON Schema validation; identical inputs give identical hash |
| FR-31 | Heatmap images per storey (PNG/SVG/JPG) | M | P0 | done | CLI test |
| FR-32 | Bill of materials CSV from the plan and catalogue | M | P3 | - | Golden-file test |
| FR-33 | Client-ready PDF report: assumptions, parameters, maps, AP table, validation status, limits | M | P3 | - | Report contains every assumption in the plan |
| FR-34 | Write planned APs back into IFC as appropriate IFC objects at the planned positions | S | P3 | - | Output opens in a viewer; positions match within 1 cm |
| FR-35 | Export drawings (DXF and/or PDF) for installers | C | P3 | - | Opens in CAD viewer |

### 1.5 Validation

| ID | Requirement | Pri | Phase | State | Verification |
|---|---|---|---|---|---|
| FR-40 | Import measurement points (x, y, z, storey, value, unit, device, timestamp) and compute error statistics vs prediction | M | P2 | - | Synthetic measurement set gives expected statistics |
| FR-41 | Validation report: RMSE, bias, error histogram, worst cells, held-out split definition | M | P2 | - | Reproducible report from CSV + plan |
| FR-42 | Display validated range on every plan ("model validated on N sites, RMSE x dB") or "not validated" | M | P2 | - | Plan metadata flag |

### 1.6 Platform

| ID | Requirement | Pri | Phase | State | Verification |
|---|---|---|---|---|---|
| FR-50 | CLI for all operations, scriptable, stable exit codes | M | P0 | done (inspect, plan, sample) | CLI tests |
| FR-51 | HTTP API (upload, plan job, status, results) as the contract for all clients | M | P4 | - | OpenAPI schema; contract tests |
| FR-52 | Web UI: upload, view/edit model, place APs, run, compare, export | M | P4 | - | E2E tests of main flow |
| FR-53 | Projects with versioned inputs, parameters and results; results comparable across versions | S | P4 | - | Re-open old version reproduces it |
| FR-54 | Multi-user accounts, tenant isolation, role-based access | S | P5 | - | Authorisation tests, cross-tenant access denied |

## 2. Non-functional requirements

Targets marked `[proposed]` are starting points to be confirmed by measurement; none has been measured yet.

| ID | Category | Requirement | Verification |
|---|---|---|---|
| NFR-01 | Determinism | Same input file, configuration and tool version give identical results (including AP order and tie-breaking). | Golden `plan.json` test, run twice and on CI matrix |
| NFR-02 | Performance | Plan a 5,000 m2 floor with a default grid in <= 60 s on an 8-core laptop `[proposed]`; report timing per stage. | Benchmark suite with budget; CI trend |
| NFR-03 | Scalability | Memory stays bounded for large floors (target <= 4 GB for 10,000 m2) `[proposed]`; no dense candidates x cells matrix beyond a limit. | Benchmark with memory profiler |
| NFR-04 | Accuracy | Calibrated held-out RMSE <= 6 dB and bias within +/- 2 dB on benchmark sites `[proposed]`; uncalibrated accuracy is reported, not hidden. | Validation suite ([validation-and-calibration.md](validation-and-calibration.md)) |
| NFR-05 | Robustness | Malformed, truncated or huge IFC never crashes the process or hangs; returns a structured error within a timeout. | Fuzz/corpus tests, timeouts |
| NFR-06 | Security | Uploaded files are untrusted input; parsing runs isolated with CPU, memory, time and size limits; no code execution from file content. See [architecture.md](architecture.md) section 9. | Threat model review, abuse tests |
| NFR-07 | Privacy | Uploaded building models are treated as confidential; defined retention, deletion on request, encrypted at rest and in transit; EU-hosted option. | Review checklist, deletion test |
| NFR-08 | Traceability | Every output states which inputs, parameters, model and tool version produced it. | Provenance fields validated |
| NFR-09 | Portability | Runs on Linux, macOS, Windows; Python 3.10 to 3.13 as declared. | CI matrix covers every declared version |
| NFR-10 | Maintainability | Core logic is pure and unit-tested; type-checked; linted; coverage >= 85% on core packages `[proposed]`. | CI gates |
| NFR-11 | Observability | Structured logs with a job id; per-stage timings; errors carry machine-readable codes. | Log schema test |
| NFR-12 | Usability | First reviewed plan in <= 10 min from upload for a typical floor `[proposed]`; every default is visible and overridable. | Usability session with design partners |
| NFR-13 | Honesty of output | Any figure derived from placeholder or unvalidated parameters is labelled as such in every output format. | Output contains provenance flag |
| NFR-14 | Compatibility | Plan artifact schema is versioned; older versions remain readable for >= 2 major releases. | Schema migration tests |

## 3. Requirements traceability

Each requirement should be reachable from one test (or review record). Maintain the mapping in
the test names (`test_fr02_import_report_lists_skipped_elements`) so a failing test names the
requirement it protects. Coverage of this matrix is reviewed at each phase gate in [roadmap.md](roadmap.md).
