# ADR Writing Context Pack — CPA Ecosystem (for cpa-architecture)

_Last updated: 2026-02-15 (America/Chicago)_  
_Purpose: Provide rich, decision-ready context so an agent can write three ADRs as separate files using your ADR templates._

This document is **not** an ADR. It is the **source material** (recommended choices + rationale + acceptance tests + placeholders) for:

- **ADR-0001 — Conventions & Units** (cpa-sim internal + API/backend conventions)
- **ADR-0002 — Result Schema Contract** (pipeline executor ↔ ML harness ↔ humans)
- **ADR-0003 — Validation Tiers & CI Policy** (unit/theoretical/experimental)

---

## Ecosystem map (who consumes what)

### Primary repos
- **cpa-sim**: library/product. Runs the CPA chain; emits structured results + artifacts.
- **phys-pipeline**: stage abstraction, caching, scheduling (infrastructure substrate).
- **abcdef-sim**: free-space stretcher/compressor physics backend (v2+).
- **fiber-sim**: in-house fiber propagation backend (v2+).
- **phys-sim-utils** (formerly research-utils): ML harness + testharness + batching + reporting.
- **cpa-testbench**: slow sweeps, notebooks, experimental comparisons, “wow plots.”

### Contract boundaries
- `cpa-sim` must be usable **without** ML tooling.
- `phys-sim-utils` orchestrates many `cpa-sim` runs and treats `cpa-sim` as a black box.
- Cross-cutting decisions (units, schema, validation policy) live in **cpa-architecture** ADRs.

---

# ADR-0001 Context — Units & Conventions (backend + API)

## Goal
Ensure every stage/backend agrees on:
- what the pulse envelope means,
- units used internally and at API boundaries,
- FFT conventions and scaling,
- dispersion/chirp sign conventions,
- grating and gaussian-beam terminology.

This ADR is critical because mismatched conventions silently produce “correct-looking” but inconsistent physics across backends.

---

## Recommended decision (matches your provided doc)

### Internal base units (used inside `cpa-sim` state and computations)
From your context:

- **time**: **fs** (femtoseconds)  
  - numeric definition: 1 fs = 1e-15 s
- **space**: **µm** (micrometers)  
  - numeric definition: 1 µm = 1e-6 m
- **angle**: **rad**
- Everything else derived from these:
  - angular frequency: **rad/fs**
  - speed of light: **c = 0.299792458 µm/fs**
  - wavenumber: rad/µm, etc.

**Rationale (why not pure SI internally):**
- CPA pulse grids are naturally fs–ps; using fs avoids extremely small dt and improves numerical conditioning.
- Free-space beam sizes and wavelengths are naturally µm-scale; using µm keeps numbers stable (waists, grating groove spacing, λ).

### External / API boundary units (recommended)
**Recommendation:** configs and results should be explicit about units and/or normalized.

Two safe options:

1) **Expose SI at boundaries**, convert internally to fs/µm.  
   - Pros: interoperable across repos and papers; less confusion for ML reports.
   - Cons: requires explicit conversions everywhere.

2) **Expose the same internal unit system at boundaries** (fs/µm), but always tag units in schema.  
   - Pros: fewer conversions; easier for human optics work.
   - Cons: ML/harness must respect non-SI units.

**Recommended choice for the ecosystem:**  
- Keep internal fs/µm/rad, but make **result schema declare `unit_system: "fs_um_rad"`** and enforce **unit suffixes** in metric keys (e.g., `_fs`, `_um`, `_rad_per_fs`, `_j`).
- Allow configs to accept SI input (m, s) as a convenience, but normalize into internal units before hashing.

> Agent instruction when writing ADR: pick one option explicitly; the recommended default above is “internal fs/µm, schema carries unit_system + suffixes.”

---

## Envelope meaning & normalization (must be explicit)

### Recommended normalization (ML-friendly and testable)
Define complex envelope `E(t)` such that:

- **Instantaneous power**: `P(t) = |E(t)|^2` in watts  
- **Pulse energy**: `U = ∫ |E(t)|^2 dt` in joules

This makes energy conservation under phase-only operations a strict invariant.

