# Codex Public Skills 使用说明

本发布包包含 5 个可直接使用的 agent skill，覆盖本地 Markdown/Obsidian 知识库读写、论文深度分析、Kimi CLI 代码分析和 Kimi CLI 联网搜索。

这些 skill 不绑定某个具体 agent。Codex、OpenClaw 或其他支持读取 `SKILL.md` 的 agent，都可以按同样的方式集成：把 skill 目录放进该 agent 的 skills 目录，确保依赖命令可用，并通过环境变量或命令参数配置本地路径。

下方命令示例默认在 `public/` 目录下执行。

## 目录内容

```text
public/
  knowledge-base-reader/
  knowledge-base-writer/
  knowledge-base-paper-analysis/
  kimi-cli/
  kimi-cli-web-search/
```

## 初次运行：最小配置

### 1. 安装或复制 skill

Codex 常见位置：

```text
~/.codex/skills/
```

OpenClaw 或其他 agent：

- 找到该 agent 的 skills 插件目录。
- 将需要的 skill 目录复制进去。
- 确认 agent 会读取每个目录下的 `SKILL.md`。

示例结构：

```text
skills/
  knowledge-base-reader/
  knowledge-base-writer/
  knowledge-base-paper-analysis/
  kimi-cli/
  kimi-cli-web-search/
```

### 2. 确认 Python 可用

```bash
python --version
```

Windows 如果 `python` 指向 Microsoft Store 占位入口，可以使用：

```powershell
py --version
```

脚本均按 Python 3.9+ 编写。

### 3. 准备知识库目录（如需）

知识库类 skill 默认使用本地 Markdown 目录：

```text
knowledge-base/
  Notes/
  Categories/
  Topics/
  References/
  Bases/
```

可以手动创建，也可以让 `knowledge-base-writer` 在创建 association 时自动补齐部分目录。

### 4. 配置环境变量

推荐给 Codex、OpenClaw 和其他 agent runner 都设置这些变量。也可以不设置，在每条命令里显式传参。

PowerShell:

```powershell
$env:KNOWLEDGE_BASE_PATH = "D:\path\to\knowledge-base"
$env:PAPER_ANALYSIS_WORKSPACE = "D:\path\to\workspace"
$env:PAPER_ARCHIVE_PATH = "D:\path\to\workspace\papers"
$env:PAPER_ANALYSIS_TMP = "D:\path\to\workspace\paper-analysis-tmp"
```

Bash:

```bash
export KNOWLEDGE_BASE_PATH="/path/to/knowledge-base"
export PAPER_ANALYSIS_WORKSPACE="/path/to/workspace"
export PAPER_ARCHIVE_PATH="/path/to/workspace/papers"
export PAPER_ANALYSIS_TMP="/path/to/workspace/paper-analysis-tmp"
```

环境变量说明：

| 变量 | 用途 | 是否必需 |
| --- | --- | --- |
| `KNOWLEDGE_BASE_PATH` / `KB_BASE_PATH` | Markdown 知识库根目录 | 知识库读写推荐 |
| `KB_VAULT_NAME` | Obsidian vault 名称 | 仅使用 Obsidian CLI 时需要 |
| `PAPER_ANALYSIS_WORKSPACE` | 论文分析工作区 | 论文分析推荐 |
| `PAPER_ARCHIVE_PATH` | PDF 归档目录 | 需要归档 PDF 时推荐 |
| `PAPER_ANALYSIS_TMP` | 论文抽取文本和分析草稿目录 | 论文分析推荐 |

路径解析优先级通常是：命令行参数 > 环境变量 > 当前目录或默认子目录。

## Skill 一览

| Skill | 什么时候用 | 必需依赖 | 可选依赖 |
| --- | --- | --- | --- |
| `knowledge-base-reader` | 从 Markdown 知识库检索笔记，并基于笔记回答问题。 | Python 3.9+；Markdown 知识库 | Obsidian CLI |
| `knowledge-base-writer` | 创建知识库笔记、taxonomy 关联，并校验 frontmatter。 | Python 3.9+；Markdown 知识库 | Obsidian CLI |
| `knowledge-base-paper-analysis` | 从 PDF 或全文深度分析论文，并整理成知识库笔记。 | Python 3.9+；论文 PDF 或已抽取文本 | PDF 提取工具；`knowledge-base-writer`；子代理/任务编排器 |
| `kimi-cli` | 用 Kimi Code CLI 辅助分析代码库。 | `kimi` CLI；已登录认证 | 无 |
| `kimi-cli-web-search` | 用 Kimi CLI 联网搜索、资料检索和事实核验。 | `kimi` CLI；已登录认证；联网搜索可用 | 其他浏览或来源核验工具 |

