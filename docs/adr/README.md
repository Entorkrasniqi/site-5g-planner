# Architecture Decision Records

An ADR captures **one** significant decision: the context, the options considered, the choice, and the
consequences, including the downsides. They are append-only; to change a decision write a new ADR that
supersedes the old one.

**Statuses:** `Proposed` (under review) / `Accepted` (in force) / `Superseded by ADR-xxxx` / `Rejected`.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-python-numpy-core.md) | Python + NumPy/Shapely for the computational core | Accepted (describes v0.1) |
| [0002](0002-canonical-site-model.md) | A canonical Site Model decouples importers from the planner | Proposed |
| [0003](0003-pluggable-propagation-model.md) | Propagation models behind one interface, versioned | Proposed |
| [0004](0004-greedy-placement-with-exact-benchmark.md) | Greedy placement as default, exact solver as benchmark | Accepted (describes v0.1), benchmark Proposed |
| [0005](0005-plan-artifact-contract.md) | The plan is a versioned, provenance-carrying artifact | Proposed |
| [0006](0006-api-first-thin-clients.md) | Core library first; API next; CLI and web as thin clients | Proposed |
| [0007](0007-calibration-first-class.md) | Calibration and validation are first-class features | Proposed |

## Template

```markdown
# ADR-NNNN: Title

- Status: Proposed | Accepted | Superseded by ADR-xxxx | Rejected
- Date: YYYY-MM-DD
- Related: requirement IDs, other ADRs

## Context
What forces are at play? What problem, constraints, and quality attributes matter?

## Options considered
1. Option A: pros / cons
2. Option B: pros / cons

## Decision
What we chose and the main reason.

## Consequences
Good, bad, and neutral results. What becomes easier, what harder. Follow-up work.

## Revisit when
Concrete conditions under which we reopen this.
```
