---
name: knowledge-base-writer
description: Create and maintain notes in a local markdown knowledge base with Categories, Topics, and References frontmatter. Use when adding notes, creating taxonomy associations, validating note metadata links, or updating a structured personal/team knowledge base.
---

# Knowledge Base Writer

Use this skill to create notes in a portable markdown knowledge base. The expected layout is:

```text
knowledge-base/
  Notes/
  Categories/
  Topics/
  References/
  Bases/
```

The skill assumes a three-part taxonomy:

- `Categories`: note types, such as `paper_analysis`, `meeting_note`, or `project_log`.
- `Topics`: concepts, domains, and subject areas.
- `References`: entities such as organizations, datasets, tools, products, algorithms, or projects.

## Configuration

Prefer explicit paths. Resolve the knowledge base path in this order:

1. `--base-path`
2. `KNOWLEDGE_BASE_PATH`
3. `KB_BASE_PATH`
4. current working directory

For Obsidian CLI commands, use `--vault`, `KB_VAULT_NAME`, or `knowledge-base`.

## Standard Workflow

1. Query existing associations:

```bash
python public/knowledge-base-writer/scripts/query_structure.py --all --base-path /path/to/knowledge-base
```

2. Reuse existing associations when possible. Create missing ones only when no suitable value exists:

```bash
python public/knowledge-base-writer/scripts/create_association.py --name "memory_systems" --dimension Topics --description "Systems and methods for storing and retrieving memory."
python public/knowledge-base-writer/scripts/create_association.py --name "paper_analysis" --dimension Categories
```

3. Create the note under `Notes/` with complete frontmatter:

```yaml
---
Categories:
  - "[[paper_analysis|paper_analysis]]"
Topics:
  - "[[memory_systems|memory_systems]]"
  - "[[retrieval_augmented_generation|retrieval_augmented_generation]]"
References:
  - "[[example_dataset|example_dataset]]"
Credibility: "80"
CreateDate: 2026-05-18
UpdateDate: 2026-05-18
tags:
  - star
title: "Example Note Title"
RelatedNotes: []
---

# Example Note Title
```

4. Verify links:

```bash
python public/knowledge-base-writer/scripts/verify_association.py --note "Notes/20260518_example_note.md" --topic "memory_systems" --category "paper_analysis"
```

## Naming Rules

- Use English `snake_case` names for association files and note slugs.
- Use a `YYYYMMDD_` prefix for dated notes when uniqueness matters.
- Do not use spaces, hyphens, or local-language characters in filenames used as association keys.
- Keep display titles in the `title` field and note heading.

## Association Files

`create_association.py` creates both:

- `Bases/<name>.base`
- `<Dimension>/<name>.md`

The `.base` file is optional for plain markdown users but useful for Obsidian Bases workflows. The markdown file embeds the matching base view with `![[<name>.base]]`.

## Writing Principles

- Choose 1-3 Categories, 2-6 Topics, and 0-5 References.
- Reuse existing associations before creating new ones.
- Create missing associations before using them in note frontmatter.
- Use UTF-8 for all markdown files.
- Verify metadata after creating or updating notes.

## Resources

- `scripts/query_structure.py`: list Categories, Topics, and References.
- `scripts/create_association.py`: create association markdown and optional base view files.
- `scripts/verify_association.py`: verify that a note's frontmatter contains expected associations.
