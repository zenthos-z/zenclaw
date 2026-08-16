<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-方法论%20%26%20增强工具-2962ff?style=flat-square&logo=openai&logoColor=white" alt="OpenClaw">
  <img src="https://img.shields.io/badge/MIT-License-green?style=flat-square" alt="License">
</p>

<h1 align="center">zenclaw</h1>

<p align="center"><b>OpenClaw 学习方法论与功能增强工具集</b></p>

<p align="center"><i>把 OpenClaw 变成你的知识工厂：知识地图 · 论文调研 · 视觉 Prompt · 文件列车</i></p>

---

## 这个项目是什么

一套经过实战检验的 **OpenClaw 学习方法论 + 功能增强工具集**。它不是技能的堆叠，而是回答三个问题：

1. **怎么学**——如何用知识地图组织知识、用论文调研管线高效阅读文献
2. **怎么用**——如何增强 OpenClaw 的交付能力（文件列车）、视觉能力（Prompt 方法论）
3. **怎么部署**——不同的部署条件下，分别该用哪些工具

> 核心理念：**方法论是通用的，工具按部署条件选择。**

---

## 适合谁

| 画像 | 特征 | 你会用到 |
|------|------|---------|
| 🎓 **科研学习者** | 频繁读论文、做调研、构建知识体系 | 论文调研法、知识地图法 |
| 🤖 **OpenClaw 重度用户** | 深度使用 Agent，追求效率上限 | 全部增强工具 |
| 🏠 **自部署者** | 把 OpenClaw 跑在 NAS / ECS / 服务器 | 文件列车、远程交付 |

## 部署条件速查

> **先看这里。** 你的部署条件决定你该用哪一层的工具。

| 级别 | 部署形态 | 可用工具 | 需要文件列车吗 |
|:----:|---------|---------|:------------:|
| **0** | 零部署（浏览器 + LLM API） | 方法论文档、本地 viewer | ❌ |
| **1** | 纯本地（OpenClaw 跑本机） | 方法论 + 本地工具 | ❌ |
| **2** | 内网 NAS（局域网多设备） | + 局域网交付 | ⭕ 可选 |
| **3** | 公网服务器（ECS/云主机） | + 文件列车完整版 | ✅ 推荐 |

**A 类受众（本地部署）** 到第 1 级即可，跳过文件列车；
**B 类受众（NAS/ECS）** 上到第 3 级，解锁完整交付能力。

---

## 📐 方法论层（所有人适用，零部署依赖）

| 目录 | 方法 | 解决什么问题 |
|------|------|-------------|
| [methodology/knowledge-map](./methodology/knowledge-map/) | **知识地图法** | 知识怎么组织才能可视化、可演进、可复用 |
| [methodology/research](./methodology/research/) | **论文调研法** | 文献调研怎么做到系统、不遗漏、可验证 |
| [methodology/visual-prompt](./methodology/visual-prompt/) | **视觉 Prompt 法** | 生图提示词怎么从「碰运气」变成「可复现」 |

## 🔧 工具层（按部署条件分档）

### 本地工具（第 0-1 级，A+B 受众）

| 工具 | 说明 | 部署要求 |
|------|------|---------|
| [knowledge-map-viewer](./tools/knowledge-map-viewer/) | 知识地图交互可视化（左侧树 + 力导向图） | 无（浏览器打开） |
| 论文调研脚本 | 四线交叉 / 覆盖矩阵 / 双层分析管线 | 无（只需 LLM API） |

### 服务化工具（第 2-3 级，B 受众）

| 工具 | 说明 | 部署要求 |
|------|------|---------|
| [serving-window（文件列车）](./tools/serving-window/) | AI 产出物统一交付窗口：manifest.json + 静态 HTML | 对象存储 + 静态托管 |

## 🔗 已开源技能（不搬运，仅引用）

以下技能已在 [my-skills](https://github.com/zenthos-z/my-skills) 维护，zenclaw 不重复收录：

| 技能 | 说明 | 链接 |
|------|------|------|
| quick-img | 快速生图（Gemini 3.1 Flash Image，网络搜索补参考图） | [my-skills/quick-img](https://github.com/zenthos-z/my-skills/tree/main/quick-img) |
| mermaid-pro | 专业 Mermaid 图表生成 | [my-skills/mermaid-pro](https://github.com/zenthos-z/my-skills/tree/main/mermaid-pro) |
| systems-thinking | 系统思考教练 | [my-skills/systems-thinking](https://github.com/zenthos-z/my-skills/tree/main/systems-thinking) |
| qunribao | 群日报生成系统 | [my-skills/qunribao](https://github.com/zenthos-z/my-skills/tree/main/qunribao) |

## 🧪 实践项目（独立仓库，仅引用）

科研/学习实践内容独立维护，此处仅列链接：

- （待添加：Dreamer 系列复现等学习实验）

---

## 依赖关系

```
方法论层（零依赖）
   │ 定义产物格式
   ▼
知识地图 JSON Schema ◄── knowledge-map-viewer（依赖 schema 版本）
   │
   ├──► 文件列车（依赖对象存储 + 静态托管，接收所有产出物）
   ├──► 论文调研脚本（依赖 arXiv API + LLM API）
   └──► 视觉 Prompt 工具（依赖生图 API）
```

| 工具 | 依赖 | 部署要求 | 可选替代 |
|------|------|---------|---------|
| knowledge-map-viewer | JSON Schema（契约） | 无 | — |
| 论文调研脚本 | arXiv + LLM API | 无 | 手动调研 |
| 文件列车 | 对象存储 + 静态托管 | 服务器级 | 纯本地 manifest |

## 快速开始

```bash
# 第 0 级：零部署，先看方法论
open methodology/knowledge-map/

# 第 1 级：本地使用，打开 viewer
open tools/knowledge-map-viewer/index.html

# 第 3 级：部署文件列车（需对象存储 + 静态托管）
# 详见 tools/serving-window/README.md
```

---

## License

MIT
