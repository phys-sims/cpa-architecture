**Title:** Canonical result schema contract for CPA runs and harness ingestion.

- **ADR ID:** ECO-0002
- **Status:** Proposed
- **Date:** 2026-02-15
- **Deciders:** @cpa-architecture, @cpa-sim, @phys-sims-leads
- **Area:** ecosystem
- **Related:** docs/adr/cpa-adr-writing-context.md (ADR-0002), docs/SYSTEM_OVERVIEW.md
- **Tags:** api, data-model, provenance, testing
- **Scope:** ecosystem
- **Visibility:** public
- **Canonical ADR:** cpa-architecture/docs/adr/ECO-0002-result-schema-contract.md
- **Impacted repos:** cpa-sim, phys-pipeline, phys-sims-utils, cpa-testbench
- **Related ecosystem ADRs:** ECO-0001, ECO-0004

### Context
- **Problem statement.** The ecosystem needs one predictable `result.json` shape across adapters and workflows so sweeps, optimization, dashboards, and regression tests do not branch on backend-specific payloads.
- **In/Out of scope.** In scope: run result contract, artifact policy, failure semantics, versioning and compatibility expectations. Out of scope: notebook visualization choices and private dataset layouts.
- **Constraints.** Must align with `phys-pipeline` metrics/artifact/provenance conventions and deterministic shared contracts in `phys-sims-utils`.

### Options Considered

**Option A — Canonical ecosystem schema with explicit versioning (recommended)**
- **Description:** One required `result.json` top-level schema, with stable required keys and compatibility policy.
- **Impact areas:** cpa-sim output writer, harness adapters, testbench ingestion, compatibility tests.
- **Pros:** Stable ingestion and easier cache/provenance analysis.
- **Cons:** Requires strict governance for key changes.
- **Risks / Unknowns:** Overly rigid if not allowing extension namespaces.
- **Perf/Resource cost:** Low.
- **Operational complexity:** Moderate.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Needs schema checks in CI.

**Option B — Repo-local schema variants with adapter mapping**
- **Description:** Each repo emits its own result payload and adapters normalize later.
- **Impact areas:** harness/testbench adapters and maintenance.
- **Pros:** Local autonomy.
- **Cons:** Adapter sprawl and drift risk.
- **Risks / Unknowns:** Silent semantic mismatch.
- **Perf/Resource cost:** Medium.
- **Operational complexity:** High.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Ongoing adapter updates.

**Option C — Loose JSON with optional keys and no strict versioning**
- **Description:** Minimal required fields; infer semantics by convention.
- **Impact areas:** all consumers.
- **Pros:** Fast to prototype.
- **Cons:** Breaks reproducibility and compatibility guarantees.
- **Risks / Unknowns:** High ingestion fragility.
- **Perf/Resource cost:** Low initial, high long-term.
- **Operational complexity:** High over time.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Requires consumer-specific fallback logic.

### Decision
- **Chosen option:** Option A.
- **Trade‑offs:** We accept formal schema governance to gain deterministic ingestion and robust cross-repo interoperability.
- **Scope of adoption:** All CPA run outputs intended for downstream analysis or automation.

### Canonical `result.json` contract (normative)
Required top-level keys for `schema_version: "cpa.result.v0.1"`:
- `schema_version` (string)
- `status` (`"ok" | "failed"`)
- `unit_system` (string, from ECO-0001)
- `run_id` (string)
- `timestamp_utc` (ISO8601)
- `config_hash` (string; normalized-config hash)
- `provenance` (object)
- `summary` (object of scalar summary values)
- `metrics` (object of scalar metric keys with unit suffix policy)
- `artifacts` (object of artifact references/paths)
- `stages` (array of stage summaries)
- `error` (object|null; required when `status="failed"`)

### Metric and unit policy
- Metric keys must be lowercase snake_case and end with explicit unit suffixes where dimensional (`_fs`, `_um`, `_j`, `_w`, `_rad_per_fs`).
- Dimensionless metrics end in `_ratio` or `_count` where applicable.
- Metrics remain scalar; vectors/grids are artifacts referenced through `artifacts`.

### Artifact and array handling
- Large arrays (time traces, spectra, fields) must be stored as files (`.npz`, `.npy`, `.csv`, images) under run artifact directory and referenced in `artifacts`.
- `metrics` stores only scalar values needed for dashboards/optimization loops.
- Stage summaries include per-stage `stage_config_hash`, `metrics`, and artifact references.

### Failure semantics
- Failed runs **must** still emit schema-valid `result.json` with:
  - `status: "failed"`
  - `error.type`, `error.message`, optional `error.stage`, optional `error.traceback`
  - any available partial `metrics`, `artifacts`, `stages`, and `provenance`

### Versioning and compatibility
- Patch: additive optional keys only.
- Minor: new required fields with transition support for previous minor versions.
- Major: key removal/rename or semantic changes.
- Meaning changes require key rename or schema version bump.

### Provenance and cache invalidation
- Provenance must include at least: repo SHA(s), backend id/version, execution seed, and environment/runtime identifiers.
- Cache reuse is invalidated when normalized config hash, code SHA, or backend version changes.
- Contract aligns with `phys-pipeline` hashing and provenance ADRs.

### Consequences
- **Positive:** Consistent ingestion path across harness/testbench; safer automation and reporting.
- **Negative / Mitigations:** Upfront migration effort; mitigate with phased adapters and compatibility tests.
- **Migration plan:**
  1. Define JSON schema + pydantic model for `cpa.result.v0.1` in cpa-sim.
  2. Add adapter ingestion tests in phys-sims-utils for both success/failure outputs.
  3. Update cpa-testbench scripts to consume only canonical keys and artifact references.
  4. Keep temporary compatibility loader for legacy outputs during one deprecation window.
- **Test strategy:** schema model tests, backward compatibility fixtures, adapter ingestion tests, and failure-path validations.
- **Monitoring & Telemetry:** collect schema version distribution and ingestion failure counts.
- **Documentation:** publish contract doc and migration examples for legacy payloads.

### How we validate
- **Schema model checks:** enforce required top-level keys and key-type contracts.
- **Backward compatibility checks:** fixture corpus from prior minor versions parsed by current loader.
- **Harness ingestion checks:** phys-sims-utils adapter/harness tests ingest canonical success and failure outputs.
- **Failure-path checks:** simulated stage failures still produce schema-valid results with actionable error payloads.

### Alternatives Considered (but not chosen)
- Repo-local schemas with adapters (Option B).
- Permissive unversioned JSON (Option C).

### Open Questions
- Final artifact filename defaults for field/spectrum arrays (`fields.npz` vs stage-specific names) can be standardized in follow-up implementation PR.

### References
- `docs/adr/cpa-adr-writing-context.md` (ADR-0002 context).
- `docs/SYSTEM_OVERVIEW.md` (cross-repo contract boundary).
- `deps/phys-pipeline/src/phys_pipeline/record.py`, `hashing.py`, and ADRs 0005/0006.
- `deps/phys-sims-utils/src/phys_sims_utils/shared/types.py`, harness core and phys-pipeline adapter.
- `deps/phys-sims-utils/docs/adr/0005-run-summary-artifact-schema.md`.
- `deps/cpa-testbench/scripts/run_pipeline.py`.

### Changelog
- `2026-02-15` — Proposed by @openai-codex

---
