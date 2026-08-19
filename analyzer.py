# ============================================================
# 分析模块 v2：分析师角色升级
# 功能：分类、分级、商业机会/风险/趋势分析、周报
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

# 用户业务背景（分析师视角，让 AI 像资深操盘手一样思考）
BUSINESS_CONTEXT = """
我是一名一人公司老板，业务有三个板块，每条情报都要从这三个角度评估价值：
1. 短剧出海（核心）：用 AI 制作短剧/漫剧，投放到海外平台（YourChannel、TikTok、ReelShort等）赚美元。关注：平台政策/分账规则/爆款题材/投流打法/工具迭代
2. AI 工具/插件：用 AI 开发能上架出售的技能、插件、小工具（SaaS）。关注：市场需求/竞品/技术可行性/变现模式
3. 知识付费：教别人 AI 内容创作与变现（线上课+线下课）。关注：学员痛点/内容选题/营销渠道

我的分析视角：
- 每条情报先判断：它能帮我赚钱吗？能省成本吗？能避坑吗？
- 关注"别人还没注意到的机会"和"即将发生的风险"
- 给出的行动建议必须具体、可执行，不是空话
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


# ---------------- 每日简报分析（分析师版） ----------------

SYSTEM_PROMPT_DAILY = f"""{BUSINESS_CONTEXT}

你是一名深耕 AI 内容出海领域的资深分析师。给你一批今天抓到的新闻，请以分析师视角逐条分析。

对每条新闻，分析输出以下字段：
- category: 业务分类：short_drama（短剧出海）/ ai_tools（AI工具）/ industry（行业动态）/ other
- level: 重要分级：
  - S（立刻行动）：直接影响我的赚钱机会、平台政策剧变、重大工具突破
  - A（今天处理）：有参考价值、需要跟进、可能影响近期决策
  - B（了解即可）：行业动态、背景信息
- why: 这条情报为什么对我重要（一句话，30字内，要点破价值）
- action: 我具体该做什么（一句话，30字内，必须是可执行的动作，如"下载测试XX工具""研究XX平台分成规则"）
- opportunity: 潜在的赚钱机会（一句话，20字内；没有则填"无"）
- risk: 潜在风险/坑（一句话，20字内；没有则填"无"）

输出格式（严格 JSON 数组，不要输出任何其他内容）：
[
  {{"title": "原标题", "category": "short_drama", "level": "S", "why": "...", "action": "...", "opportunity": "...", "risk": "..."}},
  ...
]
只输出 JSON。"""


def analyze_daily(items: list, batch_size: int = 8) -> list:
    """分批分析每日新闻，返回带分析结果的列表（分析师版）"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        news_text = ""
        for idx, it in enumerate(batch):
            summary = (it.get("summary") or "")[:MAX_NEWS_CHARS]
            news_text += f"[{idx}] 标题: {it['title']}\n摘要: {summary}\n来源: {it.get('source', '')}\n\n"

        user_prompt = f"请分析以下新闻：\n\n{news_text}"
        raw = _call_deepseek(SYSTEM_PROMPT_DAILY, user_prompt, max_tokens=4000)
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
                    "opportunity": analysis.get("opportunity", ""),
                    "risk": analysis.get("risk", ""),
                }
            )
    return results


# ---------------- 周报分析（分析师版） ----------------

SYSTEM_PROMPT_WEEKLY = f"""{BUSINESS_CONTEXT}

你是我的首席情报分析师。给你近7天收集的新闻（标题+摘要），请输出一份深度周报 JSON。

周报包含：
1. key_changes: 本周关键变化（最多5条，每条：标题 + 变化是什么 + 对我的影响）
2. opportunities: 机会清单（最多3条，每条：机会 + 为什么现在做 + 具体建议动作 + 预估变现方式）
3. risks: 风险提示（最多3条，每条：风险 + 应对策略）
4. trend_signals: 趋势信号（最多3条，每条：正在发生的趋势 + 证据 + 我该提前布局什么）
5. focus: 下周建议聚焦的一件事（一句话，具体可执行）

输出格式（严格 JSON，不要输出任何其他内容）：
{{
  "key_changes": [{{"title": "...", "summary": "...", "impact": "..."}}],
  "opportunities": [{{"title": "...", "why": "...", "action": "...", "revenue": "..."}}],
  "risks": [{{"title": "...", "mitigation": "..."}}],
  "trend_signals": [{{"title": "...", "evidence": "...", "action": "..."}}],
  "focus": "..."
}}"""


def analyze_weekly(items: list) -> dict:
    """分析一周新闻，输出深度周报 JSON"""
    news_text = ""
    for it in items[:80]:
        summary = (it.get("summary") or "")[:800]
        news_text += f"- {it['title']} | {summary}\n"

    user_prompt = f"请基于以下一周新闻生成深度周报：\n\n{news_text}"
    raw = _call_deepseek(SYSTEM_PROMPT_WEEKLY, user_prompt, max_tokens=4000)
    parsed = _parse_json_object(raw)
    return parsed or {
        "key_changes": [],
        "opportunities": [],
        "risks": [],
        "trend_signals": [],
        "focus": "本周数据不足，下周继续观察。",
    }


# ---------------- 工具函数 ----------------

def _parse_json_array(text: str) -> list:
    if not text:
        return []
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
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
