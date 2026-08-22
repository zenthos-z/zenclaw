# paddleocr-doc-parsing 配置引导（SETUP）

> 给第一次安装本技能的 Agent 的完整引导。看完这篇 + `SKILL.md` 即可投入使用。
> 技能来源：zenclaw 扩展技能 / 上游 [PaddlePaddle/PaddleOCR skills/paddleocr-doc-parsing](https://github.com/PaddlePaddle/PaddleOCR/tree/main/skills/paddleocr-doc-parsing)

## 这是什么

把 PDF / 文档图片解析成结构化 Markdown：表格（cell 级）、公式（LaTeX）、图表、多栏阅读顺序，并配套**本地高清渲染**（默认 4x，解决官方 API 图片只有 2x 偏糊的问题）。

底层是 **PaddleOCR 云 API**（PP-StructureV3 / PaddleOCR-VL 模型，百度飞桨生态，服务挂在 paddleocr.com 官网）——**不是**百度智能云 OCR，也不是百度大模型文档翻译 API，三套别混。

## 前置要求

- Python 3.9+ 与 [uv](https://docs.astral.sh/uv/)（脚本用 PEP 723 内联依赖，无需手动装包）
- 能访问外网（API 在云端）
- 一个 PaddleOCR 账号（获取凭证用，见下）

## 获取凭证（必须，一次性）

1. 打开 <https://www.paddleocr.com>，注册/登录
2. 进入 **API** 页，选择模型（推荐 `PP-StructureV3` 或 `PaddleOCR-VL`）
3. 复制两样东西：
   - **API_URL**：形如 `https://<你的服务>.aistudio-app.com/layout-parsing`（必须以 `/layout-parsing` 结尾）
   - **Token**：40 位字符串（AI Studio 访问令牌，也可在 <https://aistudio.baidu.com/account/accessToken> 查看）
4. 免费额度参考：单请求 ≤100 页、日额度 20000 页（超了返回 429 等次日或升级）

## 安装（按你的 Agent 环境选择）

```bash
# 1) 复制技能目录到你的 Agent 技能目录
cp -r skills/paddleocr-doc-parsing ~/.hermes/skills/          # Hermes
# 或
cp -r skills/paddleocr-doc-parsing ~/.claude/skills/          # Claude Code / OpenClaw
```

## 配置凭证

```bash
cd <你的技能目录>/paddleocr-doc-parsing
cp .env.example .env
chmod 600 .env
# 编辑 .env，填入上面获取的 URL 和 Token：
#   PADDLEOCR_DOC_PARSING_API_URL=https://<你的服务>.aistudio-app.com/layout-parsing
#   PADDLEOCR_ACCESS_TOKEN=<你的40位token>
```

> 本副本的 `lib.py` 已适配：运行时自动从技能目录 `.env`（或 `~/.config/paddleocr/.env`）加载凭证，**无需手动 export**。`.env` 权限 600，**绝不要提交进 git / 发到聊天**。

## 验证

```bash
cd <技能目录>/paddleocr-doc-parsing
uv run scripts/smoke_test.py --skip-api-test   # 只验证配置读取
uv run scripts/smoke_test.py                   # 含 API 连通性测试（消耗极小额度）
```

## 使用（一键流程）

```bash
uv run scripts/parse_paper.py "论文.pdf"
# 自动：解析 → 写 Markdown → 本地 4x 高清渲染图片 → 校验 md 图片引用完整性
# 输出默认落在 <论文同目录>/解析/（md + result.json + imgs/）
```

分步工具（需要时）：`layout_caller.py`（解析出 JSON）、`fetch_images.py`（下载官方 2x 原图，照片类位图用）、`render_images.py`（手动重渲染，`--scale` 可调）、`split_pdf.py`（超 100 页分片）。

## 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| `CONFIG_ERROR` | `.env` 没配置/没读取 | 检查 `.env` 位置与内容；`smoke_test.py --skip-api-test` 定位 |
| 403 Authentication failed | Token 失效 | 重新获取并更新 `.env` |
| 429 rate limit | 日额度耗尽 | 等次日或升级 |
| 图片偏糊 | 官方 API 图是页面 2x 渲染裁剪 | 用默认流程（`parse_paper.py` 自动本地 4x 渲染）；照片类位图才保留官方版 |
| md 里图片引用失效 | 脚本旧版只取了 `markdown.text` 丢 `images` | 确认用的是本技能脚本（`lib.py` 含 `.env` 适配 + `parse_paper.py` 含渲染与校验） |
| 100 页以上 | 单请求上限 | `split_pdf.py` 分片后逐片解析 |

## 验证过的效果（2026-08 实测）

- 38+ 篇世界模型论文批量解析：双栏 arXiv 阅读顺序正确、公式 LaTeX、表格重建良好
- 29 页 LeWorldModel：37/37 图本地 4x 渲染成功，Figure 1 从官方 771px → 1542px，文字锐利无锯齿
- md 图片引用完整性校验：35 张引用 100% 有对应文件
