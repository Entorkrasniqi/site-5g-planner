# Validation and calibration

Status: **planned (P2)**. Nothing here is implemented, and v0.1 has not been validated against any
measurement. This document defines how trust will be earned. For this audience (integrators who stake
quotes and reputation on predictions) it is the most important document in the set.

## 1. Principles

1. **Validation is separate from calibration.** Calibration fits parameters; validation measures error on data the fit never saw. Reporting fit error as accuracy is a known way to fool yourself.
2. **Report error, not only success.** RMSE, bias, spread, worst cases.
3. **Validated range is part of the product.** A model validated in offices at 3.5 GHz must not silently be offered for a steel-heavy factory at 28 GHz.
4. **Every plan states its validation status** (FR-42): "not validated", or "validated on N sites, RMSE x dB".
5. **Measurements are data with provenance:** device, quantity, orientation, time, operator.

## 2. What we compare

Prediction (dBm at a point) versus measurement (dBm at the same point). They must be the same
*quantity*. Typical field data: RSSI or RSRP from a phone/scanner. The model predicts total received
power; RSRP is lower by a bandwidth-dependent offset ([radio-model.md](radio-model.md) section 4). The
importer requires the quantity to be declared, and conversion is explicit and recorded.

Measurement CSV (FR-40), one row per sample:

| Column | Meaning |
|---|---|
| `x_m, y_m, z_m` | Position in the site frame, or pixel coordinates plus a transform |
| `storey` | Storey name |
| `value` | Measured value |
| `quantity` | `rsrp_dbm`, `rssi_dbm`, `rsrp_dbm_per_re`, ... (explicit) |
| `device` | Device model, antenna info |
| `source_id` | Which transmitter was measured (if known) |
| `time` | UTC timestamp |

Position accuracy matters: a 3 m position error in a room with a wall can be a 10 dB error. Record
how positions were obtained (floor-plan taps, indoor positioning).

## 3. Metrics

For N held-out points with error `e_i = predicted_i - measured_i`:

| Metric | Formula | Why |
|---|---|---|
| Bias (mean error) | `mean(e)` | Systematic over- or under-prediction; positive bias is dangerous (promises coverage that isn't there) |
| RMSE | `sqrt(mean(e^2))` | Overall accuracy in dB |
| Std of error | `std(e)` | Spread after removing bias; basis for a fade margin |
| MAE | `mean(abs(e))` | Robust summary |
| 90th percentile of `abs(e)` | percentile | What a bad day looks like |
| Coverage-decision accuracy | fraction of points where "above/below threshold" agrees; plus false-covered rate | What the customer actually cares about |

Initial targets (proposals, [requirements.md](requirements.md) NFR-04): calibrated held-out RMSE <= 6 dB,
bias within +/- 2 dB. Literature on indoor propagation typically reports shadow-fading standard
deviations in the several-dB range, so the target is not trivially achievable; set final targets from our
own data.

## 4. Calibration method

Parameters to fit: path-loss exponent `n`, a global offset, and per-material wall losses `L_m`.

Model: `P_rx = P_tx - FSPL(1m) - 10 n log10(d) - sum_m k_m(path) * L_m + c`, where `k_m(path)` is the number of
crossings of material `m` along the path.

* This is **linear in `L_m` and `c`** for fixed `n`, so solve a constrained linear least-squares problem, scanning or optimising `n` (1-D).
* Constraints: `L_m >= 0`, bounded to plausible ranges, and `n` in a plausible range.
* **Regularisation toward priors:** with few measurements, materials are not separable (identifiability). Use a penalty `lambda * ||L - L_prior||^2` where the prior is the literature or placeholder value, so unobserved materials stay near the prior instead of drifting.
* **Report the parameter uncertainty** (e.g. from the Jacobian or bootstrap) and flag materials that the data cannot determine.
* Output is a **new versioned material table** with provenance `measured` and a link to the validation report. The old table is not changed.

Design the measurement campaign for identifiability: samples that cross different wall combinations,
at varied distances, with line-of-sight points to pin down `n`.

## 5. Avoiding leakage (how not to fool ourselves)

* **Split by space, not by random point.** Neighbouring points are correlated; a random split lets the fit "see" the test points. Hold out whole rooms, or whole corridors, or whole APs (leave-one-area-out cross-validation).
* **Split by site** when claiming general accuracy: calibrate on sites A, B; test on site C.
* **Freeze** the pipeline version and parameters before looking at the test set; record the split definition in the report.
* **Do not tune the threshold or target on the test set.**

## 6. Validation levels

| Level | Data | Claim we may make |
|---|---|---|
| L0 | None (current) | "Illustrative. Qualitatively correct behaviour only." |
| L1 | Public/literature values for materials | "Plausible orders of magnitude for stated materials and band." |
| L2 | Measurements on one site, held-out split | "On this site, calibrated RMSE x dB." Not a general claim. |
| L3 | Measurements on >= 3 sites, site-level hold-out | "Across tested sites (list), RMSE x dB, bias y dB, in these environments and bands." |
| L4 | Post-deployment comparison of plans vs as-built performance across customers | A track record. |

The plan artifact records the level reached. The UI and report show it prominently (NFR-13).

## 7. Acceptance test for a model release

A new model or parameter set ships only if, on the frozen benchmark set:

1. Held-out RMSE does not regress against the previous release by more than a stated tolerance.
2. Bias stays within bounds.
3. Coverage-decision false-covered rate does not increase.
4. The validation report is regenerated and committed.

A regression in these is a failing build, like a failing unit test (see [testing-strategy.md](testing-strategy.md)).

## 8. Acquiring data

* **Design partners** (3 target): anonymised measurement + model pairs from real projects, under a data-sharing agreement.
* **Own campaigns:** a floor of a building we can access (e.g. a university floor), measured with a phone app or scanner, positions from floor-plan taps.
* **Public datasets:** indoor propagation datasets from academic literature, where licences permit. `[to be surveyed]`
* **Synthetic ground truth** for software tests only (not for accuracy claims): generate "measurements" from a known model plus noise to check that the calibration code recovers the known parameters.

## 9. What is explicitly not claimed

Until L3 is reached, no document, UI or report may state or imply the numbers predict real dBm values
within a stated accuracy. This is the honest status of v0.1 and is already stated in the main README.
