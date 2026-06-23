#!/usr/bin/env python3
"""去除小牛视频绿幕背景，生成透明 WebM。"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "public" / "videos" / "mascot-bull.mp4"
OUT = ROOT / "public" / "videos" / "mascot-bull-alpha.webm"

# 绿幕背景采样约 #219d3f
GREEN_SCREEN_COLOR = "0x219d3f"
GREEN_SCREEN_SIMILARITY = "0.12"
GREEN_SCREEN_BLEND = "0.04"


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"找不到源视频: {SRC}")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("需要安装 ffmpeg: brew install ffmpeg")

    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(SRC),
        "-vf",
        f"chromakey={GREEN_SCREEN_COLOR}:{GREEN_SCREEN_SIMILARITY}:{GREEN_SCREEN_BLEND}",
        "-an",
        "-c:v",
        "libvpx-vp9",
        "-pix_fmt",
        "yuva420p",
        "-crf",
        "32",
        "-b:v",
        "0",
        "-auto-alt-ref",
        "0",
        str(OUT),
    ]
    subprocess.run(cmd, check=True)
    print(f"已生成透明视频: {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"ffmpeg 处理失败: {exc}") from exc
