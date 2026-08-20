# ============================================================
# 数据统计模块：为可视化看板提供统计数据
#   - 今日 vs 昨日对比
#   - 关键词热度变化（上升/下降）
#   - 业务分类分布
# ============================================================

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
LATEST_REPORT_FILE = os.path.join(DATA_DIR, "latest_report.json")
MORNING_BRIEF_FILE = os.path.join(DATA_DIR, "morning_brief.json")
TODAY_ACTIONS_FILE = os.path.join(DATA_DIR, "today_actions.json")

# 与 dashboard.py 保持一致的关键词
TREND_KEYWORDS = [
    "AI短剧", "漫剧", "短剧出海", "TikTok", "YourChannel",
    "AI视频", "视频生成", "Sora", "可灵", "即梦", "Runway",
    "AI工具", "插件", "SaaS", "知识付费", "教培",
    "大模型", "多模态", "变现",
]


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("items", [])
    except Exception:
        return []


def load_report() -> dict:
    if os.path.exists(LATEST_REPORT_FILE):
        try:
            with open(LATEST_REPORT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"items": [], "date": ""}

def load_today_actions() -> dict:
    """读取今日行动清单"""
    if os.path.exists(TODAY_ACTIONS_FILE):
        try:
            with open(TODAY_ACTIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def load_morning_brief() -> dict:
    """读取分析师晨报"""
    if os.path.exists(MORNING_BRIEF_FILE):
        try:
            with open(MORNING_BRIEF_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _date_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _last_n_days(n: int) -> list:
    """返回最近 n 天的日期列表（含今天）"""
    today = datetime.now()
    return [_date_key(today - timedelta(days=i)) for i in range(n - 1, -1, -1)]


def compute_keyword_trends(items: list, days: int = 14) -> dict:
    """统计每个关键词在每天的出现次数（返回最近 days 天）"""
    date_counts = defaultdict(lambda: defaultdict(int))
    for it in items:
        date = it.get("date", "")
        if not date:
            continue
        text = f"{it.get('title', '')} {it.get('summary', '')}"
        for kw in TREND_KEYWORDS:
            if kw in text:
                date_counts[kw][date] += 1

    dates = _last_n_days(days)
    series = {}
    for kw in TREND_KEYWORDS:
        series[kw] = [date_counts[kw].get(d, 0) for d in dates]
    return {"dates": dates, "series": series}


def compute_keyword_changes(items: list) -> list:
    """计算每个关键词 今日 vs 昨日 的变化，返回升降列表"""
    today = _date_key(datetime.now())
    yesterday = _date_key(datetime.now() - timedelta(days=1))

    counts = {kw: {"today": 0, "yesterday": 0} for kw in TREND_KEYWORDS}
    for it in items:
        date = it.get("date", "")
        if date == today:
            key = "today"
        elif date == yesterday:
            key = "yesterday"
        else:
            continue
        text = f"{it.get('title', '')} {it.get('summary', '')}"
        for kw in TREND_KEYWORDS:
            if kw in text:
                counts[kw][key] += 1

    changes = []
    for kw in TREND_KEYWORDS:
        t, y = counts[kw]["today"], counts[kw]["yesterday"]
        if t == 0 and y == 0:
            continue
        if y == 0:
            pct = 100.0 if t > 0 else 0.0
            direction = "up" if t > 0 else "flat"
        else:
            pct = round((t - y) / y * 100, 1)
            direction = "up" if pct > 0 else ("down" if pct < 0 else "flat")
        changes.append(
            {
                "keyword": kw,
                "today": t,
                "yesterday": y,
                "pct": pct,
                "direction": direction,
            }
        )
    # 按今日热度排序，最热的在前
    changes.sort(key=lambda c: -c["today"])
    return changes


def _guess_category(item: dict) -> str:
    """对缺少 category 的历史数据，用关键词规则推断分类"""
    cat = item.get("category")
    if cat and cat != "other":
        return cat
    text = f"{item.get('title', '')} {item.get('summary', '')}"
    if any(k in text for k in ["短剧", "漫剧", "出海", "TikTok", "YourChannel", "ReelShort"]):
        return "short_drama"
    if any(k in text for k in ["AI工具", "插件", "SaaS", "AI绘画", "视频生成", "大模型", "智能体", "Agent"]):
        return "ai_tools"
    return "other"


def compute_category_distribution(items: list) -> dict:
    """统计最近 7 天的业务分类分布"""
    week_ago = _date_key(datetime.now() - timedelta(days=7))
    dist = defaultdict(int)
    for it in items:
        if it.get("date", "") < week_ago:
            continue
        dist[_guess_category(it)] += 1
    return dict(dist)


def compute_daily_counts(items: list, days: int = 14) -> list:
    """统计最近 days 天每天的情报总数（用于总趋势图）"""
    date_counts = defaultdict(int)
    for it in items:
        date = it.get("date", "")
        if date:
            date_counts[date] += 1
    dates = _last_n_days(days)
    return {"dates": dates, "counts": [date_counts.get(d, 0) for d in dates]}


def _build_speech_text(items: list) -> str:
    """生成语音播报文字稿（与 speaker.py 保持一致，供页面展示对照）"""
    try:
        from speaker import build_briefing_text

        return build_briefing_text(items)
    except Exception:
        return ""


def build_all_stats() -> dict:
    """组装看板需要的全部统计"""
    items = load_history()
    report = load_report()

    today = _date_key(datetime.now())
    yesterday = _date_key(datetime.now() - timedelta(days=1))

    today_items = len([i for i in items if i.get("date") == today])
    yesterday_items = len([i for i in items if i.get("date") == yesterday])

    # 今日 vs 昨日总情报变化
    if yesterday_items == 0:
        total_pct = 100.0 if today_items > 0 else 0.0
        total_dir = "up" if today_items > 0 else "flat"
    else:
        total_pct = round((today_items - yesterday_items) / yesterday_items * 100, 1)
        total_dir = "up" if total_pct > 0 else ("down" if total_pct < 0 else "flat")

    report_items = report.get("items", [])
    s_count = len([i for i in report_items if i.get("level") == "S"])
    a_count = len([i for i in report_items if i.get("level") == "A"])

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "today": today,
        "yesterday": yesterday,
        "summary": {
            "today_items": today_items,
            "yesterday_items": yesterday_items,
            "total_pct": total_pct,
            "total_dir": total_dir,
            "s_count": s_count,
            "a_count": a_count,
            "total_history": len(items),
            "report_date": report.get("date", "—"),
        },
        "keyword_trends": compute_keyword_trends(items),
        "keyword_changes": compute_keyword_changes(items),
        "category_distribution": compute_category_distribution(items),
        "daily_counts": compute_daily_counts(items),
        "report_items": report_items,
        "morning_brief": load_morning_brief(),
        "speech_text": _build_speech_text(report_items),
        "today_actions": load_today_actions(),
    }


if __name__ == "__main__":
    import json as _json

    stats = build_all_stats()
    print(_json.dumps(stats["summary"], ensure_ascii=False, indent=1))
    print("\n关键词升降（前10）:")
    for c in stats["keyword_changes"][:10]:
        arrow = "🔺" if c["direction"] == "up" else ("🔻" if c["direction"] == "down" else "➖")
        print(f"  {arrow} {c['keyword']}: 今日{c['today']} 昨日{c['yesterday']} ({c['pct']:+.1f}%)")
