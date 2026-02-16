from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "repo_ops.py"


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)


def test_repo_ops_dry_run_reads_plan(tmp_path: Path) -> None:
    patches_dir = tmp_path / "patches" / "bundle-test"
    patches_dir.mkdir(parents=True)

    patch_path = patches_dir / "demo.patch"
    patch_path.write_text("diff --git a/a.txt b/a.txt\n", encoding="utf-8")

    plan_path = patches_dir / "change_plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "bundle": "bundle-test",
                "changes": [
                    {
                        "repo": "demo-repo",
                        "branch": "codex/bundle-test/demo-repo",
                        "commit_message": "Apply bundle-test updates for demo-repo",
                        "patch_path": "patches/bundle-test/demo.patch",
                        "base_sha": "abc123",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run(
        [
            sys.executable,
            str(SCRIPT),
            "--workspace-root",
            str(tmp_path),
            "--plan",
            str(plan_path),
            "--org",
            "example-org",
            "--dry-run",
        ],
        cwd=tmp_path,
    )

    assert "Processing bundle bundle-test" in result.stdout
    assert "DRY RUN: would clone https://github.com/example-org/demo-repo.git" in result.stdout
