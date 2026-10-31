# Risks

Status: draft. Scores are judgement, not data; re-score at every phase gate ([roadmap.md](roadmap.md)).

Scale: **Likelihood** and **Impact** from 1 (low) to 5 (high). **Exposure = L x I.** Ranked by exposure.

| ID | Risk | Type | L | I | Exp | Mitigation | Early warning / owner action |
|---|---|---|---|---|---|---|---|
| R1 | Integrators are content with iBwave/Ekahau/vendor tools and nobody pays for another one | Market | 4 | 5 | 20 | Discovery before building the service; target a wedge (BIM-native, scriptable, auditable, 5G); validate willingness to pay with a paid pilot | Fewer than 2 of 5 partners would pay after seeing a calibrated plan |
| R2 | Predictions are not accurate enough to be trusted for quoting | Technical | 4 | 5 | 20 | Validation and calibration as P2; publish honest errors; report uncertainty; do not oversell | Held-out RMSE well above the target, large positive bias |
| R3 | Customers lack usable IFC models (or quality is poor) | Market/technical | 4 | 4 | 16 | Ask in interviews; canonical site model allows scaled-floor-plan input ([ADR-0002](adr/0002-canonical-site-model.md)); import report shows quality | Most partners send PDFs/DWGs, not BIM |
| R4 | Scope creep into a full RF planning suite | Product | 4 | 4 | 16 | Written non-goals ([product.md](product.md)); each phase has exit criteria; say no to features without a partner asking | Roadmap items without a named user |
| R5 | A wrong design causes a customer financial loss or a liability dispute | Legal/business | 2 | 5 | 10 | Position outputs as engineering estimates with stated uncertainty; visible validation status; terms of use; no performance guarantee; professional-indemnity advice before commercial launch | Customers treating output as guaranteed |
| R6 | Incumbents add BIM/IFC import or 5G features | Market | 3 | 4 | 12 | Compete on openness, automation and transparency; stay close to partners; keep switching costs low (open formats) | Competitor release notes |
| R7 | Performance and memory blow up on large sites | Technical | 4 | 3 | 12 | Benchmarks first; spatial index; chunking; lazy greedy ([architecture.md](architecture.md) section 8) | Benchmark exceeds budget; out-of-memory on partner models |
| R8 | Importer fails on real-world IFC variety | Technical | 4 | 3 | 12 | Corpus, fuzzing, import report, support for unit/schema variants; fall back to manual/2-D input | Corpus failures; partner files rejected |
| R9 | Dependency licensing blocks the intended commercial model | Legal | 3 | 4 | 12 | Review licences of ifcopenshell (LGPL-family, check exact terms and static/dynamic and SaaS implications), shapely, numpy, matplotlib before choosing distribution/hosting model; legal review | Unclear obligations when planning hosted or bundled distribution |
| R10 | Single maintainer (bus factor, limited capacity) | Organisational | 4 | 3 | 12 | Documentation, tests, ADRs; keep scope small; automate everything | Backlog growing; reviews skipped |
| R11 | Security incident from handling confidential building models | Security | 2 | 5 | 10 | Sandboxed import, tenant isolation, encryption, retention policy, self-hosted option ([architecture.md](architecture.md) section 9) | Findings in security review; partner refuses upload |
| R12 | Customers need capacity/SINR/latency, not just coverage | Product | 3 | 4 | 12 | Ask which quantities they specify; SINR in P3; label coverage-only clearly | Interviews show coverage alone is not decision-relevant |
| R13 | Regulatory/spectrum differences by country make defaults wrong | Product | 3 | 3 | 9 | Treat band, EIRP and licence limits as user inputs per project; no embedded regulatory claims | Partner in a region with different bands |
| R14 | No access to measurement data to validate | Technical | 3 | 5 | 15 | Own measurement campaign; design-partner data-sharing agreements; synthetic data for software tests only | No measured data by the start of P2 |
| R15 | Material attenuation is too site-specific for a generic table | Technical | 4 | 3 | 12 | Per-project calibration is a core feature, not an add-on; priors with uncertainty | Calibrated parameters vary widely between sites |
| R16 | Over-engineering the architecture before demand exists | Process | 3 | 3 | 9 | Strangler-style evolution ([architecture.md](architecture.md) section 12); service layer only after P3 | Time spent on infrastructure with no user |

## Top three, and what we do first

1. **R1/R2 market and accuracy:** both are answered only by outside evidence. Discovery interviews and a first measurement campaign start *before* heavy feature work. Cost: low. Value: avoids building the wrong thing.
2. **R14 data access:** secure one measured floor early; it unlocks P2 and shows partners the validation approach.
3. **R3 input reality:** ask what files integrators actually receive; if it is mostly PDF/DWG, the roadmap changes (non-BIM input moves earlier).

## Assumptions being made (each is a risk if false)

* Integrators care about BIM-based input enough to change workflow. `[hypothesis]`
* A transparent simple model, once calibrated, is accurate enough for quoting. `[hypothesis]`
* Customers accept hosted processing of their models, or self-hosting is acceptable. `[hypothesis]`
* Coverage prediction (with later SINR) is the quantity that drives the design decision. `[hypothesis]`
* The market sources used are directional only: they are vendor-sponsored estimates.

## Review cadence

Re-score at each phase gate; add triggered risks with an owner and date; close risks with evidence, not with time.
