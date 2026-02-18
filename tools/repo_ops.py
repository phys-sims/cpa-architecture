#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote


@dataclass(frozen=True)
class Change:
    repo: str
    branch: str
    commit_message: str
    patch_path: Path
    base_sha: str | None


@dataclass(frozen=True)
class Plan:
    schema_version: int
    bundle: str
    changes: list[Change]


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    result = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        check=True,
        text=True,
        capture_output=True,
        env=env,
    )
    return result.stdout.strip()


def load_plan(plan_path: Path) -> Plan:
    raw = json.loads(plan_path.read_text(encoding="utf-8"))
    schema_version = int(raw["schema_version"])
    bundle = str(raw["bundle"])
    changes_raw = raw.get("changes", [])
    if not isinstance(changes_raw, list) or not changes_raw:
        raise ValueError("change plan must include at least one change")

    changes: list[Change] = []
    for item in changes_raw:
        patch_path = Path(item["patch_path"])
        changes.append(
            Change(
                repo=str(item["repo"]),
                branch=str(item["branch"]),
                commit_message=str(item["commit_message"]),
                patch_path=patch_path,
                base_sha=str(item["base_sha"]) if item.get("base_sha") else None,
            )
        )

    return Plan(schema_version=schema_version, bundle=bundle, changes=changes)


def with_github_token(repo_url: str, token: str) -> str:
    if not repo_url.startswith("https://"):
        raise ValueError(f"Only https:// URLs are supported for authenticated clone: {repo_url}")

    encoded_token = quote(token, safe="")
    return repo_url.replace("https://", f"https://x-access-token:{encoded_token}@", 1)


def clone_repo(work_dir: Path, repo_url: str, branch: str, token: str) -> Path:
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    dest = work_dir / repo_name
    if dest.exists():
        shutil.rmtree(dest)

    auth_repo_url = with_github_token(repo_url, token)
    run(["git", "clone", auth_repo_url, str(dest)])
    run(["git", "checkout", "-B", branch], cwd=dest)
    run(["git", "remote", "set-url", "origin", auth_repo_url], cwd=dest)
    return dest


def checkout_base(repo_dir: Path, branch: str, base_sha: str) -> None:
    expected_exists = (
        subprocess.run(
            ["git", "cat-file", "-e", f"{base_sha}^{{commit}}"],
            cwd=str(repo_dir),
            text=True,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )
    if not expected_exists:
        head = run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
        current_branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)
        raise RuntimeError(
            "Base SHA mismatch detected.\n"
            f"Repository: {repo_dir.name}\n"
            f"Expected SHA: {base_sha}\n"
            f"Current SHA: {head}\n"
            f"Current branch: {current_branch}\n"
            "Merge-base relationship: expected SHA not found in local clone\n"
            "Suggested next steps:\n"
            "  1. Regenerate the bundle: python tools/mkpatch.py\n"
            "  2. Rerun the workflow with an updated plan_path."
        )

    run(["git", "checkout", "-B", branch, base_sha], cwd=repo_dir)


def apply_patch(repo_dir: Path, patch_path: Path) -> None:
    run(["git", "apply", str(patch_path)], cwd=repo_dir)


