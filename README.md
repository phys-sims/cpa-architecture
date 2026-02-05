# cpa-architecture

This repo contains **cross-repository architecture decisions (ADRs)** and system-level documentation for the **CPA ecosystem** in the `phys-sims` org.

If you're looking for *how a specific repo works internally*, you probably want that repo’s `docs/adr/` instead.

---

## What belongs here

This repo is the **single source of truth** for decisions that affect **two or more** of:

- `phys-pipeline`
- `abcdef-sim`
- eventual `glnse-sim` repo
- eventual `cpa-sim` repo
- public-facing conventions that downstream sims or users must follow

Typical topics:

- Cross-repo contracts (stage/result/config/state expectations)
- Repo role boundaries and ownership (what belongs where)
- Ecosystem dependency/versioning policy (dev-from-source vs published packages)
- Integration testing policy across repos
- Org-wide conventions that directly impact interoperability:
  - caching + cache key stability expectations
  - artifacts/provenance conventions
  - units/numerical conventions
  - interface contracts between sims (e.g., abcdef ↔ glnse)

---

## What does NOT belong here

### Repo-local decisions
Each repo remains understandable in isolation. Repo-specific architecture belongs in that repo’s ADRs:

- `<repo>/docs/adr/` (local ADRs)
- `<repo>/docs/how-to-*.md` (repo docs)

If a repo-local ADR depends on an ecosystem ADR, it should **link to it** rather than duplicating it.

### Internal / private decisions
Private implementation details, benchmarks, datasets, and internal ML/testing framework decisions belong in private repos (e.g., `cpa-workspace` and its private testbenches / `research-utils`).

This repo should not contain sensitive/private testbench details.

---

## Structure

- `docs/adr/`
  - `ECO-####-*.md` — ecosystem ADRs (cross-repo)
  - `_template-*.md` — ADR templates (if used here)
  - `index.md` — generated/maintained list of ecosystem ADRs

- `SYSTEM_OVERVIEW.md` *(optional)*
  - High-level map of how repos fit together (not a substitute for ADRs)

---

## How to decide where an ADR goes

Ask:

> “If this repo disappeared tomorrow, would this decision still matter?”

- **Yes** → it belongs here (ecosystem ADR)
- **No** → it belongs in the relevant repo’s `docs/adr/`
- **It’s sensitive/internal** → it belongs in a private repo (e.g., `cpa-workspace`)

---

## Linking policy

- Ecosystem ADRs should list **Impacted repos** and **Related ADRs**.
- Repo-local ADRs that rely on ecosystem decisions should link back to the relevant `ECO-####` ADR(s).

---

## Contributing

1. Create a new ADR in `docs/adr/` using the template.
2. Use the next available `ECO-####` number.
3. Add it to `docs/adr/index.md` (or run the index script if provided).
4. Keep the ADR focused on a single decision and its consequences across repos.
