---
name: kimi-cli
description: Use the Kimi Code CLI (`kimi`) as an external code-analysis helper for repository exploration, architecture review, and long-context project understanding. Use when the user explicitly asks to use Kimi, when a secondary CLI analysis pass would help on a large codebase, or when staged external analysis should be saved to files.
---

# Kimi CLI

Use Kimi Code CLI as a supporting analysis tool. The main agent remains responsible for scoping the task, reading the outputs critically, verifying important claims, and producing the final answer.

## Prerequisites

- `kimi` is installed and available on `PATH`.
- The user has authenticated if the CLI requires login.
- The target project path is safe to expose to the Kimi CLI process.

If `kimi` is unavailable or authentication fails, report that and continue with local analysis when possible.

## Basic Invocation

Prefer `--quiet` and file output:

```bash
kimi --quiet --prompt "Analyze the project architecture and save the result to analysis.md" --work-dir /path/to/project
```

For multi-step work, continue the session:

```bash
kimi --continue --quiet --prompt "Now analyze the core data flow and save to data-flow.md" --work-dir /path/to/project
```

The bundled wrapper handles UTF-8 environment setup and subprocess timeout:

```bash
python public/kimi-cli/scripts/invoke_kimi.py --prompt "Analyze the API layer. Save to api-analysis.md" --work-dir /path/to/project --output api-analysis.md
```

## Recommended Workflow

1. Ask Kimi for a broad scan that writes to a file.
2. Read the file and decide which modules deserve deeper inspection.
3. Run focused follow-up prompts for those modules.
4. Verify Kimi's claims against the actual code before relying on them.
5. Produce your own synthesis; do not forward raw Kimi output as the final answer.

## Prompt Patterns

Architecture scan:

```text
Analyze this repository from an architecture perspective. Identify major modules, ownership boundaries, data flow, external dependencies, and likely extension points. Save the full report to architecture.md.
```

Focused module analysis:

```text
Analyze the module at {path}. Explain its responsibilities, key abstractions, call graph, error handling, and risks. Save the result to {output_file}.
```

Code review support:

```text
Review {path_or_feature} for likely bugs, behavioral regressions, missing tests, and maintainability risks. Include file references when possible. Save to review-notes.md.
```

## Operating Principles

- Let Kimi scan with `--work-dir`; avoid piping large file contents into the prompt.
- Split large analyses into stages rather than asking for one exhaustive report.
- Use output files, especially on Windows, to avoid stdout encoding and truncation issues.
- Treat Kimi's output as a hypothesis until checked against local code.
- Keep generated analysis files in an appropriate scratch or project-local location.

## Troubleshooting

- If output is missing, check whether the prompt explicitly asked Kimi to save to the exact file.
- If the process times out, narrow the scope from repository to package, then to file.
- If authentication is required, ask the user to run `kimi login` in their environment.
- If Unicode output fails on Windows, use the wrapper script or set `PYTHONIOENCODING=utf-8`.

## Resources

- `scripts/invoke_kimi.py`: wrapper for Kimi CLI invocation.
- `references/kimi-cli-guide.md`: concise command reference.
- `references/timeout-recovery.md`: timeout diagnosis and recovery.
