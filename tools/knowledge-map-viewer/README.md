# knowledge-map-viewer

> **知识地图交互可视化**：左侧结构树 + 右侧力导向图，双视图（关系图 / 时间线）。

## 使用

打开 `knowledge-map-viewer.html`，将页面内 `${DATA_JSON}` 替换为你的知识地图 JSON（`${名称}` / `${版本}` 同理），浏览器打开即可。

**零部署**：file:// 双击即用，无需任何服务器。

## 数据契约

遵循 `../methodology/knowledge-map/` 的 schema：

- 节点：`node_id` / `title` / `tags` / `status` / `year` / `created` / `updated`
- 节点可选字段：`body`（详情正文，Markdown，点击节点时右侧面板渲染）/ `maturity`（成熟度）
- 关系：`depends_on` / `replaces` / `triggers` / `conflicts` / `supports` / `subtopic_of`
- 关系字段：`mechanism`（机制说明，必填）/ `papers`（佐证论文数组，可选）
- 证据 tag：`#原文引用` / `#结构推导` / `#领域推断`

## 功能

- 左侧树：层级色（骨架=蓝 展开=绿 实例=橙），点击展开/折叠 + 详情面板
- 力导向图：拖拽/缩放/悬停高亮/点击选中
- 时间线视图：顶部按钮切换，节点按 `year` 定位，成熟度用边框区分
- 标签筛选图例：按 tags 过滤节点

## 部署选项

| 方式 | 说明 |
|------|------|
| 本地打开 | 内嵌 JSON 或替换占位符，file:// 即用 |
| 内联渲染 | 把 JSON 嵌入 HTML（`window.__KM_INLINE__`），分享单文件 |
| 远程加载 | viewer 与 JSON 同源部署（如文件列车），fetch 加载 |

## 版本

- 与知识地图 schema v1.1 配套
- 模板为单文件 HTML，无外部依赖
