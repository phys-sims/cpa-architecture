from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "docs" / "context" / "sources.yml"
SNAPSHOTS_ROOT = ROOT / "docs" / "context" / "snapshots"


@dataclasses.dataclass(frozen=True)
class SourceSpec:
    repo: str
    ref: str
    paths: list[str]


def parse_sources_file(path: Path) -> list[SourceSpec]:
    """Parse docs/context/sources.yml using a constrained schema.

    Supported YAML shape:

    sources:
      - repo: owner/name
        ref: branch-or-tag
        paths:
          - file.md
    """

    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise ValueError("sources file is empty")

    specs: list[SourceSpec] = []
    in_sources = False
    current: dict[str, object] | None = None
    in_paths = False

    def flush_current() -> None:
        nonlocal current
        if current is None:
            return
        repo = current.get("repo")
        ref = current.get("ref")
        paths = current.get("paths")
        if not isinstance(repo, str) or not repo:
            raise ValueError("Each source requires a non-empty 'repo'")
        if not isinstance(ref, str) or not ref:
            raise ValueError("Each source requires a non-empty 'ref'")
        if not isinstance(paths, list) or not paths or not all(isinstance(p, str) and p for p in paths):
            raise ValueError("Each source requires a non-empty string list for 'paths'")
        specs.append(SourceSpec(repo=repo, ref=ref, paths=paths))
        current = None

    for raw_line in lines:
        line = raw_line.split("#", 1)[0].rstrip()
        if not line:
            continue

        if not in_sources:
            if line.strip() == "sources:":
                in_sources = True
                continue
            raise ValueError("Expected top-level 'sources:' key")

        stripped = line.lstrip(" ")
        indent = len(line) - len(stripped)

        if indent == 2 and stripped.startswith("- "):
            flush_current()
            current = {"paths": []}
            in_paths = False
            maybe_keyval = stripped[2:]
            if maybe_keyval:
                key, sep, value = maybe_keyval.partition(":")
                if sep != ":":
                    raise ValueError(f"Malformed source entry line: {raw_line}")
                current[key.strip()] = value.strip()
            continue

        if current is None:
            raise ValueError(f"Unexpected content before first source entry: {raw_line}")

        if indent == 4 and stripped.startswith("paths:"):
            in_paths = True
            continue

        if indent == 6 and stripped.startswith("- ") and in_paths:
            path_value = stripped[2:].strip()
            if not path_value:
                raise ValueError("Path list entries must be non-empty")
            cast_paths = current.setdefault("paths", [])
            if not isinstance(cast_paths, list):
                raise ValueError("'paths' must be a list")
            cast_paths.append(path_value)
            continue

        if indent == 4:
            key, sep, value = stripped.partition(":")
            if sep != ":":
                raise ValueError(f"Malformed key/value line: {raw_line}")
            current[key.strip()] = value.strip()
            if key.strip() != "paths":
                in_paths = False
            continue

        raise ValueError(f"Unsupported or mis-indented line: {raw_line}")

    flush_current()

    if not specs:
        raise ValueError("No sources configured")

    return specs


def _http_get(url: str, headers: dict[str, str] | None = None) -> bytes:
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req) as response:  # noqa: S310 - URL built from trusted config
        return response.read()


def fetch_ref_sha(repo: str, ref: str) -> str | None:
    api_url = f"https://api.github.com/repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}"
    try:
        body = _http_get(api_url, headers={"Accept": "application/vnd.github+json"})
    except urllib.error.HTTPError:
        return None
    except urllib.error.URLError:
        return None

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return None

    sha = payload.get("sha")
    return sha if isinstance(sha, str) else None


def fetch_raw_markdown(repo: str, ref: str, path: str) -> str:
    url = f"https://raw.githubusercontent.com/{repo}/{urllib.parse.quote(ref, safe='')}/{path}"
    data = _http_get(url)
    return data.decode("utf-8")


def sync_sources(sources: list[SourceSpec]) -> Path:
    SNAPSHOTS_ROOT.mkdir(parents=True, exist_ok=True)
    sync_time = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    index_lines = [
        "# Context snapshots index",
        "",
        f"- Sync date (UTC): {sync_time}",
        "",
        "## Sources",
    ]

    for source in sources:
        sha = fetch_ref_sha(source.repo, source.ref)
        index_lines.append("")
        index_lines.append(f"### {source.repo}@{source.ref}")
        index_lines.append(f"- Commit SHA: {sha or 'unavailable'}")
        index_lines.append("- Files:")

        repo_dir = SNAPSHOTS_ROOT / source.repo
        for relative_path in source.paths:
            destination = repo_dir / relative_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            markdown = fetch_raw_markdown(source.repo, source.ref, relative_path)
            destination.write_text(markdown, encoding="utf-8")
            index_lines.append(f"  - `{source.repo}/{relative_path}`")

    index_path = SNAPSHOTS_ROOT / "INDEX.md"
    index_path.write_text("\n".join(index_lines) + "\n", encoding="utf-8")
    return index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync dependency context snapshots")
    parser.add_argument("--sources", type=Path, default=SOURCES_FILE, help="Path to sources.yml")
    args = parser.parse_args()

    sources = parse_sources_file(args.sources)
    index_path = sync_sources(sources)
    print(f"Synced {len(sources)} sources. Index written to {index_path}")


if __name__ == "__main__":
    main()
