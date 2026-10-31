# site5g documentation

Status: living documents. Last reviewed 2026-10-27. Code baseline: **v0.1.0** (CLI, single storey).

These docs describe where `site5g` is **now** (v0.1) and where it should go to become a
product for **private 5G system integrators and wireless design consultancies**. Every document
marks what is *implemented*, what is *planned*, and what is only a *hypothesis*. If a claim is
not backed by code, a test, a measurement or a cited source, it says so.

## Reading order

| # | Document | Question it answers |
|---|---|---|
| 1 | [product.md](product.md) | Who is this for, what job do they hire it for, what is out of scope, how do we know it works? |
| 2 | [requirements.md](requirements.md) | What exactly must it do (numbered, testable, prioritised)? |
| 3 | [architecture.md](architecture.md) | How is it structured, and why those boundaries? |
| 4 | [domain-model.md](domain-model.md) | What are the core concepts and data, with units and invariants? |
| 5 | [radio-model.md](radio-model.md) | What maths do we use, what does it ignore, how wrong can it be? |
| 6 | [validation-and-calibration.md](validation-and-calibration.md) | How do we *prove* the numbers deserve trust? |
| 7 | [testing-strategy.md](testing-strategy.md) | How do we test numerical, geometric and file-parsing code? |
| 8 | [roadmap.md](roadmap.md) | In what order do we build, and what does "done" mean per phase? |
| 9 | [risks.md](risks.md) | What could kill the project, and what do we do about it? |
| 10 | [contributing.md](contributing.md) | Workflow, quality gates, definition of done |
| - | [adr/](adr/README.md) | One file per significant decision, with alternatives and trade-offs |

## Conventions used everywhere

* **Units are part of every name or type**: `_m`, `_db`, `_dbm`, `_ghz`. dB is a ratio, dBm is
  absolute power; never add two dBm values.
* **Requirement IDs** (`FR-12`, `NFR-04`) are stable. Tests and ADRs cite them.
* **Maturity tags**: `[implemented]`, `[planned: Pn]`, `[hypothesis]`.
* **No silent failure**: where the code skips or guesses something, the docs list it as a gap.

## Known gaps in the current baseline (found while writing these docs)

These are facts about v0.1, not opinions. They feed [requirements.md](requirements.md) and
[roadmap.md](roadmap.md).

1. The IFC loader silently skips walls and rooms it cannot triangulate (`except Exception: continue`
   in `ifc_loader.py`). An integrator would get a plan for a building with missing walls and no warning.
2. `pyproject.toml` declares `requires-python >= 3.10` but CI tests only 3.12 and 3.13.
3. `plan.json` records the configuration but not the tool version, model version or an input file hash,
   so a result cannot be reproduced or audited from the file alone.
4. The loader has only ever read the IFC file this repo generates itself.
5. No linter, type checker or coverage gate is configured.
6. Performance and memory have not been measured; the planner builds a dense candidates x cells matrix.
