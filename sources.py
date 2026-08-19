# ============================================================
# 信源定义
# 每个信源包含：名称、类型（rss）、URL、业务标签、抓取条数
# ============================================================

RSS_SOURCES = [
    {
        "name": "36氪快讯",
        "type": "rss",
        "url": "https://rsshub.rssforever.com/36kr/newsflashes",
        "tags": ["industry", "ai_tools"],
        "max_items": 25,
        "weight": 5,
    },
    {
        "name": "IT之家",
        "type": "rss",
        "url": "https://www.ithome.com/rss/",
        "tags": ["industry"],
        "max_items": 20,
        "weight": 3,
    },
    {
        "name": "极客公园",
        "type": "rss",
        "url": "https://www.geekpark.net/rss",
        "tags": ["industry", "ai_tools"],
        "max_items": 20,
        "weight": 4,
    },
    {
        "name": "少数派",
        "type": "rss",
        "url": "https://sspai.com/feed",
        "tags": ["ai_tools", "industry"],
        "max_items": 15,
        "weight": 3,
    },
    {
        "name": "雷峰网",
        "type": "rss",
        "url": "https://rsshub.ktachibana.party/leiphone",
        "tags": ["industry", "ai_tools"],
        "max_items": 15,
        "weight": 4,
    },
    {
        "name": "虎嗅资讯",
        "type": "rss",
        "url": "https://rsshub.rssforever.com/huxiu/article",
        "tags": ["industry"],
        "max_items": 15,
        "weight": 3,
    },
]

# 关键词预过滤（本地过滤，不花 API 费用）
# 命中任一关键词的新闻才进入 AI 分析环节
# 分为【必须命中】和【可选命中】两组
FILTER_KEYWORDS_MUST = [
    # AI 视频/内容生产
    "AI视频", "AI 视频", "视频生成", "文生视频", "图生视频", "AI短剧", "AI 短剧",
    "漫剧", "AIGC", "AI动画", "AI 动画",
    # 短剧出海
    "短剧", "出海", "TikTok", "海外市场", "ReelShort", "YourChannel",
    # AI 工具
    "AI工具", "AI 工具", "插件", "SaaS", "AI绘画", "AI 绘画", "智能体", "Agent",
    "大模型", "多模态", "模型",
    # 知识付费/教培
    "知识付费", "教培", "教育", "培训", "课程", "内容创作", "变现",
    # 平台
    "抖音", "快手", "红果", "即梦", "可灵", "Runway", "Sora", "Luma", "Midjourney",
    "Stable Diffusion", "OpenAI", "字节", "剪映",
]

# 这些词命中说明大概率无关，直接排除（避免噪声）
FILTER_KEYWORDS_EXCLUDE = [
    "股票", "基金", "A股", "港股", "楼市", "房地产", "国债", "油价",
    "世界杯", "奥运", "足球", "篮球",
]

# 备用 RSSHub 实例（主实例失败时切换）
BACKUP_RSSHUB_INSTANCES = [
    "https://rsshub.ktachibana.party",
    "https://rsshub.rssforever.com",
]