### Implication for internal units
If time is in fs internally, then the numeric integral uses `dt_fs`. You must convert when reporting joules:

- `U_J = ∑ |E|^2 * (dt_fs * 1e-15)`

**Required ADR statement:** whether `PulseState.field` is:
- `sqrt(W)` envelope (recommended), or
- unitless normalized envelope (not recommended for a lab-facing product).

---

## FFT / spectral conventions (must be locked)

### Recommended discrete convention (numpy-friendly, deterministic)
- Store time-domain samples `E_t[n]` on uniform grid with spacing `dt_fs`.
- Define frequency grid via numpy conventions:
  - `f = fftfreq(N, d=dt_s)` in Hz, where `dt_s = dt_fs * 1e-15`
  - `ω = 2π f` in rad/s (or convert to rad/fs for internal)
- Use numpy FFT sign convention (forward has `exp(-i 2π nk/N)`).

### Scaling (recommended)
To approximate the continuous-time Fourier transform consistently, define the **scaled spectrum**:

- `Ê(ω_k) = dt_s * FFT(E_t)`  
- Inverse: `E_t = (1/dt_s) * IFFT(Ê)`

**Why this matters:** without a scaling convention, spectra and bandwidth metrics won’t match across backends and tests.

### Shift policy (recommended)
- Store raw FFT ordering internally (unshifted).  
- Provide helpers for plotting: `fftshift` versions.

---

## Chirp sign convention (must be one sentence, mathematically)

### Recommended definition
- Instantaneous angular frequency: `ω_inst(t) = ω0 + dφ/dt`
- **Positive chirp** means frequency increases with time:
  - `dω_inst/dt > 0`  ⇔  `d²φ/dt² > 0`

This ties “chirp” to phase unambiguously.

---

## Fiber conventions (from your context + recommended additions)

### Given (your context)
- **GDD > 0**: stretching  
- **GDD < 0**: compression

### What the ADR must add
- Relationship between GDD sign and β₂ sign for your propagation model/backends.
- Explicit statement of what sign of β₂ corresponds to normal vs anomalous dispersion **in your configs**.

**Recommended pragmatic rule (v1):**
- Make `FiberCfg` semantics match the chosen v1 solver backend exactly (e.g., gnlse).  
- If conversion is required, document it and add a test that detects sign inversion.

---

## Free-space conventions (from your context + recommended choices)

### Gaussian beam / spot size terminology
Given:
- “spot radius at beam waist: 1/(e**2) of max value”

Interpretation to lock:
- Use **1/e² intensity radius** `w` as the beam radius (standard in laser optics).
- Intensity profile: `I(r) = I0 * exp(-2 r² / w²)`
- `w0` denotes beam waist radius at focus (minimum `w`).

**ADR should include a glossary**:
- beam waist radius `w0`
- spot size / beam radius `w(z)`
- Rayleigh range `zR`
- M² if used (v2+)

### Grating equation and sign conventions (recommended, vendor-independent)
Because “Plymouth vs Newport” conventions differ, avoid vendor terms as source-of-truth.
Pick a coordinate system and define your own sign rules:

**Recommended baseline equation:**
- `m λ = d (sin α + sin β)`
where:
- `m` is signed diffraction order (often `m = -1` in Martinez stretchers)
- `d` is groove spacing (µm)
- `α` is incidence angle from grating normal
- `β` is diffraction angle from grating normal

**Angle sign rule (recommended):**
- Define a right-handed coordinate system with grating normal as +z.
- Angles α, β are positive when rotating the ray toward +x (choose x direction explicitly in text/diagram).
- If you implement 2D only, state that explicitly.

**Vendor mapping note (recommended):**
- Include a short appendix mapping your `m, α, β` to any vendor documentation you rely on (but vendor docs are not the spec).

---

## Canonical invariants and acceptance tests (must appear in ADR-0001)

### Unit/invariant tests (fast)
- **Energy conservation** for phase-only stages:  
  `U_out / U_in ≈ 1` within tolerance.
- **Parseval consistency** (if you store scaled spectrum):  
  energy computed in time domain matches energy computed in frequency domain within tolerance.

