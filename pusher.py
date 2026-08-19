# ============================================================
# 飞书推送模块：把报告推送到飞书群
# ============================================================

import requests

from config import FEISHU_WEBHOOK, FEISHU_WEBHOOK_ALERT, TIMEOUT


def _post(webhook: str, payload: dict) -> bool:
    """通用推送，返回是否成功"""
    if not webhook or "xxxxxxxx" in webhook:
        return False
    try:
        resp = requests.post(webhook, json=payload, timeout=TIMEOUT)
        data = resp.json()
        ok = data.get("code") == 0 or data.get("StatusCode") == 0
        if not ok:
            print(f"[feishu] 推送失败: {data}")
        return ok
    except Exception as e:
        print(f"[feishu] 推送异常: {e}")
        return False


def send_feishu_text(text: str, webhook: str = None) -> bool:
    """推送文本消息到飞书群"""
    webhook = webhook or FEISHU_WEBHOOK
    if not webhook or "xxxxxxxx" in webhook:
        print("[feishu] 未配置有效的飞书 webhook，跳过推送")
        return False

    payload = {"msg_type": "text", "content": {"text": text}}
    return _post(webhook, payload)


def send_feishu_markdown(title: str, markdown_text: str, webhook: str = None) -> bool:
    """推送富文本（周报用），使用 post 消息类型"""
    webhook = webhook or FEISHU_WEBHOOK
    if not webhook or "xxxxxxxx" in webhook:
        print("[feishu] 未配置有效的飞书 webhook，跳过推送")
        return False

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "title": title,
                "content": [
                    [
                        {
                            "tag": "text",
                            "text": markdown_text[:2000],  # 飞书单条限制
                        }
                    ]
                ],
            }
        },
    }
    return _post(webhook, payload)


def send_alert_card(title: str, body: str) -> bool:
    """S 级预警：推送一张醒目的卡片（独立 webhook 或主 webhook）"""
    webhook = FEISHU_WEBHOOK_ALERT or FEISHU_WEBHOOK
    if not webhook or "xxxxxxxx" in webhook:
        print("[feishu] 未配置飞书 webhook，跳过预警推送")
        return False

    # 飞书 interactive 卡片，红色主题突出预警
    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": "red",
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": body}},
                {"tag": "hr"},
                {"tag": "note", "elements": [{"tag": "plain_text", "content": "来自你的 AI 情报雷达站"}]},
            ],
        },
    }
    return _post(webhook, payload)
