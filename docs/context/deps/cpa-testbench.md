# Dependency context: `cpa-testbench`

## Purpose
- `cpa-testbench` is a private research testbench scaffold for config-driven experiments, scripts, notebooks, and CI.
- For `cpa-sim`, it is the downstream environment for slower/experimental validations and research comparisons.

## How `cpa-sim` integrates
- Integration points (APIs, file formats, CLI commands):
  - YAML experiment config convention (example: `configs/pipeline.yaml`).
  - Script-level execution entrypoint (`scripts/run_pipeline.py`) designed to load configs and resolve stages from simulation libraries.
  - Notebook-based experimentation (`notebooks/demo.ipynb`).
- Invocation direction and ownership boundaries:
  - `cpa-testbench` invokes simulation packages (`cpa-sim`, potentially `abcdef-sim`) rather than being called as a library by them.
  - Testbench owns experiment orchestration/reporting scaffolding; simulation physics/contracts remain owned by simulation repos.

## Contract assumptions
- Schema/interface assumptions relied on by `cpa-sim`:
  - Testbench can consume stable stage/backend configuration surfaces exposed by `cpa-sim`.
  - Config-driven run entrypoints remain script-first and lightweight.
- Stability level for each assumption (hard/soft):
  - Hard: repository role as testbench scaffold with config + script flow.
  - Soft: exact config schema and script API, currently marked as example/TODO.
- Failure modes and fallback behavior:
  - If config schema drifts, maintain compatibility adapters or versioned config loaders in testbench.
  - If direct stage resolution is not yet available, keep script behavior stubbed while preserving config format contracts.

## Upstream links
- Repository: `deps/cpa-testbench` (workspace clone), upstream `https://github.com/phys-sims/cpa-testbench`.
- Primary docs:
  - `deps/cpa-testbench/README.md`
  - `deps/cpa-testbench/configs/pipeline.yaml`
  - `deps/cpa-testbench/scripts/run_pipeline.py`
- ADRs/specs used as source material: none currently documented in this repo.

## Version policy
- Supported ref range for `cpa-sim`: workspace currently tracks `main` for `cpa-testbench`.
- Pinning strategy (branch/tag/SHA): develop against `main`; pin SHA when freezing reproducible study bundles.
- Upgrade cadence and compatibility checks: sync alongside `cpa-sim` experiment interface changes; run script smoke tests after each update.
