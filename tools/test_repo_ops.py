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
    assert "DRY RUN: would checkout codex/bundle-test/demo-repo at abc123" in result.stdout


def test_repo_ops_dry_run_without_base_sha_reports_tip_checkout(tmp_path: Path) -> None:
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
                        "base_sha": None,
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

    assert "DRY RUN: no base_sha provided; would keep cloned branch tip" in result.stdout


def test_checkout_base_resets_branch_to_base_sha(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    run(["git", "init"], cwd=repo_dir)
    run(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)

    tracked = repo_dir / "README.md"
    tracked.write_text("initial\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=repo_dir)
    run(["git", "commit", "-m", "initial commit"], cwd=repo_dir)
    base_sha = run(["git", "rev-parse", "HEAD"], cwd=repo_dir).stdout.strip()

    tracked.write_text("second\n", encoding="utf-8")
    run(["git", "commit", "-am", "second commit"], cwd=repo_dir)

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from tools.repo_ops import checkout_base; "
                f"checkout_base(Path(r'{repo_dir}'), 'codex/test-branch', '{base_sha}')"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    head = run(["git", "rev-parse", "HEAD"], cwd=repo_dir).stdout.strip()
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir).stdout.strip()
    assert head == base_sha
    assert branch == "codex/test-branch"


def test_assert_base_sha_mismatch_has_remediation(tmp_path: Path) -> None:
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    run(["git", "init"], cwd=repo_dir)
    run(["git", "config", "user.name", "Test User"], cwd=repo_dir)
    run(["git", "config", "user.email", "test@example.com"], cwd=repo_dir)

    tracked = repo_dir / "README.md"
    tracked.write_text("initial\n", encoding="utf-8")
    run(["git", "add", "README.md"], cwd=repo_dir)
    run(["git", "commit", "-m", "initial commit"], cwd=repo_dir)

    missing_sha = "f" * 40
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from tools.repo_ops import assert_base_sha; "
                f"assert_base_sha(Path(r'{repo_dir}'), '{missing_sha}')"
            ),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Base SHA mismatch detected." in result.stderr
    assert "Repository: repo" in result.stderr
    assert "Suggested next steps:" in result.stderr
    assert "python tools/mkpatch.py" in result.stderr
    assert "updated plan_path" in result.stderr


def test_with_github_token_encodes_special_characters() -> None:
    from tools.repo_ops import with_github_token

    url = with_github_token("https://github.com/example-org/demo-repo.git", "ghs_ab:c/+=?")

    assert url == "https://x-access-token:ghs_ab%3Ac%2F%2B%3D%3F@github.com/example-org/demo-repo.git"


def test_with_github_token_requires_https() -> None:
    from tools.repo_ops import with_github_token

    try:
        with_github_token("git@github.com:example-org/demo-repo.git", "token")
    except ValueError as exc:
        assert "Only https:// URLs are supported" in str(exc)
    else:
        raise AssertionError("Expected ValueError for non-https URL")


def test_resolve_plan_path_repairs_patch_file_suffix(tmp_path: Path) -> None:
    from tools.repo_ops import resolve_plan_path

    workspace = tmp_path
    bundle_dir = workspace / "patches" / "bundle-test"
    bundle_dir.mkdir(parents=True)
    expected_plan = bundle_dir / "change_plan.json"
    expected_plan.write_text("{}", encoding="utf-8")

    malformed = Path("patches/bundle-test/demo.patch/change_plan.json")

    resolved = resolve_plan_path(malformed, workspace)

    assert resolved == expected_plan


def test_resolve_plan_path_accepts_bundle_directory(tmp_path: Path) -> None:
    from tools.repo_ops import resolve_plan_path

    workspace = tmp_path
    bundle_dir = workspace / "patches" / "bundle-test"
    bundle_dir.mkdir(parents=True)

    resolved = resolve_plan_path(Path("patches/bundle-test"), workspace)

    assert resolved == bundle_dir / "change_plan.json"


def test_repo_ops_reports_resolved_plan_path_when_missing(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--workspace-root",
            str(tmp_path),
            "--plan",
            "patches/bundle-test/demo.patch/change_plan.json",
            "--org",
            "example-org",
            "--dry-run",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Plan file not found." in result.stderr
    assert "Provided: patches/bundle-test/demo.patch/change_plan.json" in result.stderr
    assert "Resolved:" in result.stderr
