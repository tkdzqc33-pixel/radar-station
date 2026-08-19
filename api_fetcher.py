# ============================================================
# 免费 API 数据源 v2
# - GitHub 仓库搜索：AI 视频/短剧开源工具趋势
# - GitHub Releases：追踪具体工具版本更新（无需 key）
# - Hacker News：全球 AI 技术风向
# - Product Hunt（可选，需在 config.py 填 PRODUCT_HUNT_TOKEN）
# - GNews（可选，需在 config.py 填 GNEWS_API_KEY）
# ============================================================

import time

import requests

from config import TIMEOUT, USER_AGENT, DEBUG
from sources import FILTER_KEYWORDS_MUST, FILTER_KEYWORDS_EXCLUDE

# ---------- 配置（从 config 读取，可选）----------
try:
    from config import PRODUCT_HUNT_TOKEN, PRODUCT_HUNT_CLIENT_ID, PRODUCT_HUNT_CLIENT_SECRET, GNEWS_API_KEY
except ImportError:
    PRODUCT_HUNT_TOKEN = ""
    PRODUCT_HUNT_CLIENT_ID = ""
    PRODUCT_HUNT_CLIENT_SECRET = ""
    GNEWS_API_KEY = ""

# 追踪的 AI 视频/短剧工具仓库（releases 监控）
TRACKED_REPOS = [
    ("Open-Sora", "hpcaitech/Open-Sora"),
    ("Toonflow短剧工具", "HBAI-Ltd/Toonflow-app"),
    ("LivePortrait", "KwaiVGI/LivePortrait"),
    ("ComfyUI", "comfyanonymous/ComfyUI"),
    ("MoneyPrinter", "harry0703/MoneyPrinterTurbo"),
]

# GitHub 搜索关键词
GITHUB_SEARCH_QUERIES = [
    ("AI视频工具", "AI video generation tool"),
    ("短剧/AI动画", "short drama AI animated"),
    ("AI绘画", "AI image generation"),
    ("Sora/可灵工具", "sora video tool OR kling"),
    ("视频工作流", "AI video workflow pipeline"),
]

# Hacker News 搜索关键词
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
            time.sleep(1)
        except Exception as e:
            if DEBUG:
                print(f"[github] {label} 失败: {e}")
    return items


