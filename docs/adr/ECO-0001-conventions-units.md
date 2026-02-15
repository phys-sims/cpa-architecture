**Title:** Conventions and units contract for CPA simulation inputs, state, and outputs.

- **ADR ID:** ECO-0001
- **Status:** Proposed
- **Date:** 2026-02-15
- **Deciders:** @cpa-architecture, @cpa-sim, @phys-sims-leads
- **Area:** ecosystem
- **Related:** docs/adr/cpa-adr-writing-context.md (ADR-0001)
- **Tags:** api, data-model, physics, testing
- **Scope:** ecosystem
- **Visibility:** public
- **Canonical ADR:** cpa-architecture/docs/adr/ECO-0001-conventions-units.md
- **Impacted repos:** cpa-sim, phys-pipeline, phys-sims-utils, cpa-testbench
- **Related ecosystem ADRs:** ECO-0004

### Context
- **Problem statement.** Current CPA repos have placeholder stage implementations and evolving contracts; without explicit unit/sign conventions, physics outputs can look plausible while disagreeing numerically across backends and harnesses.
- **In/Out of scope.** In scope: internal units, boundary unit declaration, envelope normalization, FFT/scaling convention, chirp/dispersion sign conventions, and free-space grating sign rules. Out of scope: selecting final v2 free-space/fiber solver implementations.
- **Constraints.** Must align with `phys-pipeline` deterministic typed stage contracts, support run hashing/provenance, and be ingestible by `phys-sims-utils` and testbench tooling.

### Options Considered

**Option A — Internal fs/um/rad with explicit schema unit declarations (recommended)**
- **Description:** Standardize internal computations/state to fs, um, rad; keep boundary schema explicit via `unit_system` and metric suffixes.
- **Impact areas:** cpa-sim state model, result schema, harness ingestion, testbench reporting.
- **Pros:** Numerically stable optics grids; minimal internal conversion churn; explicit boundary semantics.
- **Cons:** Non-SI boundary fields require disciplined schema/documentation.
- **Risks / Unknowns:** Drift if suffix policy is not enforced in tests.
- **Perf/Resource cost:** Low.
- **Operational complexity:** Moderate.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Requires schema checks in phys-sims-utils.

**Option B — Internal SI with SI-only boundaries**
- **Description:** Use seconds/meters/radians everywhere.
- **Impact areas:** stage implementations, config authoring, reporting.
- **Pros:** Familiar units for broad tooling interoperability.
- **Cons:** Poor numerical scaling for ultrafast optics values; higher risk of precision/conditioning pain.
- **Risks / Unknowns:** Increased silent roundoff sensitivity in pulse/time grids.
- **Perf/Resource cost:** Low.
- **Operational complexity:** Moderate.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Requires broad refactors in existing optics-centric code.

**Option C — Repo-local conventions per backend**
- **Description:** Let each backend/repo choose independent conventions with adapter conversions.
- **Impact areas:** every cross-repo interface.
- **Pros:** Local flexibility.
- **Cons:** High drift and integration burden.
- **Risks / Unknowns:** Contract breakages and incorrect cross-backend comparisons.
- **Perf/Resource cost:** High integration overhead.
- **Operational complexity:** High.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Requires complex adapter matrix.

### Decision
- **Chosen option:** Option A.
- **Trade‑offs:** We accept explicit unit metadata and suffix governance overhead to gain deterministic, comparable physics behavior across repos.
- **Scope of adoption:** All cpa-sim stage/state computations and all ecosystem result/config contracts consumed by phys-sims-utils and cpa-testbench.

### Convention contract (normative)
1. **Internal base units:** time `fs`, space `um`, angle `rad`; derived frequency uses `rad/fs`; `c = 0.299792458 um/fs`.
2. **Boundary declaration:** required top-level `unit_system: "fs_um_rad"` in result/config contracts, plus metric key suffixes (`_fs`, `_um`, `_rad_per_fs`, `_j`, `_w`).
3. **Envelope normalization:** `PulseState.field` is complex envelope in `sqrt(W)` so `P(t)=|E(t)|^2` in W and `U_J = sum(|E|^2 * dt_fs * 1e-15)`.
4. **FFT convention:** NumPy sign convention with scaled transform `Ew = dt_s * FFT(Et)` and inverse `Et = (1/dt_s) * IFFT(Ew)`, with unshifted storage and shift only in plotting utilities.
5. **Chirp/dispersion sign:** positive chirp means `dω_inst/dt > 0`; `ω_inst=ω0+dφ/dt`; GDD sign follows `d²φ/dω²`; mapping to backend β₂ must be documented at integration boundary with explicit sign test.
6. **Free-space grating convention (vendor-neutral):** define beam propagation `+z`; grating normal `+n`; grooves along `+y`; diffraction in x–z plane; signed order `m` enters `m*λ = d(sin α + sin β)` and positive incidence/exit angles are measured from grating normal toward `+x`.

### Glossary (beam terminology)
- **Beam radius (`w`)**: 1/e² intensity radius.
- **Waist (`w0`)**: minimum 1/e² intensity radius.
- **Rayleigh length (`zR`)**: `π w0² / λ` in consistent units.
- **M²**: beam quality factor (if reported, must be tagged explicitly).

### Consequences
- **Positive:** Physics metrics become comparable across backends; harness contracts can rely on one convention surface.
- **Negative / Mitigations:** Migration friction for existing configs/metrics; mitigate with conversion helpers and transition validators.
- **Migration plan:**
  1. Add `unit_system` + suffix checks in result schema validators (phys-sims-utils).
  2. Implement cpa-sim state/config normalization helpers to fs/um/rad before hashing/execution.
  3. Add testbench compatibility checks for reported unit suffixes and envelope-based energy metrics.
- **Test strategy:** Tier-0 invariant checks in cpa-sim (energy preservation under phase-only operations), contract checks in phys-sims-utils for unit metadata/suffixes, and end-to-end sanity in cpa-testbench.
- **Monitoring & Telemetry:** Record `unit_system`, backend id, and convention/version in run provenance.
- **Documentation:** Update cpa-sim README + config docs with accepted boundary units and conversion policy.

### How we validate
- **cpa-sim fast invariants:** energy conservation under phase-only free-space/fiber transforms and chirp sign regression tests.
- **phys-sims-utils contract checks:** schema validation ensuring `unit_system` present and metric suffix policy enforced.
- **cpa-testbench end-to-end sanity:** pipeline script/tests verify ingestable outputs and stable convention metadata.

### Alternatives Considered (but not chosen)
- SI-only everywhere (Option B).
- Backend-specific local conventions + adapter conversions (Option C).

### Open Questions
- Exact β₂ sign statement for first production fiber backend should be pinned once backend integration lands.

### References
- `docs/adr/cpa-adr-writing-context.md` (ADR-0001 context and acceptance criteria).
- `deps/cpa-sim/src/cpa_sim/pipeline.py` and stage placeholders indicating convention decisions are pending.
- `deps/cpa-sim/src/cpa_sim/stages/free_space/treacy_grating.py`.
- `deps/cpa-sim/src/cpa_sim/stages/fiber/fiber_sim.py`.
- `deps/phys-pipeline/src/phys_pipeline/types.py` and ADR-0011 policy propagation.
- `deps/phys-sims-utils/docs/adr/0001-canonical-result-contracts.md`.
- `deps/cpa-testbench/configs/pipeline.yaml`.

### Changelog
- `2026-02-15` — Proposed by @openai-codex

---
