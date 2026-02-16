#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DirtyRepo:
    name: str
    path: Path
    base_sha: str
    summary: str
    patch_text: str


def suggested_branch(bundle_name: str, repo_name: str) -> str:
    safe_repo = repo_name.replace("_", "-")
    return f"codex/{bundle_name}/{safe_repo}"


def suggested_commit_message(bundle_name: str, repo_name: str) -> str:
    return f"Apply {bundle_name} updates for {repo_name}"


def run_git(repo: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        text=True,
        capture_output=True,
    )


def list_dirty_repos(deps_dir: Path) -> list[DirtyRepo]:
    dirty_repos: list[DirtyRepo] = []
    if not deps_dir.exists():
        return dirty_repos

    for repo_path in sorted(p for p in deps_dir.iterdir() if p.is_dir() and (p / ".git").exists()):
        status = run_git(repo_path, ["status", "--porcelain"]).stdout.strip()
        if not status:
            continue

        base_sha = run_git(repo_path, ["rev-parse", "HEAD"]).stdout.strip()
        summary = run_git(repo_path, ["status", "--short"]).stdout.strip()
        patch_text = run_git(repo_path, ["diff", "HEAD"]).stdout
        dirty_repos.append(
            DirtyRepo(
                name=repo_path.name,
                path=repo_path,
                base_sha=base_sha,
                summary=summary,
                patch_text=patch_text,
            )
        )

    return dirty_repos


def write_change_report(bundle_dir: Path, repos: list[DirtyRepo]) -> None:
    affected = "\n".join(f"- {repo.name}" for repo in repos)
    base_shas = "\n".join(f"- {repo.name}: `{repo.base_sha}`" for repo in repos)
    summary_lines = "\n\n".join(f"### {repo.name}\n```\n{repo.summary}\n```" for repo in repos)
    repo_names = " ".join(repo.name for repo in repos)

    content = f"""# Change Report

## Affected repos
{affected}

## Base SHAs
{base_shas}

## Summary
{summary_lines}

## Apply instructions
```bash
for repo in {repo_names}; do
  (cd deps/"$repo" && git apply ../../patches/{bundle_dir.name}/"$repo".patch)
done
```

## Tests
- Add commands used to validate this bundle here.
"""

    (bundle_dir / "change_report.md").write_text(content, encoding="utf-8")


def write_bundle(repos: list[DirtyRepo], patches_dir: Path, bundle_name: str) -> Path:
    bundle_dir = patches_dir / bundle_name
    bundle_dir.mkdir(parents=True, exist_ok=False)

    for repo in repos:
        patch_path = bundle_dir / f"{repo.name}.patch"
        patch_path.write_text(repo.patch_text, encoding="utf-8")

    plan = {
        "schema_version": 1,
        "bundle": bundle_name,
        "changes": [
            {
                "repo": repo.name,
                "branch": suggested_branch(bundle_name, repo.name),
                "commit_message": suggested_commit_message(bundle_name, repo.name),
                "patch_path": f"patches/{bundle_name}/{repo.name}.patch",
                "base_sha": repo.base_sha,
            }
            for repo in repos
        ],
    }
    (bundle_dir / "change_plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    write_change_report(bundle_dir, repos)
    return bundle_dir


def make_bundle_name(now: dt.datetime | None = None) -> str:
    instant = now or dt.datetime.now(dt.timezone.utc)
    return instant.strftime("bundle-%Y%m%d-%H%M%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create patch bundles from dirty deps repos.")
    parser.add_argument("--bundle", help="Override bundle directory name.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Workspace root containing deps/.")
    args = parser.parse_args()

    deps_dir = args.root / "deps"
    patches_dir = args.root / "patches"

    dirty_repos = list_dirty_repos(deps_dir)
    if not dirty_repos:
        print("No dirty repos detected under deps/.")
        return 0

    bundle_name = args.bundle or make_bundle_name()
    bundle_dir = write_bundle(dirty_repos, patches_dir, bundle_name)
    print(f"Created patch bundle: {bundle_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
