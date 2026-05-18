#!/usr/bin/env python3
"""Run a Kimi CLI web-search prompt with UTF-8 handling."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def run_kimi_search(prompt: str, work_dir: str = ".", output_file: str | None = None, timeout: int = 180) -> dict[str, object]:
    work_dir_path = Path(work_dir).expanduser().resolve()
    if not work_dir_path.exists():
        return {"success": False, "output_path": None, "error": f"work-dir not found: {work_dir_path}", "elapsed": 0.0}

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    expected_output: Path | None = None
    if output_file:
        expected_output = Path(output_file).expanduser()
        if not expected_output.is_absolute():
            expected_output = work_dir_path / expected_output
        if str(expected_output) not in prompt:
            prompt = f"{prompt}\n\nSave the complete result to: {expected_output}"

    cmd = ["kimi", "--quiet", "--prompt", prompt, "--work-dir", str(work_dir_path)]
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return {"success": False, "output_path": None, "error": "kimi CLI not found", "elapsed": time.time() - start}
    except subprocess.TimeoutExpired:
        output_path = str(expected_output) if expected_output and expected_output.exists() else None
        return {"success": False, "output_path": output_path, "error": f"timeout after {timeout}s", "elapsed": time.time() - start}

    output_path = str(expected_output) if expected_output and expected_output.exists() else None
    if result.returncode == 0 or output_path:
        return {
            "success": True,
            "output_path": output_path,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "elapsed": time.time() - start,
        }

    message = result.stderr or result.stdout or "unknown error"
    return {"success": False, "output_path": None, "error": message[:1000], "elapsed": time.time() - start}


def main() -> int:
    parser = argparse.ArgumentParser(description="Kimi CLI web-search wrapper")
    parser.add_argument("prompt", help="Search prompt")
    parser.add_argument("--work-dir", default=".", help="Working directory")
    parser.add_argument("--output", help="Expected output file path")
    parser.add_argument("--timeout", type=int, default=180, help="Subprocess timeout in seconds")
    args = parser.parse_args()

    result = run_kimi_search(args.prompt, args.work_dir, args.output, args.timeout)
    if result["success"]:
        print(f"SUCCESS in {result['elapsed']:.1f}s")
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
