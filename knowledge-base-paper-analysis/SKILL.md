---
name: knowledge-base-paper-analysis
description: Analyze research papers from PDF or extracted text and turn them into detailed, narrative-style markdown knowledge-base notes. Use when the user provides a paper PDF, arXiv link, extracted text, or asks for deep paper reading, PDF archiving, sub-agent paper analysis, or integration into a Categories/Topics/References knowledge base.
---

# Knowledge Base Paper Analysis

Use this skill for deep academic paper analysis and optional integration into a markdown knowledge base. Prefer a complete PDF/text pipeline over abstract-only summaries. Keep all workspace, archive, temporary, and knowledge-base paths configurable; do not hard-code user home directories, vault names, or machine-specific paths.

## Dependencies

Required:

- Python 3.9+ for bundled helper scripts.
- A paper PDF, arXiv/source link, or already extracted full text.

Recommended:

- A PDF extraction tool or PDF skill for full-text extraction.
- `knowledge-base-writer` for note creation, taxonomy associations, and metadata verification.
- A long-running task runner or external agent/orchestrator when the analysis may take more than one turn.
- Sub-agent support when available, because deep paper analysis is usually better isolated from the main session.

## Configuration

Resolve paths in this order:

- Workspace root: `--workspace`, `PAPER_ANALYSIS_WORKSPACE`, then current working directory.
- Knowledge base: `--base-path`, `KNOWLEDGE_BASE_PATH`, `KB_BASE_PATH`, then `<workspace>/knowledge-base`.
- Paper archive: `--archive-dir`, `PAPER_ARCHIVE_PATH`, then `<workspace>/papers`.
- Temporary files: `PAPER_ANALYSIS_TMP`, then `<workspace>/paper-analysis-tmp`.

Recommended environment variables for Codex, OpenClaw, or other agent runners:

```text
PAPER_ANALYSIS_WORKSPACE=/path/to/workspace
KNOWLEDGE_BASE_PATH=/path/to/knowledge-base
PAPER_ARCHIVE_PATH=/path/to/papers
PAPER_ANALYSIS_TMP=/path/to/paper-analysis-tmp
```

## Standard Workflow

### 1. Identify and Archive the PDF

If the user provides a PDF, first extract basic metadata from the first pages: title, authors, venue, year, arXiv ID, DOI, and code URL if present.

Archive the PDF with a descriptive filename:

```text
YYYYMMDD_descriptive_paper_slug.pdf
```

Examples:

```text
20260518_attention_is_all_you_need.pdf
20260518_retrieval_augmented_generation_knowledge_intensive_nlp.pdf
```

Do not keep opaque filenames such as `paper.pdf`, `download.pdf`, or only an arXiv ID unless no metadata can be recovered.

### 2. Extract Complete Text

Use a PDF extraction tool or PDF skill. Extract the full paper, not just the abstract. Preserve:

- title/authors/venue/date metadata
- abstract and introduction
- method and algorithm sections
- formulas and variable definitions
- experiment tables and captions
- ablation studies
- limitations and appendix content when relevant
- references when needed for lineage or related work

Save extracted text using a paper-specific filename:

```text
paper-analysis-tmp/{paper_id}_text.txt
```

If extraction fails:

- try a different PDF extractor
- use arXiv HTML or source when available
- fetch an official project page or publisher page for metadata only
- clearly label the analysis as partial if full text cannot be recovered

### 3. Prepare the Analysis Handoff

Run the helper script to validate resources and produce a sub-agent handoff prompt:

```bash
python public/knowledge-base-paper-analysis/scripts/prepare_paper_analysis.py \
  --workspace /path/to/workspace \
  --paper-text paper-analysis-tmp/{paper_id}_text.txt \
  --paper-id {paper_id} \
  --output paper-analysis-tmp/{paper_id}_analysis.md \
  --pages 24 \
  --min-words 3800 \
  --max-words 6000
```

With PDF archiving:

```bash
python public/knowledge-base-paper-analysis/scripts/prepare_paper_analysis.py \
  --workspace /path/to/workspace \
  --pdf incoming/paper.pdf \
  --archive-pdf \
  --archive-name 20260518_descriptive_paper_slug.pdf \
  --paper-text paper-analysis-tmp/{paper_id}_text.txt \
  --paper-id {paper_id} \
  --output paper-analysis-tmp/{paper_id}_analysis.md \
  --pages 24
```

The script checks that files exist, creates output directories, reports archive/base/tmp paths, calculates a recommended timeout, and prints a prompt that can be passed to a sub-agent or external orchestrator.

### 4. Use a Sub-Agent When Available

