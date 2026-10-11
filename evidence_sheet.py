#!/usr/bin/env python3
"""Compose an evidence sheet (image grid + captions) for a geolocation run.

Reads a spec JSON so it is reusable across cases (not hard-coded to one photo).

Spec format:
{
  "title": "geo-sleuth | <case name>",
  "base": "<dir containing the images; optional, defaults to cwd>",
  "rows": [
    {"images": ["a.jpg", "b.png"], "height": 300, "caption": "..."},
    ...
  ],
  "footer": ["conclusion line 1", "conclusion line 2"]
}

Usage:
    uv run --with pillow evidence_sheet.py spec.json [out=evidence.jpg]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, PAD, BAR = 1600, 14, 50
BG, FG, ACC = (20, 20, 24), (238, 238, 244), (255, 176, 60)
LINE = 23


def load(p, base):
    fp = Path(base) / p if base else Path(p)
    return Image.open(fp).convert("RGB")


def font(sz):
    for p, idx in [
        ("/System/Library/Fonts/PingFang.ttc", 0),
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
    ]:
        try:
            return ImageFont.truetype(p, sz, index=idx)
        except Exception:  # noqa: BLE001
            pass
    return ImageFont.load_default()


f_title, f_cap = font(27), font(16)


def make_row(paths, target_h, row_w, base):
    ims = [load(p, base) for p in paths]
    out = [i.resize((max(1, round(i.width * target_h / i.height)), target_h)) for i in ims]
    total = sum(i.width for i in out) + PAD * (len(out) - 1)
    if total > row_w:
        s = (row_w - PAD * (len(out) - 1)) / sum(i.width for i in out)
        out = [i.resize((max(1, round(i.width * s)), max(1, round(i.height * s)))) for i in out]
    return out


def wrap(text, f, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    spec_path = sys.argv[1] if len(sys.argv) > 1 else "spec.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "evidence.jpg"
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = spec.get("base", "")
    row_w = W - 2 * PAD
    blocks = []
    for row in spec["rows"]:
        ims = make_row(row["images"], row.get("height", 300), row_w, base)
        lines = wrap(row.get("caption", ""), f_cap, row_w)
        blocks.append((ims, lines, max(i.height for i in ims) + len(lines) * LINE + 14))
    foot_lines = []
    for t in spec.get("footer", []):
        foot_lines += wrap(t, f_cap, row_w)
    foot_h = len(foot_lines) * LINE + 16
    canvas_h = BAR + PAD + sum(b[2] + PAD for b in blocks) + foot_h
    canvas = Image.new("RGB", (W, canvas_h), BG)
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, W, BAR], fill=(32, 32, 38))
    d.text((PAD, 10), spec.get("title", "geo-sleuth evidence"), font=f_title, fill=ACC)
    y = BAR + PAD
    for ims, lines, bh in blocks:
        x = PAD
        for im in ims:
            canvas.paste(im, (x, y))
            x += im.width + PAD
        ty = y + max(i.height for i in ims) + 6
        for ln in lines:
            d.text((PAD, ty), ln, font=f_cap, fill=FG)
            ty += LINE
        y += bh + PAD
    for ln in foot_lines:
        d.text((PAD, y), ln, font=f_cap, fill=(255, 210, 120))
        y += LINE
    canvas.save(out, quality=90)
    print(f"saved {out} {canvas.size}")


if __name__ == "__main__":
    main()
