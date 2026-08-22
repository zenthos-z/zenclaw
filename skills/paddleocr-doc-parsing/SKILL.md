---
name: paddleocr-doc-parsing
description: >-
  Use this skill to extract structured Markdown/JSON from PDFs and document images—tables with
  cell-level precision, formulas as LaTeX, figures, seals, charts, headers/footers, multi-column
  layout and correct reading order.
  Trigger terms: 文档解析, 版面分析, 版面还原, 表格提取, 公式识别, 多栏排版, 扫描件结构化,
  发票, 财报, 复杂 PDF, PDF转Markdown, 图表, 阅读顺序; reading order, formula, LaTeX,
  layout parsing, structure extraction, PP-StructureV3, PaddleOCR-VL.
compatibility: Requires Python 3.9+, uv, and internet access.
metadata:
  openclaw:
    requires:
      env:
        - PADDLEOCR_DOC_PARSING_API_URL
        - PADDLEOCR_ACCESS_TOKEN
      bins:
        - uv
    primaryEnv: PADDLEOCR_ACCESS_TOKEN
    emoji: "📄"
    homepage: https://github.com/PaddlePaddle/PaddleOCR/tree/main/skills/paddleocr-doc-parsing
---

# PaddleOCR Document Parsing Skill

## When to Use This Skill

**Trigger keywords (routing)**: Bilingual trigger terms (Chinese and English) are listed in the YAML `description` above—use that field for discovery and routing.

**Use this skill for**:

- Documents with tables (invoices, financial reports, spreadsheets)
- Documents with mathematical formulas (academic papers, scientific documents)
- Documents with charts and diagrams
- Multi-column layouts (newspapers, magazines, brochures)
- Complex document structures requiring layout analysis
- Any document requiring structured understanding

**Do not use for**:

- Simple text-only extraction
- Quick OCR tasks where speed is critical
- Screenshots or simple images with clear text

## Installation