If sub-agents are available, delegate the deep reading task after the preparation script passes. The sub-agent should:

1. Read `references/sub-agent-prompt-template.md`.
2. Read the extracted paper text.
3. Follow the seven-section analysis structure.
4. Write the complete analysis directly to `{paper_id}_analysis.md`.
5. Return only a short completion report: metadata found, sections completed, uncertainty, extraction gaps.

If sub-agents are not available, run the same template in the main agent, but preserve the same output-file discipline.

Suggested sub-agent prompt:

```text
Read these files:
1. public/knowledge-base-paper-analysis/references/sub-agent-prompt-template.md
2. paper-analysis-tmp/{paper_id}_text.txt

Follow the template exactly enough to produce a deep, narrative-style paper analysis.
Target length: 3800-6000 words unless the user requests otherwise.
Write the full markdown analysis to:
paper-analysis-tmp/{paper_id}_analysis.md

Do not paste the full analysis into chat. Report only completion status, section coverage, and any extraction gaps.
```

Timeout guidance:

- Short workshop paper: 20-35 minutes.
- Standard 8-15 page paper: 30-60 minutes.
- Long paper with appendix: 60-90 minutes.

### 5. Create Knowledge-Base Associations

Before writing the final note, query existing taxonomy with `knowledge-base-writer`:

```bash
python public/knowledge-base-writer/scripts/query_structure.py --all --base-path /path/to/knowledge-base
```

Use or create:

- `Categories`: usually `paper_analysis`.
- `Topics`: 3-6 concepts/domains.
- `References`: 2-5 entities such as methods, datasets, benchmarks, labs, systems, algorithms, or core techniques. Do not list every author as a Reference.

Create missing associations before using them:

```bash
python public/knowledge-base-writer/scripts/create_association.py \
  --base-path /path/to/knowledge-base \
  --name new_topic \
  --dimension Topics \
  --description "Short description."
```

### 6. Write the Knowledge-Base Note

Final note path:

```text
knowledge-base/Notes/YYYYMMDD_descriptive_paper_slug.md
```

Required frontmatter:

```yaml
---
Categories:
  - "[[paper_analysis|paper_analysis]]"
Topics:
  - "[[topic_one|topic_one]]"
  - "[[topic_two|topic_two]]"
References:
  - "[[method_or_dataset|method_or_dataset]]"
Credibility: "100"
CreateDate: YYYY-MM-DD
UpdateDate: YYYY-MM-DD
tags:
  - star
title: "Full Paper Title"
RelatedNotes: []
dg-publish: true
---
```

Suggested body sections:

- Basic information
- Research Summary
- Theoretical Framework
- Technical Architecture
- Experimental Evaluation
- Case Studies
- Value and Limitations
- Further Reading and Open Questions
- Extraction Notes, if the source text was incomplete

### 7. Verify

Run association verification:

```bash
python public/knowledge-base-writer/scripts/verify_association.py \
  --base-path /path/to/knowledge-base \
  --note Notes/YYYYMMDD_descriptive_paper_slug.md \
  --category paper_analysis \
  --topic topic_one \
  --reference method_or_dataset
```

## Analysis Depth Requirements

Default target length: 3800-6000 words for a standard paper. Use 2500-3800 words only for short or simple papers. For landmark, theoretical, or technically dense papers, 6000-9000 words is appropriate if the user wants a comprehensive reading note.

Default seven-section targets:

- Research Summary: 500-800 words.
- Theoretical Framework: 800-1200 words.
- Technical Architecture: 800-1200 words.
- Experimental Evaluation: 600-900 words.
- Case Studies: 400-600 words.
- Value and Limitations: 400-600 words.
- Further Reading and Open Questions: 300-500 words.

Write in narrative prose. Avoid bullet-list summaries except for compact metadata, result tables, parameter tables, or final checklists. Every formula must be explained in prose before or after it appears.

## Quality Checks

- PDF is archived with a descriptive filename when a PDF was provided.
- Extracted text is complete enough for the requested depth.
- Analysis is grounded in full text, not only abstract and introduction.
- Metadata is explicit, with unknown fields labeled rather than invented.
- Formulas, algorithms, and experiment tables are interpreted, not merely copied.
- Strengths and limitations are tied to the paper's method and evidence.
- Topics and References exist before they are used in frontmatter.
- Verification passes after the final note is written.

## Resources

- `scripts/prepare_paper_analysis.py`: validate PDF/text/template paths, archive PDF, calculate timeout, and print a sub-agent handoff prompt.
- `references/sub-agent-prompt-template.md`: detailed sub-agent analysis instructions, section requirements, writing style, and quality checklist.
