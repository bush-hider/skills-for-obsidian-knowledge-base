# Sub-Agent Paper Analysis Guide

Use this guide when producing a deep paper analysis from an extracted PDF text file. Read both this guide and the full extracted paper text. The output must be a complete markdown analysis written to the requested output file.

Do not rely on the abstract alone. If the extraction is incomplete, explicitly state what is missing and lower confidence for affected sections.

## Sub-Agent Task

1. Read the full extracted paper text.
2. Identify metadata from the first pages and any paper header/footer clues.
3. Check whether core sections are present: abstract, introduction, method, experiments, results, limitations, conclusion, appendix if relevant.
4. Write a detailed narrative analysis to `{paper_id}_analysis.md`.
5. Return only a short completion message to the main agent: output path, sections completed, extraction gaps, and confidence.

Do not paste the full analysis into the chat response.

## Metadata Block

Start the output with:

```markdown
# Full Paper Title

## Metadata

| Field | Value |
| --- | --- |
| Title | ... |
| Authors | ... |
| Venue | ... |
| Year | ... |
| DOI/arXiv | ... |
| Code | ... |
| PDF/Text completeness | Complete / Partial, with reason |
```

Use `Unknown` only when the paper text does not provide the information. Do not invent venue, code URLs, affiliations, or results.

## Target Length

Default target for a standard full paper: 3800-6000 words.

Use:

- 2500-3800 words for short workshop papers or simple empirical papers.
- 3800-6000 words for normal research papers.
- 6000-9000 words for landmark, theoretical, methods-heavy, or appendix-heavy papers when the user asks for comprehensive reading notes.

If the extracted text is partial, write only what the evidence supports and include an `Extraction Notes` section.

## Required Structure

Write these sections in flowing narrative prose. Use paragraphs, transitions, explanation, and concrete examples. Avoid bullet lists or numbered lists in the main analysis. Tables are allowed only for experimental comparisons, taxonomies, datasets, parameter settings, or compact metadata.

### 1. Research Summary (500-800 words)

Explain the fundamental problem, why it matters, what prior approaches could not solve, and what the paper contributes. Make the paper's intellectual move clear: what changed in how the problem is framed, modeled, measured, or solved.

Cover:

- core research problem
- motivation and field context
- key insight
- 2-4 main contributions as part of one coherent argument
- key findings and why they matter
- likely influence on future research or practice

### 2. Theoretical Framework (800-1200 words)

Explain the paper's concepts and assumptions in depth. Trace the intellectual lineage: what prior methods, theories, tasks, or evaluation traditions does it build on?

For formulas:

- use inline math `$...$` and block math `$$...$$`
- explain every variable
- explain what relationship the equation captures
- explain why this formulation matters

For algorithms:

- describe the core logic in prose
- explain inputs, intermediate states, outputs, and optimization/training objective
- distinguish what is novel from what is inherited

### 3. Technical Architecture (800-1200 words)

Describe the method or system as an architecture, not as disconnected components.

Cover:

- system overview
- data flow from input to output
- component interactions
- key design choices and why they matter
- training/inference procedure
- implementation details that affect behavior
- computational cost or scalability when discussed

Use analogies only when they clarify a technical mechanism; avoid vague metaphor.

### 4. Experimental Evaluation (600-900 words)

Explain the experiments as evidence for or against the paper's claims.

Cover:

- datasets and why they are suitable
- baselines and what they represent
- metrics and what they measure
- main results and interpretation
- ablations and what they reveal
- robustness, variance, or statistical limitations
- missing experiments or evaluation risks

Use tables for important quantitative comparisons, then interpret the table in prose.

### 5. Case Studies (400-600 words)

If the paper includes examples, qualitative outputs, figures, or case studies, choose one or two and explain them carefully.

Cover:

- what the example demonstrates
- how the method processes the case
- what intermediate behavior or output reveals
- what the case shows about strengths, weaknesses, or failure modes

If the paper contains no concrete case studies, omit this section and expand the theoretical, architecture, or experimental sections proportionally.

### 6. Value and Limitations (400-600 words)

Give a balanced critical assessment.

Cover:

- theoretical significance
- practical impact
- strongest aspects of the work
- assumptions that may not hold
- deployment or generalization risks
- missing evidence
- how the paper changes or fails to change the field

Do not add generic limitations. Tie every limitation to method, data, evaluation, or scope.

### 7. Further Reading and Open Questions (300-500 words)

Connect the paper to the broader literature.

Cover:

- prior work the paper builds on
- related approaches with different assumptions
- future directions opened by the paper
- unresolved questions
- what a reader should study next to understand this area

## Writing Style

- Write the main analysis in Chinese unless the user requests another language.
- Keep English technical terms when they are standard; give Chinese explanations on first use when useful.
- Use author-year references for papers mentioned in the extracted text.
- Explain causal and logical links: do not merely restate paper sections.
- Preserve uncertainty: if evidence is incomplete, say exactly which conclusion is uncertain.
- Avoid long bibliographic dumps.
- Avoid polishing language at the cost of technical precision.

## Extraction Quality Check

Before finalizing, inspect the extracted text for common PDF failures:

- missing formulas or broken math symbols
- missing tables
- repeated headers/footers
- columns merged in the wrong order
- references mixed into body text
- appendix absent despite being cited
- figures/captions omitted

If these issues affect interpretation, include an `Extraction Notes` section and recommend a re-extraction or source check.

## Final Checklist

- [ ] Metadata block is present.
- [ ] Full text, not only abstract, was used.
- [ ] Each required section is present or explicitly omitted with reason.
- [ ] Word count is appropriate for paper length and user request.
- [ ] Formulas and algorithms are explained in prose.
- [ ] Experimental tables are interpreted, not merely copied.
- [ ] Limitations are concrete and evidence-linked.
- [ ] Extraction gaps are disclosed.
- [ ] Complete analysis is written to the requested file, not pasted into chat.
