# Prompt: Write Proposed ADR-0002 (Result Schema Contract)

You are drafting an ecosystem ADR in `cpa-architecture`.

## Task
Create a **proposed** ADR for the run-result data contract as:
- `docs/adr/ECO-0002-result-schema-contract.md`

Use the existing full ADR style used in this repository.

## Required source context (must read before writing)
From this repo:
- `docs/adr/cpa-adr-writing-context.md` (ADR-0002 section + placeholders)
- `docs/adr/_template-full.md`
- `docs/SYSTEM_OVERVIEW.md`

From dependency repos (must reference concretely in rationale):
- `deps/phys-pipeline/src/phys_pipeline/types.py`
- `deps/phys-pipeline/src/phys_pipeline/record.py`
- `deps/phys-pipeline/src/phys_pipeline/hashing.py`
- `deps/phys-pipeline/docs/adr/0005-artifact-recording.md`
- `deps/phys-pipeline/docs/adr/0006-provenance-and-namespace.md`
- `deps/phys-sims-utils/src/phys_sims_utils/harness/core.py`
- `deps/phys-sims-utils/src/phys_sims_utils/harness/adapters/phys_pipeline.py`
- `deps/phys-sims-utils/docs/adr/0005-run-summary-artifact-schema.md`
- `deps/cpa-testbench/scripts/run_pipeline.py`

## Decision constraints
The ADR must define:
1. Canonical `result.json` top-level schema and required keys.
2. Metric naming conventions + unit suffix policy.
3. Artifact layout + array handling policy (`metrics` vs files).
4. Failure semantics (schema-valid outputs even for failed runs).
5. Schema versioning and compatibility expectations.
6. Provenance and cache invalidation expectations across repos.

## Validation section requirements
Include concrete validation expectations for:
- schema model checks,
- backward compatibility checks,
- ingestion checks in harness tooling,
- failure-path checks.

## Output quality bar
- Status: **Proposed**.
- Include alternatives (single schema vs repo-local schemas, strict vs permissive versioning, etc.).
- Include migration plan with phased rollout and deprecation window.
- Include explicit "impacted repos" list.
