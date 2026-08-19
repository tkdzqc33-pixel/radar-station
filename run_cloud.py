# ============================================================
# 云端构建脚本（GitHub Actions 定时运行）
# 流程：抓取 → AI分析 → 生成看板数据(stats.json) + 语音(briefing.mp3)
# 产物提交到仓库，GitHub Pages 自动更新
# ============================================================

import json
import os
import sys
from datetime import datetime

# 确保能 import 本目录模块
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fetcher import fetch_all
from analyzer import analyze_daily
from reporter import format_daily_report
from stats import build_all_stats
from speaker import generate_speech, build_briefing_text
from morning_brief import generate_morning_brief, save_morning_brief

DATA_DIR = os.path.join(BASE_DIR, "data")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
BRIEFING_FILE = os.path.join(DATA_DIR, "briefing.mp3")
LATEST_REPORT_FILE = os.path.join(DATA_DIR, "latest_report.json")
ICONS_DIR = os.path.join(DATA_DIR, "icons")


def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ICONS_DIR, exist_ok=True)


def write_pwa_files():
    """生成 PWA 所需静态文件（manifest + sw.js），云端无后端也要支持添加到主屏幕"""
    manifest = {
        "name": "AI 情报雷达站",
        "short_name": "雷达站",
        "description": "你的 AI 情报雷达站：短剧出海/AI工具/知识付费 实时情报",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "background_color": "#050505",
        "theme_color": "#CCFF00",
        "orientation": "portrait",
        "icons": [
            {"src": "./data/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "./data/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    with open(os.path.join(BASE_DIR, "manifest.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)

    sw = """
const CACHE_NAME = 'radar-cloud-v1';
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(['./', './data/stats.json'])));
  self.skipWaiting();
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((res) => {
      if (res.ok && !e.request.url.includes('/data/')) {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match('./')))
  );
});
"""
    with open(os.path.join(BASE_DIR, "sw.js"), "w", encoding="utf-8") as f:
        f.write(sw)
    print("  manifest.webmanifest + sw.js 已生成")


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("items", [])
        except Exception:
            pass
    return []


def save_history(items: list):
    history = load_history()
    seen = {i["title"][:50] for i in history}
    for it in items:
        key = it["title"][:50]
        if key not in seen:
            history.append(
                {
                    "title": it["title"],
                    "link": it.get("link", ""),
                    "summary": it.get("summary", "")[:2000],
                    "source": it.get("source", ""),
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "category": it.get("category", "other"),
                    "level": it.get("level", "B"),
                }
            )
    history = history[-3000:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"items": history}, f, ensure_ascii=False, indent=1)


def build():
    ensure_dirs()
    print("📡 云端构建开始")

    # 1. 抓取
    print("→ 抓取新闻...")
    items = fetch_all()
    print(f"  抓取到 {len(items)} 条")

    # 2. AI 分析（需要 DEEPSEEK_API_KEY 环境变量）
    analyzed = []
    if items:
        print("→ AI 分析...")
        analyzed = analyze_daily(items)
        print(f"  分析完成 {len(analyzed)} 条")
    else:
        print("  ⚠️ 未抓到新闻，使用历史数据")

    # 3. 保存历史 + 写 latest_report.json（供 stats 生成看板数据）
    if analyzed:
        save_history(analyzed)
        with open(LATEST_REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "report_text": format_daily_report(analyzed),
                    "items": analyzed,
                },
                f,
                ensure_ascii=False,
                indent=1,
            )
        print(f"  latest_report.json: {len(analyzed)} 条")

    # 4. 生成 stats.json（看板数据）
    print("→ 生成 stats.json...")
    stats_data = build_all_stats()
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats_data, f, ensure_ascii=False, indent=1)
    print(f"  stats.json: {os.path.getsize(STATS_FILE)} bytes")

    report_items = stats_data.get("report_items", [])

    # 4.5 生成分析师晨报
    print("→ 生成分析师晨报...")
    if report_items:
        try:
            brief = generate_morning_brief(report_items)
            save_morning_brief(brief)
        except Exception as e:
            print(f"  ⚠️ 晨报生成失败: {e}")
    else:
        print("  ⚠️ 无简报，跳过晨报")

    # 5. 生成语音简报（晓晓）
    print("→ 生成语音简报...")
    if report_items:
        try:
            text = build_briefing_text(report_items)
            mp3 = generate_speech(text)
            # 复制为固定的 briefing.mp3
            import shutil

            shutil.copy(mp3, BRIEFING_FILE)
            print(f"  briefing.mp3: {os.path.getsize(BRIEFING_FILE)} bytes")
        except Exception as e:
            print(f"  ⚠️ 语音生成失败: {e}")
    else:
        print("  ⚠️ 无简报，跳过语音生成")

    # 6. 图标 + PWA 文件
    print("→ 检查图标...")
    if not os.path.exists(os.path.join(ICONS_DIR, "icon-192.png")):
        try:
            from icon_gen import generate_icons

            generate_icons(ICONS_DIR)
        except Exception as e:
            print(f"  ⚠️ 图标生成失败: {e}")

    write_pwa_files()

    print("✅ 云端构建完成")


if __name__ == "__main__":
    build()
