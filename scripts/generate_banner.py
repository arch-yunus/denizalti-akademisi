"""
Generate the Denizalti Akademisi repository banner.

The output intentionally avoids external assets so the banner can be rebuilt
from source whenever the visual language changes.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "banner.png"
W = 1024
H = 1024


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    top = (5, 22, 31)
    mid = (8, 50, 62)
    bottom = (3, 9, 16)
    for y in range(H):
        t = y / (H - 1)
        if t < 0.54:
            p = t / 0.54
            color = tuple(lerp(top[i], mid[i], p) for i in range(3))
        else:
            p = (t - 0.54) / 0.46
            color = tuple(lerp(mid[i], bottom[i], p) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)


def draw_noise(img: Image.Image) -> None:
    random.seed(42)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(1600):
        x = random.randrange(W)
        y = random.randrange(H)
        alpha = random.randrange(5, 20)
        shade = random.randrange(120, 220)
        d.point((x, y), fill=(shade, shade + 12, 255, alpha))
    img.alpha_composite(layer)


def draw_sonar(draw: ImageDraw.ImageDraw) -> None:
    center = (W // 2, 440)
    aqua = (64, 222, 211, 52)
    bright = (98, 247, 230, 130)

    for radius in range(110, 560, 78):
        box = [
            center[0] - radius,
            center[1] - radius,
            center[0] + radius,
            center[1] + radius,
        ]
        draw.ellipse(box, outline=aqua, width=2)

    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        end = (center[0] + math.cos(rad) * 560, center[1] + math.sin(rad) * 560)
        draw.line([center, end], fill=(64, 222, 211, 24), width=1)

    sweep = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    for i in range(34):
        angle = math.radians(-18 + i)
        end = (center[0] + math.cos(angle) * 610, center[1] + math.sin(angle) * 610)
        sd.line([center, end], fill=(83, 245, 226, max(0, 82 - i * 2)), width=5)
    sweep = sweep.filter(ImageFilter.GaussianBlur(2))
    draw.bitmap((0, 0), sweep, fill=None)

    draw.ellipse([center[0] - 7, center[1] - 7, center[0] + 7, center[1] + 7], fill=bright)


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    horizon = 682
    for i in range(18):
        y = horizon + i * 22
        alpha = max(0, 72 - i * 4)
        draw.line([(0, y), (W, y)], fill=(74, 210, 199, alpha), width=1)

    vanishing = (W // 2, horizon - 18)
    for x in range(-120, W + 140, 86):
        draw.line([(x, H), vanishing], fill=(74, 210, 199, 42), width=1)


def draw_submarine(draw: ImageDraw.ImageDraw) -> None:
    shadow = (0, 7, 12, 210)
    steel = (24, 52, 62, 245)
    edge = (96, 225, 212, 150)
    cx, cy = 520, 617

    hull = [178, cy - 56, 850, cy + 64]
    draw.ellipse(hull, fill=steel, outline=edge, width=3)
    draw.rectangle([308, cy - 56, 720, cy + 64], fill=steel)
    draw.arc(hull, 185, 354, fill=edge, width=3)
    draw.arc(hull, 8, 174, fill=(255, 255, 255, 24), width=2)

    draw.polygon([(248, cy), (120, cy - 56), (120, cy + 56)], fill=shadow, outline=edge)
    draw.polygon([(824, cy), (918, cy - 38), (918, cy + 38)], fill=shadow, outline=edge)
    draw.polygon([(485, cy - 62), (552, cy - 62), (578, cy - 138), (461, cy - 138)], fill=steel, outline=edge)
    draw.rounded_rectangle([470, cy - 160, 564, cy - 132], radius=9, fill=(36, 77, 88, 235), outline=edge, width=2)

    for x in [385, 446, 507, 568, 629]:
        draw.ellipse([x - 14, cy - 14, x + 14, cy + 14], fill=(12, 32, 42, 240), outline=(104, 233, 221, 120), width=2)

    draw.ellipse([cx - 380, cy + 84, cx + 380, cy + 130], fill=(0, 0, 0, 70))


def draw_text(draw: ImageDraw.ImageDraw) -> None:
    title = "DENİZALTI AKADEMİSİ"
    subtitle = "TRL İZLEME VE SU ALTI TEKNOLOJİLERİ"
    title_font = font(56, bold=True)
    subtitle_font = font(24, bold=True)
    small_font = font(18)

    badge = "OPEN SOURCE INTELLIGENCE"
    badge_box = [270, 114, 754, 160]
    draw.rounded_rectangle(badge_box, radius=8, fill=(6, 34, 42, 190), outline=(78, 229, 215, 135), width=2)
    draw.text((W // 2, 137), badge, anchor="mm", font=small_font, fill=(173, 239, 232))

    draw.text((W // 2 + 3, 219 + 3), title, anchor="mm", font=title_font, fill=(0, 0, 0, 150))
    draw.text((W // 2, 219), title, anchor="mm", font=title_font, fill=(238, 255, 251))
    draw.text((W // 2, 274), subtitle, anchor="mm", font=subtitle_font, fill=(91, 235, 221))
    draw.line([(250, 310), (774, 310)], fill=(91, 235, 221, 130), width=3)
    draw.text((W // 2, 850), "Sessizlikte Güç · Derinlikte Hakimiyet", anchor="mm", font=font(27, bold=True), fill=(232, 246, 242))
    draw.text((W // 2, 889), "Mavi Vatan için sistematik teknoloji hafızası", anchor="mm", font=font(21), fill=(154, 190, 184))


def main() -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_gradient(draw)
    draw_noise(img)
    draw_sonar(draw)
    draw_grid(draw)
    draw_submarine(draw)
    draw_text(draw)
    img = img.convert("RGB")
    img.save(OUT, quality=95, optimize=True)
    print(f"Wrote {OUT} ({W}x{H})")


if __name__ == "__main__":
    main()
