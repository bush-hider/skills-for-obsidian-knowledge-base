# Timeout Recovery

Kimi CLI may take several minutes on large repositories because it scans files and performs remote model work.

## Typical Wait Times

- Small single-file analysis: 1-3 minutes.
- Package or module analysis: 3-5 minutes.
- Whole-repository architecture scan: 5-10 minutes.

## Recovery Steps

1. Check whether the requested output file was created. It may be usable even if the wrapper timed out.
2. Narrow `--work-dir` to a subdirectory.
3. Ask for a smaller output, such as architecture only or bug risks only.
4. Continue with `--continue` after a partial result if the session is still recoverable.
5. If repeated failures mention authentication, run `kimi login`.
