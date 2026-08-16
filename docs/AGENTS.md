# 🤖 Agent 部署引导（Agent Deployment Guide）

> 本文件是给 **AI Agent**（Claude Code / OpenClaw / Codex 等）的部署引导。当用户要求「部署 zenclaw / 安装这套工具」时，按此流程执行。

## 仓库定位速览

```
zenclaw/
├── methodology/            # 方法论（纯文档，零部署）——直接可读
├── tools/serving-window/   # 文件列车（manifest.json + 静态 HTML）
├── tools/knowledge-map-viewer/  # 知识地图可视化（单文件 HTML）
├── docs/deployment-matrix.md    # 部署阶梯详解
└── README.md
```

**判断用户部署级别**（先问或用默认）：用户有服务器 → 第 3 级；NAS → 第 2 级；仅本机 → 第 1 级；只想看 → 第 0 级。

## 部署流程

### Step 1 · 判定部署级别

| 级别 | 用户条件 | 要做的事 |
|:----:|---------|---------|
| 0 | 只有浏览器 | 打开 methodology/ 文档 + viewer 本地预览 |
| 1 | OpenClaw 本机 | 方法论 + 本地工具，跳过文件列车 |
| 2 | 内网 NAS | 文件列车部署到 NAS 静态服务 |
| 3 | ECS/云主机 | 文件列车完整版（对象存储 + 域名） |

### Step 2 · 部署文件列车（第 2-3 级才需要）

1. 复制 `tools/serving-window/文件列车.html` 到托管根目录
2. 将 `tools/serving-window/manifest.example.json` 复制为 `manifest.json` 并编辑条目
3. **关键配置**：编辑 HTML 中 `MANIFEST_URL`（第 ~838 行）：
   ```js
   const MANIFEST_URL='__MANIFEST_URL__'; // ← 替换为你的 manifest 地址
   ```
   留空 = 仅本地模式；填 URL = 联网拉取（需 CORS 允许）。
4. 上传 manifest.json 到与 HTML 同源可 fetch 的路径
5. 验证：浏览器打开 HTML → 应看到卡片列表；F12 控制台无 CORS 报错

### Step 3 · 配置知识地图 viewer

- 打开 `tools/knowledge-map-viewer/knowledge-map-viewer.html`
- 将 `${DATA_JSON}` 替换为知识地图 JSON（`${名称}` / `${版本}` 同理）
- 本地 file:// 直接可用；远程部署须与 JSON 同源

### Step 4 · 关联已开源技能（可选）

需要生图/图表/日报能力时，从 my-skills 安装（zenclaw 不重复收录）：

```bash
# 生图（Gemini Flash Image，OpenClaw 新版）
# 来源: https://github.com/zenthos-z/my-skills/tree/main/quick-img
cp -r <clone>/quick-img ~/.claude/skills/   # 或放入 OpenClaw skills/ 目录
# 配置: cp assets/.env.example assets/.env → 填入 DMX_API_KEY
```

## 常见坑（务必检查）

| 坑 | 现象 | 修复 |
|----|------|------|
| CORS 拦截 | 卡片加载不出，控制台 `blocked by CORS` | manifest 与 HTML 同源，或托管端配 CORS 头 |
| MANIFEST_URL 未替换 | 一直显示演示数据 | 检查 HTML 内 `MANIFEST_URL` 是否还是 `__MANIFEST_URL__` |
| 知识地图 fetch 失败 | 地图区空白 | JSON 必须与 viewer 同源（OSS 直链默认不可 fetch） |
| manifest 格式错 | 卡片不显示 | 字段名严格：`id/type/title/group/version/persistence/url`，`updated` 用 ISO 时间戳 |

## 产出物交付惯例

- 每次新增产出：上传资源 → 更新 manifest.json（`version+1`，追加 item）→ 用户刷新即可见
- `persistence`: `persistent`（长期）/ `temp`（3 天过期）
- 知识地图条目：`"type": "knowledge-map"`，url 指向 JSON（须同源）

## 方法论文档直接可用

`methodology/` 三个目录是纯 Markdown 规范，agent 可直接读取并按其执行：
- `knowledge-map/README.md` — 构建知识地图（schema/分层流程/陷阱）
- `research/README.md` — 论文调研管线（覆盖矩阵/四线交叉/双层筛选）
- `visual-prompt/README.md` — 视觉提示词方法论（V15/拓扑/头图）