### Chirp sign test (fast)
- Apply known quadratic phase; compute `ω_inst(t)` and verify sign of chirp.

### Backend interface consistency (fast)
- A pulse passed through v1 `FreeSpaceStage` then inverse should reproduce (within tolerance) when parameters are inverted.

---

# ADR-0002 Context — Result Schema Contract (executor ↔ ML harness ↔ humans)

## Goal
Define a stable, machine-readable “run result” contract so:
- pipeline executors can cache, resume, and produce consistent artifacts,
- ML harness can ingest runs at scale without custom parsing,
- humans can reproduce and interpret runs.

This ADR is about **data contract**, not UI.

---

## Recommended architecture: one canonical `result.json` per run

### Required top-level fields (RunResult)
- `schema_version`: e.g. `"cpa.result.v0.1"`
- `unit_system`: e.g. `"fs_um_rad"` (or `"si"` if you choose SI boundaries)
- `run_id`: unique ID
- `status`: `"ok" | "fail" | "invalid_config"`
- `started_at`, `finished_at` (ISO timestamps)
- `config_hash`: stable hash of normalized config
- `provenance`:
  - `git_sha` (repo SHA)
  - `package_version`
  - `python_version`, `platform`
  - `backend_versions` (e.g., gnlse, numpy)
- `metrics`: flat-ish dict of scalar outputs (ML-facing)
- `artifacts`: paths/refs to saved plots, arrays, logs, copied config
- `stages`: optional list of stage summaries (StageResultSummary)
- `error`: optional structured error info (even when failed)

### Metrics naming (recommended)
Use dot-separated namespaces + unit suffixes:

Examples:
- `pulse.in.energy_j`
- `pulse.out.energy_j`
- `pulse.out.fwhm_fs` (or `_s` if SI boundaries)
- `spectrum.out.bandwidth_thz` (or `_hz`)
- `fiber.b_integral_rad` (or `_dimensionless` with definition)
- `objective.value` (if ML defines one)

**Rule:** arrays never live in `metrics`. Arrays are saved as `.npz` and referenced in `artifacts`.

### Artifacts layout (recommended)
- `out/<run_id>/result.json`
- `out/<run_id>/metrics.json` (optional convenience)
- `out/<run_id>/artifacts/plots/*.png`
- `out/<run_id>/artifacts/states/*.npz`
- `out/<run_id>/artifacts/config.yaml` (copied normalized config)

### Stage summaries (recommended for provenance/debug)
Each stage summary includes:
- `stage_name` (e.g., `"fiber"`)
- `stage_kind` (e.g., `"gnlse"`)
- `stage_config_hash`
- `metrics` (small scalars only)
- `artifacts` (paths)
- optional `state_ref` into `.npz`

---

## Schema versioning rules (must be explicit)
Recommended compatibility policy:
- **Patch**: add optional fields, add new metric keys (non-breaking).
- **Minor**: add required fields only if you bump `schema_version` and continue supporting previous version(s) for a transition window.
- **Major**: rename/remove fields or change meaning of existing metrics keys.

**Hard rule:** if a metric changes meaning, bump schema or change the key name.

---

## Failure handling (required)
ML harness will explore invalid regions. Failures must be first-class:

- Always write `result.json` even on failure.
- `status` indicates failure type.
- `error` should include:
  - `type`
  - `message`
  - optional `stage`
  - optional `traceback` (human-only)

This allows ML to label invalid configs instead of crashing.

---

## Relationship to phys-pipeline caching
The executor/harness should be able to safely use:
- `config_hash` (normalized + units-resolved)
- optional per-stage config hashes
- provenance (git SHA, backend versions)

Cache invalidation should trigger when:
- config changes
- code version changes
- backend version changes (if physics-relevant)

---

## Acceptance tests for ADR-0002
- `result.json` validates against the pydantic model / JSON schema.
- A failed run still produces schema-valid `result.json`.
- ML harness can ingest N run results without special-casing by backend.

---

# ADR-0003 Context — Validation Tiers & CI Policy

## Goal
Make validation honest, scalable, and automation-friendly by separating:
- software correctness
- theoretical regression against known examples
- experimental comparisons and uncertainty