def assert_base_sha(repo_dir: Path, base_sha: str | None) -> None:
    if not base_sha:
        return
    head = run(["git", "rev-parse", "HEAD"], cwd=repo_dir)
    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir)
    expected_exists = (
        subprocess.run(
            ["git", "cat-file", "-e", f"{base_sha}^{{commit}}"],
            cwd=str(repo_dir),
            text=True,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )

    relationship = "expected SHA not found in local clone"
    if expected_exists:
        if head == base_sha:
            return

        expected_is_ancestor = (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", base_sha, "HEAD"],
                cwd=str(repo_dir),
                text=True,
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )
        head_is_ancestor = (
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", "HEAD", base_sha],
                cwd=str(repo_dir),
                text=True,
                capture_output=True,
                check=False,
            ).returncode
            == 0
        )

        if expected_is_ancestor:
            relationship = "expected SHA is an ancestor of current HEAD"
        elif head_is_ancestor:
            relationship = "current HEAD is an ancestor of expected SHA"
        else:
            relationship = "expected SHA and current HEAD are on different branches"

    raise RuntimeError(
        "Base SHA mismatch detected.\n"
        f"Repository: {repo_dir.name}\n"
        f"Expected SHA: {base_sha}\n"
        f"Current SHA: {head}\n"
        f"Current branch: {branch}\n"
        f"Merge-base relationship: {relationship}\n"
        "Suggested next steps:\n"
        "  1. Regenerate the bundle: python tools/mkpatch.py\n"
        "  2. Rerun the workflow with an updated plan_path."
    )


def has_changes(repo_dir: Path) -> bool:
    status = run(["git", "status", "--porcelain"], cwd=repo_dir)
    return bool(status)


def commit_and_push(repo_dir: Path, commit_message: str, branch: str) -> None:
    run(["git", "add", "-A"], cwd=repo_dir)
    run(["git", "commit", "-m", commit_message], cwd=repo_dir)
    run(["git", "push", "-u", "origin", branch, "--force-with-lease"], cwd=repo_dir)


def open_pr(repo_dir: Path, branch: str, base_branch: str, title: str, body: str) -> str:
    return run(
        [
            "gh",
            "pr",
            "create",
            "--head",
            branch,
            "--base",
            base_branch,
            "--title",
            title,
            "--body",
            body,
        ],
        cwd=repo_dir,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply cross-repo patch plan and publish PRs.")
    parser.add_argument("--plan", type=Path, required=True, help="Path to change_plan.json")
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd())
    parser.add_argument("--work-dir", type=Path, default=Path(".repo-ops-work"))
    parser.add_argument("--org", required=True, help="GitHub org, e.g. phys-sims")
    parser.add_argument("--base-branch", default="main")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        raise RuntimeError("GH_TOKEN or GITHUB_TOKEN is required unless --dry-run is used")

    plan = load_plan(args.plan)
    patch_root = args.workspace_root

    work_dir = args.work_dir
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing bundle {plan.bundle} with {len(plan.changes)} repo changes")
    for change in plan.changes:
        repo_url = f"https://github.com/{args.org}/{change.repo}.git"
        patch_path = patch_root / change.patch_path
        if not patch_path.exists():
            raise FileNotFoundError(f"Patch not found: {patch_path}")

        print(f"--- {change.repo} ---")
        if args.dry_run:
            print(f"DRY RUN: would clone {repo_url}")
            if change.base_sha:
                print(f"DRY RUN: would checkout {change.branch} at {change.base_sha}")
            else:
                print("DRY RUN: no base_sha provided; would keep cloned branch tip")
            print(f"DRY RUN: would apply patch {patch_path}")
            print(f"DRY RUN: would commit '{change.commit_message}' on {change.branch}")
            print(f"DRY RUN: would open PR to {args.base_branch}")
            continue

        repo_dir = clone_repo(work_dir, repo_url, change.branch, token)
        if change.base_sha:
            checkout_base(repo_dir, change.branch, change.base_sha)
        assert_base_sha(repo_dir, change.base_sha)
        apply_patch(repo_dir, patch_path)

        if not has_changes(repo_dir):
            print("No changes after patch apply; skipping push and PR.")
            continue

        commit_and_push(repo_dir, change.commit_message, change.branch)
        pr_body = (
            f"Automated cross-repo publication for bundle `{plan.bundle}`.\n\n"
            f"Applied patch: `{change.patch_path}`\n"
            f"Base SHA: `{change.base_sha or 'not specified'}`\n"
        )
        pr_url = open_pr(repo_dir, change.branch, args.base_branch, change.commit_message, pr_body)
        print(f"Opened PR: {pr_url}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
