# ============================================================
# 免费 API 数据源（结构化、实时、精准）
# - GitHub API：追踪 AI 视频/短剧工具开源趋势
# - Hacker News Algolia：全球 AI 技术风向（英文，领先国内媒体）
# - Product Hunt（可选，需 token）
# 全部免费，无需 API key（GitHub 未认证有速率限制但够用）
# ============================================================

import re
import time

import requests

from config import TIMEOUT, USER_AGENT, DEBUG
from sources import FILTER_KEYWORDS_MUST, FILTER_KEYWORDS_EXCLUDE

# GitHub 搜索关键词（追踪 AI 工具/短剧开源生态）
GITHUB_SEARCH_QUERIES = [
    ("AI视频工具", "AI video generation tool"),
    ("短剧/AI动画", "short drama AI animated"),
    ("AI绘画", "AI image generation"),
    ("Sora/可灵工具", "sora video tool OR kling"),
    ("视频工作流", "AI video workflow pipeline"),
]

# Hacker News 搜索关键词（全球 AI 风向，英文）
HN_SEARCH_QUERIES = [
    "AI video generation",
    "short drama",
    "text to video",
    "Sora",
    "AI film",
]


def _headers():
    return {"User-Agent": "radar-station-intel/1.0"}


def _passes_filter(title: str, summary: str) -> bool:
    text = f"{title} {summary}"
    for kw in FILTER_KEYWORDS_EXCLUDE:
        if kw in text:
            return False
    for kw in FILTER_KEYWORDS_MUST:
        if kw in text:
            return True
    return False


def fetch_github_trending() -> list:
    """GitHub 仓库搜索：发现 AI 视频/短剧工具开源项目"""
    items = []
    for label, query in GITHUB_SEARCH_QUERIES:
        try:
            url = "https://api.github.com/search/repositories"
            resp = requests.get(
                url,
                params={"q": query, "sort": "stars", "per_page": 8},
                headers={**_headers(), "Accept": "application/vnd.github+json"},
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for repo in data.get("items", []):
                desc = repo.get("description") or ""
                title = repo["full_name"]
                # 组合标题和描述用于过滤
                combined = f"{title} {desc}"
                if not _passes_filter(combined, desc):
                    continue
                items.append(
                    {
                        "title": f"[GitHub] {title}: {desc[:80]}" if desc else f"[GitHub] {title}",
                        "link": repo.get("html_url", ""),
                        "summary": f"⭐{repo.get('stargazers_count', 0)}星 | 语言:{repo.get('language') or '未知'} | 更新:{repo.get('updated_at', '')[:10]} | {desc[:200]}",
                        "source": "GitHub开源",
                        "biz_tags": ["ai_tools"],
                    }
                )
            time.sleep(1)  # GitHub 速率限制保护
        except Exception as e:
            if DEBUG:
                print(f"[github] {label} 失败: {e}")
    return items


def fetch_hn_trending() -> list:
    """Hacker News Algolia：全球 AI 技术风向（领先国内媒体数天）"""
    items = []
    for query in HN_SEARCH_QUERIES:
        try:
            url = "https://hn.algolia.com/api/v1/search"
            resp = requests.get(
                url,
                params={"query": query, "tags": "story", "hitsPerPage": 8},
                headers=_headers(),
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for hit in data.get("hits", []):
                title = hit.get("title") or ""
                url_text = hit.get("url") or ""
                story_text = hit.get("story_text") or ""
                combined = f"{title} {url_text}"
                if not _passes_filter(combined, story_text):
                    continue
                points = hit.get("points", 0)
                # 低分过滤：至少 20 分才值得看
                if points < 20:
                    continue
                items.append(
                    {
                        "title": f"[HN] {title[:90]}",
                        "link": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                        "summary": f"👍{points}分 | {hit.get('num_comments', 0)}评论 | {hit.get('created_at', '')[:10]} | {story_text[:200]}",
                        "source": "Hacker News",
                        "biz_tags": ["industry", "ai_tools"],
                    }
                )
            time.sleep(1)
        except Exception as e:
            if DEBUG:
                print(f"[hn] {query} 失败: {e}")
    return items


def fetch_all_apis() -> list:
    """抓取所有免费 API 数据源"""
    items = []
    items.extend(fetch_github_trending())
    items.extend(fetch_hn_trending())

    # 去重
    seen = set()
    unique = []
    for it in items:
        key = it["title"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(it)
    if DEBUG:
        print(f"[api] total {len(unique)} items (github+hn)")
    return unique


if __name__ == "__main__":
    items = fetch_all_apis()
    print(f"API 数据源抓到 {len(items)} 条")
    for it in items[:15]:
        print(f"- [{it['source']}] {it['title'][:70]}")
