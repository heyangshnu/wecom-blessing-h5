from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _lerp_color(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def generate_common_preview(output_path: Path) -> Path:
    width, height = 1068, 455
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    top = (255, 94, 98)
    mid = (255, 154, 86)
    bottom = (255, 206, 84)
    for y in range(height):
        t = y / height
        color = _lerp_color(top, mid, t * 2) if t < 0.5 else _lerp_color(mid, bottom, (t - 0.5) * 2)
        draw.line([(0, y), (width, y)], fill=color)

    for cx, cy, radius, fill in [
        (180, 90, 70, (255, 255, 255, 60)),
        (900, 120, 90, (255, 255, 255, 50)),
        (820, 360, 60, (255, 120, 180, 70)),
        (120, 340, 55, (120, 220, 255, 70)),
    ]:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=fill)
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        (70, 50, width - 70, height - 50),
        radius=28,
        outline="#ffffff",
        width=4,
    )

    title_font = _load_font(54)
    hint_font = _load_font(24)

    draw.text((width // 2, 165), "你好，初次见面", fill="#ffffff", font=title_font, anchor="mm")
    draw.text((width // 2, 235), "请多多指教", fill="#fff8dc", font=title_font, anchor="mm")
    draw.text((width // 2, 340), "✨ 点击开启随机祝福 ✨", fill="#ffffff", font=hint_font, anchor="mm")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "JPEG", quality=92)
    return output_path
