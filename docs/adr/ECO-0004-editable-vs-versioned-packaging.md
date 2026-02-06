**Title:** Editable/source checkouts vs versioned packages
**ADR ID:** ECO-0004
**Status:** Proposed
**Date:** 2025-02-19

**Scope:** ecosystem
**Visibility:** public
**Canonical ADR:** phys-sims/cpa-architecture/docs/adr/ECO-0004-editable-vs-versioned-packaging.md

**Context:**
The CPA ecosystem uses both editable/source checkouts (e.g., workspace `deps/`)
and versioned packages (published or tagged releases). We need a consistent rule
for when each is appropriate, plus CI expectations, to avoid mismatched
contracts across `phys-pipeline` and `abcdef-sim`, both of which are packaged via
`pyproject.toml`.

**Options:**
- **A) Prefer editable/source checkouts** for all workflows, including CI.
- **B) Use editable/source checkouts for local development and coordinated
  cross-repo work, and use versioned packages for CI and releases.**

**Decision:**
Choose **Option B**. Editable installs remain the right tool for fast local
iteration and cross-repo API changes, while CI and released artifacts must use
versioned packages to validate real-world dependency boundaries.

**Consequences:**
- **Editable/source checkouts** are the default for local development when:
  - You are changing an upstream API/contract and need downstream repo updates
    in the same workspace.
  - You are debugging cross-repo integration issues.
  - You are working before a release exists.
- **Versioned packages** are required when:
  - Running CI pipelines (unit, lint, type-checking, packaging checks).
  - Producing release artifacts or validating release candidates.
  - Testing against the same dependency resolution as downstream users.

**CI expectations:**
- **For editable/source checkouts:**
  - CI must explicitly document the editable install step (e.g., `pip install -e
    deps/phys-pipeline`), and should run downstream tests when API changes are
    in flight.
  - CI should only use editable installs in integration jobs meant to validate
    in-flight cross-repo changes.
- **For versioned packages:**
  - CI must install dependencies by version (e.g., from PyPI or internal
    indexes) and ensure versions are pinned to released tags.
  - CI must fail if a repo relies on a local checkout without a corresponding
    version pin.

**Packaging guidance tied to current repos:**
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

**References:**
- `deps/phys-pipeline/pyproject.toml`
- `deps/abcdef-sim/pyproject.toml`

---