## `knowledge-base-reader`

用于读取和检索本地 Markdown 知识库。适合：

- 查找某个 Topic、Category 或 Reference 关联的笔记。
- 基于知识库回答问题，并给出笔记来源。
- 快速了解知识库里有哪些分类、主题和实体。

常用命令：

```bash
python knowledge-base-reader/scripts/query_structure.py --all --base-path /path/to/knowledge-base
python knowledge-base-reader/scripts/search_notes.py --topic memory_systems --base-path /path/to/knowledge-base
python knowledge-base-reader/scripts/search_notes.py --keyword "retrieval augmented generation" --json --base-path /path/to/knowledge-base
```

Agent 触发示例：

```text
Use $knowledge-base-reader to search my knowledge base for notes about memory systems and answer with citations.
```

## `knowledge-base-writer`

用于写入和维护本地 Markdown 知识库。它可以创建 taxonomy 文件、生成 Obsidian Bases 视图文件，并校验笔记 frontmatter。

常用命令：

```bash
python knowledge-base-writer/scripts/query_structure.py --all --base-path /path/to/knowledge-base
python knowledge-base-writer/scripts/create_association.py --name memory_systems --dimension Topics --base-path /path/to/knowledge-base
python knowledge-base-writer/scripts/verify_association.py --note Notes/20260518_example.md --topic memory_systems --base-path /path/to/knowledge-base
```

Agent 触发示例：

```text
Use $knowledge-base-writer to create a structured note for this content in my knowledge base.
```

命名约定：

- taxonomy 名称使用英文 `snake_case`。
- 笔记文件建议使用 `YYYYMMDD_note_slug.md`。
- `Categories` 表示笔记类型。
- `Topics` 表示概念主题。
- `References` 表示组织、数据集、工具、方法、产品或项目等实体。

## `knowledge-base-paper-analysis`

用于论文深度分析。公共版已经强化 PDF 完整处理和子代理分析流程：它要求优先抽取完整 PDF 文本，保留公式、表格、实验和 appendix 线索，并通过准备脚本生成可交给子代理或其他 orchestrator 的 handoff prompt。

推荐工作流：

1. 准备论文 PDF。
2. 从 PDF 抽取完整文本，保存为 `paper-analysis-tmp/{paper_id}_text.txt`。
3. 运行准备脚本检查 PDF/text/template，并生成子代理提示：

```bash
python knowledge-base-paper-analysis/scripts/prepare_paper_analysis.py \
  --workspace /path/to/workspace \
  --pdf incoming/paper.pdf \
  --archive-pdf \
  --archive-name 20260518_descriptive_paper_slug.pdf \
  --paper-text paper-analysis-tmp/sample-paper_text.txt \
  --paper-id sample-paper \
  --output paper-analysis-tmp/sample-paper_analysis.md \
  --pages 24 \
  --min-words 3800 \
  --max-words 6000
```

4. 让子代理读取：

```text
knowledge-base-paper-analysis/references/sub-agent-prompt-template.md
paper-analysis-tmp/sample-paper_text.txt
```

5. 子代理将完整分析写入：

```text
paper-analysis-tmp/sample-paper_analysis.md
```

6. 如果要入库，再配合 `knowledge-base-writer` 创建/复用 associations，并写入 `knowledge-base/Notes/YYYYMMDD_slug.md`。

Agent 触发示例：

```text
Use $knowledge-base-paper-analysis to archive this PDF, extract full text, delegate a deep sub-agent analysis if available, and prepare a knowledge-base note.
```

默认分析长度：

- 标准论文：3800-6000 words。
- 短论文：2500-3800 words。
- 经典或理论密集论文：6000-9000 words，按用户需求调整。

