# AGENTS.md (cpa-architecture)

## Purpose of this repo
`cpa-architecture` serves both as:

1. **Architecture documentation repo** (cross-repo ADRs and system docs), and
2. **Workspace metarepo** for agent-driven multi-repo work.

Treat both as first-class responsibilities.

## Repository layout
- `docs/` – ecosystem-level ADRs and system documentation.
- `manifest/repos.toml` – workspace manifest (repo list + refs).
- `tools/bootstrap.py` – materializes/updates repo working copies in `deps/`.
- `tools/mkpatch.py` – creates patch bundles from dirty `deps/*` repos.
- `tools/repo_ops.py` – applies patch plans and publishes branches/PRs to target repos.
- `deps/` – generated dependency repos (gitignored; never commit).
- `patches/` – patch bundles for cross-repo publication.

## Scope and change targeting
- Update this repo when changing:
  - cross-repo ADRs/system docs,
  - workspace automation (`tools/bootstrap.py`, `tools/mkpatch.py`, `tools/repo_ops.py`),
  - workspace manifest (`manifest/repos.toml`),
  - agent/operator guidance.
- Update repos inside `deps/<repo>/` for product code changes.
- Do not scan every repo by default; only inspect repos relevant to the task.

## First action in any task
1. Check whether workspace repos are present:
   - `ls deps/`
2. If missing, run:
   - `python tools/bootstrap.py`
3. If bootstrap fails due environment/setup issues (for example manifest mismatch or network limits), clearly report the blocker and continue with any work that can still be done safely in this repo.

## Cross-repo safety protocol
When changing an upstream API or shared contract:
1. Identify downstream consumers.
2. Search usages before edits (example):
   - `rg "<Symbol>" deps/abcdef-sim`
   - `rg "<Symbol>" deps/abcdef-testbench`
3. Apply provider changes.
4. Update downstream repos to preserve compatibility.
5. Add/adjust tests to catch regressions.

If unsure whether a change is breaking, assume it might be and verify.

## Codex Cloud publication runbook (repo-ops publisher)
Use this when Codex Cloud cannot push directly from `deps/*` repos.

1. Make and validate code changes in target repos under `deps/<repo>/`.
2. Build a patch bundle from dirty repos:
   - `python tools/mkpatch.py`
3. Review generated artifacts in `patches/<bundle>/`:
   - `<repo>.patch`
   - `change_plan.json`
   - `change_report.md`
4. Optionally validate publication logic locally:
   - `python tools/repo_ops.py --workspace-root . --plan patches/<bundle>/change_plan.json --org <github-org> --dry-run`
5. Commit the bundle in this metarepo (never commit `deps/`).
6. Run GitHub Action **Repo Ops Publish** (`.github/workflows/repo-ops-publish.yml`) with:
   - `plan_path`: `patches/<bundle>/change_plan.json`
   - `github_org`: org owning destination repos
   - `base_branch`: PR base branch (usually `main`)
   - `dry_run`: `false` for real publication

### Trigger from CLI
When publication is required, agents must execute (not just describe) the CLI commands below.

1. Authenticate and verify:
   - `gh auth status`
2. Trigger workflow:
   - `gh workflow run repo-ops-publish.yml --ref <metarepo-branch> -f plan_path=patches/<bundle>/change_plan.json -f github_org=<org> -f base_branch=main -f dry_run=false`
3. Watch run:
   - `gh run watch --exit-status`
4. Inspect result/logs:
   - `gh run view --log`

### Repo-ops prerequisites and guardrails
- Non-dry-run requires `REPO_OPS_GH_TOKEN` configured in Actions secrets.
- `tools/repo_ops.py` checks `base_sha` from `change_plan.json`; publication fails on mismatch.
- If a patch applies with no file changes, repo-ops skips push/PR for that repo.
- Ensure branch and commit message values in `change_plan.json` are acceptable before publishing.

## Validation expectations
For each repo changed, run appropriate checks for that repo. Typical baseline:
- `pre-commit run -a`
- `pytest`
- `ruff check .`
- `mypy`

If a nested `AGENTS.md` exists in a changed repo, follow the more specific instructions there.

## Git and PR workflow
- Keep changes scoped.
- Commit in the repo you changed.
- Open a PR with:
  - what changed,
  - why it changed,
  - impacted repo(s),
  - exact commands run for validation.
- If publishing is required, verify branch push to `origin`.

## Efficiency guidelines
- Prefer `rg`/`git grep` over broad scans.
- Avoid generated artifacts unless needed.
- Never commit `deps/` content from this metarepo.
