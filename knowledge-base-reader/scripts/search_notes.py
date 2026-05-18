#!/usr/bin/env python3
"""Search local markdown notes by frontmatter and keyword."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


DIMENSION_FIELDS = {
    "category": "Categories",
    "topic": "Topics",
    "reference": "References",
}


def resolve_base_path(value: str | None) -> Path:
    raw = value or os.environ.get("KNOWLEDGE_BASE_PATH") or os.environ.get("KB_BASE_PATH") or "."
    return Path(raw).expanduser().resolve()


def split_frontmatter(text: str) -> tuple[str, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return "", text
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, flags=re.S)
    if not match:
        return "", text
    return match.group(1), match.group(2)


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if key_match:
            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            data[current_key] = [] if value == "" else clean_value(value)
            continue
        item_match = re.match(r"^\s*-\s*(.*)$", line)
        if item_match and current_key:
            if not isinstance(data.get(current_key), list):
                data[current_key] = [data[current_key]]
            data[current_key].append(clean_value(item_match.group(1).strip()))
    return data


def clean_value(value: str) -> str:
    value = value.strip().strip("'\"")
    wiki = re.match(r"^\[\[([^|\]]+)(?:\|([^\]]+))?\]\]$", value)
    if wiki:
        return (wiki.group(2) or wiki.group(1)).split("/")[-1]
    return value


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def note_title(path: Path, meta: dict[str, Any], body: str) -> str:
    title_values = as_list(meta.get("title"))
    if title_values:
        return title_values[0]
    heading = re.search(r"^#\s+(.+)$", body, flags=re.M)
    return heading.group(1).strip() if heading else path.stem


def contains_value(values: list[str], expected: str | None) -> bool:
    if not expected:
        return True
    expected = expected.lower()
    normalized = {value.lower() for value in values}
    return expected in normalized


def is_starred(meta: dict[str, Any]) -> bool:
    tags = [tag.lstrip("#").lower() for tag in as_list(meta.get("tags"))]
    return "star" in tags or "starred" in tags


def search_notes(base_path: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    notes_dir = base_path / "Notes"
    if not notes_dir.is_dir():
        return []

    results: list[dict[str, Any]] = []
    keyword = args.keyword.lower() if args.keyword else None

    for path in sorted(notes_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        frontmatter, body = split_frontmatter(text)
        meta = parse_frontmatter(frontmatter)

        if args.starred and not is_starred(meta):
            continue
        if not contains_value(as_list(meta.get("Categories")), args.category):
            continue
        if not contains_value(as_list(meta.get("Topics")), args.topic):
            continue
        if not contains_value(as_list(meta.get("References")), args.reference):
            continue
        if keyword and keyword not in text.lower():
            continue

        rel_path = path.relative_to(base_path).as_posix()
        results.append(
            {
                "path": rel_path,
                "title": note_title(path, meta, body),
                "categories": as_list(meta.get("Categories")),
                "topics": as_list(meta.get("Topics")),
                "references": as_list(meta.get("References")),
                "update_date": as_list(meta.get("UpdateDate"))[:1],
                "credibility": as_list(meta.get("Credibility"))[:1],
            }
        )
        if args.limit and len(results) >= args.limit:
            break
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Search notes in a markdown knowledge base")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--topic", help="Filter by topic")
    parser.add_argument("--reference", help="Filter by reference")
    parser.add_argument("--keyword", help="Keyword search over whole note text")
    parser.add_argument("--starred", action="store_true", help="Only notes tagged star/starred")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--base-path", help="Knowledge base root path")
    args = parser.parse_args()

    if not any((args.category, args.topic, args.reference, args.keyword, args.starred)):
        print("Error: provide at least one search criterion", flush=True)
        return 2

    base_path = resolve_base_path(args.base_path)
    results = search_notes(base_path, args)

    if args.json:
        print(json.dumps({"base_path": str(base_path), "count": len(results), "notes": results}, indent=2, ensure_ascii=False))
    else:
        print(f"Found {len(results)} notes in {base_path}:")
        for item in results:
            print(f"- {item['path']} :: {item['title']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
