---
name: knowledge-base-reader
description: Read and retrieve notes from a local markdown knowledge base organized with Categories, Topics, and References frontmatter. Use when answering from a user's knowledge base, searching notes by structured metadata, discovering available taxonomy values, or citing retrieved notes.
---

# Knowledge Base Reader

Use this skill to retrieve evidence from a markdown knowledge base before answering. The expected vault layout is:

```text
knowledge-base/
  Notes/
  Categories/
  Topics/
  References/
  Bases/          optional Obsidian Bases views
```

Notes use YAML frontmatter with `Categories`, `Topics`, and `References` values. Values are usually wiki links such as `[[paper_analysis|paper_analysis]]`, but scripts also tolerate plain strings.

## Configuration

Prefer explicit paths. If the user does not provide them, resolve the knowledge base path in this order:

1. `--base-path`
2. `KNOWLEDGE_BASE_PATH`
3. `KB_BASE_PATH`
4. current working directory

For Obsidian CLI commands, use `--vault`, `KB_VAULT_NAME`, or `knowledge-base`.

## Retrieval Workflow

1. Query the available structure before choosing filters:

```bash
python public/knowledge-base-reader/scripts/query_structure.py --all --base-path /path/to/knowledge-base
```

2. Search structured metadata first, then fall back to keyword search:

```bash
python public/knowledge-base-reader/scripts/search_notes.py --topic "memory_systems" --base-path /path/to/knowledge-base
python public/knowledge-base-reader/scripts/search_notes.py --category "paper_analysis" --reference "transformer" --limit 5
python public/knowledge-base-reader/scripts/search_notes.py --keyword "retrieval augmented generation" --json
```

3. Read the most relevant notes directly from `Notes/` or with Obsidian CLI:

```bash
obsidian read vault="knowledge-base" path="Notes/example_note.md"
```

4. Answer from the retrieved content, not from the search result titles alone.

## Citation Format

Cite each note with its title and frontmatter context:

```text
According to "Note Title" (Categories: paper_analysis; Topics: memory_systems, rag; References: transformer), ...
```

If a note lacks useful metadata, cite the note path and say which metadata is missing.

## Retrieval Principles

- Prefer structured filters over broad keyword search when suitable values exist.
- Use exact `snake_case` names for Categories, Topics, and References.
- Start with 3-6 notes; broaden only when the answer still has gaps.
- Prefer recent and high-credibility notes when the frontmatter contains `UpdateDate` or `Credibility`.
- Surface uncertainty when notes conflict, are stale, or do not directly answer the question.

## Resources

- `scripts/query_structure.py`: list available Categories, Topics, and References.
- `scripts/search_notes.py`: search local markdown notes by metadata, keyword, starred tag, and limit.
