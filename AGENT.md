# AGENT.md

Compatibility entrypoint for agent instructions.

- Primary guidance lives in `AGENTS.md`.
- For cloud publication, follow the **Codex Cloud publication runbook (repo-ops publisher)** section in `AGENTS.md`, which mirrors the current `README.md` workflow.
- Key scripts:
  - `python tools/mkpatch.py`
  - `python tools/repo_ops.py --workspace-root . --plan patches/<bundle>/change_plan.json --org <github-org> [--dry-run]`
- Key GitHub Action:
  - `.github/workflows/repo-ops-publish.yml` (workflow dispatch)
