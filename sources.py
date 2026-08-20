# ============================================================
# 信源定义 v2（垂直化升级）
# 覆盖：短剧出海 / AI工具 / AI视频生成 / 行业动态 / 知识付费
# ============================================================

RSS_SOURCES = [
    # ---------- 短剧出海垂直信源 ----------
    {
        "name": "白鲸出海",
        "type": "rss",
        "url": "https://www.baijing.cn/feed",
        "tags": ["short_drama", "industry"],
        "max_items": 10,
        "weight": 3,
        "note": "出海媒体（含短剧栏目），限条数防刷屏",
    },
    # ---------- AI 行业核心信源 ----------
    {
        "name": "36氪快讯",
        "type": "rss",
        "url": "https://rsshub.rssforever.com/36kr/newsflashes",
        "tags": ["industry", "ai_tools"],
        "max_items": 25,
        "weight": 5,
    },
    {
        "name": "36氪深度",
        "type": "rss",
        "url": "https://www.36kr.com/feed",
        "tags": ["industry", "ai_tools"],
        "max_items": 12,
        "weight": 4,
        "note": "36氪深度报道，含AI/商业深度分析",
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
        "name": "爱范儿",
        "type": "rss",
        "url": "https://www.ifanr.com/feed",
        "tags": ["industry", "ai_tools"],
        "max_items": 20,
        "weight": 4,
        "note": "泛科技+AI应用，内容质量高",
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

# 备用 RSSHub 实例（主实例失败时切换）
BACKUP_RSSHUB_INSTANCES = [
    "https://rsshub.ktachibana.party",
    "https://rsshub.rssforever.com",
]

# 关键词预过滤（本地过滤，不花 API 费用）
# 命中任一关键词的新闻才进入 AI 分析环节
FILTER_KEYWORDS_MUST = [
    # ===== 短剧出海线（核心业务）=====
    "短剧", "漫剧", "AI短剧", "AI 短剧", "微短剧", "小程序短剧",
    "短剧出海", "出海短剧", "ReelShort", "YourChannel", "DramaBox",
    "TikTok", "TikTok Ads", "TikTok Shop",
    "红果", "番茄短剧", "九州文化", "点众", "麦芽",
    "海外短剧", "美剧出海", "短剧投流", "短剧分账", "短剧买量",
    "出海", "海外市场", "跨境电商", "出海营销",
    # ===== AI 视频生成线 =====
    "AI视频", "AI 视频", "视频生成", "文生视频", "图生视频", "视频模型",
    "即梦", "可灵", "Kling", "Runway", "Sora", "Luma", "Vidu", "海螺",
    "Midjourney", "Stable Diffusion", "Pika", "Gen-3", "Veo",
    "AI动画", "AI 动画", "AIGC", "AI绘画", "AI 绘画", "AI绘图",
    # ===== AI 工具/开发线 =====
    "AI工具", "AI 工具", "插件", "SaaS", "智能体", "Agent", "Workflow",
    "大模型", "多模态", "LLM", "GPT", "Claude", "DeepSeek", "Gemini",
    "API", "自动化工具", "效率工具", "AI助手", "AI 助手",
    # ===== 知识付费/教培线 =====
    "知识付费", "教培", "教育", "培训", "课程", "内容创作", "变现",
    "付费社群", "训练营", "陪跑", "私域", "直播带货", "IP",
    # ===== 平台/公司动态 =====
    "抖音", "快手", "字节", "剪映", "CapCut", "腾讯", "阿里",
    "OpenAI", "Anthropic", "Google", "Meta", "YouTube",
]

# 排除词（命中说明大概率无关）
FILTER_KEYWORDS_EXCLUDE = [
    # 财经噪声
    "股票", "基金", "A股", "港股", "美股", "国债", "期货", "外汇",
    "楼市", "房地产", "房价", "油价", "黄金价格",
    # 体育娱乐噪声
    "世界杯", "奥运", "足球", "篮球", "中超", "NBA", "CBA",
    # 无关硬件
    "手机发布会", "手机评测", "显卡", "主板", "CPU跑分",
    # 无关行业（机器人/具身智能/汽车/电池等）
    "人形机器人", "具身智能", "宇树", "机器人", "自动驾驶",
    "新能源汽车", "电池", "光伏", "芯片制造", "半导体设备",
    "卫星", "火箭", "航天", "量子计算", "生物医药",
    # 无关生活
    "菜谱", "健身", "减肥",
]