This prevents “overclaiming” and prevents CI from becoming unusably slow.

---

## Recommended tier definitions (strict)

### Tier 0 — Unit (fast, PR-gated)
Purpose: code mechanics correctness (not physics truth)

Examples:
- config validation + error messages
- deterministic hashing and serialization
- energy conservation for phase-only stages
- state shape/dtype invariants
- stage registry selects correct backend

Location:
- `cpa-sim/tests/unit`

Runs:
- every PR (required gate)

---

### Tier 1 — Theoretical regression (pinned “golden”)
Purpose: reproduce known results from canonical solver examples or analytic baselines

Examples:
- fiber backend reproduces one upstream solver canonical example (pinned metrics)
- free-space backend reproduces one trusted numeric golden case
- analytic sanity checks (quadratic phase stretching)

Location:
- `cpa-sim/tests/physics` if fast enough, otherwise in a separate workflow

Runs:
- nightly or manual (`workflow_dispatch`) if slow

---

### Tier 2 — Experimental comparisons (paper/lab)
Purpose: compare to measurement data with uncertainty

Examples:
- SPM-broadened spectra vs a paper/lab trace
- efficiency vs power curves vs lab data

Location:
- `cpa-testbench` (not in cpa-sim)

Runs:
- manual / report builds (not PR-gated)

---

## Tolerance policy (recommended defaults)
- Tier 0: tight tolerances (mostly exact, or 1e-12–1e-6 relative depending on floats)
- Tier 1: metric-specific tolerances (relative where possible)
  - energy: 1e-6 rel
  - FWHM: 1e-3 rel
  - bandwidth: 1e-3 rel
- Tier 2: data-derived uncertainty + documented fit method

Also decide:
- absolute vs relative tolerances per metric
- whether nondeterminism is allowed (recommended: no in v1)

---

## CI policy + pytest markers (recommended)
Markers:
- `unit`, `integration`, `physics`, `slow`

PR gate:
- `-m "not slow and not physics"`

Nightly/manual:
- `-m physics`

Slow (if needed):
- `-m slow` (manual or scheduled)

**Rule:** experimental comparisons should not live in cpa-sim CI.

---

## Validation records and reporting (tie to ADR-0002)
Every validation should produce a structured record:
- tier
- reference (solver example / paper citation)
- metrics compared + tolerances
- pass/fail + numeric deltas
- provenance (git SHAs, backend versions)

Recommended output:
- `validation_report.json` + `validation_report.md` generated by testbench or harness.

---

## Acceptance tests for ADR-0003
- Tier 0 failures block merges.
- Tier 1 failures show numeric diffs and reference baselines.
- Tier 2 outputs a report with plots + uncertainty + provenance.

---

# Open placeholders (fill these before agent writes ADRs)

## For ADR-0001 (Conventions)
- [ ] Confirm boundary unit strategy: SI boundaries vs unit_system+suffixes.
- [ ] Confirm whether `|E|^2 = W` envelope normalization is adopted.
- [ ] Lock FFT scaling: scaled spectrum `Ê = dt_s*FFT(E)`.
- [ ] State β₂ sign convention and mapping to chosen v1 solver backend.
- [ ] Choose grating coordinate sign rules (write a small diagram in ADR).

## For ADR-0002 (Result Schema)
- [ ] Pick schema id strings: `cpa.result.v0.1`, `cpa.config.v0.1`.
- [ ] Decide metric namespaces and required key set for v1.
- [ ] Decide artifact filenames and whether arrays always saved or optional.

## For ADR-0003 (Validation)
- [ ] Choose one canonical fiber test case (from solver docs) + tolerances.
- [ ] Choose one free-space golden case (from your trusted code) + tolerances.
- [ ] Decide which tests are PR-gated vs nightly.

---

## Agent-ready instructions (use in your prompt)
When writing ADRs from this context:
- Use the repository’s ADR template.
- Include: **Decision**, **Rationale**, **Consequences**, **Alternatives considered**, **How we validate**, **Migration plan**.
- Make unit/sign conventions explicit and testable (include acceptance test list).
- Do not copy vendor docs as source-of-truth; document our coordinate convention instead.
