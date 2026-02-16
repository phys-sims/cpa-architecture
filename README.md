# cpa-architecture

`cpa-architecture` has **two roles**:

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


## Cross-repo publication from Codex Cloud

When Codex Cloud cannot push branches from `deps/*`, use the patch-bundle + repo-ops workflow:

1. Make changes in `deps/<repo>/` locally in the Codex run.
2. Generate a bundle with machine-readable plan:

```bash
python tools/mkpatch.py --prune-old --keep 3
```

This writes `patches/<bundle>/` containing:
- `<repo>.patch` files
- `change_report.md`
- `change_plan.json` (repo, branch, commit message, patch path, base SHA)

Bundle retention policy: keep only the newest 3 `patches/bundle-*` directories. CI enforces this on pull requests that touch `patches/`:

```bash
python tools/check_patch_retention.py --max-bundles 3
```

If the check fails, remove the stale bundle directories listed in the output and regenerate a bundle with pruning when needed:

```bash
python tools/mkpatch.py --prune-old --keep 3
```

3. Commit the bundle to `cpa-architecture`.
4. Run GitHub Action **Repo Ops Publish** (`.github/workflows/repo-ops-publish.yml`) with:
   - `plan_path` = path to `change_plan.json`
   - `github_org` = owner org
   - `base_branch` = PR base branch
5. The workflow uses `REPO_OPS_GH_TOKEN` to clone target repos, apply patches, commit, push branches, and open PRs.
6. If a change entry includes `base_sha`, `tools/repo_ops.py` verifies that commit exists in the clone and explicitly checks out the publication branch at that exact commit (`git checkout -B <branch> <base_sha>`) before applying the patch. If the SHA is missing, publication fails fast with remediation guidance.

Dry run validation (no push/PR):

```bash
python tools/repo_ops.py --workspace-root . --plan patches/<bundle>/change_plan.json --org phys-sims --dry-run
```

## What does not belong here

- Repo-local ADRs that only matter to one codebase (put those in that repo’s docs).
  - When a repo-local ADR adopts an ecosystem ADR, follow `docs/adr/deps-adr-authoring-guide.md` for naming and required local instructions.
- Private implementation details, datasets, or internal-only testbench content.
- Direct commits to `deps/` (generated workspace state).

## Contributing

- For architecture work: add/update ADRs in `docs/adr/` and keep `docs/adr/index.md` current.
- For metarepo work: update `manifest/repos.toml`, `tools/bootstrap.py`, and/or workspace-level docs.
- Follow `AGENTS.md` for agent workflow, validation, and PR expectations.
