# `cpa-sim` v1 development prerequisites

This note answers a single question: **what context from `phys-pipeline` and `phys-sim-utils` must be explicit before implementation starts?**

Use this as a preflight checklist for `cpa-sim` v1 planning and kickoff.

## 1) Required context from `phys-pipeline`

### Runtime and contract baseline (must be pinned)
- Confirm `cpa-sim` will use `phys-pipeline` as the execution runtime (not a custom executor).
- Pin the baseline capability level to sequential execution first; treat DAG/scheduler/cache acceleration as opt-in.
- Record the minimum accepted version/ref in `cpa-sim` planning docs.

### Type and stage boundary assumptions (must be documented)
- Lock the stage contract expectations `cpa-sim` relies on (stage config, stage input/output typing, result envelope).
- Define where `cpa-sim` owns adaptation versus where `phys-pipeline` remains the source of truth.
- Capture expected error behavior at stage boundaries so failing stage adapters are diagnosable.

### Provenance and reproducibility hooks (must be consumed)
- Decide which pipeline provenance fields `cpa-sim` will pass through into its own result model.
- Decide whether cache keys and metadata are surfaced directly or normalized through a `cpa-sim` adapter.
- Ensure the v1 result contract keeps enough execution metadata for deterministic reruns.

### Compatibility risk posture (must be agreed)
- Treat advanced `phys-pipeline` APIs as soft dependencies for v1.
- Require adapter-level compatibility tests before any dependency bump.
- Keep a fallback path that remains functional in sequential-only mode.

## 2) Required context from `phys-sim-utils`

### Optional integration boundary (must be explicit)
- Confirm `phys-sim-utils` is optional for `cpa-sim` core runtime.
- Define the integration entrypoints as adapter surfaces (harness/optimization/reporting), not core simulation logic.
- Keep installation extras and capability detection explicit so v1 stays lean by default.

### Canonical experiment/result model alignment (must be mapped)
- Map `cpa-sim` outputs to `phys-sim-utils` canonical evaluation/result structures.
- Decide which metrics, objective values, and provenance fields are required for first-party sweeps.
- Document any transformation layer between `cpa-sim` native outputs and harness-compatible outputs.

### Determinism requirements (must be testable)
- Require seeded execution paths for any `cpa-sim` workflow integrated with strategies/sweeps.
- Define repeatability tolerances and expected stable ordering for generated records.
- Add contract checks that the same config + seed yields stable adapter outputs.

### Degradation behavior (must be designed)
- If optional ML/optimizer dependencies are missing, integrations must degrade gracefully.
- Keep fallback behavior explicit (for example: disable optimization runners, keep baseline evaluation).
- Avoid embedding simulation-specific assumptions inside shared `phys-sim-utils` core contracts.

## 3) Cross-dependency context `cpa-sim` needs before coding

Before v1 implementation begins, the team should capture these decisions in one place:

1. **Dependency stance:** which features are hard requirements versus optional integrations.
2. **Adapter boundaries:** exactly where `cpa-sim` touches each dependency.
3. **Result/provenance contract:** the minimal metadata that must survive through pipeline + harness layers.
4. **Determinism guarantees:** seeds, tolerance rules, and rerun expectations.
5. **Upgrade policy:** when dependency bumps are allowed and what compatibility tests gate them.

If any item is unknown, mark it `TBD` and block corresponding implementation work until resolved.

## 4) Suggested first implementation artifacts

- A `cpa-sim` dependency policy note (versions/pins + optional extras policy).
- A thin `phys-pipeline` adapter contract test suite (sequential baseline first).
- A thin `phys-sim-utils` harness adapter mapping doc + deterministic smoke test.
- A v1 compatibility matrix that tracks supported refs for both dependencies.

## Related context docs
- `docs/context/deps/phys-pipeline.md`
- `docs/context/deps/phys-sim-utils.md`
- `docs/context/reading-list.md`
