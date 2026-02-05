# CPA Ecosystem System Overview

This doc is the high-level map of how the CPA ecosystem repos fit together.
It is not a replacement for ADRs; it’s a navigation aid and a shared mental model.

---

## Repo map

### Core libraries / simulations
- **phys-pipeline**
  - Generic simulation pipeline API: stage contract, configs, caching/provenance expectations, pipeline executor semantics.

- **abcdef-sim**
  - “Linear/structured optics” simulation built on phys-pipeline (e.g., layout/transfer/optics chain pieces).

- **glnse-sim**
  - Nonlinear propagation simulation (GLNSE-style) built on phys-pipeline, designed to plug into CPA chains.

- **cpa-sim** (future)
  - “Product” simulation that composes abcdef-sim + glnse-sim into an end-to-end CPA system model.
  - Owns CPA-specific end-to-end behavior, defaults, validation, and user-facing docs.

### Private workspace (dev + experimentation)
- **cpa-workspace** (private)
  - A development workspace that contains:
    - test benches (private)
    - research-utils (private ML/testing framework + experimentation code)
    - submodules/working checkouts of the public repos above
  - Used for agent work and integration iteration, but **not** the canonical public documentation home.

---

## How code flows through the ecosystem (conceptual)

A typical CPA simulation composition looks like:

1) **Setup / system preset**  
   User defines a CPA system layout and parameters.

2) **Linear optics / structured stages** (abcdef-sim)  
   Stretcher/compressor/layout transformations, etc.

3) **Nonlinear propagation** (glnse-sim)  
   Fiber/amp stages with nonlinear + dispersive evolution.

4) **End-to-end orchestration** (cpa-sim)  
   Connects the chain, defines outputs/metrics, and provides user workflows.

All stages and results conform to the **phys-pipeline** stage/result/config conventions so they can be chained, cached, and swept consistently.

---

## Documentation and ADR boundaries

### What lives in each repo
- Repo-local ADRs (implementation choices, internal architecture):  
  `<repo>/docs/adr/`

- Repo-local documentation (how to use that repo):  
  `<repo>/README.md`, `<repo>/docs/*`

### What lives here (cpa-architecture)
- Cross-repo contracts and policies that affect two or more repos:
  - stage contract conventions across sims
  - dependency/versioning policy between pipeline + sims
  - integration testing strategy across repos
  - shared conventions (units, serialization, artifacts, caching expectations)

### What stays private
- Testbench design, datasets, internal evaluation frameworks, and research-utils internals remain in private repos/workspaces.

---

## CI and automation conventions (current)

- Org-wide templates live in: `phys-sims/.github` (public)
- Reusable workflows live in: `phys-sims/ci-workflows` (private)
- Each repo contains a thin caller workflow that invokes reusable workflows.
- Some repos require from-source installs of other repos during CI for integration (e.g., a sim that depends on phys-pipeline).

---

## “When does an ecosystem ADR exist?”

Use an ecosystem ADR when the decision:
- changes how two+ repos interact, or
- defines a contract that downstream sims or users must rely on, or
- prevents drift across repos (conventions, compatibility, integration policy).

Otherwise, keep it local to the repo.
