# ============================================================
# 分析师晨报：每天生成一段"今日最关键的一件事"深度解读
# 显示在看板顶部 + 推送飞书
# ============================================================

import json
import os

from analyzer import _call_deepseek

BRIEF_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "morning_brief.json")

SYSTEM_PROMPT_BRIEF = """
你是一名深耕 AI 内容出海领域的首席分析师。基于今天的全部情报（含分类/分级/机会/风险标注），
写一份"今日晨报"，要求：

1. 找出今天【最关键的一件事】——对短剧出海/AI工具变现影响最大的那个情报
2. 给出你的【深度判断】——为什么重要、连锁影响、红利窗口期多长
3. 给出【今日行动清单】——3-5 条具体可执行的动作（做内容/试工具/研究平台）
4. 给一个【风险提醒】——今天情报里最该警惕的坑

写作要求：
- 口语化、像资深操盘手给同行发微信语音，不要公文腔
- 控制在 300 字以内
- 不要空话，每条判断都要落到"我能做什么"

输出格式（严格 JSON）：
{
  "top_story": "今天最关键的一件事（一句话）",
  "judgment": "深度判断（100字内）",
  "actions": ["行动1", "行动2", "行动3"],
  "risk_alert": "风险提醒（一句话）",
  "mood": "今日情绪（乐观/谨慎/激进，一句话）"
}
只输出 JSON。"""


def generate_morning_brief(items: list) -> dict:
    """基于今日情报生成分析师晨报"""
    # 优先取 S/A 级，带机会的
    def sort_key(it):
        level_score = {"S": 3, "A": 2}.get(it.get("level"), 1)
        opp_score = 1 if it.get("opportunity") and it["opportunity"] != "无" else 0
        return (level_score, opp_score)

    sorted_items = sorted(items, key=sort_key, reverse=True)

    news_lines = []
    for it in sorted_items[:25]:
        title = it.get("title", "")[:60]
        why = it.get("why", "")
        opp = it.get("opportunity", "")
        line = f"[{it.get('level','B')}] {title}"
        if why:
            line += f" | {why}"
        if opp and opp != "无":
            line += f" | 机会:{opp}"
        news_lines.append(line)
    news_text = "\n".join(news_lines) or "（今日无重要情报）"

    user_prompt = f"今日情报如下：\n{news_text}\n\n请生成今日分析师晨报。"
    raw = _call_deepseek(SYSTEM_PROMPT_BRIEF, user_prompt, max_tokens=2000)

    from analyzer import _parse_json_object

    return _parse_json_object(raw)


def save_morning_brief(data: dict):
    """保存晨报到文件（供看板读取）"""
    os.makedirs(os.path.dirname(BRIEF_FILE), exist_ok=True)
    with open(BRIEF_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"  morning_brief.json 已保存")


def format_morning_brief(data: dict) -> str:
    """格式化为可读文本（飞书推送）"""
    if not data:
        return "📊 今日晨报：暂无数据"
    lines = [
        "📊 分析师晨报 · 今日最关键的一件事",
        "=" * 30,
        f"\n🔝 {data.get('top_story', '')}",
    ]
    if data.get("judgment"):
        lines.append(f"\n🧠 判断：{data['judgment']}")
    actions = data.get("actions", [])
    if actions:
        lines.append("\n✅ 今日行动清单：")
        for i, a in enumerate(actions, 1):
            lines.append(f"  {i}. {a}")
    if data.get("risk_alert"):
        lines.append(f"\n⚠️ 风险提醒：{data['risk_alert']}")
    if data.get("mood"):
        lines.append(f"\n🎭 今日情绪：{data['mood']}")
    return "\n".join(lines)
