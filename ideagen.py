# ============================================================
# 选题生成器：基于近期情报 + 业务背景，AI 产出可执行的选题
# ============================================================

from config import IDEA_COUNT
from analyzer import _call_deepseek

SYSTEM_PROMPT_IDEAS = """
你是一名深耕 AI 内容领域的选题策划总监。我的业务有三个板块：
1. 短剧出海：用 AI 制作短剧/漫剧，投放到海外平台（YourChannel、TikTok）赚美元
2. AI 工具/插件：用 AI 开发能上架出售的技能、插件、小工具
3. 知识付费：教别人 AI 内容创作与变现（线上课+线下课）

基于我提供的近期情报，请产出 {count} 个高质量的选题方向。
选题要：紧跟情报里的趋势、符合我的业务、具体可执行、有变现想象力。

每个选题输出（严格 JSON 数组）：
[
  {{
    "business": "short_drama 或 ai_tools 或 knowledge",  // 属于哪个业务
    "title": "选题标题（有吸引力，可直接用）",
    "why": "为什么现在做这个（结合情报中的趋势，一句话）",
    "how": "具体怎么做（步骤，2-3 句）",
    "roi": "预期变现方式或收益路径（一句话）",
    "difficulty": "难度：低/中/高"
  }}
]
只输出 JSON。"""


def generate_ideas(items: list, count: int = None) -> list:
    """基于近期新闻情报生成选题"""
    count = count or IDEA_COUNT

    # 取近期情报的标题，作为选题依据
    news_lines = []
    for it in items[:40]:
        title = it.get("title", "")[:80]
        if title:
            news_lines.append(f"- {title}")
    news_text = "\n".join(news_lines) or "（暂无情报，基于你的业务直接策划）"

    user_prompt = (
        f"近期情报如下：\n{news_text}\n\n"
        f"请基于这些情报，产出 {count} 个选题方向。"
    )
    raw = _call_deepseek(
        SYSTEM_PROMPT_IDEAS.format(count=count), user_prompt, max_tokens=4000
    )

    # 复用 analyzer 的 JSON 数组解析
    from analyzer import _parse_json_array

    ideas = _parse_json_array(raw)
    return ideas


def format_ideas(ideas: list) -> str:
    """把选题列表格式化为可读文本（用于飞书推送）"""
    biz_label = {
        "short_drama": "🎬 短剧出海",
        "ai_tools": "🛠️ AI工具",
        "knowledge": "🎓 知识付费",
    }
    lines = ["💡 情报雷达 · 选题生成器", "=" * 30]
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
        diff = idea.get("difficulty", "")
        if diff:
            lines.append(f"   📊 难度: {diff}")

    return "\n".join(lines)
