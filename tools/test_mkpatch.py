from __future__ import annotations

import json
import os
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

    plan = json.loads((tmp_path / "patches" / "bundle-plan" / "change_plan.json").read_text(encoding="utf-8"))
    assert plan["schema_version"] == 1
    assert plan["bundle"] == "bundle-plan"
    assert plan["changes"][0]["repo"] == "another-repo"
    assert plan["changes"][0]["patch_path"] == "patches/bundle-plan/another-repo.patch"


def test_prune_old_keeps_newest_bundle_directories(tmp_path: Path) -> None:
    patches_dir = tmp_path / "patches"
    patches_dir.mkdir(parents=True)

    bundles = []
    for idx in range(5):
        bundle = patches_dir / f"bundle-20240101-00000{idx}"
        bundle.mkdir()
        marker = bundle / "marker.txt"
        marker.write_text(str(idx), encoding="utf-8")
        bundles.append(bundle)

    for idx, bundle in enumerate(bundles):
        ts = 10_000 + idx
        marker = bundle / "marker.txt"
        marker.touch()
        os.utime(bundle, (ts, ts))
        os.utime(marker, (ts, ts))

    from tools.mkpatch import prune_old_bundles

    deleted = prune_old_bundles(patches_dir, keep=3)

    assert [path.name for path in deleted] == [
        "bundle-20240101-000001",
        "bundle-20240101-000000",
    ]
    remaining = sorted(path.name for path in patches_dir.glob("bundle-*") if path.is_dir())
    assert remaining == [
        "bundle-20240101-000002",
        "bundle-20240101-000003",
        "bundle-20240101-000004",
    ]


def test_mkpatch_prune_old_prints_deleted_summary(tmp_path: Path) -> None:
    deps_dir = tmp_path / "deps"
    patches_dir = tmp_path / "patches"
    deps_dir.mkdir()
    patches_dir.mkdir()

    for idx in range(4):
        bundle = patches_dir / f"bundle-20240101-00000{idx}"
        bundle.mkdir()
        marker = bundle / "marker.txt"
        marker.write_text("old", encoding="utf-8")
        ts = 20_000 + idx
        os.utime(bundle, (ts, ts))
        os.utime(marker, (ts, ts))

    repo_dir = deps_dir / "prune-repo"
    run(["git", "init", repo_dir.name], cwd=deps_dir)
    run(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)

    tracked = repo_dir / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    run(["git", "add", "tracked.txt"], cwd=repo_dir)
    run(["git", "commit", "-m", "initial"], cwd=repo_dir)
    tracked.write_text("after\n", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--bundle",
            "bundle-new",
            "--root",
            str(tmp_path),
            "--prune-old",
            "--keep",
            "2",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "Deleted stale bundles:" in result.stdout
    assert str(patches_dir / "bundle-20240101-000000") in result.stdout
    assert str(patches_dir / "bundle-20240101-000001") in result.stdout

    remaining = sorted(path.name for path in patches_dir.glob("bundle-*") if path.is_dir())
    assert remaining == ["bundle-20240101-000002", "bundle-20240101-000003", "bundle-new"]
