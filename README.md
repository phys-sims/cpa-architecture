# cpa-architecture

`cpa-architecture` now has **two roles**:

1. **Architecture repo** for ecosystem-level ADRs and system documentation.
2. **Agent-friendly workspace metarepo** used to materialize working copies of related repos under `deps/`.

## What this repository is for

### 1) Cross-repo architecture decisions
Use this repo for decisions that affect multiple repositories (contracts, repo boundaries, conventions, compatibility expectations).

Primary docs location:

- `docs/adr/` for ecosystem ADRs (`ECO-####-*.md`)
- `docs/SYSTEM_OVERVIEW.md` for a high-level map

### 2) Workspace orchestration
Use this repo to bootstrap local working copies of the ecosystem repos for cross-repo work.

Workspace files:

- `manifest/repos.toml` – source-of-truth list of repos and refs
- `tools/bootstrap.py` – clones/updates repos into `deps/<repo>/`
- `deps/` – generated working copies (gitignored)

## Quick start (metarepo usage)

```bash
python tools/bootstrap.py
```

Then work inside a dependency repo, for example:

- `deps/phys-pipeline/`
- `deps/abcdef-sim/`
- `deps/abcdef-testbench/`
- `deps/cpa-sim/`
- `deps/cpa-testbench/`
- `deps/phys-sims-utils/`

## What does not belong here

- Repo-local ADRs that only matter to one codebase (put those in that repo’s docs).
- Private implementation details, datasets, or internal-only testbench content.
- Direct commits to `deps/` (generated workspace state).

## Contributing

- For architecture work: add/update ADRs in `docs/adr/` and keep `docs/adr/index.md` current.
- For metarepo work: update `manifest/repos.toml`, `tools/bootstrap.py`, and/or workspace-level docs.
- Follow `AGENTS.md` for agent workflow, validation, and PR expectations.
