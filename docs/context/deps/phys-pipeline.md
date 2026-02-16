# Dependency context: `phys-pipeline`

## Purpose
- `phys-pipeline` is the shared runtime framework for typed physics simulation pipelines, sequential and DAG execution, provenance, and caching hooks.
- `cpa-sim` consumes it as foundational execution infrastructure rather than implementing its own executor stack.

## How `cpa-sim` integrates
- Integration points (APIs, file formats, CLI commands):
  - Python package dependency (`phys-pipeline`) used for stage/state/result abstractions and pipeline execution.
  - Core interfaces include stage contracts (`PipelineStage`, `StageConfig`, `StageResult`), sequential runtime, and optional DAG/scheduler/caching surfaces.
  - No CLI integration is required for normal `cpa-sim` usage.
- Invocation direction and ownership boundaries:
  - `cpa-sim` implements domain stages/configs and calls `phys-pipeline` for orchestration and execution semantics.
  - `phys-pipeline` owns generic runtime contracts, typing guarantees, and executor behavior.

## Contract assumptions
- Schema/interface assumptions relied on by `cpa-sim`:
  - Typed stage/state/result protocol is stable enough for backend wrappers.
  - Policy propagation and provenance/caching semantics remain explicit.
  - Sequential baseline remains available even as DAG features evolve.
- Stability level for each assumption (hard/soft):
  - Hard: package scope and core role as pipeline runtime.
  - Soft: advanced DAG/scheduler/cache APIs may evolve across major versions.
- Failure modes and fallback behavior:
  - If advanced APIs drift, keep `cpa-sim` on sequential pipeline mode and gate DAG-only features.
  - If stage typing contracts change, adjust adapter layers in `cpa-sim` and run contract tests before bumping dependency.

## Upstream links
- Repository: `deps/phys-pipeline` (workspace clone), upstream `https://github.com/phys-sims/phys-pipeline`.
- Primary docs:
  - `deps/phys-pipeline/README.md`
  - `deps/phys-pipeline/docs/how-to-build-simulations.md`
  - `deps/phys-pipeline/docs/v2-performance.md`
- ADRs/specs used as source material:
  - `deps/phys-pipeline/docs/adr/INDEX.md`

## Version policy
- Supported ref range for `cpa-sim`: workspace currently tracks `main`; upstream package version in repo is `2.0.0`.
- Pinning strategy (branch/tag/SHA): iterate on `main` in workspace; pin tags/SHAs for release branches and reproducible runs.
- Upgrade cadence and compatibility checks: monitor `phys-pipeline` major/minor updates; run `cpa-sim` stage contract + pipeline integration tests on each bump.
