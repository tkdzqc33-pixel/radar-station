# ============================================================
# 抓取模块：从 RSS 信源抓取新闻，本地关键词预过滤
# ============================================================

import re
import time

import feedparser
import requests

from config import TIMEOUT, USER_AGENT, MAX_ITEMS_PER_SOURCE, DEBUG
from sources import RSS_SOURCES, FILTER_KEYWORDS_MUST, FILTER_KEYWORDS_EXCLUDE
from api_fetcher import fetch_all_apis


def _headers():
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }


def fetch_rss(url: str, max_items: int = MAX_ITEMS_PER_SOURCE, retries: int = 1) -> list:
    """抓取一个 RSS 源，返回新闻列表（带重试和降频）"""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, headers=_headers(), timeout=TIMEOUT)
            if resp.status_code == 429:
                # 触发限流：短暂等待后重试一次，仍失败则跳过该源
                wait = 2 * (attempt + 1)
                print(f"[fetch_rss] 429 rate-limited {url}, wait {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            break
        except Exception as e:
            if attempt < retries:
                print(f"[fetch_rss] retry {attempt+1} for {url}: {e}")
                time.sleep(2 * (attempt + 1))
            else:
                print(f"[fetch_rss] FAILED {url}: {e}")
                return []
    try:
        feed = feedparser.parse(resp.content)
        items = []
        for entry in feed.entries[:max_items]:
            item = {
                "title": entry.get("title", "").strip(),
                "link": entry.get("link", ""),
                "summary": _clean_summary(entry.get("summary", "")),
                "published": entry.get("published", "") or entry.get("updated", ""),
                "source": feed.feed.get("title", url),
            }
            if item["title"]:
                items.append(item)
        if DEBUG:
            print(f"[fetch_rss] {url} -> {len(items)} items")
        return items
    except Exception as e:
        print(f"[fetch_rss] parse FAILED {url}: {e}")
        return []


def _clean_summary(html_text: str) -> str:
    """去掉 summary 中的 HTML 标签，保留完整内容（不截断）"""
    text = re.sub(r"<[^>]+>", " ", html_text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _passes_filter(title: str, summary: str) -> bool:
    """本地关键词过滤：命中必须词 且 未命中排除词"""
    text = f"{title} {summary}"

    # 排除词优先
    for kw in FILTER_KEYWORDS_EXCLUDE:
        if kw in text:
            return False

    # 必须命中至少一个
    for kw in FILTER_KEYWORDS_MUST:
        if kw in text:
            return True
    return False


def fetch_all() -> list:
    """抓取所有信源，本地过滤 + 去重后返回新闻列表"""
    all_items = []
    seen = set()

    sources = sorted(RSS_SOURCES, key=lambda s: -s.get("weight", 1))
    for src in sources:
        items = fetch_rss(src["url"], src.get("max_items", MAX_ITEMS_PER_SOURCE))
        src_count = 0
        for item in items:
            item["biz_tags"] = src.get("tags", [])
            # 本地关键词过滤
            if not _passes_filter(item["title"], item.get("summary", "")):
                continue
            all_items.append(item)
            src_count += 1
            # 每个信源最多贡献 8 条，防止单一信源刷屏
            if src_count >= 8:
                break
        time.sleep(0.8)  # 礼貌间隔，避免触发限流

    # 追加免费 API 数据源（GitHub 开源趋势 + Hacker News 全球风向）
    print("  [api] 抓取免费 API 数据源...")
    api_items = fetch_all_apis()
    all_items.extend(api_items)

    # 去重（按标题前50字）
    unique = []
    for item in all_items:
        key = item["title"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    if DEBUG:
        print(f"[fetch_all] raw={len(all_items)} unique={len(unique)}")
    return unique


if __name__ == "__main__":
    items = fetch_all()
    print(f"过滤后共 {len(items)} 条")
    for it in items[:20]:
        print(f"- [{it['source']}] {it['title'][:60]}")
