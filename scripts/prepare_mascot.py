#!/usr/bin/env python3
"""抠图：去除 GIF 灰底并输出透明背景动图。"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "public" / "images" / "mascot-bull.gif"
OUT = ROOT / "public" / "images" / "mascot-bull-cutout.gif"


def is_background(r: int, g: int, b: int) -> bool:
    if r > 210 and g > 210 and b > 210:
        return True
    if abs(r - g) < 18 and abs(g - b) < 18 and r > 165:
        dist = ((r - 239) ** 2 + (g - 239) ** 2 + (b - 239) ** 2) ** 0.5
        return dist < 42
    return False


def remove_bg(frame: Image.Image) -> Image.Image:
    rgba = frame.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if is_background(r, g, b):
                px[x, y] = (r, g, b, 0)
            else:
                dist = ((r - 239) ** 2 + (g - 239) ** 2 + (b - 239) ** 2) ** 0.5
                if 42 <= dist < 72:
                    fade = int(255 * (dist - 42) / 30)
                    px[x, y] = (r, g, b, min(a, fade))
    return rgba


def union_bbox(frames: list[Image.Image], padding: int = 6) -> tuple[int, int, int, int]:
    left = top = 10**9
    right = bottom = 0
    for frame in frames:
        box = frame.getbbox()
        if not box:
            continue
        left = min(left, box[0])
        top = min(top, box[1])
        right = max(right, box[2])
        bottom = max(bottom, box[3])
    return (
        max(0, left - padding),
        max(0, top - padding),
        right + padding,
        bottom + padding,
    )


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"找不到源 GIF: {SRC}")

    src = Image.open(SRC)
    frames: list[Image.Image] = []
    durations: list[int] = []

    for i in range(src.n_frames):
        src.seek(i)
        frames.append(remove_bg(src))
        durations.append(src.info.get("duration", 80))

    crop_box = union_bbox(frames)
    frames = [frame.crop(crop_box) for frame in frames]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
    )
    print(f"已生成: {OUT} ({frames[0].size[0]}x{frames[0].size[1]}, {len(frames)} 帧)")


if __name__ == "__main__":
    main()
