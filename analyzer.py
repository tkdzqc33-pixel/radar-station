# ============================================================
# 分析模块：调用 DeepSeek API 对新闻做智能分析
# 功能：分类、分级（S/A/B）、三行简报、周报趋势分析
# ============================================================

import json

import requests

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    DEEPSEEK_MODEL,
    MAX_NEWS_CHARS,
    DEBUG,
)

# 用户业务背景，让 AI 分析更有针对性
BUSINESS_CONTEXT = """
我是一名一人公司老板，业务有三个板块：
1. 短剧出海：用 AI 制作短剧/漫剧，投放到海外平台（如 YourChannel、TikTok）赚美元
2. AI 工具/插件：用 AI 开发能上架出售的技能、插件、小工具
3. 知识付费：教别人 AI 内容创作与变现（线上课+线下课）
我重点关注：AI 视频生成、短剧出海平台政策、变现模式、AI 工具动态。
"""


def _call_deepseek(system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
    """调用 DeepSeek Chat API"""
    url = f"{DEEPSEEK_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.3,
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[deepseek] FAILED: {e}")
        if DEBUG:
            print(resp.text if "resp" in dir() else "")
        return ""


# ---------------- 每日简报分析 ----------------

SYSTEM_PROMPT_DAILY = f"""{BUSINESS_CONTEXT}

你是我的情报分析师。给你一批今天抓到的新闻，请逐条分析并输出 JSON。

对每条新闻，分析：
- category: 属于哪个板块：short_drama（短剧出海）/ ai_tools（AI工具）/ industry（行业动态）/ other
- level: 重要性分级：S（立刻行动，直接影响赚钱）/ A（当天处理）/ B（周报汇总即可）
- why: 为什么这条对我重要（一句话，30字内）
- action: 我该做什么（一句话，30字内，具体可执行）

输出格式（严格 JSON 数组，不要输出其他内容）：
[
  {{"title": "原标题", "category": "short_drama", "level": "S", "why": "...", "action": "..."}},
  ...
]
只输出 JSON。"""


def analyze_daily(items: list, batch_size: int = 10) -> list:
    """分批分析每日新闻，返回带分析结果的列表"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        news_text = ""
        for idx, it in enumerate(batch):
            summary = (it.get("summary") or "")[:MAX_NEWS_CHARS]
            news_text += f"[{idx}] 标题: {it['title']}\n摘要: {summary}\n来源: {it.get('source', '')}\n\n"

        user_prompt = f"请分析以下新闻：\n\n{news_text}"
        raw = _call_deepseek(SYSTEM_PROMPT_DAILY, user_prompt, max_tokens=3000)
        parsed = _parse_json_array(raw)

        for idx, it in enumerate(batch):
            analysis = parsed[idx] if idx < len(parsed) else {}
            results.append(
                {
                    **it,
                    "category": analysis.get("category", "other"),
                    "level": analysis.get("level", "B"),
                    "why": analysis.get("why", ""),
                    "action": analysis.get("action", ""),
                }
            )
    return results


# ---------------- 周报分析 ----------------

SYSTEM_PROMPT_WEEKLY = f"""{BUSINESS_CONTEXT}

你是我的情报分析师。给你近7天收集的新闻（标题+摘要），请输出一份中文周报 JSON。

周报包含：
1. key_changes: 本周关键变化（最多5条，每条：标题 + 一句话说明 + 对我的影响）
2. opportunities: 机会清单（最多3条，每条：机会是什么 + 为什么现在做 + 建议动作）
3. risks: 风险提示（最多3条，每条：风险 + 应对）
4. focus: 下周建议聚焦的一件事（一句话）

输出格式（严格 JSON，不要输出其他内容）：
{{
  "key_changes": [{{"title": "...", "summary": "...", "impact": "..."}}],
  "opportunities": [{{"title": "...", "why": "...", "action": "..."}}],
  "risks": [{{"title": "...", "mitigation": "..."}}],
  "focus": "..."
}}"""


def analyze_weekly(items: list) -> dict:
    """分析一周新闻，输出周报 JSON"""
    # 只保留标题+摘要，控制 token
    news_text = ""
    for it in items[:80]:  # 最多取 80 条
        summary = (it.get("summary") or "")[:800]
        news_text += f"- {it['title']} | {summary}\n"

    user_prompt = f"请基于以下一周新闻生成周报：\n\n{news_text}"
    raw = _call_deepseek(SYSTEM_PROMPT_WEEKLY, user_prompt, max_tokens=3000)
    parsed = _parse_json_object(raw)
    return parsed or {
        "key_changes": [],
        "opportunities": [],
        "risks": [],
        "focus": "本周数据不足，下周继续观察。",
    }


# ---------------- 工具函数 ----------------

def _parse_json_array(text: str) -> list:
    """从 LLM 输出中解析 JSON 数组，容错处理"""
    if not text:
        return []
    # 去掉可能的 markdown 代码块标记
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        # 尝试提取 [ ... ] 部分
        import re

        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, list) else []
            except json.JSONDecodeError:
                return []
        return []


def _parse_json_object(text: str) -> dict:
    """从 LLM 输出中解析 JSON 对象，容错处理"""
    if not text:
        return {}
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        import re

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {}
        return {}
