**Title:** Repository roles and boundaries in the CPA ecosystem.

- **ADR ID:** ECO-0004
- **Status:** Proposed
- **Date:** 2026-02-06
- **Deciders:** @cpa-architecture, @phys-sims-leads
- **Area:** ecosystem
- **Related:** TBD
- **Tags:** api, data-model, testing, ops
- **Scope:** ecosystem
- **Visibility:** public
- **Canonical ADR:** cpa-architecture/docs/adr/ECO-0004-repository-roles-boundaries.md
- **Impacted repos:** phys-pipeline, abcdef-sim, abcdef-testbench, cpa-architecture
- **Related ecosystem ADRs:** _None_

### Context
- **Problem statement.** The CPA ecosystem now includes multiple repos that can blur responsibilities. We need an explicit set of boundaries so that pipeline contracts remain stable, simulation domain logic stays cohesive, and downstream testbench code does not become an unofficial API surface.
- **In/Out of scope.** In scope: repository responsibilities, forbidden responsibilities, and how they align with pipeline contracts in `phys-pipeline` and simulation domain modules in `abcdef-sim`. Out of scope: detailed API versioning policy, release cadence, or staffing decisions.
- **Constraints.** Maintain contract stability for the pipeline types (`PipelineStage`, `StageConfig`, `StageResult`, `State`) and keep domain assembly logic such as the `SystemAssembler` pipeline builder inside `abcdef-sim` while testbench remains a consumer-only repo.

### Options Considered

**Option A — Explicit repo boundaries anchored to pipeline contracts (recommended)**
- **Description:** Define responsibilities and explicit “must not” rules per repo, anchored on the `phys-pipeline` contract types and the `abcdef-sim` domain assembly modules.
- **Impact areas:** public API contracts, simulation composition, documentation, and tests.
- **Pros:** Clear ownership, less API drift, easier onboarding, and reduced cross-repo coupling.
- **Cons:** Requires periodic enforcement and updates as new repos appear.
- **Risks / Unknowns:** Potential friction when teams want to place quick fixes in downstream repos.
- **Perf/Resource cost:** None.
- **Operational complexity:** Moderate (needs review checklists).
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Requires aligning PR review expectations across repos.

**Option B — Implicit boundaries via tribal knowledge**
- **Description:** Keep boundaries in people’s heads and rely on review comments when issues appear.
- **Impact areas:** API stability, documentation, testbench scope.
- **Pros:** No documentation overhead.
- **Cons:** Repeated confusion, increased coupling, and drift in responsibility.
- **Risks / Unknowns:** High risk of breaking pipeline contracts and domain encapsulation.
- **Perf/Resource cost:** None.
- **Operational complexity:** High long-term complexity due to rework.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** None.

**Option C — Centralize all responsibilities in a single repo**
- **Description:** Move pipeline, simulation domain, and testbench into one repo.
- **Impact areas:** repository structure, CI, and ownership.
- **Pros:** Single location for changes.
- **Cons:** Not aligned with current ecosystem structure; large migration cost.
- **Risks / Unknowns:** High risk of slowed development velocity.
- **Perf/Resource cost:** Significant migration effort.
- **Operational complexity:** High.
- **Security/Privacy/Compliance:** None.
- **Dependencies / Externalities:** Requires major tooling changes.

### Decision
- **Chosen option:** Option A. Explicitly document repo roles with hard boundaries anchored to pipeline contracts and domain assembly responsibilities.
- **Trade‑offs:** We accept some documentation maintenance in exchange for clarity and stability.
- **Scope of adoption:** Applies to the entire CPA ecosystem. Exceptions must be documented in future ADRs.

### Consequences
- **Positive:** Stable pipeline contracts, clearer dependency direction, and reduced accidental API surface expansion.
- **Negative / Mitigations:** Extra review overhead; mitigate with checklist-based reviews and ADR references.
- **Migration plan:** No immediate code changes. Update repo documentation and reference this ADR in future PRs that touch boundaries.
- **Test strategy:** Add repo-level checks in each impacted repo to ensure boundaries are respected when new modules are added.
- **Monitoring & Telemetry:** Track cross-repo dependency PRs and ensure they cite this ADR when touching interfaces.
- **Documentation:** Add references in repo READMEs and architecture docs as needed.

### Repository Responsibilities and Forbidden Responsibilities

**phys-pipeline (pipeline contracts and execution)**
- **Responsibilities:**
  - Define pipeline contracts such as `PipelineStage`, `StageConfig`, `StageResult`, and `State` used by all simulation pipelines.
  - Provide generic pipeline execution primitives (e.g., sequential or DAG orchestration) that remain domain-agnostic.
- **Forbidden responsibilities:**
  - Domain-specific simulation logic, optics assembly, or concrete stage configuration generation.
  - Testbench scenarios or acceptance criteria.

**abcdef-sim (domain modeling and pipeline assembly)**
- **Responsibilities:**
  - Implement simulation domain models, configs, and pipeline assembly layers such as the `SystemAssembler` that builds stage configurations and instantiates domain-specific stages.
  - Own the mapping from domain inputs (presets/specs) to pipeline stages while consuming the `phys-pipeline` contracts.
- **Forbidden responsibilities:**
  - Redefining pipeline contracts or duplicating generic pipeline orchestration.
  - Owning end-to-end testbench harnesses or golden-output acceptance suites.

**abcdef-testbench (validation and benchmarking)**
- **Responsibilities:**
  - Provide integration/acceptance tests, scenario coverage, and benchmarking against expected outputs.
  - Validate that `abcdef-sim` implementations adhere to `phys-pipeline` contract expectations.
- **Forbidden responsibilities:**
  - Publishing new public APIs or pipeline contracts.
  - Introducing new domain logic that bypasses `abcdef-sim` modules.

**cpa-architecture (ecosystem governance and documentation)**
- **Responsibilities:**
  - Own ecosystem-level ADRs, cross-repo policies, and boundary documentation.
  - Capture decisions about repo responsibilities and dependency direction.
- **Forbidden responsibilities:**
  - Shipping runtime code, production configs, or simulation pipelines.
  - Hosting testbench suites or pipeline contract implementations.

### Alternatives Considered (but not chosen)
- Keep boundaries informal and rely on reviewer feedback (Option B).
- Collapse repos into a single monorepo (Option C).

### Open Questions
- Should we encode these boundaries as automated repo checks (e.g., lint rules or dependency guards)?
- Which repo should host a shared checklist for boundary reviews?

### References
- Pipeline contract definitions in `phys-pipeline` (`PipelineStage`, `StageConfig`, `StageResult`, `State`).
- Domain pipeline assembly in `abcdef-sim` (`SystemAssembler` building stage configs and stages).

### Changelog
- `2026-02-06` — Proposed by @cpa-architecture

---
