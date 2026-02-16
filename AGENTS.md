# AGENTS.md (cpa-architecture)

## Purpose of this repo
`cpa-architecture` serves both as:

1. **Architecture documentation repo** (cross-repo ADRs and system docs), and
2. **Workspace metarepo** for agent-driven multi-repo work.

Treat both as first-class responsibilities.

---

## Repository layout
- `docs/` – ecosystem-level ADRs and system documentation.
- `manifest/repos.toml` – workspace manifest (repo list + refs).
- `tools/bootstrap.py` – materializes/updates repo working copies in `deps/`.
- `tools/mkpatch.py` – creates patch bundles from dirty `deps/*` repos.
- `tools/repo_ops.py` – applies patch plans and publishes branches/PRs to target repos.
- `deps/` – generated dependency repos (gitignored; never commit).
- `patches/` – patch bundles for cross-repo publication.

---

## Scope and change targeting
- Update this repo when changing:
  - cross-repo ADRs/system docs,
  - workspace automation (`tools/bootstrap.py`, `tools/mkpatch.py`, `tools/repo_ops.py`),
  - workspace manifest (`manifest/repos.toml`),
  - agent/operator guidance.
- Update repos inside `deps/<repo>/` for product code changes.
- Do not scan every repo by default; only inspect repos relevant to the task.

---

## First action in any task (required)
1. Check whether workspace repos are present:
   - `ls deps/`
2. If missing, run:
   - `python tools/bootstrap.py`
3. If bootstrap fails due environment/setup issues (for example manifest mismatch or network limits), clearly report the blocker and continue with any work that can still be done safely in this repo.

---

## Mandatory execution model for agents

### Core rule
For product code changes, agents may edit inside `deps/<repo>/`, but **must use this metarepo as the publication surface**.

### Non-optional sequence when `deps/*` changes exist
1. Make and validate changes in `deps/<repo>/`.
2. Generate a patch bundle from dirty repos:
   - `python tools/mkpatch.py --prune-old --keep 3`
3. Verify generated artifacts in `patches/<bundle>/`:
   - `<repo>.patch`
   - `change_plan.json`
   - `change_report.md`
4. Commit generated bundle artifacts in **this metarepo**.
5. Open a PR from this metarepo branch.

### Prohibited behaviors
- Do **not** treat direct push from `deps/*` as the default delivery path.
- Do **not** end with only dirty `deps/*` and no metarepo artifacts.
- Do **not** claim completion if `python tools/mkpatch.py --prune-old --keep 3` was required but not run.
- Do **not** commit `deps/` contents in this metarepo.

### Definition of done for cross-repo/product changes
A task is complete only when all are true:
1. Code changes are made/validated in relevant `deps/<repo>/` repos.
2. A new bundle exists at `patches/<bundle>/` with patch files and plan/report.
3. A commit exists in `cpa-architecture` containing the bundle artifacts.
4. A metarepo PR exists describing impacted repos and validation commands.

If publication is requested, completion additionally requires repo-ops workflow execution (see runbook below).

---

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

---

## Codex Cloud publication runbook (repo-ops publisher)
Use this when Codex Cloud cannot push directly from `deps/*` repos.

1. Make and validate code changes in target repos under `deps/<repo>/`.
2. Build a patch bundle from dirty repos:
   - `python tools/mkpatch.py --prune-old --keep 3`
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

### Trigger from CLI (required when publication requested)
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

---

## Fail-fast checks before task completion
Agents must run these checks conceptually (and command-line checks where possible) before finishing:

1. If files were changed in `deps/*`, ensure `patches/<bundle>/` exists.
2. If `patches/<bundle>/` does not exist, run `python tools/mkpatch.py --prune-old --keep 3`.
3. Ensure metarepo `git status` includes only intended tracked artifacts (no `deps/` files staged).
4. Ensure final output includes:
   - impacted `deps/<repo>` names,
   - bundle path,
   - metarepo commit SHA,
   - PR URL,
   - repo-ops run URL (when publication was requested).

Any missing required item means the task is incomplete.

---

## Validation expectations
For each repo changed, run appropriate checks for that repo. Typical baseline:
- `pre-commit run -a`
- `pytest`
- `ruff check .`
- `mypy`

If a nested `AGENTS.md` exists in a changed repo, follow the more specific instructions there.

---

## Git and PR workflow
- Keep changes scoped.
- Run `python tools/mkpatch.py --prune-old --keep 3` before committing metarepo bundle artifacts.
- Commit in the repo you changed.
- Open a PR with:
  - what changed,
  - why it changed,
  - impacted repo(s),
  - exact commands run for validation.
- If publishing is required, verify branch push to `origin`.

---

## Operator-facing response contract (required output format)
When reporting task completion, include these sections explicitly:

1. **Impacted repos**: list each `deps/<repo>` changed.
2. **Patch bundle**: exact `patches/<bundle>/` path.
3. **Validation run**: exact commands executed and outcomes.
4. **Metarepo commit**: SHA and commit title.
5. **PR**: URL to metarepo PR.
6. **Publication** (if requested): workflow run URL and status.

This contract exists to prevent “changes only in deps/” outcomes.

---

## Efficiency guidelines
- Prefer `rg`/`git grep` over broad scans.
- Avoid generated artifacts unless needed.
- Never commit `deps/` content from this metarepo.
