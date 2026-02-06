**Title:** Use editable checkouts for active integration; use versioned packages for releases

- **ADR ID:** ECO-0004
- **Status:** Proposed
- **Date:** 2026-02-06
- **Deciders:** @phys-sims-arch
- **Area:** ecosystem
- **Related:** TBD
- **Tags:** packaging, ci, dev-ex
- **Scope:** ecosystem
- **Visibility:** public
- **Canonical ADR:** cpa-architecture/docs/adr/ECO-0004-editable-vs-versioned-packages.md
- **Impacted repos:** phys-pipeline, abcdef-sim, abcdef-testbench
- **Related ecosystem ADRs:** ECO-0001 (TBD)

### Context
- The workspace includes multiple repos with a dependency chain (`abcdef-testbench → abcdef-sim → phys-pipeline`).
- The upstream repos define package versions in `pyproject.toml` (e.g., `phys-pipeline` and `abcdef-sim`).
- We need a consistent policy for when downstream work should use editable/source checkouts versus published, versioned packages, along with CI expectations for both paths.

### Options Considered

**Option A — Default to editable/source checkouts for active development**
- **Description:** In integration branches and local dev, downstream repos install upstream dependencies from source (editable mode) to catch breaking changes early.
- **Impact areas:** CI, developer workflow, release validation.
- **Pros:** Fast feedback on API/contract changes; avoids stale artifacts.
- **Cons:** CI can be slower; requires workspace bootstrap.
- **Risks / Unknowns:** Coupling between repos can increase if used for release gating.

**Option B — Default to versioned packages everywhere**
- **Description:** Downstream repos always install published versions from an index.
- **Impact areas:** Release validation, reproducibility.
- **Pros:** Reproducible installs; clear version boundaries.
- **Cons:** Contract breaks are discovered later; requires release first.
- **Risks / Unknowns:** May hide integration issues until after publish.

**Option C — Hybrid policy (editable for integration, versioned for release)**
- **Description:** Use editable installs for active integration and contract validation; require pinned versioned packages for release and downstream consumption.
- **Impact areas:** CI, release process, dependency updates.
- **Pros:** Balances early break detection with reproducibility.
- **Cons:** Requires CI to test both pathways (integration vs release).
- **Risks / Unknowns:** Requires discipline to keep pins updated.

### Decision
- **Chosen option:** Option C (Hybrid policy).
- **Trade-offs:** We accept the complexity of dual CI paths to gain early integration feedback and stable releases.
- **Scope of adoption:** Applies to all ecosystem repos, especially the `phys-pipeline` → `abcdef-sim` → `abcdef-testbench` chain.

### Consequences
- **Positive:** Contract changes are caught earlier, while releases stay reproducible.
- **Negative / Mitigations:** CI workload increases; mitigate by scoping integration runs to PRs that touch upstream APIs.
- **Migration plan:** No code migration required; update CI pipelines and dependency pinning practices.
- **Test strategy:**
  - **Editable/source CI path:**
    - For PRs in `phys-pipeline`, run downstream tests in `abcdef-sim` using an editable install of `phys-pipeline` (e.g., `pip install -e ../phys-pipeline`).
    - For PRs in `abcdef-sim`, run downstream tests in `abcdef-testbench` using an editable install of `abcdef-sim` (and, transitively, `phys-pipeline`).
  - **Versioned/release CI path:**
    - For release branches/tags, run tests using versioned packages that match the versions declared in `pyproject.toml`.
- **Documentation:**
  - Downstream repos must pin published versions in their dependency files (e.g., `pyproject.toml` or requirements). For releases, prefer exact pins like `phys-pipeline==1.0.0` and `abcdef-sim==0.1.0`, matching the version fields in each upstream `pyproject.toml`.
  - When upstream versions change, downstream pins must be updated in the same change set (or a coordinated follow-up) before release.

### Alternatives Considered (but not chosen)
- Enforce only versioned packages in all CI paths.

### Open Questions
- Should we enforce automated checks that validate downstream pins against upstream `pyproject.toml` versions?

### References
- `deps/phys-pipeline/pyproject.toml`
- `deps/abcdef-sim/pyproject.toml`

### Changelog
- 2026-02-06 — Proposed by @phys-sims-arch

---