Scripts declare their dependencies inline ([PEP 723](https://peps.python.org/pep-0723/)). No separate install step is needed — [uv](https://docs.astral.sh/uv/) resolves dependencies automatically:

```bash
uv run scripts/layout_caller.py --help
```

## How to Use This Skill

> **Working directory**: All `uv run scripts/...` commands below should be run from this skill's root directory (the directory containing this SKILL.md file).

### Basic Workflow

1. **Identify the input source**:
   - User provides URL: Use the `--file-url` parameter
   - User provides local file path: Use the `--file-path` parameter

2. **Execute document parsing**:

   ```bash
   uv run scripts/layout_caller.py --file-url "URL provided by user" --pretty
   ```

   Or for local files:

   ```bash
   uv run scripts/layout_caller.py --file-path "file path" --pretty
   ```

   **Optional: explicitly set file type**:

   ```bash
   uv run scripts/layout_caller.py --file-url "URL provided by user" --file-type 0 --pretty
   ```

   - `--file-type 0`: PDF
   - `--file-type 1`: image
   - If omitted, the type is auto-detected from the file extension. For local files, a recognized extension (`.pdf`, `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`, `.webp`) is required; otherwise pass `--file-type` explicitly. For URLs with unrecognized extensions, the service attempts inference.

   > **Performance note**: Parsing time scales with document complexity. Single-page images typically complete in 1-5 seconds; large PDFs (50+ pages) may take several minutes. Allow adequate time before assuming a timeout.

   **Default behavior: save raw JSON to a temp file**:
   - If `--output` is omitted, the script saves automatically under the system temp directory
   - Default path pattern: `<system-temp>/paddleocr/doc-parsing/results/result_<timestamp>_<id>.json`
   - If `--output` is provided, it overrides the default temp-file destination
   - If `--stdout` is provided, JSON is printed to stdout and no file is saved
   - In save mode, the script prints the absolute saved path on stderr: `Result saved to: /absolute/path/...`
   - In default/custom save mode, read and parse the saved JSON file before responding
   - Use `--stdout` only when you explicitly want to skip file persistence

3. **Parse JSON response**:
   - Check the `ok` field: `true` means success, `false` means error
   - The output contains complete document data: text, tables, formulas (LaTeX), figures, seals, headers/footers, and reading order
   - Use the appropriate field based on what the user needs:
     - `text` — full document text across all pages
     - `result.result.layoutParsingResults[n].markdown.text` — page-level markdown
     - `result.result.layoutParsingResults[n].prunedResult` — structured layout data with positions and confidence
   - Handle errors: If `ok` is false, display `error.message`

4. **Present results to user**:
   - Display content based on what the user requested (see "Complete Output Display" below)
   - If the content is empty, the document may contain no extractable text
   - In save mode, always tell the user the saved file path and that full raw JSON is available there

### What to Do After Parsing

Common next steps once you have the structured output:

- **Save as Markdown**: Write the `text` field to a `.md` file — tables, headings, and formulas are preserved
- **Extract specific tables**: Navigate `result.result.layoutParsingResults[n].prunedResult` to access individual layout elements with position and confidence data
- **Feed to RAG / search pipeline**: The `text` field is structured markdown, ready for chunking and indexing
- **Poor results**: See "Tips for Better Results" below before retrying

### Complete Output Display

Display the COMPLETE extracted content based on what the user asked for. The parsed output is only useful if the user receives all of it — truncation silently drops data.

- If user asks for "all text", show the entire `text` field
- If user asks for "tables", show ALL tables in the document
- If user asks for "main content", filter out headers/footers but show ALL body text
- Do not truncate with "..." unless content is excessively long (>10,000 chars)
- Do not say "Here's a preview" when user expects complete output

**Example - Correct**:

```
User: "Extract all the text from this document"
Agent: I've parsed the complete document. Here's all the extracted text:

[Display entire text field or concatenated regions in reading order]

Document Statistics:
- Total regions: 25
- Text blocks: 15
- Tables: 3
- Formulas: 2
Quality: Excellent (confidence: 0.92)
```

**Example - Incorrect**:

```
User: "Extract all the text"
Agent: "I found a document with multiple sections. Here's the beginning:
'Introduction...' (content truncated for brevity)"
```

### Understanding the Output

The script returns an envelope with `ok`, `text`, `result`, and `error`. Use `text` for the full document content; navigate `result.result.layoutParsingResults[n]` for per-page structured data.

For the complete schema and field-level details, see `references/output_schema.md`.

> Raw result location (default): the temp-file path printed by the script on stderr

### Usage Examples

**Example 1: Extract Full Document Text**

```bash
uv run scripts/layout_caller.py \
  --file-url "https://example.com/paper.pdf" \
  --pretty
```

Then use:

- Top-level `text` for quick full-text output
- `result.result.layoutParsingResults[n].markdown` when page-level output is needed

**Example 2: Extract Structured Page Data**

```bash
uv run scripts/layout_caller.py \
  --file-path "./financial_report.pdf" \
  --pretty
```

Then use:

- `result.result.layoutParsingResults[n].prunedResult` for structured parsing data (layout/content/confidence)

**Example 3: Print JSON to stdout (without saving to file)**

```bash
uv run scripts/layout_caller.py \
  --file-url "URL" \
  --stdout \
  --pretty
```

By default the script writes JSON to a temp file and prints the path to stderr. Add `--stdout` to print the full JSON directly to stdout instead. Use this when you need to inspect the result inline or pipe it to another tool.

### First-Time Configuration

**When API is not configured**, the script outputs:

```json
{
  "ok": false,
  "text": "",
  "result": null,
  "error": {
    "code": "CONFIG_ERROR",
    "message": "PADDLEOCR_DOC_PARSING_API_URL not configured. Get your API at: https://paddleocr.com"
  }
}
```

**Configuration workflow**:

1. **Show the exact error message** to the user.

2. **Guide the user to obtain credentials**: Visit the [PaddleOCR website](https://www.paddleocr.com), click **API**, select a model (`PP-StructureV3`, `PaddleOCR-VL`, or `PaddleOCR-VL-1.5`), then copy the `API_URL` and `Token`. They map to these environment variables:
   - `PADDLEOCR_DOC_PARSING_API_URL` — full endpoint URL ending with `/layout-parsing`
   - `PADDLEOCR_ACCESS_TOKEN` — 40-character alphanumeric string

   Optionally configure `PADDLEOCR_DOC_PARSING_TIMEOUT` for request timeout. Recommend using the host application's standard configuration method rather than pasting credentials in chat.

3. **Apply credentials** — one of:
   - **User configured via the host UI**: ask the user to confirm, then retry.
   - **User pastes credentials in chat**: warn that they may be stored in conversation history, help the user persist them using the host's standard configuration method, then retry.

### Handling Large Files

For PDFs, the maximum is 100 pages per request.

#### Optimize Large Images Before Parsing

For large image files, compress before uploading — this reduces upload time and can improve processing stability:

```bash
uv run scripts/optimize_file.py input.png output.jpg --quality 85
uv run scripts/layout_caller.py --file-path "output.jpg" --pretty
```

`--quality` controls JPEG/WebP lossy compression (1-100, default 85); it has no effect on PNG output. Use `--target-size` (in MB, default 20) to set the max file size — the script iteratively downscales until the target is met.

#### Use URL for Large Local Files (Recommended)

For very large local files, prefer `--file-url` over `--file-path` to avoid base64 encoding overhead:

```bash
uv run scripts/layout_caller.py --file-url "https://your-server.com/large_file.pdf"
```

#### Process Specific Pages (PDF Only)

If you only need certain pages from a large PDF, extract them first:

```bash
# Extract pages 1-5
uv run scripts/split_pdf.py large.pdf pages_1_5.pdf --pages "1-5"

# Mixed ranges are supported
uv run scripts/split_pdf.py large.pdf selected_pages.pdf --pages "1-5,8,10-12"

# Then process the smaller file
uv run scripts/layout_caller.py --file-path "pages_1_5.pdf"
```

### Error Handling

All errors return JSON with `ok: false`. Show the error message and stop — do not fall back to your own vision capabilities. Identify the issue from `error.code` and `error.message`:

**Authentication failed (403)** — `error.message` contains "Authentication failed"

- Token is invalid, reconfigure with correct credentials

**Quota exceeded (429)** — `error.message` contains "API rate limit exceeded"

- Daily API quota exhausted, inform user to wait or upgrade

**Unsupported format** — `error.message` contains "Unsupported file format"

- File format not supported, convert to PDF/PNG/JPG

**No content detected**:

- `text` field is empty
- Document may be blank, image-only, or contain no extractable text

### Tips for Better Results

If parsing quality is poor:

- **Large or high-resolution images**: Compress with `optimize_file.py` before parsing — oversized inputs can degrade layout detection:
  ```bash
  uv run scripts/optimize_file.py input.png optimized.jpg --quality 85
  ```
- **Check confidence**: `result.result.layoutParsingResults[n].prunedResult` includes confidence scores per layout element — low values indicate regions worth reviewing

## Reference Documentation

- `references/output_schema.md` — Full output schema, field descriptions, and command examples

> **Note**: Model version and capabilities are determined by your API endpoint (`PADDLEOCR_DOC_PARSING_API_URL`).

## Testing the Skill

To verify the skill is working properly:

```bash
uv run scripts/smoke_test.py
uv run scripts/smoke_test.py --skip-api-test
uv run scripts/smoke_test.py --test-url "https://..."
```

The first form tests configuration and API connectivity. `--skip-api-test` checks configuration only. `--test-url` overrides the default sample document URL.

---

## 安装与配置（通用版）

> 完整引导见 [SETUP.md](./SETUP.md)。要点：

1. **前置**：Python 3.9+、[uv](https://docs.astral.sh/uv/)（脚本 PEP 723 内联依赖，无需手动装包）
2. **凭证**（一次性）：去 <https://www.paddleocr.com> → API 页获取 `API_URL`（以 `/layout-parsing` 结尾）+ `Token`（40 位）
3. **安装**：`cp -r skills/paddleocr-doc-parsing <你的agent技能目录>/`（如 `~/.hermes/skills/`、`~/.claude/skills/`）
4. **配置**：`cp .env.example .env` 填入凭证，`chmod 600 .env`。`lib.py` 已适配自动从技能根 `.env`（或 `~/.config/paddleocr/.env`）加载，无需手动 export。`.env` 勿进 git
5. **验证**：`uv run scripts/smoke_test.py --skip-api-test`（配置）→ `uv run scripts/smoke_test.py`（API 连通）

**一键用法**（从技能根目录跑）：

```bash
uv run scripts/parse_paper.py "论文.pdf"            # 解析 → md → 本地 4x 高清渲染 → 校验
uv run scripts/parse_paper.py "论文.pdf" /自定义/输出目录
```

**图片：默认本地 4x，不下载 API 图**：
- `parse_paper.py` 默认只做：解析 → md → **本地 pymupdf 4x 渲染**（bbox 从 markdown.images 文件名解析，坐标=PDF点×2）。API 的 2x 图不再下载——对比实测 4x 明显更清晰，且省一次网络步骤
- **完整性保障**：渲染失败的图自动回退下载 API 副本（md 引用永不悬空）；最后校验 md 全部 `<img>` 引用文件存在，缺失会 WARN
- 需要官方原图（照片类位图）时手动用 `fetch_images.py`（不占默认流程）

```bash
uv run scripts/fetch_images.py /path/out.json              # 可选：API 原图（2x）
uv run scripts/render_images.py /path/out.json paper.pdf   # 手动重渲染（--scale 可调）
```

**已知坑（实战沉淀）**：
- ⚠️ 部分旧版封装脚本只提取 `markdown.text`、丢弃 `markdown.images` 映射——跑出的 md 图片全挂。本技能配套 `fetch_images.py`（取回官方图）+ `render_images.py`（本地高清）已解决，务必整套使用
- 单请求 ≤100 页（`scripts/split_pdf.py` 分片），日额度 20000 页（429 即额度耗尽）
- 大文件优先 `--file-url`；`--file-path` 走 base64 上传
- 403 = token 失效；`ok:false` 按错误码处理，**禁止 fallback 到本地视觉能力**
- 50+ 页需数分钟，勿早判超时；`PADDLEOCR_DOC_PARSING_TIMEOUT` 默认 600s
- 扫描版 PDF 必须走它（本身就是 OCR 管线）
- 双栏 arXiv 阅读顺序正确、公式 LaTeX、表格重建 Markdown，均经 38+1 篇世界模型论文验证
