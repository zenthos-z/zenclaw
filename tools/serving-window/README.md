# 文件列车 · Serving Window

> **AI 产出物统一交付窗口**：manifest.json + 纯静态 HTML，无需后端。

## 它能做什么

AI 对话中产生的所有产出物（Markdown 报告、PDF、图片、音频、知识地图 JSON 等），通过一个 `manifest.json` 清单自动同步到交互式预览窗口：

- 卡片化展示：markdown / pdf / image / audio / video / knowledge-map / text 多类型
- 分组 dock：按项目/用途分组浏览
- 知识地图内联渲染：JSON 直接渲染为交互式知识地图
- 本地优先：离线时自动回退到本地 `manifest.json` 或演示数据

## 部署要求

| 项 | 要求 |
|----|------|
| 静态托管 | 任意（对象存储 OSS / GitHub Pages / Cloudflare Pages / 本地 file://） |
| 后端 | **无**（纯前端 + 静态 JSON） |
| CORS | 托管 manifest 的域名需允许 fetch 跨域（OSS 需配置 CORS） |

**零服务器也能用**：本目录的 HTML 直接 `file://` 打开即可浏览本地 `manifest.json`。

## 快速开始

### 模式 ① 纯本地（第 0-1 级）

```bash
cp manifest.example.json manifest.json   # 编辑你的条目
# 浏览器打开 文件列车.html（file:// 即可）
```

### 模式 ② 静态托管（第 3 级，推荐）

1. 将 `文件列车.html` 部署到你的静态托管（ECS + Nginx / OSS 静态网站 / Pages）
2. 上传 `manifest.json` 到同源可 fetch 的位置
3. 编辑 HTML 中 `MANIFEST_URL` 为你的 manifest 地址
4. 每次有新产品：更新 manifest.json（version+1，追加条目）→ 前端自动刷新

## manifest.json 格式

```json
{
  "updated": "2026-08-16T10:00:00Z",
  "version": 1,
  "title": "我的产出",
  "items": [
    {
      "id": "report-01",
      "type": "markdown",
      "title": "调研报告",
      "size": 34923,
      "group": "research",
      "version": 2,
      "persistence": "persistent",
      "url": "report.md"
    }
  ]
}
```

| 字段 | 说明 |
|------|------|
| `type` | markdown / pdf / image / audio / video / knowledge-map / text |
| `group` | 分组名（dock 按此聚合） |
| `persistence` | `persistent`（长期）/ `temp`（3 天过期） |
| `url` | 资源地址（同源相对路径或绝对 URL） |

> ⚠️ **知识地图条目**：`type="knowledge-map"` 的 JSON 必须与 HTML **同源**（否则浏览器 CORS 拦截 fetch），或托管端配置好 CORS。

## 与其他工具的关系

- 接收所有方法论的产出物（知识地图 JSON、调研报告、封面图）
- 知识地图 viewer 的部署规范见 `../knowledge-map-viewer/`

## 版本与维护

- 模板源码：`文件列车.html`（单文件，无外部依赖）
- 清洗说明：开源版已将部署者专属的 manifest 地址参数化为 `__MANIFEST_URL__`，见文件内注释
