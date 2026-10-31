# Contributing and engineering workflow

Status: **target process.** Today the repo has pytest and one CI workflow. The tools below marked
`[to add]` are not yet configured; adding them is part of roadmap phase P0.

## 1. Setup

```bash
python3.11 -m venv .venv && source .venv/bin/activate     # Python >= 3.10 (the default macOS python3 may be 3.9: too old)
pip install -e ".[dev]"
pytest -q
site5g plan examples/sample_office.ifc --out out
```

## 2. Workflow

* **Trunk-based development with short-lived branches.** `main` is always releasable. One logical change per pull request, ideally under 400 changed lines.
* Branch names: `feat/...`, `fix/...`, `docs/...`, `refactor/...`.
* **Commit messages:** imperative subject <= 72 chars, body explains *why*. Reference requirement or ADR IDs (`FR-02`, `ADR-0003`).
* **Every behavioural change** updates tests and, if it changes a decision or a contract, the relevant doc or ADR in the same PR.
* **Reviews:** at least one reviewer for core/model changes; while there is a single maintainer, use a self-review checklist (below) and a 24-hour cool-off for anything that changes numerical results.

## 3. Quality gates (CI must pass to merge)

| Gate | Tooling | Status |
|---|---|---|
| Tests on all declared Python versions (3.10-3.13) and Linux/macOS/Windows | pytest, CI matrix | partial (CI: 3.12, 3.13, Linux only) |
| Lint and format | ruff `[to add]` | - |
| Static types on core packages | mypy or pyright, strict on `core` `[to add]` | - |
| Coverage >= 85% on core | pytest-cov `[to add]` | - |
| Architecture boundaries (core imports no adapters) | import-linter `[to add]` | - |
| Property-based tests | hypothesis `[to add]` | - |
| Golden `plan.json` determinism test | pytest | - |
| Plan the sample floor end to end | CI step | done |
| Dependency and licence audit | pip-audit, licence checker `[to add]` | - |
| Schema validation of emitted artifacts | jsonschema `[to add]` | - |
| Nightly: benchmarks, fuzzing, validation suite | scheduled workflow `[to add]` | - |

## 4. Coding standards

* **Core is pure:** no file, network, plotting or global state in `core` modules. Side effects live in adapters.
* **Units in names:** `distance_m`, `power_dbm`, `loss_db`, `freq_ghz`. Never a bare `float` for a physical quantity in a public signature without a unit in the name or type.
* **Immutability by default:** frozen dataclasses for domain objects.
* **Type hints everywhere** in public APIs; arrays documented with shape and unit in the docstring.
* **No silent failure:** do not use bare `except Exception: continue`. Catch specific exceptions, record a structured warning, continue only if the requirements say so.
* **Determinism:** no unseeded randomness; iteration order over dicts/sets must not affect results; ties broken explicitly.
* **Comments explain why, not what.** Keep the existing style: the maths and assumptions explained next to the code that uses them.
* **Errors** use the error taxonomy in [architecture.md](architecture.md) section 11 with actionable messages.
* **Numerics:** compare with tolerances, never `==`; document tolerances.
* **Dependencies:** each new dependency needs a reason, a licence check and a pin; prefer the standard library and the existing stack.

## 5. Definition of done

A change is done when:

- [ ] It satisfies the cited requirement(s) and their verification method is automated.
- [ ] Tests cover the happy path, edge cases, and a regression for any bug fixed.
- [ ] Lint, types and coverage gates pass; no new warnings.
- [ ] Public behaviour is documented; docs and ADRs are updated.
- [ ] Results that change numbers are explained, and golden files updated deliberately with a stated reason.
- [ ] Error paths return structured errors; limits and timeouts are considered for untrusted input.
- [ ] Performance impact checked against the benchmark if it touches hot paths.
- [ ] Security and privacy considered if it touches uploads, storage, or logs (no confidential content in logs).
- [ ] Changelog entry for user-visible changes.

## 6. Self-review checklist (numerical changes)

1. Did I verify units on every quantity I touched?
2. Is there an independent oracle (hand calculation or standard) for the new behaviour?
3. Did the change alter any existing result, and do I know exactly why?
4. Did I test the edge geometry (touching, parallel, zero length)?
5. Does the model's version need to change because results changed?
6. Does the plan artifact still record everything needed to reproduce this?

## 7. Architecture decisions

Any decision that is hard to reverse, affects several modules, or trades off qualities gets an ADR in
[adr/](adr/README.md) *before or with* the implementation. Superseding a decision means writing a new ADR, not editing the old one.

## 8. Versioning and releases

* **Semantic versioning** for the package. The plan artifact schema and each propagation model have their own versions.
* A release requires: green CI on the full matrix, regenerated validation report (when models changed), updated changelog, tagged commit, reproducible build (pinned dependencies / lock file).
* Pre-1.0: minor versions may break the CLI/API but must not break artifact readability without a migration note.

## 9. Security practices

* Never commit customer models, measurements or secrets. Examples in the repo are synthetic or licence-cleared.
* Treat every input file as hostile ([architecture.md](architecture.md) section 9).
* Report vulnerabilities privately to the maintainer; fix before disclosure.
* Pin dependencies, review updates, run audits in CI.

## 10. Documentation

Docs live in `docs/` and are reviewed like code. A document that disagrees with the code is a bug:
fix one or the other in the same PR. Each document keeps its maturity tags (`[implemented]`,
`[planned]`, `[hypothesis]`) accurate.
