# ============================================================
# 自然语音播报模块
# 使用微软 edge-tts 神经网络语音（免费、自然）
# 音色：晓晓（女声，自然温柔）
# 用法：python speaker.py "要播报的文字"
# ============================================================

import asyncio
import os
import subprocess
import sys
import tempfile

VOICE = "zh-CN-XiaoxiaoNeural"  # 晓晓女声
RATE = "+0%"  # 语速：可调 "+10%" 更快，"-10%" 更慢
VOLUME = "+0%"

TMP_DIR = os.path.join(os.path.dirname(__file__), "data", "tts_cache")
os.makedirs(TMP_DIR, exist_ok=True)


def _normalize_rate(rate: str) -> str:
    """把用户输入的语速规范化为 edge-tts 格式"""
    rate = rate.strip()
    if not rate:
        return "+0%"
    if rate.endswith("%"):
        return rate
    try:
        val = int(rate)
        return f"{val:+d}%"
    except ValueError:
        return "+0%"


async def _generate(text: str, voice: str, rate: str, out_path: str):
    import edge_tts

    communicate = edge_tts.Communicate(text, voice, rate=_normalize_rate(rate))
    await communicate.save(out_path)


def generate_speech(text: str, voice: str = VOICE, rate: str = RATE) -> str:
    """生成语音 mp3 文件，返回文件路径"""
    import hashlib

    # 用内容哈希命名，相同文本不重复生成
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:12]
    out_path = os.path.join(TMP_DIR, f"speech_{h}.mp3")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
        return out_path

    asyncio.run(_generate(text, voice, rate, out_path))
    return out_path


def speak(text: str, voice: str = VOICE, rate: str = RATE, block: bool = True) -> bool:
    """生成并播放语音（跨平台）"""
    try:
        path = generate_speech(text, voice, rate)
    except Exception as e:
        print(f"[speaker] 生成语音失败: {e}")
        return False

    import platform

    system = platform.system()
    if system == "Darwin":
        cmd = ["afplay", path]
    elif system == "Windows":
        cmd = ["start", "", path]
    elif system == "Linux":
        cmd = ["ffplay", "-nodisp", "-autoexit", path]
    else:
        print(f"[speaker] 不支持的平台: {system}")
        return False

    try:
        subprocess.run(cmd, check=False)
        return True
    except Exception as e:
        print(f"[speaker] 播放失败: {e}")
        return False


def build_briefing_text(items: list) -> str:
    """把情报组装成适合播报的自然语言文案"""
    if not items:
        return "今天没有新的情报。"

    s_items = [i for i in items if i.get("level") == "S"]
    a_items = [i for i in items if i.get("level") == "A"]
    b_count = len(items) - len(s_items) - len(a_items)

    lines = []
    lines.append(f"情报雷达站，为您播报今天的简报。")
    lines.append(f"今天共有{len(items)}条情报，其中需要立刻行动的{s_items and len(s_items) or 0}条，今天处理的{a_items and len(a_items) or 0}条。")

    if s_items:
        lines.append("首先，需要立刻行动的重要情报。")
        for i, it in enumerate(s_items, 1):
            lines.append(
                f"第{i}条。{it.get('title', '')}。"
                f"{it.get('why', '')}。建议您{it.get('action', '')}。"
            )

    if a_items:
        lines.append("接下来，需要今天处理的情报。")
        for i, it in enumerate(a_items, 1):
            lines.append(
                f"第{i}条。{it.get('title', '')}。"
                f"{it.get('why', '')}。建议您{it.get('action', '')}。"
            )

    if b_count:
        lines.append(f"另外还有{b_count}条一般情报，稍后可以在看板中查看。")
    lines.append("播报完毕，祝您工作顺利。")
    return " ".join(lines)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        ok = speak(text)
        print("播报成功 ✅" if ok else "播报失败 ❌")
    else:
        print("用法: python speaker.py \"要播报的文字\"")