def fetch_github_releases() -> list:
    """GitHub Releases：追踪关键工具的版本更新（新版本=能力升级信号）"""
    items = []
    for label, repo in TRACKED_REPOS:
        try:
            url = f"https://api.github.com/repos/{repo}/releases"
            resp = requests.get(
                url,
                params={"per_page": 2},
                headers={**_headers(), "Accept": "application/vnd.github+json"},
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                continue
            releases = resp.json()
            if not isinstance(releases, list) or not releases:
                continue
            latest = releases[0]
            body = (latest.get("body") or "")[:200]
            items.append(
                {
                    "title": f"[版本更新] {label} {latest.get('tag_name', '')}: {latest.get('name', '')[:50]}",
                    "link": latest.get("html_url", ""),
                    "summary": f"{latest.get('published_at', '')[:10]} 发布 | {body}",
                    "source": "GitHub版本",
                    "biz_tags": ["ai_tools"],
                }
            )
            time.sleep(0.8)
        except Exception as e:
            if DEBUG:
                print(f"[release] {repo} 失败: {e}")
    return items


def fetch_hn_trending() -> list:
    """Hacker News Algolia：全球 AI 技术风向"""
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


def _get_product_hunt_token() -> str:
    """获取 Product Hunt token：优先用已配置 token，否则用 Client ID/Secret 换取"""
    if PRODUCT_HUNT_TOKEN:
        return PRODUCT_HUNT_TOKEN
    if PRODUCT_HUNT_CLIENT_ID and PRODUCT_HUNT_CLIENT_SECRET:
        try:
            resp = requests.post(
                "https://api.producthunt.com/v2/oauth/token",
                json={
                    "client_id": PRODUCT_HUNT_CLIENT_ID,
                    "client_secret": PRODUCT_HUNT_CLIENT_SECRET,
                    "grant_type": "client_credentials",
                },
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=TIMEOUT,
            )
            if resp.status_code == 200:
                return resp.json().get("access_token", "")
        except Exception as e:
            if DEBUG:
                print(f"[ph] token换取失败: {e}")
    return ""


def fetch_product_hunt() -> list:
    """Product Hunt：新产品首发（自动换 token，未配置则跳过）"""
    token = _get_product_hunt_token()
    if not token:
        return []
    items = []
    try:
        query = '{ posts(order: NEWEST, first: 12) { edges { node { name tagline url description } } } }'
        resp = requests.post(
            "https://api.producthunt.com/v2/api/graphql",
            json={"query": query},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=TIMEOUT,
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        for edge in data.get("data", {}).get("posts", {}).get("edges", []):
            node = edge.get("node", {})
            name = node.get("name", "")
            tagline = node.get("tagline", "")
            desc = node.get("description", "")
            combined = f"{name} {tagline} {desc}"
            # PH 新品源：只收 AI/内容创作/视频/教育相关（精准匹配）
            lower = combined.lower()
            ai_kw = ["ai ", "ai-", " a.i", "artificial intelligence", "gpt", "llm", "diffusion", "video", "image", "photo", "story", "script", "drama", "animation", "content", "creator", "generate", "text to", "prompt", "voice", "audio", "design", "learning", "course", "education"]
            if not any(k in lower for k in ai_kw):
                continue
            items.append(
                {
                    "title": f"[新品] {name}: {tagline[:60]}",
                    "link": node.get("url", ""),
                    "summary": f"{desc[:200]}",
                    "source": "Product Hunt",
                    "biz_tags": ["ai_tools", "industry"],
                }
            )
    except Exception as e:
        if DEBUG:
            print(f"[ph] 失败: {e}")
    return items


def fetch_gnews() -> list:
    """GNews：全球新闻搜索（需 API key，未配置则跳过）"""
    if not GNEWS_API_KEY:
        return []
    items = []
    queries = ["AI 短剧", "AI video", "short drama"]
    for q in queries:
        try:
            resp = requests.get(
                "https://gnews.io/api/v4/search",
                params={"q": q, "lang": "zh", "max": 5, "apikey": GNEWS_API_KEY},
                timeout=TIMEOUT,
            )
            if resp.status_code != 200:
                continue
            data = resp.json()
            for article in data.get("articles", []):
                title = article.get("title", "")
                desc = article.get("description", "")
                if not _passes_filter(title, desc):
                    continue
                items.append(
                    {
                        "title": f"[新闻] {title[:90]}",
                        "link": article.get("url", ""),
                        "summary": f"{article.get('publishedAt', '')[:10]} | {desc[:200]}",
                        "source": "GNews",
                        "biz_tags": ["industry"],
                    }
                )
            time.sleep(1)
        except Exception as e:
            if DEBUG:
                print(f"[gnews] {q} 失败: {e}")
    return items


def fetch_all_apis() -> list:
    """抓取所有免费 API 数据源"""
    items = []
    items.extend(fetch_github_trending())
    items.extend(fetch_github_releases())
    items.extend(fetch_hn_trending())
    items.extend(fetch_product_hunt())
    items.extend(fetch_gnews())

    seen = set()
    unique = []
    for it in items:
        key = it["title"][:50]
        if key not in seen:
            seen.add(key)
            unique.append(it)
    if DEBUG:
        print(f"[api] total {len(unique)} items")
    return unique


if __name__ == "__main__":
    items = fetch_all_apis()
    print(f"API 数据源抓到 {len(items)} 条")
    for it in items[:15]:
        print(f"- [{it['source']}] {it['title'][:70]}")
