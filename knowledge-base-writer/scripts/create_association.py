#!/usr/bin/env python3
"""Create a Category, Topic, or Reference association."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


VALID_DIMENSIONS = ("Categories", "Topics", "References")


def resolve_base_path(value: str | None) -> Path:
    raw = value or os.environ.get("KNOWLEDGE_BASE_PATH") or os.environ.get("KB_BASE_PATH") or "."
    return Path(raw).expanduser().resolve()


def validate_name(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", name):
        raise ValueError("name must be lowercase snake_case using letters, digits, and underscores")


def create_association(base_path: Path, name: str, dimension: str, description: str | None) -> dict[str, str]:
    if dimension not in VALID_DIMENSIONS:
        raise ValueError(f"dimension must be one of: {', '.join(VALID_DIMENSIONS)}")
    validate_name(name)

    bases_dir = base_path / "Bases"
    dimension_dir = base_path / dimension
    bases_dir.mkdir(parents=True, exist_ok=True)
    dimension_dir.mkdir(parents=True, exist_ok=True)

    base_file = bases_dir / f"{name}.base"
    md_file = dimension_dir / f"{name}.md"

    base_file.write_text(
        f"""filters:
  and:
    - {dimension}.contains(link("{name}"))
views:
  - type: table
    name: Table
""",
        encoding="utf-8",
    )

    lines = ["---", "dg-publish: true", "---", ""]
    if description:
        lines.extend([description.strip(), ""])
    lines.append(f"![[{name}.base]]")
    md_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {"base_file": str(base_file), "md_file": str(md_file), "dimension": dimension}


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a knowledge base association")
    parser.add_argument("--name", required=True, help="Association name in lowercase snake_case")
    parser.add_argument("--dimension", required=True, choices=VALID_DIMENSIONS, help="Association dimension")
    parser.add_argument("--description", help="Optional description for the markdown file")
    parser.add_argument("--base-path", help="Knowledge base root path")
    args = parser.parse_args()

    try:
        result = create_association(resolve_base_path(args.base_path), args.name, args.dimension, args.description)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        return 1

    print(f"[CREATED] {result['base_file']}")
    print(f"[CREATED] {result['md_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
