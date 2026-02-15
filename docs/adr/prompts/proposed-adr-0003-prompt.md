# Prompt: Write Proposed ADR-0003 (Validation Tiers & CI Policy)

You are drafting an ecosystem ADR in `cpa-architecture`.

## Task
Create a **proposed** ADR for validation tiers and CI policy as:
- `docs/adr/ECO-0003-validation-tiers-ci-policy.md`

Use the existing full ADR style used in this repository.

## Required source context (must read before writing)
From this repo:
- `docs/adr/cpa-adr-writing-context.md` (ADR-0003 section + placeholders)
- `docs/adr/_template-full.md`
- `docs/adr/ECO-0004-repository-roles-boundaries.md`

From dependency repos (must reference concretely in rationale):
- `deps/cpa-sim/STATUS.md`
- `deps/cpa-sim/tests/test_placeholder.py`
- `deps/cpa-sim/tests/unit/stages/amp_placeholder.py`
- `deps/cpa-sim/tests/physics/stages/fiber_placeholder.py`
- `deps/phys-pipeline/tests/test_smoke.py`
- `deps/phys-pipeline/tests/test_dag_integration.py`
- `deps/phys-pipeline/docs/adr/0012-testing-strategy.md`
- `deps/phys-sims-utils/tests/test_end_to_end_dummy_example.py`
- `deps/phys-sims-utils/tests/test_sweep_determinism.py`
- `deps/cpa-testbench/tests/test_e2e.py`

## Decision constraints
The ADR must explicitly define:
1. Tier 0/1/2 goals and scope boundaries.
2. Which tiers are PR-gated vs nightly/manual.
3. Marker strategy and expected CI command lines.
4. Tolerance policy and where tolerances live.
5. Required structured validation outputs and provenance fields.

## Validation section requirements
Add "How we validate" with explicit checks for:
- deterministic test behavior,
- golden regression diffs,
- experimental-report generation boundaries.

## Output quality bar
- Status: **Proposed**.
- Include alternatives (all-in-PR vs tiered execution, no markers vs marker-based policy).
- Include migration plan for introducing markers and moving slow tests.
- Include risks and mitigations for flaky/non-deterministic tests.
