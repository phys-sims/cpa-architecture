**Title:** Editable/source checkouts vs versioned packages

- **ADR ID:** ECO-0004
- **Status:** Proposed
- **Date:** 2025-02-19
- **Deciders:** @cpa-architecture, @phys-sims-leads
- **Area:** ecosystem
- **Related:** TBD
- **Tags:** packaging, ci, dependencies
- **Scope:** ecosystem
- **Visibility:** public
- **Canonical ADR:** cpa-architecture/docs/adr/ECO-0004-repository-roles-boundaries.md
- **Impacted repos:** phys-pipeline, abcdef-sim, abcdef-testbench
- **Related ecosystem ADRs:** _None_

### Context
The CPA ecosystem uses both editable/source checkouts (e.g., workspace `deps/`)
and versioned packages (published or tagged releases). We need a consistent rule
for when each is appropriate, plus CI expectations, to avoid mismatched
contracts across `phys-pipeline` and `abcdef-sim`, both of which are packaged via
`pyproject.toml`.

### Options Considered

**Option A — Prefer editable/source checkouts for all workflows, including CI**
- **Description:** Use editable installs everywhere, including CI and release
  verification.
- **Pros:** Fast iteration with zero packaging friction.
- **Cons:** Hides packaging issues and diverges from downstream consumption.

**Option B — Use editable/source checkouts for local development and coordinated cross-repo work, and use versioned packages for CI and releases (recommended)**
- **Description:** Editable installs for local integration; versioned packages in
  CI and releases.
- **Pros:** Preserves fast local iteration while validating real dependency
  boundaries in CI.
- **Cons:** Requires CI job separation and explicit pinning discipline.

### Decision
- **Chosen option:** Option B.
- **Trade‑offs:** We accept additional CI setup in exchange for enforcing
  packaging contracts.
- **Scope of adoption:** Applies to all repos in the CPA ecosystem.

### Consequences

#### Editable/source checkouts
Use editable installs when:
- You are changing an upstream API/contract and need downstream repo updates in
  the same workspace.
- You are debugging cross-repo integration issues.
- You are working before a release exists.

#### Versioned packages
Use versioned packages when:
- Running CI pipelines (unit, lint, type-checking, packaging checks).
- Producing release artifacts or validating release candidates.
- Testing against the same dependency resolution as downstream users.

### CI Expectations

**Editable/source checkouts**
- CI must explicitly document the editable install step (e.g., `pip install -e
  deps/phys-pipeline`) and should run downstream tests when API changes are in
  flight.
- CI should only use editable installs in integration jobs meant to validate
  in-flight cross-repo changes.

**Versioned packages**
- CI must install dependencies by version (e.g., from PyPI or internal indexes)
  and ensure versions are pinned to released tags.
- CI must fail if a repo relies on a local checkout without a corresponding
  version pin.

### Packaging Guidance (current repos)
- `phys-pipeline` and `abcdef-sim` are versioned via `pyproject.toml`. Version
  bumps are the contract boundary for downstream consumers.
- Downstream repos **must pin** these dependencies by version (or a compatible
  range agreed by maintainers) in their `pyproject.toml` or requirements files.
  Example guidance:
  - `abcdef-sim` should pin `phys-pipeline` (e.g., `phys-pipeline==1.0.0` or an
    explicitly approved range) when using packaged dependencies.
  - `abcdef-testbench` should pin `abcdef-sim` and any direct dependencies on
    `phys-pipeline` similarly.
- If a repo needs editable installs for integration testing, it must still keep
  version pins in the manifest and override only in the CI job that uses
  editable installs.

### References
- `deps/phys-pipeline/pyproject.toml`
- `deps/abcdef-sim/pyproject.toml`

### Changelog
- `2025-02-19` — Proposed by @cpa-architecture

---
