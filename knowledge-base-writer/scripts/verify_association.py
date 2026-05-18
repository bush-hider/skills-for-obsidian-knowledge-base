#!/usr/bin/env python3
"""Verify that note frontmatter contains expected associations."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


FIELDS = {
    "Categories": "category",
    "Topics": "topic",
    "References": "reference",
}


def resolve_base_path(value: str | None) -> Path:
    raw = value or os.environ.get("KNOWLEDGE_BASE_PATH") or os.environ.get("KB_BASE_PATH") or "."
    return Path(raw).expanduser().resolve()


def resolve_note_path(base_path: Path, note: str) -> Path:
    path = Path(note).expanduser()
    if path.is_absolute():
        return path
    return (base_path / path).resolve()


def split_frontmatter(text: str) -> str:
    text = text.lstrip("\ufeff")
    match = re.match(r"^---\s*\n(.*?)\n---", text, flags=re.S)
    return match.group(1) if match else ""


def clean_value(value: str) -> str:
    value = value.strip().strip("'\"")
    wiki = re.match(r"^\[\[([^|\]]+)(?:\|([^\]]+))?\]\]$", value)
    if wiki:
        return (wiki.group(2) or wiki.group(1)).split("/")[-1]
    return value


def parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in frontmatter.splitlines():
        line = raw_line.rstrip()
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


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def verify(base_path: Path, note: str, expected: dict[str, list[str]]) -> dict[str, Any]:
    note_path = resolve_note_path(base_path, note)
    if not note_path.exists():
        return {"note": str(note_path), "all_passed": False, "error": "note not found"}

    frontmatter = split_frontmatter(note_path.read_text(encoding="utf-8", errors="replace"))
    meta = parse_frontmatter(frontmatter)
    report: dict[str, Any] = {"note": str(note_path), "all_passed": True, "fields": {}}

    for field, names in expected.items():
        actual = {value.lower() for value in as_list(meta.get(field))}
        field_report = {}
        for name in names:
            exists = (base_path / field / f"{name}.md").exists()
            linked = name.lower() in actual
            status = "PASS" if exists and linked else "FAIL"
            field_report[name] = {"association_file_exists": exists, "linked_in_note": linked, "status": status}
            if status != "PASS":
                report["all_passed"] = False
        report["fields"][field] = field_report
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify note associations")
    parser.add_argument("--note", required=True, help="Note path, absolute or relative to base path")
    parser.add_argument("--category", action="append", default=[], help="Expected Category")
    parser.add_argument("--topic", action="append", default=[], help="Expected Topic")
    parser.add_argument("--reference", action="append", default=[], help="Expected Reference")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--base-path", help="Knowledge base root path")
    args = parser.parse_args()

    expected = {
        "Categories": args.category,
        "Topics": args.topic,
        "References": args.reference,
    }
    if not any(expected.values()):
        print("[ERROR] provide at least one expected association")
        return 2

    report = verify(resolve_base_path(args.base_path), args.note, expected)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("ASSOCIATION VERIFICATION REPORT")
        print("=" * 50)
        if "error" in report:
            print(f"[FAIL] {report['error']}: {report['note']}")
        else:
            for field, values in report["fields"].items():
                if values:
                    print(f"\n{field}:")
                    for name, data in values.items():
                        print(f"  [{data['status']}] {name} file={data['association_file_exists']} linked={data['linked_in_note']}")
            print("\nALL PASSED" if report["all_passed"] else "\nSOME CHECKS FAILED")
    return 0 if report.get("all_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
