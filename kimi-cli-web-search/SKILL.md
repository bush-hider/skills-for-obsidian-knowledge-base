---
name: kimi-cli-web-search
description: Use Kimi CLI's web search capability as an external retrieval path for current web information, Chinese-language search, source discovery, and claim verification. Use when the user asks to search with Kimi, when Kimi web search is the available retrieval tool, or when multi-source web aggregation should be saved to files for later synthesis.
---

# Kimi CLI Web Search

Use Kimi CLI as a web retrieval helper. The main agent remains responsible for deciding what to search, judging source quality, verifying important claims, and writing the final synthesis.

## Prerequisites

- `kimi` is installed, authenticated, and able to access web search tools.
- The user permits use of the external Kimi service for the query.
- Search outputs can be saved in the working directory or a scratch directory.

## Search Workflow

1. Define the information gap: fact, timeline, source list, competing claims, or current status.
2. Write a targeted prompt with scope, time range, source preferences, and output format.
3. Invoke Kimi with `--quiet` and ask it to save results to a file.
4. Read the result, extract the key claims and URLs, and verify high-impact claims with primary sources when possible.
5. Synthesize in your own words. Do not forward raw Kimi output.

## Invocation

Direct CLI:

```bash
kimi --quiet --prompt "Search for official sources about {topic}. Include URLs and save to search-result.md" --work-dir .
```

Wrapper:

```bash
python public/kimi-cli-web-search/scripts/invoke_search.py "Search for recent official sources about {topic}. Save to search-result.md" --output search-result.md --timeout 180
```

On Windows, the wrapper sets UTF-8 environment variables to reduce encoding failures.

## Prompt Templates

Research survey:

```text
Search the web for {topic} in {time_range}. Focus on {aspect_1}, {aspect_2}, and {aspect_3}. Prefer primary sources, papers, official documentation, and reputable technical media. Produce a structured report with URLs and save it to {output_file}.
```

Claim verification:

```text
Verify this claim: "{claim}". Find the original source when possible, evidence for and against the claim, publication dates, and a confidence judgment. Save the report with URLs to {output_file}.
```

Chinese-language search:

```text
Search Chinese-language and English-language sources for {topic}. Prefer official announcements, papers, technical documentation, and reputable media. Summarize key facts, timelines, source URLs, and save the report to {output_file}.
```

## Verification Rules

- Treat Kimi's web summary as a lead, not as final authority.
- Prefer primary sources for laws, product docs, releases, model specs, papers, and company announcements.
- For recent events, compare publication dates and event dates.
- If sources disagree, report the disagreement instead of forcing one answer.
- Cite the original URLs you independently checked whenever possible.

## Resources

- `scripts/invoke_search.py`: wrapper for search prompts.
- `references/encoding-guide.md`: Windows UTF-8 notes.
- `references/thinking-framework.md`: staged search and synthesis guidance.
