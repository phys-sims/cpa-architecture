**Title:** Validation tiers and CI execution policy for CPA ecosystem repos.

- **ADR ID:** ECO-0003
- **Status:** Proposed
- **Date:** 2026-02-15
- **Deciders:** @cpa-architecture, @cpa-sim, @phys-sims-leads
- **Area:** ecosystem
- **Related:** docs/adr/cpa-adr-writing-context.md (ADR-0003), ECO-0004
- **Tags:** testing, ci, reproducibility, ops
- **Scope:** ecosystem
- **Visibility:** public
- **Canonical ADR:** cpa-architecture/docs/adr/ECO-0003-validation-tiers-ci-policy.md
- **Impacted repos:** cpa-sim, phys-pipeline, phys-sims-utils, cpa-testbench
- **Related ecosystem ADRs:** ECO-0001, ECO-0002, ECO-0004

### Context
- **Problem statement.** Current tests include placeholders and mixed runtime intent; the ecosystem needs explicit test tiers so PR gates remain fast while preserving rigorous theoretical and experimental validation.
- **In/Out of scope.** In scope: tier definitions, marker strategy, CI command lines, tolerance ownership, and required validation outputs. Out of scope: specific lab dataset choices.
- **Constraints.** Must preserve determinism expectations from harness tests and DAG/cache behavior while avoiding PR-time execution of expensive experimental workflows.

### Options Considered

**Option A — Tiered policy with marker-based CI partitioning (recommended)**
- **Description:** Define Tier 0/1/2 by goal and runtime cost; gate Tier 0 on PR, run Tier 1 nightly/manual, keep Tier 2 manual/report-driven.
- **Impact areas:** pytest markers, workflow split, tolerance governance, reporting.
- **Pros:** Fast PR feedback plus high-value deeper validation.
- **Cons:** Requires discipline to keep marker hygiene current.
- **Risks / Unknowns:** Mis-marked tests may leak slow physics checks into PR gate.
- **Perf/Resource cost:** Low for PR, moderate for scheduled jobs.
- **Operational complexity:** Moderate.
- **Security/Privacy/Compliance:** Tier 2 data provenance controls needed when private datasets are involved.
- **Dependencies / Externalities:** Workflow support in each repo.

**Option B — Run all tests on every PR**
- **Description:** No tier partition; everything blocks merges.
- **Impact areas:** CI runtime and developer velocity.
- **Pros:** Maximum immediate coverage.
- **Cons:** Slow/flaky gates; poor throughput.
- **Risks / Unknowns:** Teams bypass tests due queue pressure.
- **Perf/Resource cost:** High.
- **Operational complexity:** High.
- **Security/Privacy/Compliance:** None specific.
- **Dependencies / Externalities:** Requires large compute budget.

**Option C — Minimal PR smoke only, no formal tiers**
- **Description:** Keep only smoke tests in CI; run deeper checks ad hoc.
- **Impact areas:** regression detection and confidence.
- **Pros:** Fast PR cycle.
- **Cons:** Missed physics regressions and drift.
- **Risks / Unknowns:** Quality debt accumulates quickly.
- **Perf/Resource cost:** Low.
- **Operational complexity:** Low short-term, high long-term.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Heavy reliance on manual discipline.

### Decision
- **Chosen option:** Option A.
- **Trade‑offs:** We accept marker/process overhead to preserve deterministic, scalable validation without blocking development.
- **Scope of adoption:** All ecosystem repos with automated tests.

### Tier definitions and CI policy (normative)
- **Tier 0 (unit/mechanics):** deterministic software correctness and fast invariants; PR-gated.
- **Tier 1 (theoretical regression):** pinned golden comparisons against canonical solver/analytic references; nightly or manual unless runtime proves PR-feasible.
- **Tier 2 (experimental comparison):** paper/lab alignment with uncertainty reporting; manual/report workflows, not PR-gated.

### Marker strategy and expected commands
- Required markers: `unit`, `physics`, `slow`, `integration`.
- PR gate command baseline:
  - `python -m pytest -q -m "not slow and not physics" --durations=10`
- Nightly/manual theoretical command baseline:
  - `python -m pytest -q -m "physics" --durations=10`
- Optional scheduled slow suite:
  - `python -m pytest -q -m "slow" --durations=10`

### Tolerance policy and ownership
- Tier 0: tight deterministic tolerances (exact or very small relative tolerance).
- Tier 1: metric-specific tolerances owned near canonical test fixtures.
- Tier 2: uncertainty-aware tolerances documented with dataset source and fit method.
- Tolerances must be version-controlled and reviewed with test updates.

### Required validation outputs
Each Tier 1 and Tier 2 run must emit structured validation records containing:
- tier id
- reference case id/citation
- compared metrics + tolerance values
- pass/fail with numeric deltas
- provenance (repo SHAs, backend versions, seed, timestamp)

Recommended files: `validation_report.json` plus optional `validation_report.md` and plots.

### Consequences
- **Positive:** Better signal-to-cost ratio in CI; explicit confidence ladder.
- **Negative / Mitigations:** Marker drift/flakiness risk; mitigate with periodic audit and deterministic seeding requirements.
- **Migration plan:**
  1. Add markers to current placeholder and existing tests in cpa-sim/phys-pipeline/phys-sims-utils.
  2. Split CI workflows into PR vs nightly/manual jobs per marker policy.
  3. Introduce first canonical Tier 1 fiber and free-space golden cases with pinned tolerances.
  4. Add Tier 2 report-generation workflows in cpa-testbench.
- **Test strategy:** enforce deterministic seed behavior, golden regression diffs, and report schema checks.
- **Monitoring & Telemetry:** track flaky test counts, suite durations, and marker distribution trends.
- **Documentation:** update STATUS/testing sections in each impacted repo.

### How we validate
- **Deterministic behavior:** verify same seed produces identical sweep ordering/results (phys-sims-utils determinism tests).
- **Golden regression diffs:** Tier 1 runs must print/reference numeric baseline deltas.
- **Experimental boundaries:** Tier 2 workflows must emit report artifacts with provenance and uncertainty metadata.

### Alternatives Considered (but not chosen)
- All tests on every PR (Option B).
- Smoke-only PR policy without formal tiers (Option C).

### Open Questions
- Exact first canonical free-space and fiber golden fixtures for Tier 1 should be finalized in cpa-sim implementation PRs.

### References
- `docs/adr/cpa-adr-writing-context.md` (ADR-0003 context).
- `docs/adr/ECO-0004-repository-roles-boundaries.md`.
- `deps/cpa-sim/STATUS.md` and placeholder tests under `deps/cpa-sim/tests`.
- `deps/phys-pipeline/tests/test_smoke.py`, `test_dag_integration.py`, and ADR-0012 testing strategy.
- `deps/phys-sims-utils/tests/test_end_to_end_dummy_example.py`, `test_sweep_determinism.py`.
- `deps/cpa-testbench/tests/test_e2e.py`.

### Changelog
- `2026-02-15` — Proposed by @openai-codex

---
