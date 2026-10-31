# Radio model

Status: section 2 is **implemented** in `propagation.py` and `planner.py`. Sections 4-8 are planned
extensions. **No part of the model has been validated against measurements.** The wall attenuation
numbers are illustrative placeholders (see `materials.py`).

## 1. What the model answers

Given a floor with walls and rooms and one or more access points, estimate the **received power** at
points in the rooms, then decide where it is above a required threshold. It is a *coverage* model.
It is not (yet) a capacity, interference or throughput model.

## 2. Current model (v0.1)

For access point A and receiver point R:

```
P_rx (dBm) = P_tx (dBm, includes antenna gain) - PL(d) - L_walls

PL(d)      = FSPL(1 m) + 10 * n * log10(max(d, 1 m))
FSPL(1 m)  = 20 * log10(4 * pi * f / c)
L_walls    = sum over walls whose centre-line the straight segment A->R crosses of attenuation_db(wall)
```

| Symbol | Meaning | Unit | Default | Where |
|---|---|---|---|---|
| `f` | carrier frequency | Hz (config in GHz) | 3.5 GHz | `PlanConfig.freq_ghz` |
| `P_tx` | AP transmit power incl. antenna gain (EIRP-like) | dBm | 23 | `tx_power_dbm` |
| `n` | path-loss exponent | - | 3.0 | `path_loss_exponent` |
| `d` | 2-D distance A-R, clamped to >= 1 m | m | - | `received_power_dbm` |
| `attenuation_db` | per-crossing wall loss | dB | by material | `materials.py` |
| threshold | min received power to count as covered | dBm | -70 | `threshold_dbm` |

Sanity check: `FSPL(1 m)` at 3.5 GHz is `20 log10(4 pi 3.5e9 / 3e8)` = 43.3 dB. This is a golden value in the tests.

**Best server:** at each point the strongest AP wins; coverage uses that power.

**Wall crossing test:** vectorised segment-segment intersection of A->R against each wall centre-line;
each intersected wall counts once. Thickness is not used in the loss (a documented simplification).

**Material lookup:** lower-cased IFC material names are substring-matched against a keyword table;
a layered wall sums the distinct matched keywords; unmatched walls use `UNKNOWN_DB = 6 dB`.

## 3. Assumptions and what the model ignores

| Ignored effect | Typical consequence | Mitigation (planned) |
|---|---|---|
| Reflection, diffraction, waveguiding in corridors | Underestimates signal along corridors and around corners; overestimates sharp shadows | Ray-tracing option (later); calibrated exponent per zone |
| Angle of incidence and wall thickness | A grazing ray through a wall suffers more than a perpendicular one | Thickness- or angle-aware loss (P3) |
| Floors and ceilings | Single storey only | Multi-storey with floor loss (P3) |
| Antenna pattern and mounting height | Omni, 2-D | Equipment catalogue and patterns (P3) |
| Furniture, machinery, people, racking | Industrial sites differ greatly from offices | Zone-specific exponent; calibration |
| Shadow fading (random variation) | A point prediction hides a spread of several dB | Report uncertainty / fade margin (FR-14) |
| Interference between APs | Coverage is not capacity | SINR model (P3) |
| Uplink | UE transmits at lower power than the AP; uplink often limits | Uplink budget (P3) |
| Frequency dependence of wall loss | Placeholders are for roughly 3.5 GHz only | Per-band material table |
| Windows and low-e glass, metal studs, rebar | Large per-building variation | Measured values and calibration |

## 4. The threshold is not RSRP

`threshold_dbm = -70` is a generic "usable signal" level. 3GPP RSRP is the average power of a single
reference-signal resource element, which is much lower than total received power over the channel.
Do not compare our threshold to an RSRP target without converting. Until the SINR model exists, the
honest statement is "predicted received power exceeds -70 dBm (model units)", not "RSRP is good".
Which quantity customers specify (RSRP, SINR, throughput, latency) is a discovery question
([product.md](product.md) section 8).

## 5. Downlink versus uplink

A cell can have strong downlink and unusable uplink. A first uplink check, per point:

```
P_rx_AP (dBm) = P_tx_UE (dBm) + G_UE (dBi) + G_AP (dBi) - PL(d) - L_walls
covered_UL    = P_rx_AP >= sensitivity_AP (dBm)
```

Assuming path reciprocity (same path loss both ways), the planner should require both links. UE
power classes and AP sensitivity come from the equipment catalogue; they are inputs, not constants.

## 6. Standard model option: 3GPP TR 38.901 Indoor-Office

Planned as a selectable model (FR-11), giving integrators a reference they recognise. For the
indoor-office (mixed office) scenario the spec gives, with `d_3D` in metres and `f_c` in GHz:

```
PL_LOS  = 32.4 + 17.3 * log10(d_3D) + 20 * log10(f_c)
PL_NLOS = max(PL_LOS, 38.3 * log10(d_3D) + 17.30 + 24.9 * log10(f_c))
```

Shadow-fading standard deviations are given in the spec for LOS and NLOS. **Verify the formulas and the
validity range against the current TR 38.901 text before implementing**; this document is a plan, not a
substitute for reading the standard. The model has no concept of individual walls, so it would be used
either alone (generic) or combined with wall loss as a documented, validated hybrid.

## 7. Uncertainty

Predictions should carry a margin. Sources, in decreasing importance for indoor sites:

1. Material attenuation error (placeholder values can be off by many dB).
2. Unmodelled propagation effects (section 3).
3. Geometry import error (missing walls, wrong thickness).
4. Measurement error when calibrating (device, orientation, body).

Approach: estimate residual standard deviation `sigma` on held-out measurements
([validation-and-calibration.md](validation-and-calibration.md)); report coverage as
`P(P_rx >= threshold)` or apply a fade margin of `k * sigma` for a target confidence. Never present a
point prediction as exact.

## 8. Model interface and versioning

Models implement one interface ([architecture.md](architecture.md) section 7, [ADR-0003](adr/0003-pluggable-propagation-model.md)),
declare an `id`, a `version`, and a **valid range** (frequency, distance, environment). Any change to
the formula, defaults or numerical behaviour bumps the version, because it changes results. The plan
artifact records the model id and version.

Candidate models:

| Id | Description | Status |
|---|---|---|
| `simple-wall` | Current model (log-distance + wall crossings) | implemented as v0.1 behaviour |
| `3gpp-inh` | TR 38.901 Indoor-Office | planned P2 |
| `calibrated-wall` | `simple-wall` with parameters fitted to measurements | planned P2 |
| `multi-wall-floor` | Adds floor/ceiling loss, 3-D distance (COST 231 style multi-wall-and-floor idea) | planned P3 |
| `ray-tracing` | Image or shooting-and-bouncing rays on the site geometry | exploratory, post-P4 |

## 9. Numerical considerations

* Work in dB/dBm for sums; convert to linear power (mW) only for combining interference (SINR).
* Clamp distances at the 1 m reference to avoid `log10(0)`.
* Parallel or degenerate segments are rejected by a tolerance on the cross product (`1e-12`); touching a wall endpoint counts as a crossing. Behaviour at exact wall endpoints should be covered by tests so results are stable.
* Float32 may be used for large grids (memory) once tests prove the differences are far below 0.1 dB.
