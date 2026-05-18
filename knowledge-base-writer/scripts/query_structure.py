#!/usr/bin/env python3
"""Query knowledge base structure."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


DIMENSIONS = ("Categories", "Topics", "References")


def resolve_base_path(value: str | None) -> Path:
    raw = value or os.environ.get("KNOWLEDGE_BASE_PATH") or os.environ.get("KB_BASE_PATH") or "."
    return Path(raw).expanduser().resolve()


def query_structure(base_path: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {dimension: [] for dimension in DIMENSIONS}
    for dimension in DIMENSIONS:
        folder = base_path / dimension
        if folder.is_dir():
            result[dimension] = sorted(path.stem for path in folder.glob("*.md"))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Query knowledge base structure")
    parser.add_argument("--all", action="store_true", help="Query all dimensions")
    parser.add_argument("--categories", action="store_true", help="Show Categories")
    parser.add_argument("--topics", action="store_true", help="Show Topics")
    parser.add_argument("--references", action="store_true", help="Show References")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--base-path", help="Knowledge base root path")
    args = parser.parse_args()

    if not any((args.all, args.categories, args.topics, args.references)):
        args.all = True

    structure = query_structure(resolve_base_path(args.base_path))
    if not args.all:
        filtered: dict[str, list[str]] = {}
        if args.categories:
            filtered["Categories"] = structure["Categories"]
        if args.topics:
            filtered["Topics"] = structure["Topics"]
        if args.references:
            filtered["References"] = structure["References"]
        structure = filtered

    if args.json:
        print(json.dumps(structure, indent=2, ensure_ascii=False))
    else:
        print("KNOWLEDGE BASE STRUCTURE")
        print("=" * 50)
        for dimension, values in structure.items():
            print(f"\n{dimension} ({len(values)} items):")
            for value in values:
                print(f"  - {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