## `kimi-cli`

用于调用 Kimi Code CLI 做代码库辅助分析。适合大项目结构梳理、模块理解、风险扫描和第二视角审查。

先确认 CLI 可用：

```bash
kimi --version
kimi login
```

直接调用示例：

```bash
kimi --quiet --prompt "Analyze this repository architecture and save to architecture.md" --work-dir /path/to/project
```

使用 wrapper：

```bash
python kimi-cli/scripts/invoke_kimi.py \
  --prompt "Analyze the API layer and save to api-analysis.md" \
  --work-dir /path/to/project \
  --output api-analysis.md
```

Agent 触发示例：

```text
Use $kimi-cli to run a staged Kimi analysis of this repository, then verify and summarize the findings.
```

注意事项：

- Kimi 的输出应保存到文件，再由主 agent 读取、核查和整合。
- 不要把敏感项目交给外部 CLI，除非你确认可以这样做。
- 大项目建议分阶段分析，而不是一次生成超长报告。

## `kimi-cli-web-search`

用于调用 Kimi CLI 的联网搜索能力。适合中文资料检索、近期信息补充、多来源汇总和事实核验。

先确认 CLI 可用并已登录：

```bash
kimi --version
kimi login
```

直接调用示例：

```bash
kimi --quiet --prompt "Search for official sources about the topic, include URLs, and save to search-result.md" --work-dir .
```

使用 wrapper：

```bash
python kimi-cli-web-search/scripts/invoke_search.py \
  "Search for recent official sources about the topic. Include URLs and save to search-result.md" \
  --output search-result.md \
  --timeout 180
```

Agent 触发示例：

```text
Use $kimi-cli-web-search to find current sources about this topic, verify key claims, and summarize with citations.
```

使用建议：

- 把 Kimi 搜索结果当作线索，不要直接当作最终答案。
- 重要结论尽量回到原始来源、官方文档、论文或公告核验。
- 对近期事件同时检查发布日期和事件发生日期。

## OpenClaw / 其他 Agent 集成建议

如果你的 agent 不是 Codex，也可以按下面的方式集成：

1. 将 skill 目录复制到该 agent 的 skill/plugin 目录。
2. 确认该 agent 会读取 `SKILL.md` 的 YAML frontmatter 和正文。
3. 将该 agent 的 workspace 设为可读写位置。
4. 设置上面的环境变量，尤其是 `KNOWLEDGE_BASE_PATH` 和 `PAPER_ANALYSIS_WORKSPACE`。
5. 如果 agent 支持子代理，论文分析时把 `prepare_paper_analysis.py` 输出的 handoff prompt 交给子代理。
6. 如果 agent 不支持子代理，就在主 agent 中按模板执行，并把长分析写入文件。

OpenClaw 类 agent 常见推荐：

```text
workspace/
  knowledge-base/
  papers/
  paper-analysis-tmp/
  skills/
```

## 常见问题

### Obsidian CLI 是必需的吗

不是。`knowledge-base-reader` 和 `knowledge-base-writer` 的核心脚本直接读写 Markdown 文件。只有使用 `obsidian read`、`obsidian search` 等命令时才需要 Obsidian CLI。

### PDF skill 是必需的吗

不是，但强烈推荐使用可靠的 PDF 抽取工具。`knowledge-base-paper-analysis` 的质量取决于全文抽取是否完整。只有 abstract 或部分正文时，必须标注分析为 partial。

### Kimi CLI skill 会自动安装 Kimi 吗

不会。`kimi-cli` 和 `kimi-cli-web-search` 只提供调用方式和 wrapper。你需要自己安装、登录并确认外部服务使用权限。

### 不想设置环境变量怎么办

每次命令显式传入路径即可：

```bash
python knowledge-base-reader/scripts/search_notes.py --topic memory_systems --base-path /path/to/knowledge-base
```

## 推荐组合

- 只读知识库：`knowledge-base-reader`
- 写入知识库：`knowledge-base-writer`
- 论文入库：`knowledge-base-paper-analysis` + `knowledge-base-writer`
- 大代码库分析：`kimi-cli`
- 外部资料检索：`kimi-cli-web-search`
