# ============================================================
# 报告生成模块：把分析结果格式化为可读的日报/周报文本
# ============================================================

from datetime import datetime

# 分级 emoji
LEVEL_EMOJI = {"S": "🚨", "A": "🔶", "B": "🔹"}
CATEGORY_LABEL = {
    "short_drama": "🎬 短剧出海",
    "ai_tools": "🛠️ AI工具",
    "industry": "📡 行业动态",
    "other": "📄 其他",
}


def format_daily_report(items: list) -> str:
    """生成每日简报文本（用于飞书推送）"""
    today = datetime.now().strftime("%Y-%m-%d")

    s_items = [i for i in items if i.get("level") == "S"]
    a_items = [i for i in items if i.get("level") == "A"]
    b_items = [i for i in items if i.get("level") == "B"]

    lines = [
        f"📡 情报雷达 · 每日简报 {today}",
        f"今日情报 {len(items)} 条 | 🚨S级 {len(s_items)} | 🔶A级 {len(a_items)}",
        "=" * 30,
    ]

    if s_items:
        lines.append("\n🚨 【S级 · 立刻行动】")
        for it in s_items:
            lines.append(_format_item(it))
    if a_items:
        lines.append("\n🔶 【A级 · 今天处理】")
        for it in a_items:
            lines.append(_format_item(it))
    if b_items:
        lines.append("\n🔹 【B级 · 了解即可】")
        for it in b_items:
            lines.append(_format_item(it, show_action=False))

    if not items:
        lines.append("\n今日未抓到有效情报（可能是网络或信源问题）")

    return "\n".join(lines)


def _format_item(it: dict, show_action: bool = True) -> str:
    """格式化单条新闻（分析师版：含机会/风险）"""
    cat = CATEGORY_LABEL.get(it.get("category", "other"), it.get("category", ""))
    title = it.get("title", "")
    why = it.get("why", "")
    action = it.get("action", "")
    opportunity = it.get("opportunity", "")
    risk = it.get("risk", "")
    source = it.get("source", "")
    link = it.get("link", "")

    lines = [f"\n▎{cat} | {title}"]
    if why:
        lines.append(f"   💡 {why}")
    if show_action and action:
        lines.append(f"   👉 {action}")
    if opportunity and opportunity != "无":
        lines.append(f"   💰 机会: {opportunity}")
    if risk and risk != "无":
        lines.append(f"   ⚠️ 风险: {risk}")
    lines.append(f"   📎 {source}")
    if link and link.startswith("http"):
        lines.append(f"   🔗 {link}")
    return "\n".join(lines)


def format_weekly_report(data: dict) -> str:
    """生成周报文本"""
    end = datetime.now().strftime("%Y-%m-%d")
    lines = [f"📊 情报雷达 · 每周深度报告（截止 {end}）", "=" * 30]

    changes = data.get("key_changes", [])
    if changes:
        lines.append("\n🔑 【本周关键变化】")
        for c in changes:
            lines.append(f"▎{c.get('title', '')}")
            if c.get("summary"):
                lines.append(f"   📝 {c['summary']}")
            if c.get("impact"):
                lines.append(f"   ⚡ 影响: {c['impact']}")

    opps = data.get("opportunities", [])
    if opps:
        lines.append("\n💰 【机会清单】")
        for o in opps:
            lines.append(f"▎{o.get('title', '')}")
            if o.get("why"):
                lines.append(f"   ❓ 为什么: {o['why']}")
            if o.get("action"):
                lines.append(f"   👉 行动: {o['action']}")

    risks = data.get("risks", [])
    if risks:
        lines.append("\n⚠️ 【风险提示】")
        for r in risks:
            lines.append(f"▎{r.get('title', '')}")
            if r.get("mitigation"):
                lines.append(f"   🛡️ 应对: {r['mitigation']}")

    focus = data.get("focus", "")
    if focus:
        lines.append(f"\n🎯 【下周聚焦】\n{focus}")

    return "\n".join(lines)
