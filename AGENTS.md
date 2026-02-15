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
- `deps/` – generated dependency repos (gitignored; never commit).

## Scope and change targeting
- Update this repo when changing:
  - cross-repo ADRs/system docs,
  - workspace automation (`tools/bootstrap.py`),
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
