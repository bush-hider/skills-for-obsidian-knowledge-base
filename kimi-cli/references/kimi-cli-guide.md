# Kimi CLI Guide

## Core Commands

```bash
kimi --version
kimi login
kimi --quiet --prompt "Analyze this project. Save to analysis.md" --work-dir ./project
kimi --continue --quiet --prompt "Continue with the API layer. Save to api.md" --work-dir ./project
```

## Useful Options

- `--work-dir <path>`: directory Kimi can inspect.
- `--prompt <text>`: task instruction.
- `--quiet`: reduce terminal output; pair with an explicit file-save instruction.
- `--continue`: continue the previous session.
- `--model <name>`: use a model override if supported by the installed CLI.

## Best Practices

- Ask Kimi to save complete output to a named file.
- Keep each prompt focused on one analysis goal.
- Start broad, inspect the result, then ask focused follow-ups.
- Verify specific claims against local code before acting on them.
