# Dependency context: `abcdef-sim`

## Purpose
- `abcdef-sim` is an architecture-first simulation scaffold for frequency-dependent ABCDEF optics built on top of `phys-pipeline`.
- For `cpa-sim`, it is the intended free-space backend surface for grating/optics chain assembly and execution.

## How `cpa-sim` integrates
- Integration points (APIs, file formats, CLI commands):
  - Python package dependency (`abcdef-sim`) with typed data + pipeline assembly surfaces.
  - Intended assembly/runtime interfaces include `SystemPreset`, `OpticSpec`, `LaserSpec`, `SystemAssembler`, and `AbcdefOpticStage` style wrappers.
  - No stable CLI contract is documented in the current upstream README/docs.
- Invocation direction and ownership boundaries:
  - `cpa-sim` should call into `abcdef-sim` as a backend adapter for free-space stages.
  - `abcdef-sim` owns optics models, cfg generation, and pipeline wiring for its domain.

## Contract assumptions
- Schema/interface assumptions relied on by `cpa-sim`:
  - Config/state split is explicit (immutable spec models vs mutable runtime state).
  - Assembly is driven by laser grid + policy and produces stage configs aligned to omega grid.
  - Pipeline execution is delegated through `phys-pipeline` contracts.
- Stability level for each assumption (hard/soft):
  - Hard: package exists and targets ABCDEF optics + `phys-pipeline` integration.
  - Soft: exact class/module names and stage internals, because upstream marks parts of architecture as planned/future work.
- Failure modes and fallback behavior:
  - If assembly/stage APIs change, `cpa-sim` should keep a local backend adapter boundary and pin to a known-good ref.
  - If placeholder stage physics remains incomplete upstream, keep `cpa-sim` free-space backend behind feature flags or backend selection.

## Upstream links
- Repository: `deps/abcdef-sim` (workspace clone), upstream `https://github.com/phys-sims/abcdef-sim`.
- Primary docs:
  - `deps/abcdef-sim/README.md`
  - `deps/abcdef-sim/docs/architecture.md`
  - `deps/abcdef-sim/docs/how-to-use.md`
- ADRs/specs used as source material:
  - `deps/abcdef-sim/docs/adr/INDEX.md`

## Version policy
- Supported ref range for `cpa-sim`: workspace currently tracks `main` for `abcdef-sim`.
- Pinning strategy (branch/tag/SHA): develop against `main` in workspace; pin SHA for reproducible releases/integration gates.
- Upgrade cadence and compatibility checks: update on demand when `cpa-sim` free-space integration advances; re-run `cpa-sim` adapter/integration tests on each bump.
