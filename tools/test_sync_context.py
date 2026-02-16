from __future__ import annotations

from pathlib import Path
from textwrap import dedent

from tools.sync_context import SourceSpec, parse_sources_file


def test_parse_sources_file_reads_expected_schema(tmp_path: Path) -> None:
    sources_file = tmp_path / "sources.yml"
    sources_file.write_text(
        dedent(
            """
            sources:
              - repo: org/repo-a
                ref: main
                paths:
                  - README.md
                  - docs/spec.md
              - repo: org/repo-b
                ref: v1.2.3
                paths:
                  - docs/contract.md
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )

    parsed = parse_sources_file(sources_file)

    assert parsed == [
        SourceSpec(repo="org/repo-a", ref="main", paths=["README.md", "docs/spec.md"]),
        SourceSpec(repo="org/repo-b", ref="v1.2.3", paths=["docs/contract.md"]),
    ]
