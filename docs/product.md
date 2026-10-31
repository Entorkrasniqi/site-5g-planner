# Product

Status: draft for review. Many statements here are **hypotheses** about customers; they are
labelled and the plan to test them is in section 8.

## 1. One-sentence product

A vendor-neutral, BIM-native indoor **5G coverage and access-point planning tool** that gives
private-network integrators and design consultancies a fast, auditable, calibratable first design
(and a defensible quote) from the customer's building model.

## 2. Primary audience

**Private 5G system integrators and wireless design consultancies.** Firms that win a project for
a factory, port, campus, hospital, logistics hub or construction site, and are paid to design,
deliver and often operate the network.

Why this audience (from the research, with its limits):

* Design is **billable work** for them, so a tool that saves hours converts directly to margin.
* They **already pay** for comparable tools. Ekahau (Wi-Fi) lists at about USD 5,995 for AI Pro
  plus roughly USD 2,000 per year subscription
  ([CDW](https://www.cdw.com/product/ekahau-ai-pro-license-1-license/5896213), reseller prices);
  one 2019 user reported roughly USD 40,000 for iBwave with about USD 5,000 per year renewal
  ([PeerSpot](https://www.peerspot.com/questions/what-is-your-experience-regarding-pricing-and-costs-for-ibwave-wi-fi),
  a single anecdote). These establish that professionals pay four to five figures per seat; they do
  not establish that they would pay *us*.
* The segment is growing by vendor-sponsored estimates (private 5G integrator market about
  USD 2.2B in 2026, [Mordor Intelligence](https://www.mordorintelligence.com/industry-reports/private-5g-system-integrator-market)).
  Treat as directional only.

Secondary audiences (served by the same product, not designed for first):

* **Equipment-vendor pre-sales engineers** who need a quick indicative design to size a quote.
* **Enterprise owners** (industrial, campus) who commission the integrator and want to review the plan.
* **Construction/BIM teams**: the original Nokia/YIT idea. `[hypothesis]` that they have budget.

## 3. Archetypes (hypothetical, to be replaced by interview findings)

| Archetype | Context | Wants | Fears |
|---|---|---|---|
| **RF design engineer** at a 20-200 person integrator | Designs 3-15 sites a quarter; already has iBwave/Ekahau/vendor tools | Faster first draft; scriptable; clear assumptions; export their tools can open | A pretty map that is wrong and embarrasses them in front of the customer |
| **Solutions architect / pre-sales lead** | Needs a number of radios and a price this week | AP count and BOM within an agreed error band, in hours not days | Under-quoting, then paying for extra radios from margin |
| **Independent consultant** (1-5 people) | Cannot afford high-end licences; many small sites | Low cost, runs on a laptop, report they can hand to the customer | Tooling that needs a team to operate |
| **Customer's network/IT manager** (reviewer, not user) | Receives the design | To understand and challenge the assumptions | Black boxes |

## 4. Jobs to be done

1. *"Give me a defensible AP count and layout for this building before we quote."* (pre-sales)
2. *"Let me iterate: move radios, change band, add constraints, see the effect immediately."* (design)
3. *"Show me why you believe this, and how wrong it might be."* (trust)
4. *"After we measure on site, tune the model so the rest of the plan improves."* (calibration)
5. *"Hand me deliverables I can send: drawings, BOM, assumptions."* (delivery)
6. *"Fit into my toolchain: take the architect's model in, send results to CAD/BIM and to our other tools."* (integration)

## 5. Value proposition and honest positioning

| Competitor | Strength | Our angle | Our weakness today |
|---|---|---|---|
| **iBwave** (in-building cellular design) | Mature, trusted, large equipment libraries, de facto standard `[to verify]` | BIM-native input, scriptable/API, open and auditable model, lower cost | No equipment library, no interference/capacity model, unvalidated |
| **Ekahau** (Wi-Fi design and survey) | Excellent survey + design workflow | Cellular/5G focus, BIM input | Not a survey tool at all |
| **CYPETEL Wireless** (IFC/Revit import, Wi-Fi/Bluetooth/Zigbee; [CYPE](https://info.cype.com/en/software/cypetel-wireless/)) | Already reads IFC and Revit, reports and quantities | 5G-specific planning and optimisation | Its 5G support and current licence terms are unverified by us |
| **Vendor planning tools** (e.g. Ericsson's enterprise coverage estimator) | Vendor-endorsed | Vendor-neutral | Cannot match vendor radio data |
| **Spreadsheets and rules of thumb** | Free, familiar | Wall-aware, repeatable, shows a map | Trust must be earned |

We do **not** claim to beat incumbents on accuracy. Our wedge is: *BIM-native + transparent +
calibratable + automatable*, for firms that want to do more design faster and keep their own judgement in the loop.

## 6. Scope

**In scope (target product):** IFC import, wall/opening/floor attenuation, pluggable propagation
models, AP placement with constraints, multi-storey, downlink and uplink budgets, SINR and indicative
capacity, calibration from site measurements, validation reports, exports (JSON, CSV BOM, PDF,
IFC write-back), CLI + API + web UI.

**Out of scope (explicit non-goals):**

* Not a site-survey measurement tool (we *consume* measurements, we do not capture them).
* Not a network-operations/RAN-planning tool for macro networks, handover/frequency planning at city scale.
* Not a spectrum-licensing advisor; regulatory facts are user input, not product claims.
* Not a certified or guaranteed-performance design; outputs are engineering estimates with stated uncertainty.
* Not a replacement for the radio vendor's own dimensioning for contractual performance guarantees.
* No outdoor/macro propagation in the first versions.

## 7. Success metrics

Product metrics are proposals; thresholds are to be ratified after interviews.

| Metric | Definition | Initial target | Phase |
|---|---|---|---|
| Time to first plan | Upload IFC to first reviewed plan, median | <= 10 min on a typical floor | P4 |
| Prediction error (calibrated) | RMSE of predicted vs measured received power on held-out points | <= 6 dB `[hypothesis; to be set from literature and own data]` | P2 |
| Prediction bias | Mean signed error on held-out points | within +/- 2 dB | P2 |
| AP-count agreement | Our count vs an expert's design on benchmark sites | within +/- 1 AP on >= 80% of benchmark sites | P2 |
| Import fidelity | Wall count and room area vs the model in a viewer | >= 98% of walls and rooms imported, 100% of skipped elements reported | P1 |
| Reproducibility | Same input, config and version give byte-identical `plan.json` | 100% | P0 |
| Adoption (commercial) | Integrators using it on a real quote | 3 design partners by end of P2 `[hypothesis]` | P2 |
| Willingness to pay | Design partners who commit to a paid pilot | >= 2 of 5 | after P2 |

## 8. Validating the product hypotheses (customer discovery)

The largest risk is not technical (see [risks.md](risks.md)): it is that integrators are content
with incumbents and nobody pays. Before building the web product, run discovery.

**Plan:** 8-10 interviews with integrators, consultancies and vendor pre-sales engineers; 3 of them become design partners who test v0.2+ on real (anonymised) sites.

**Questions to ask (do not pitch; listen):**

1. Walk me through the last site you designed, from first call to handover. Where did time go?
2. Which tools did you use at each step? What did they cost? Who pays?
3. Do you receive BIM/IFC models from the customer? How often, what quality? What do you do when you don't?
4. How do you decide how many radios to quote? How wrong were you last time, and what did it cost?
5. What do you do after install: do you measure? With what? What happens to the measurements afterwards?
6. What would make you distrust a prediction tool? What evidence would convince you?
7. What would you need to export for it to be usable on your next project?
8. If this saved you a day per site, what would that be worth? How do you buy software (seat, project, vendor lock)?

**Decision gates:**

* If fewer than half have usable BIM models regularly, prioritise non-BIM inputs (scaled floor plans) over IFC depth. See [ADR-0002](adr/0002-canonical-site-model.md).
* If nobody trusts an uncalibrated model, calibration moves ahead of capacity modelling.
* If they would pay only for a vendor-specific tool, reconsider the vendor-neutral position.

## 9. Pricing and packaging (hypotheses only)

Do not fix prices before discovery. Candidates to test: per-seat annual subscription (anchored to the
Ekahau range above), per-project fee for consultants, enterprise licence with API access for
integrators who automate. The open-source core (MIT today) plus a paid hosted/web product is one option;
the licensing of dependencies must be checked first ([risks.md](risks.md), R9).

## 10. Product principles

1. **Trust before polish.** Every number shows its assumptions; every plan can state how wrong it might be.
2. **Auditable and reproducible.** A plan is a file with provenance, not a screenshot.
3. **Human in the loop.** The engineer overrides, constrains and signs off; the tool proposes.
4. **Open interfaces.** Standard formats in and out; the CLI/API are first-class, not an afterthought to the UI.
5. **Say what we don't know.** Uncertainty and limits are product features.
