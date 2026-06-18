#!/usr/bin/env python3
"""
Generate brand images for Warrenville Proud:
  assets/og-image.png        1200x630 social/preview card
  assets/favicon.png         64x64 browser tab icon
  assets/apple-touch-icon.png 180x180 home-screen icon

Run once (re-run only if branding changes): python3 scripts/make_assets.py
Requires Pillow.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)

PRAIRIE = (47, 107, 62)
PRAIRIE_DK = (28, 62, 38)
GOLD = (201, 138, 27)
CREAM = (251, 250, 247)
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def vgradient(w, h, top, bottom):
    base = Image.new("RGB", (w, h), top)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        t = y / max(h - 1, 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (w, y)], fill=c)
    return base

# ---------- OG image ----------
def og():
    w, h = 1200, 630
    img = vgradient(w, h, PRAIRIE, PRAIRIE_DK)
    d = ImageDraw.Draw(img)
    # gold accent bar
    d.rectangle([80, 250, 200, 262], fill=GOLD)
    d.text((78, 150), "WARRENVILLE, ILLINOIS", font=font(BOLD, 30), fill=(200, 222, 205))
    d.text((76, 280), "Warrenville", font=font(BOLD, 104), fill=CREAM)
    d.text((76, 392), "Proud", font=font(BOLD, 104), fill=GOLD)
    d.text((80, 520), "Local events, news, and good things happening in town.",
           font=font(REG, 30), fill=(214, 230, 218))
    # founding sponsor strip
    d.rectangle([0, h - 56, w, h], fill=(20, 46, 28))
    d.text((80, h - 44), "Founding sponsor: Sound & Fury Print Shop",
           font=font(BOLD, 24), fill=(255, 231, 179))
    img.save(os.path.join(ASSETS, "og-image.png"), "PNG")
    print("wrote assets/og-image.png")

# ---------- icons (WP monogram) ----------
def icon(size, name):
    img = Image.new("RGB", (size, size), PRAIRIE)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([2, 2, size - 3, size - 3], radius=int(size * 0.22), fill=PRAIRIE)
    fnt = font(BOLD, int(size * 0.5))
    text = "WP"
    box = d.textbbox((0, 0), text, font=fnt)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text(((size - tw) / 2 - box[0], (size - th) / 2 - box[1]), text, font=fnt, fill=CREAM)
    # small gold underline
    d.rectangle([int(size * 0.3), int(size * 0.74), int(size * 0.7), int(size * 0.78)], fill=GOLD)
    img.save(os.path.join(ASSETS, name), "PNG")
    print("wrote assets/" + name)

if __name__ == "__main__":
    og()
    icon(64, "favicon.png")
    icon(180, "apple-touch-icon.png")
