#!/usr/bin/env python3
"""Validate resources for paper analysis and print an agent handoff plan."""

from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path


def workspace_path(value: str | None) -> Path:
    raw = value or os.environ.get("PAPER_ANALYSIS_WORKSPACE") or "."
    return Path(raw).expanduser().resolve()


def env_path(name: str, fallback: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw).expanduser().resolve() if raw else fallback.resolve()


def resolve_path(path: str, workspace: Path) -> Path:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (workspace / candidate).resolve()


def calculate_timeout(pages: int | None) -> int:
    pages = pages if pages and pages > 0 else 10
    return min(1200 + pages * 90, 5400)


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "paper"


def validate_file(path: Path, label: str) -> tuple[bool, str]:
    if not path.exists():
        return False, f"{label} not found: {path}"
    if not path.is_file():
        return False, f"{label} is not a file: {path}"
    size = path.stat().st_size
    if size == 0:
        return False, f"{label} is empty: {path}"
    return True, f"{label}: {path} ({size} bytes)"


def optional_pdf_check(path: str | None, workspace: Path) -> tuple[bool, Path | None, str | None]:
    if not path:
        return True, None, None
    pdf = resolve_path(path, workspace)
    ok, message = validate_file(pdf, "PDF")
    if not ok:
        return False, pdf, message
    if pdf.suffix.lower() != ".pdf":
        return False, pdf, f"PDF path does not end with .pdf: {pdf}"
    return True, pdf, message


def copy_pdf_to_archive(pdf: Path | None, archive_dir: Path, archive_name: str | None) -> Path | None:
    if not pdf:
        return None
    archive_dir.mkdir(parents=True, exist_ok=True)
    target_name = archive_name or pdf.name
    if not target_name.lower().endswith(".pdf"):
        target_name += ".pdf"
    target = archive_dir / target_name
    if pdf.resolve() != target.resolve():
        shutil.copy2(pdf, target)
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare resources for paper analysis")
    parser.add_argument("--paper-text", required=True, help="Extracted paper text file")
    parser.add_argument("--paper-id", required=True, help="Short paper identifier")
    parser.add_argument("--output", required=True, help="Target analysis output file")
    parser.add_argument("--pages", type=int, help="Paper page count")
    parser.add_argument("--workspace", help="Workspace root for relative paths")
    parser.add_argument("--pdf", help="Optional original PDF path to validate")
    parser.add_argument("--archive-pdf", action="store_true", help="Copy --pdf into the archive directory")
    parser.add_argument("--archive-name", help="Archive filename, usually YYYYMMDD_descriptive_slug.pdf")
    parser.add_argument("--archive-dir", help="PDF archive directory")
    parser.add_argument("--base-path", help="Knowledge base root path")
    parser.add_argument("--language", default="Chinese", help="Preferred analysis language")
    parser.add_argument("--min-words", type=int, default=3800, help="Minimum target analysis length")
    parser.add_argument("--max-words", type=int, default=6000, help="Maximum target analysis length")
    parser.add_argument(
        "--template",
        default="public/knowledge-base-paper-analysis/references/sub-agent-prompt-template.md",
        help="Analysis prompt template path",
    )
    args = parser.parse_args()

    workspace = workspace_path(args.workspace)
    paper_text = resolve_path(args.paper_text, workspace)
    output = resolve_path(args.output, workspace)
    template = resolve_path(args.template, workspace)
    base_path = resolve_path(args.base_path, workspace) if args.base_path else env_path("KNOWLEDGE_BASE_PATH", workspace / "knowledge-base")
    archive_dir = resolve_path(args.archive_dir, workspace) if args.archive_dir else env_path("PAPER_ARCHIVE_PATH", workspace / "papers")

    all_ok = True
    pdf_ok, pdf_path, pdf_message = optional_pdf_check(args.pdf, workspace)
    checks = [validate_file(paper_text, "Paper text"), validate_file(template, "Prompt template")]
    if pdf_message:
        checks.append((pdf_ok, pdf_message))

    for ok, message in checks:
        print(("[PASS] " if ok else "[FAIL] ") + message)
        all_ok = all_ok and ok

    output.parent.mkdir(parents=True, exist_ok=True)
    archived_pdf = None
    if all_ok and args.archive_pdf:
        archived_pdf = copy_pdf_to_archive(pdf_path, archive_dir, args.archive_name)
        if archived_pdf:
            print(f"[PASS] Archived PDF: {archived_pdf}")

    timeout_seconds = calculate_timeout(args.pages)
    expected_slug = slugify(args.paper_id)
    print(f"[INFO] Paper ID: {args.paper_id}")
    print(f"[INFO] Suggested slug: {expected_slug}")
    print(f"[INFO] Workspace: {workspace}")
    print(f"[INFO] Knowledge base path: {base_path}")
    print(f"[INFO] PDF archive directory: {archive_dir}")
    print(f"[INFO] Analysis output target: {output}")
    print(f"[INFO] Target analysis length: {args.min_words}-{args.max_words} words")
    print(f"[INFO] Recommended timeout: {timeout_seconds // 60} minutes ({timeout_seconds} seconds)")
    print("[INFO] Sub-agent handoff prompt:")
    print("-----")
    print(f"Read the prompt template at: {template}")
    print(f"Read the extracted paper text at: {paper_text}")
    print(f"Write a complete {args.language} narrative analysis to: {output}")
    print(f"Target length: {args.min_words}-{args.max_words} words unless the user requests otherwise.")
    print("Do not paste the full analysis into the chat response; write it to the output file.")
    print("After writing, report only metadata, section coverage, limitations, and any extraction gaps.")
    print("-----")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
