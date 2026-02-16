# Dependency context: `phys-sims-utils`

## Purpose
- `phys-sims-utils` provides shared deterministic experimentation infrastructure (harness, optimization strategies, canonical result contracts, and agent tooling).
- For `cpa-sim`, it is an optional integration surface for sweeps/optimization/reporting and reproducibility-oriented tooling.

## How `cpa-sim` integrates
- Integration points (APIs, file formats, CLI commands):
  - Python package dependency (optional extras by capability: harness/ml/agent).
  - Typed optimization and parameter-space interfaces (`Parameter`, `ParameterSpace`, strategy ask/tell patterns).
  - Canonical experiment/result artifacts for downstream analysis.
- Invocation direction and ownership boundaries:
  - `cpa-sim` can expose adapters that feed simulation evaluations into `phys-sims-utils` harness/ML workflows.
  - `phys-sims-utils` owns generic experiment orchestration contracts and must remain simulation-agnostic.

## Contract assumptions
- Schema/interface assumptions relied on by `cpa-sim`:
  - Deterministic execution expectations (seeded strategy behavior, canonical result contracts).
  - Optional-dependency boundary: direct `phys-pipeline` coupling is adapter-scoped in `phys-sims-utils`.
  - Extras-based install model enables lean dependency footprints.
- Stability level for each assumption (hard/soft):
  - Hard: repository purpose and optional-dependency boundary policy.
  - Soft: specific strategy/catalog details and higher-level helper APIs can evolve.
- Failure modes and fallback behavior:
  - If optional ML deps are absent, `cpa-sim` integrations should degrade to baseline/non-ML workflows.
  - If adapter contracts evolve, keep adapter code isolated and version-gated in integration layers.

## Upstream links
- Repository: `deps/phys-sims-utils` (workspace clone), upstream `https://github.com/phys-sims/phys-sims-utils`.
- Primary docs:
  - `deps/phys-sims-utils/README.md`
  - `deps/phys-sims-utils/docs/how-to-use-harness.md`
  - `deps/phys-sims-utils/docs/how-to-add-optimizer.md`
  - `deps/phys-sims-utils/docs/how-to-write-adapter.md`
- ADRs/specs used as source material:
  - `deps/phys-sims-utils/docs/adr/INDEX.md`

## Version policy
- Supported ref range for `cpa-sim`: workspace currently tracks `main`; upstream package version in repo is `0.4.0`.
- Pinning strategy (branch/tag/SHA): use `main` during active integration, then pin SHA/tag per experiment or release branch.
- Upgrade cadence and compatibility checks: review on each tooling/optimization integration change; run deterministic regression checks for seeded workflows after upgrades.
