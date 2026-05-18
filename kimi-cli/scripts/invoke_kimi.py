#!/usr/bin/env python3
"""Invoke Kimi CLI with UTF-8 handling and a subprocess timeout."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def check_kimi_installed() -> bool:
    try:
        result = subprocess.run(["kimi", "--version"], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def invoke_kimi(
    prompt: str,
    work_dir: str,
    output_path: str | None = None,
    timeout_ms: int = 600_000,
    model: str | None = None,
    continue_session: bool = False,
) -> dict[str, object]:
    if not check_kimi_installed():
        return {
            "success": False,
            "output_path": None,
            "error": "kimi CLI not found. Install and authenticate Kimi CLI before using this wrapper.",
        }

    work_dir_path = Path(work_dir).expanduser().resolve()
    if not work_dir_path.exists():
        return {"success": False, "output_path": None, "error": f"work-dir not found: {work_dir_path}"}

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    cmd = ["kimi", "--quiet"]
    if continue_session:
        cmd.append("--continue")
    if model:
        cmd.extend(["--model", model])
    cmd.extend(["--work-dir", str(work_dir_path)])

    if output_path:
        output = Path(output_path).expanduser()
        if not output.is_absolute():
            output = work_dir_path / output
        if str(output) not in prompt:
            prompt = f"{prompt}\n\nSave the complete response to: {output}"
    else:
        output = None

    cmd.extend(["--prompt", prompt])

    timeout_sec = timeout_ms / 1000
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            env=env,
        )
    except subprocess.TimeoutExpired:
        existing = str(output) if output and output.exists() else None
        return {"success": False, "output_path": existing, "error": f"timeout after {timeout_sec:.0f}s"}

    output_created = str(output) if output and output.exists() else None
    if result.returncode != 0 and not output_created:
        message = result.stderr or result.stdout or "unknown error"
        if "auth" in message.lower() or "login" in message.lower():
            message = "authentication required; run `kimi login` first"
        return {"success": False, "output_path": None, "error": message[:1000]}

    return {
        "success": True,
        "output_path": output_created,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Invoke Kimi CLI")
    parser.add_argument("--prompt", required=True, help="Task prompt")
    parser.add_argument("--work-dir", required=True, help="Project or working directory")
    parser.add_argument("--output", help="Expected output file path")
    parser.add_argument("--timeout", type=int, default=600_000, help="Subprocess timeout in milliseconds")
    parser.add_argument("--model", help="Optional Kimi model override")
    parser.add_argument("--continue", dest="continue_session", action="store_true", help="Continue prior Kimi session")
    args = parser.parse_args()

    result = invoke_kimi(args.prompt, args.work_dir, args.output, args.timeout, args.model, args.continue_session)
    if result["success"]:
        print("SUCCESS")
        if result.get("output_path"):
            print(f"Output: {result['output_path']}")
        return 0

    print(f"ERROR: {result['error']}")
    if result.get("output_path"):
        print(f"Partial output: {result['output_path']}")
    return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    raise SystemExit(main())
