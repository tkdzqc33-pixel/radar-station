# ============================================================
# 选题生成器 v2：基于分析师分析（机会/风险字段）产出高质量选题
# ============================================================

from config import IDEA_COUNT
from analyzer import _call_deepseek, _parse_json_array

SYSTEM_PROMPT_IDEAS = """
你是一名深耕 AI 内容出海领域的选题策划总监，同时是资深操盘手。我的业务有三个板块：
1. 短剧出海（核心）：用 AI 制作短剧/漫剧，投放到海外平台赚美元
2. AI 工具/插件：用 AI 开发能上架出售的技能、插件、小工具
3. 知识付费：教别人 AI 内容创作与变现

我给你近期情报（含分析师标注的机会/风险），请产出 {count} 个高质量选题。

选题要求：
- 必须结合情报中的【机会】和【趋势】，不是凭空想
- 每个选题要能直接指导我下一步行动（做内容/做产品/做课程）
- 优先选"红利窗口期"的机会（平台扶持、工具突破、新赛道刚起）

每个选题输出（严格 JSON 数组）：
[
  {{
    "business": "short_drama 或 ai_tools 或 knowledge",
    "title": "选题标题（有吸引力，可直接用）",
    "why": "为什么现在做（结合情报中的机会/趋势）",
    "how": "具体怎么做（步骤，2-3 句，可执行）",
    "roi": "预期变现方式或收益路径",
    "difficulty": "难度：低/中/高",
    "urgency": "紧迫度：高（红利窗口期，尽快做）/中/低",
    "evidence": "支撑这个选题的情报标题（从提供的情报里选1条）"
  }}
]
只输出 JSON。"""


def generate_ideas(items: list, count: int = None) -> list:
    """基于分析师分析过的情报生成选题（含机会/风险依据）"""
    count = count or IDEA_COUNT

    # 取情报（含分析字段），S/A 级优先、带机会的优先
    def sort_key(it):
        level_score = {"S": 3, "A": 2, "B": 1}.get(it.get("level"), 0)
        opp_score = 1 if it.get("opportunity") and it["opportunity"] != "无" else 0
        return (level_score, opp_score)

    sorted_items = sorted(items, key=sort_key, reverse=True)
    news_lines = []
    for it in sorted_items[:30]:
        title = it.get("title", "")[:60]
        opp = it.get("opportunity", "")
        risk = it.get("risk", "")
        line = f"- {title}"
        if opp and opp != "无":
            line += f" | 机会: {opp}"
        if risk and risk != "无":
            line += f" | 风险: {risk}"
        news_lines.append(line)
    news_text = "\n".join(news_lines) or "（暂无情报，基于你的业务直接策划）"

    user_prompt = (
        f"近期情报（含分析师标注）如下：\n{news_text}\n\n"
        f"请基于这些情报，产出 {count} 个高质量选题方向。"
    )
    raw = _call_deepseek(
        SYSTEM_PROMPT_IDEAS.format(count=count), user_prompt, max_tokens=5000
    )
    ideas = _parse_json_array(raw)
    return ideas


def format_ideas(ideas: list) -> str:
    """把选题列表格式化为可读文本（用于飞书推送）"""
    biz_label = {
        "short_drama": "🎬 短剧出海",
        "ai_tools": "🛠️ AI工具",
        "knowledge": "🎓 知识付费",
    }
    lines = ["💡 情报雷达 · 选题生成器 v2", "=" * 30]
    if not ideas:
        lines.append("\n（本次未生成选题，可稍后重试）")
        return "\n".join(lines)

    for i, idea in enumerate(ideas, 1):
        biz = biz_label.get(idea.get("business", ""), idea.get("business", "📄 其他"))
        lines.append(f"\n{i}. {biz}")
        lines.append(f"   📌 {idea.get('title', '')}")
        if idea.get("why"):
            lines.append(f"   💡 {idea['why']}")
        if idea.get("how"):
            lines.append(f"   🔧 {idea['how']}")
        if idea.get("roi"):
            lines.append(f"   💰 {idea['roi']}")
        urgency = idea.get("urgency", "")
        diff = idea.get("difficulty", "")
        meta = []
        if urgency:
            meta.append(f"紧迫度:{urgency}")
        if diff:
            meta.append(f"难度:{diff}")
        if meta:
            lines.append(f"   📊 {' | '.join(meta)}")
        if idea.get("evidence"):
            lines.append(f"   📎 依据: {idea['evidence']}")

    return "\n".join(lines)
