#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]


def sorted_bundle_dirs(patches_dir: Path) -> list[Path]:
    if not patches_dir.exists():
        return []

    bundle_dirs = [path for path in patches_dir.glob("bundle-*") if path.is_dir()]
    return sorted(bundle_dirs, key=lambda path: (path.stat().st_mtime, path.name), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate patches/bundle-* retention policy.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Workspace root containing patches/.")
    parser.add_argument(
        "--max-bundles",
        type=int,
        default=3,
        help="Maximum number of bundle-* directories allowed under patches/.",
    )
    args = parser.parse_args()

    if args.max_bundles < 0:
        parser.error("--max-bundles must be zero or greater")

    patches_dir = args.root / "patches"
    bundle_dirs = sorted_bundle_dirs(patches_dir)
    bundle_count = len(bundle_dirs)

    if bundle_count <= args.max_bundles:
        print(
            "Patch retention check passed: "
            f"{bundle_count} bundle(s) found (max allowed: {args.max_bundles})."
        )
        return 0

    stale_bundles = bundle_dirs[args.max_bundles:]
    stale_display = "\n".join(f"- {bundle_path.relative_to(args.root)}" for bundle_path in stale_bundles)
    print(
        "Patch retention policy violated.\n"
        f"Found {bundle_count} bundles under patches/, but the maximum allowed is {args.max_bundles}.\n"
        "Remove the following stale bundles (oldest beyond retention window):\n"
        f"{stale_display}"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
