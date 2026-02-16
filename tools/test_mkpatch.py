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

    assert patch_file.exists()
    assert report_file.exists()

    report = report_file.read_text(encoding="utf-8")
    assert "## Affected repos" in report
    assert "## Base SHAs" in report
    assert "## Summary" in report
    assert "## Apply instructions" in report
    assert "## Tests" in report
