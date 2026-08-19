# ============================================================
# App 图标生成器：生成 PWA 需要的 PNG 图标（纯标准库，无需 PIL）
# 生成霓虹绿雷达风格图标：192x192 和 512x512
# ============================================================

import math
import os
import struct
import zlib


def _make_png(width: int, height: int, pixel_fn) -> bytes:
    """纯标准库 PNG 编码器。pixel_fn(x, y) -> (r, g, b, a)"""
    raw = b""
    for y in range(height):
        raw += b"\x00"  # filter type 0 (None)
        for x in range(width):
            r, g, b, a = pixel_fn(x, y)
            raw += bytes([r, g, b, a])

    def chunk(typ: bytes, data: bytes) -> bytes:
        c = struct.pack(">I", len(data)) + typ + data
        c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return c

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8bit RGBA
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def _icon_pixel(size: int):
    """霓虹绿雷达图标：深色圆角方块 + 雷达波纹"""
    ACCENT = (204, 255, 0)  # #CCFF00
    BG = (5, 5, 5)

    def pixel_fn(x, y):
        # 圆角遮罩（圆角半径约为 size 的 22%）
        corner = size * 0.22
        cx = min(max(x, corner), size - corner)
        cy = min(max(y, corner), size - corner)
        dx, dy = x - cx, y - cy
        if dx * dx + dy * dy > corner * corner:
            return (0, 0, 0, 0)  # 圆角外透明

        # 中心
        mx, my = size / 2, size / 2
        dist = math.hypot(x - mx, y - my) / (size / 2)

        # 雷达波纹：三个同心圆环
        ring_colors = [
            (0.85, 0.55),  # 外环
            (0.55, 0.75),  # 中环
            (0.25, 0.95),  # 内环
        ]
        for ring_dist, alpha in ring_colors:
            if abs(dist - ring_dist) < 0.035:
                a = int(alpha * 255)
                return (ACCENT[0], ACCENT[1], ACCENT[2], a)

        # 中心实心点
        if dist < 0.13:
            return (ACCENT[0], ACCENT[1], ACCENT[2], 255)

        # 背景（带微弱光晕）
        glow = max(0, 1 - dist * 1.4) * 0.35
        return (
            int(BG[0] + (ACCENT[0] - BG[0]) * glow),
            int(BG[1] + (ACCENT[1] - BG[1]) * glow),
            int(BG[2] + (ACCENT[2] - BG[2]) * glow),
            255,
        )

    return pixel_fn


def generate_icons(out_dir: str = None):
    """生成 192 和 512 图标，返回路径列表"""
    out_dir = out_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "icons")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for size in (192, 512):
        png = _make_png(size, size, _icon_pixel(size))
        path = os.path.join(out_dir, f"icon-{size}.png")
        with open(path, "wb") as f:
            f.write(png)
        paths.append(path)
        print(f"✅ 图标已生成: {path} ({len(png)} bytes)")
    return paths


if __name__ == "__main__":
    generate_icons()
