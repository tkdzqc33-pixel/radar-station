# ============================================================
# 今日行动清单：AI 从情报中提炼"今天该做什么"
# 产出：
#   - tools_to_test: 今天要测试的工具/平台（重点）
#   - things_to_watch: 要持续关注的事
#   - research_topics: 要研究/调研的主题
#   - daily_focus: 今天最重要的一件事
# ============================================================

import json
import os
from datetime import datetime

from analyzer import _call_deepseek, _parse_json_object

ACTIONS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "today_actions.json"
)

SYSTEM_PROMPT_ACTIONS = """
你是一名深耕 AI 内容出海领域的首席分析师兼操盘手。基于今天的全部情报（含分级/机会/风险标注），
生成"今日行动清单"——把情报转成【我今天具体要做什么】。

要求：
1. tools_to_test: 今天值得【动手测试/试用】的工具、平台、开源项目（最多5个）
   - 只挑真正值得今天动手的（S级、有新版本、有机会信号）
   - 每个给出：名字、一句话说明它是什么、为什么今天测（结合情报）、预计用时
2. things_to_watch: 需要持续【关注/跟踪】但不急于动手的事（最多3个）
3. research_topics: 需要【研究/调研】的主题（最多3个，比如某平台分成规则、某新赛道）
4. daily_focus: 今天最重要的一件事（一句话，具体可执行）
5. 如果情报里没有值得测试的，tools_to_test 给空数组，不要硬凑

输出格式（严格 JSON）：
{
  "tools_to_test": [
    {"name": "工具名", "what": "一句话说明", "why_today": "为什么今天测（结合情报）", "time_est": "预计用时", "source": "依据的情报标题"}
  ],
  "things_to_watch": [{"item": "关注什么", "reason": "为什么"}],
  "research_topics": [{"topic": "研究主题", "why": "为什么研究"}],
  "daily_focus": "今天最重要的一件事"
}
只输出 JSON。"""


def generate_today_actions(items: list) -> dict:
    """从今日情报生成行动清单"""
    # 按重要度排序，取 S/A 级为主
    def sort_key(it):
        return {"S": 3, "A": 2, "B": 1}.get(it.get("level"), 0)

    sorted_items = sorted(items, key=sort_key, reverse=True)

    news_lines = []
    for it in sorted_items[:30]:
        title = it.get("title", "")[:70]
        why = it.get("why", "")
        opp = it.get("opportunity", "")
        action = it.get("action", "")
        line = f"[{it.get('level', 'B')}] {title}"
        if why:
            line += f" | {why}"
        if opp and opp != "无":
            line += f" | 机会:{opp}"
        if action:
            line += f" | 建议:{action}"
        news_lines.append(line)
    news_text = "\n".join(news_lines) or "（今日无重要情报）"

    user_prompt = f"今日情报如下：\n{news_text}\n\n请生成今日行动清单。"
    raw = _call_deepseek(SYSTEM_PROMPT_ACTIONS, user_prompt, max_tokens=2500)
    result = _parse_json_object(raw)

    # 兜底：AI 失败时用简单规则生成
    if not result or not result.get("daily_focus"):
        result = _fallback_actions(items)
    return result


def _fallback_actions(items: list) -> dict:
    """AI 失败时的兜底：提取 action 字段里带"测试/试用"的情报"""
    tools = []
    for it in items:
        action = it.get("action", "")
        if any(k in action for k in ["测试", "试用", "下载", "体验"]) and len(tools) < 5:
            tools.append(
                {
                    "name": it.get("title", "")[:30],
                    "what": it.get("summary", "")[:50],
                    "why_today": it.get("why", ""),
                    "time_est": "约30分钟",
                    "source": it.get("title", ""),
                }
            )
    return {
        "tools_to_test": tools,
        "things_to_watch": [
            {"item": it["title"], "reason": it.get("why", "")}
            for it in items
            if it.get("level") == "S"
        ][:3],
        "research_topics": [],
        "daily_focus": "研究今日 S 级情报并决定测试哪个工具",
    }


def save_today_actions(data: dict):
    os.makedirs(os.path.dirname(ACTIONS_FILE), exist_ok=True)
    with open(ACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"  today_actions.json 已保存")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    # 测试：用现有报告数据
    with open(os.path.join(os.path.dirname(__file__), "data", "latest_report.json"), encoding="utf-8") as f:
        report = json.load(f)
    data = generate_today_actions(report.get("items", []))
    print(json.dumps(data, ensure_ascii=False, indent=1))
