# ============================================================
# 趋势仪表盘：基于历史情报数据统计关键词热度，生成 HTML 图表
# 生成的文件可直接用浏览器打开，无需联网
# ============================================================

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

# 监控的关键词（可自定义）
TREND_KEYWORDS = [
    "AI短剧", "漫剧", "短剧出海", "TikTok", "YourChannel",
    "AI视频", "视频生成", "Sora", "可灵", "即梦", "Runway",
    "AI工具", "插件", "SaaS", "知识付费", "教培",
    "大模型", "多模态", "变现",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "dashboard.html")


def load_history() -> list:
    """加载历史新闻"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("items", [])
    except Exception:
        return []


def compute_trends(items: list, days: int = 30) -> dict:
    """统计每个关键词在每天的出现次数"""
    # 初始化日期范围
    date_counts = defaultdict(lambda: defaultdict(int))
    dates = set()

    for it in items:
        date = it.get("date", "")
        if not date:
            continue
        dates.add(date)
        text = f"{it.get('title', '')} {it.get('summary', '')}"
        for kw in TREND_KEYWORDS:
            if kw in text:
                date_counts[kw][date] += 1

    # 排序日期
    sorted_dates = sorted(dates)
    if len(sorted_dates) > days:
        sorted_dates = sorted_dates[-days:]

    return {
        "dates": sorted_dates,
        "series": {
            kw: [date_counts[kw].get(d, 0) for d in sorted_dates]
            for kw in TREND_KEYWORDS
        },
    }


def build_html(trends: dict, total_items: int) -> str:
    """生成自包含 HTML（内嵌 Chart.js CDN，浏览器打开即用）"""
    dates_json = json.dumps(trends["dates"], ensure_ascii=False)
    series_json = json.dumps(trends["series"], ensure_ascii=False)
    keywords_json = json.dumps(TREND_KEYWORDS, ensure_ascii=False)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 图例在 Python 端生成（避免 f-string 与 JS 模板字符串冲突）
    colors = ["#38bdf8", "#f472b6", "#4ade80", "#facc15", "#fb923c",
              "#a78bfa", "#2dd4bf", "#f87171", "#fbbf24", "#34d399",
              "#60a5fa", "#c084fc", "#fda4af", "#bef264", "#67e8f9",
              "#f9a8d4", "#6ee7b7", "#fcd34d"]
    legend_html = "".join(
        f'<span class="kw" style="color:{colors[i % len(colors)]}">● {kw}</span>'
        for i, kw in enumerate(TREND_KEYWORDS)
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>📡 情报雷达 · 趋势仪表盘</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
         background: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color: #94a3b8; font-size: 13px; margin-bottom: 20px; }}
  .cards {{ display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 16px 20px; flex: 1; min-width: 140px; }}
  .card .num {{ font-size: 28px; font-weight: 700; color: #38bdf8; }}
  .card .label {{ font-size: 13px; color: #94a3b8; margin-top: 4px; }}
  .chart-box {{ background: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 20px; }}
  .chart-box h2 {{ font-size: 15px; margin: 0 0 12px; color: #cbd5e1; }}
  canvas {{ max-height: 360px; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px; font-size: 12px; color: #94a3b8; }}
  .kw {{ background: #334155; padding: 3px 10px; border-radius: 20px; }}
</style>
</head>
<body>
  <h1>📡 情报雷达 · 趋势仪表盘</h1>
  <div class="sub">数据截至 {now} · 基于本地历史情报统计（无需联网）</div>

  <div class="cards">
    <div class="card"><div class="num">{total_items}</div><div class="label">累计情报条数</div></div>
    <div class="card"><div class="num">{len(trends['dates'])}</div><div class="label">覆盖天数</div></div>
    <div class="card"><div class="num">{len(TREND_KEYWORDS)}</div><div class="label">监控关键词</div></div>
  </div>

  <div class="chart-box">
    <h2>📈 关键词热度趋势（近 {len(trends['dates'])} 天）</h2>
    <canvas id="trendChart"></canvas>
    <div class="legend">{legend_html}</div>
  </div>

<script>
const dates = {dates_json};
const series = {series_json};
const keywords = {keywords_json};

const colors = ['#38bdf8','#f472b6','#4ade80','#facc15','#fb923c',
                '#a78bfa','#2dd4bf','#f87171','#fbbf24','#34d399',
                '#60a5fa','#c084fc','#fda4af','#bef264','#67e8f9',
                '#f9a8d4','#6ee7b7','#fcd34d'];

new Chart(document.getElementById('trendChart'), {{
  type: 'line',
  data: {{
    labels: dates,
    datasets: keywords.map((kw, i) => ({{
      label: kw,
      data: series[kw],
      borderColor: colors[i % colors.length],
      backgroundColor: colors[i % colors.length] + '22',
      borderWidth: 2,
      pointRadius: 2,
      tension: 0.3,
      fill: false,
    }}))
  }},
  options: {{
    responsive: true,
    interaction: {{ mode: 'index', intersect: false }},
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{ backgroundColor: '#0f172a', titleColor: '#e2e8f0', bodyColor: '#cbd5e1' }}
    }},
    scales: {{
      x: {{ ticks: {{ color: '#94a3b8', maxTicksLimit: 10 }}, grid: {{ color: '#1e293b' }} }},
      y: {{ beginAtZero: true, ticks: {{ color: '#94a3b8', stepSize: 1 }}, grid: {{ color: '#1e293b' }} }}
    }}
  }}
}});
</script>
</body>
</html>"""


def generate_dashboard() -> str:
    """生成仪表盘 HTML，返回文件路径"""
    items = load_history()
    trends = compute_trends(items)
    html = build_html(trends, len(items))
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"📊 趋势仪表盘已生成: {OUTPUT_FILE}")
    print(f"   累计情报 {len(items)} 条 | 覆盖 {len(trends['dates'])} 天 | 监控 {len(TREND_KEYWORDS)} 个关键词")
    return OUTPUT_FILE


if __name__ == "__main__":
    generate_dashboard()
