# 🔥 GitHub Trend Monitor

[![GitHub Actions](https://github.com/difyz9/github-trend-monitor/actions/workflows/daily_scraper.yml/badge.svg)](https://github.com/difyz9/github-trend-monitor/actions)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

自动追踪 GitHub 热点项目 + 大厂模型发布 + arXiv 论文，每周生成 AI 行业洞察报告。

---

## ✨ 核心功能

| 模块 | 说明 |
|------|------|
| **每日 GitHub 趋势爬取** | 按 AI Agent / RAG / 多模态 / 长文本 / 推理优化等 5 大领域，增量爬取新仓库 |
| **每日 Star 数更新** | 使用 GraphQL 批量查询，高效获取活跃项目最新 Star 数 |
| **智能淘汰机制** | 基于"连续无增长天数"（分级阈值）自动标记冷门项目 |
| **大厂发布日历** | 跟踪 OpenAI、Google、DeepSeek、智谱等 8+ 厂商的模型/技术发布 |
| **arXiv 论文 RSS** | 自动抓取 cs.AI/cs.LG/cs.CL/cs.CV 方向最新论文 |
| **AI 周报生成** | 调用大模型（GLM/Gemini/Qwen）自动生成结构化周报 |
| **邮件推送** | 每周一上午 9:00（北京时间）发送精美 HTML 报告 |
| **在线日历** | 部署于 GitHub Pages，支持按厂商/类型筛选 |

---

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/difyz9/github-trend-monitor.git
cd github-trend-monitor
```

### 2. 创建虚拟环境并安装依赖

```bash
make setup
```

### 3. 配置环境变量

项目会自动读取根目录下的 `.env` 文件，例如：

```bash
export GITHUB_TOKEN=your_github_token
export GLM_API_KEY=your_glm_api_key  # 可选，用于生成周报
```

也可以将这些变量写入 `.env`，然后直接使用下面的 `make` 命令运行。

### 4. 运行爬虫

```bash
make run
```

### 5. 生成报告

```bash
make analyze
make report
```

也可以运行完整流程：

```bash
make pipeline
```

运行 `make help` 可查看所有可用命令。默认虚拟环境目录为 `.venv`，可以通过 `make VENV=其他目录 setup` 修改。

---

## 📁 项目结构

```
github-trend-monitor/
├── data/                       # 数据存储目录
├── src/github_trend_monitor/
│   ├── crawlers/               # GitHub、厂商和 arXiv 数据抓取
│   ├── analysis/               # Star 分析与 AI 分析
│   ├── reports/                # 周报生成、渲染与发送
│   ├── calendar/               # 发布日历生成与维护
│   └── queries.py              # 搜索查询配置
├── Makefile                    # 环境创建与常用运行命令
└── requirements.txt            # 依赖列表
```

---

## 🔧 配置说明

### 搜索领域配置

编辑 `src/github_trend_monitor/queries.py` 中的 `DOMAIN_QUERIES`：

```python
DOMAIN_QUERIES = {
    "AI Agent": [
        "topic:ai-agent",
        "LLM Agent",
        "Agentic",
        # ...
    ],
    "RAG": [
        "topic:rag",
        "Retrieval-Augmented Generation",
        # ...
    ],
    # ...
}
```

### 淘汰机制配置

编辑 `src/github_trend_monitor/analysis/analyzer.py` 中的阈值：

```python
# 连续无增长天数阈值
STALE_THRESHOLDS = {
    'cold': 7,      # 7天无增长 → 标记为冷门
    'frozen': 14,   # 14天无增长 → 标记为冻结
    'archive': 30   # 30天无增长 → 归档
}
```

---

## 📊 报告示例

### 周报内容

- 🔥 本周热门项目 TOP 10
- 📈 增长最快的项目
- 🏢 大厂发布动态
- 📚 热门论文推荐
- 💡 技术趋势分析

### 在线日历

部署于 GitHub Pages，支持：
- 按厂商筛选（OpenAI、Google、DeepSeek 等）
- 按类型筛选（模型发布、技术更新、开源项目）
- 点击查看详情

---

## 🚀 GitHub Actions 配置

### 1. 创建 Repository Secrets

| Secret | 说明 |
|--------|------|
| `GH_TOKEN` | GitHub Personal Access Token |
| `GLM_API_KEY` | 智谱 GLM API Key（可选） |

### 2. 工作流说明

- **每日执行**：UTC 2:00（北京时间 10:00）
- **手动触发**：支持 workflow_dispatch
- **自动提交**：数据更新后自动 commit 并 push

---

## 📝 自定义扩展

### 添加新的搜索领域

1. 在 `src/github_trend_monitor/queries.py` 中添加新的领域关键词
2. 重新运行 `make run`

### 添加新的大厂

1. 在 `src/github_trend_monitor/crawlers/company_crawler.py` 中添加厂商配置
2. 更新 RSS 源

### 自定义报告格式

编辑 `src/github_trend_monitor/reports/generate_weekly_report.py` 中的模板

---

## 📜 License

MIT License

---

## 🙏 致谢

- [GitHub API](https://docs.github.com/en/rest) - 数据源
- [arXiv](https://arxiv.org/) - 论文数据
- [智谱 GLM](https://open.bigmodel.cn/) - AI 周报生成
