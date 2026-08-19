import json
import os
from datetime import datetime
from pathlib import Path

import requests

from github_trend_monitor.web.server import read_repositories

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INSIGHTS_FILE = PROJECT_ROOT / "data" / "ai_insights.json"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"
# DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"

#     "model": "google/gemma-4-26b-a4b-it:free",


def _compact_repositories(repositories, limit=30):
    ranked = sorted(repositories, key=lambda repo: (repo["stars"], repo["forks"]), reverse=True)
    return [
        {
            "name": repo["name"],
            "stars": repo["stars"],
            "forks": repo["forks"],
            "language": repo["language"],
            "domains": repo["domains"],
            "topics": repo["topics"][:8],
            "description": repo["description"][:240],
            "first_seen": repo["first_seen"],
            "url": repo["url"],
        }
        for repo in ranked[:limit]
    ]


def _build_prompt(repositories):
    dataset = json.dumps(_compact_repositories(repositories), ensure_ascii=False)
    return f"""你是一名严谨的 AI 开源生态分析师。请基于下面的 GitHub 项目数据，提炼对技术负责人、产品经理和开发者真正有用的结论。

项目数据：
{dataset}

请用中文输出 Markdown，严格按以下结构：
# AI 开源趋势洞察
## 一句话判断
用一句话判断当前最重要的变化。
## 三个高价值信号
列出 3 条，每条包含：信号、证据（项目名和具体 Stars/Forks/领域）、为什么重要。
## 值得优先研究的项目
推荐最多 5 个项目，每个说明适合谁、解决什么问题、建议的下一步。
## 风险与误区
指出数据可能造成的误判，例如 Stars 不等于真实采用，以及还需要补充什么数据。
## 行动建议
给出未来 7 天可以执行的 3 个具体动作。

要求：只基于提供的数据，不编造项目能力；每个关键判断尽量引用具体项目名和数字；总长度控制在 1000-1600 字。"""


def call_openrouter(prompt):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("未设置 OPENROUTER_API_KEY，请在 .env 中配置")

    payload = {
        "model": os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
        "messages": [{"role": "user", "content": prompt}],
        "reasoning": {"enabled": True},
        "temperature": 0.3,
        "max_tokens": 3000,
    }
    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1:8000",
            "X-Title": "GitHub Trend Monitor",
        },
        json=payload,
        timeout=120,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"OpenRouter 请求失败（HTTP {response.status_code}）")
    message = response.json()["choices"][0]["message"]
    return {
        "content": message.get("content", ""),
        "reasoning_details": message.get("reasoning_details"),
        "model": payload["model"],
    }


def generate_insights(force=False):
    if not force and INSIGHTS_FILE.exists():
        cached = json.loads(INSIGHTS_FILE.read_text(encoding="utf-8"))
        if cached.get("content"):
            return cached

    repositories = read_repositories()
    if not repositories:
        raise RuntimeError("没有可供分析的 GitHub 项目数据")
    result = call_openrouter(_build_prompt(repositories))
    result.update({"generated_at": datetime.now().isoformat(timespec="seconds"), "repository_count": len(repositories)})
    INSIGHTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    INSIGHTS_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    result = generate_insights(force=True)
    print(result["content"])
