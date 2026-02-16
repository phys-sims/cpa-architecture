from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "mkpatch.py"


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def test_mkpatch_generates_patch_and_report(tmp_path: Path) -> None:
    deps_dir = tmp_path / "deps"
    patches_dir = tmp_path / "patches"
    deps_dir.mkdir()

    repo_dir = deps_dir / "demo-repo"
    run(["git", "init", repo_dir.name], cwd=deps_dir)
    run(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)

    tracked = repo_dir / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    run(["git", "add", "tracked.txt"], cwd=repo_dir)
    run(["git", "commit", "-m", "initial"], cwd=repo_dir)

    tracked.write_text("after\n", encoding="utf-8")

    run([
        sys.executable,
        str(SCRIPT),
        "--bundle",
        "bundle-test",
        "--root",
        str(tmp_path),
    ], cwd=tmp_path)

    bundle_dir = patches_dir / "bundle-test"
    patch_file = bundle_dir / "demo-repo.patch"
    report_file = bundle_dir / "change_report.md"
    plan_file = bundle_dir / "change_plan.json"

    assert patch_file.exists()
    assert report_file.exists()
    assert plan_file.exists()

    report = report_file.read_text(encoding="utf-8")
    assert "## Affected repos" in report
    assert "## Base SHAs" in report
    assert "## Summary" in report
    assert "## Apply instructions" in report
    assert "## Tests" in report



def test_mkpatch_writes_machine_readable_plan(tmp_path: Path) -> None:
    deps_dir = tmp_path / "deps"
    deps_dir.mkdir(parents=True)

    repo_dir = deps_dir / "another-repo"
    run(["git", "init", repo_dir.name], cwd=deps_dir)
    run(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)

    tracked = repo_dir / "file.txt"
    tracked.write_text("one\n", encoding="utf-8")
    run(["git", "add", "file.txt"], cwd=repo_dir)
    run(["git", "commit", "-m", "initial"], cwd=repo_dir)

    tracked.write_text("two\n", encoding="utf-8")

    run([sys.executable, str(SCRIPT), "--bundle", "bundle-plan", "--root", str(tmp_path)], cwd=tmp_path)

    import json

    plan = json.loads((tmp_path / "patches" / "bundle-plan" / "change_plan.json").read_text(encoding="utf-8"))
    assert plan["schema_version"] == 1
    assert plan["bundle"] == "bundle-plan"
    assert plan["changes"][0]["repo"] == "another-repo"
    assert plan["changes"][0]["patch_path"] == "patches/bundle-plan/another-repo.patch"
