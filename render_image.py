#!/usr/bin/env python3
"""Render entry.png: 'The World in One Picture' for Friday 20 November 2026.

Reads stories.json (kicker / headline / sublabel per panel) and composes a
newspaper-style front page at 2x supersampling, then downscales to
1024x1024 for clean edges. All text is drawn by PIL from the JSON data,
so the wording can be refreshed by editing stories.json only.
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
S = 2  # supersample factor
W = 1024
M = 34  # page margin
RX = W - M  # right edge of the content column
CW = RX - M  # content width

PAPER = (247, 242, 231)
CARD = (255, 253, 246)
INK = (27, 42, 74)
RED = (179, 39, 30)
BODY = (40, 44, 54)

SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
DJ_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size * S)


def u(v):
    """Scale a base-unit length to render pixels."""
    return int(round(v * S))


def draw_tracked(d, cx, y, text, fnt, fill, tracking):
    """Draw text centred at cx with extra letter tracking (base units)."""
    widths = [d.textlength(ch, font=fnt) for ch in text]
    total = sum(widths) + u(tracking) * (len(text) - 1)
    x = u(cx) - total / 2
    for ch, w in zip(text, widths):
        d.text((x, u(y)), ch, font=fnt, fill=fill)
        x += w + u(tracking)


def draw_tracked_left(d, x, y, text, fnt, fill, tracking):
    """Draw tracked text starting exactly at x (base units)."""
    cx = u(x)
    for ch in text:
        d.text((cx, u(y)), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt) + u(tracking)


def fit_size(d, text, path, start, max_width):
    """Largest font size <= start (base units) whose text fits max_width."""
    size = start
    while size > 10:
        if d.textlength(text, font=font(path, size)) <= u(max_width):
            return size
        size -= 2
    return size


def wrap(d, text, fnt, max_width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=fnt) <= u(max_width):
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_one_line(d, text, path, start, max_width, minimum=15):
    size = start
    while size > minimum and d.textlength(text, font=font(path, size)) > u(max_width):
        size -= 1
    return font(path, size)


def fit_wrapped(d, text, path, sizes, max_width, max_lines):
    """First size in `sizes` whose wrapping needs at most max_lines lines."""
    for size in sizes:
        fnt = font(path, size)
        lines = wrap(d, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
    fnt = font(path, sizes[-1])
    return fnt, wrap(d, text, fnt, max_width)


# ---------------------------------------------------------------- icons

def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((u(cx) + rad * S * math.cos(ang), u(cy) + rad * S * math.sin(ang)))
    d.polygon(pts, fill=fill)


def icon_summit(d, x, y):
    # three flags' stars over a negotiating table
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(24, 58, 74))
    gold = (242, 194, 48)
    for cx in (21, 41, 61):
        star(d, x + cx, y + 20, 7, gold)
    d.rectangle([u(x + 12), u(y + 48), u(x + 70), u(y + 58)], fill=gold)
    d.rectangle([u(x + 18), u(y + 58), u(x + 24), u(y + 70)], fill=gold)
    d.rectangle([u(x + 58), u(y + 58), u(x + 64), u(y + 70)], fill=gold)


def icon_culture(d, x, y):
    # retro sunset disc with palm silhouettes
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(64, 28, 88))
    sun = (255, 148, 74)
    d.ellipse([u(x + 19), u(y + 14), u(x + 63), u(y + 58)], fill=sun)
    for sy in (42, 49, 55):
        d.rectangle([u(x + 19), u(y + sy), u(x + 63), u(y + sy + 2.5)], fill=(64, 28, 88))
    sil = (26, 14, 40)
    d.rectangle([u(x), u(y + 68), u(x + 82), u(y + 82)], fill=sil)

    def palm(px, lean):
        top_x, top_y = px + lean, y + 40
        for i in range(10):
            t0, t1 = i / 10, (i + 1) / 10
            d.line([u(x + px + lean * t0 * t0), u(y + 68 - 28 * t0),
                    u(x + px + lean * t1 * t1), u(y + 68 - 28 * t1)],
                   fill=sil, width=u(3.5))
        for ang in (-170, -130, -90, -50, -10):
            ex = top_x + 15 * math.cos(math.radians(ang))
            ey = top_y - 8 * math.sin(math.radians(ang)) + 4
            d.line([u(x + top_x), u(top_y), u(x + ex), u(ey)], fill=sil, width=u(2.5))

    palm(14, 5)
    palm(68, -5)


def icon_asia(d, x, y):
    # cyclone swirl over a coastline
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(14, 110, 110))
    for r, start in ((11, 20), (18, 110), (25, 200)):
        d.arc([u(x + 41 - r), u(y + 34 - r), u(x + 41 + r), u(y + 34 + r)],
              start=start, end=start + 235, fill=(234, 246, 246), width=u(5))
    d.ellipse([u(x + 37), u(y + 30), u(x + 45), u(y + 38)], fill=(234, 246, 246))
    coast = [(x, y + 82), (x, y + 68), (x + 18, y + 64), (x + 38, y + 70),
             (x + 58, y + 63), (x + 82, y + 69), (x + 82, y + 82)]
    d.polygon([(u(px), u(py)) for px, py in coast], fill=(228, 200, 127))
    d.arc([u(x + 6), u(y + 52), u(x + 30), u(y + 64)], start=180, end=330,
          fill=(234, 246, 246), width=u(2.5))


def icon_mideast(d, x, y):
    # tanker on the sea, flames and smoke amidships
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(16, 42, 64))
    d.rectangle([u(x), u(y + 60), u(x + 82), u(y + 82)], fill=(10, 70, 96))
    hull = (10, 14, 22)
    d.polygon([(u(x + 8), u(y + 48)), (u(x + 74), u(y + 48)), (u(x + 68), u(y + 60)),
               (u(x + 14), u(y + 60))], fill=hull)
    d.rectangle([u(x + 14), u(y + 43), u(x + 56), u(y + 48)], fill=hull)
    d.rectangle([u(x + 60), u(y + 36), u(x + 68), u(y + 48)], fill=hull)
    d.line([u(x + 20), u(y + 43), u(x + 20), u(y + 32)], fill=hull, width=u(2.5))

    def flame(cx, base, h, w, fill):
        pts = [(cx - w, base), (cx - w * 0.4, base - h * 0.45), (cx, base - h),
               (cx + w * 0.4, base - h * 0.45), (cx + w, base),
               (cx + w * 0.45, base - h * 0.18), (cx - w * 0.45, base - h * 0.18)]
        d.polygon([(u(px), u(py)) for px, py in pts], fill=fill)

    flame(x + 34, y + 44, 22, 8, (240, 110, 40))
    flame(x + 34, y + 44, 14, 5, (250, 180, 60))
    flame(x + 46, y + 44, 15, 6, (240, 110, 40))
    flame(x + 46, y + 44, 9, 3.5, (255, 230, 140))
    smoke = (105, 110, 120)
    d.ellipse([u(x + 26), u(y + 8), u(x + 38), u(y + 18)], fill=smoke)
    d.ellipse([u(x + 36), u(y + 4), u(x + 50), u(y + 15)], fill=smoke)
    d.ellipse([u(x + 44), u(y + 12), u(x + 54), u(y + 21)], fill=smoke)


def icon_markets(d, x, y):
    # a chart line plunging through a faint grid
    d.rectangle([u(x), u(y), u(x + 82), u(y + 82)], fill=(14, 38, 32))
    grid = (40, 80, 70)
    for gx in (20, 41, 62):
        d.line([u(x + gx), u(y + 4), u(x + gx), u(y + 78)], fill=grid, width=u(1))
    for gy in (22, 44, 66):
        d.line([u(x + 4), u(y + gy), u(x + 78), u(y + gy)], fill=grid, width=u(1))
    pts = [(8, 16), (24, 25), (38, 21), (50, 38), (62, 55), (74, 70)]
    d.line([(u(x + px), u(y + py)) for px, py in pts], fill=(224, 60, 48), width=u(4))
    for px, py in pts[:-1]:
        d.ellipse([u(x + px - 2.5), u(y + py - 2.5), u(x + px + 2.5), u(y + py + 2.5)],
                  fill=(224, 60, 48))
    d.polygon([(u(x + 74), u(y + 70)), (u(x + 64), u(y + 68)), (u(x + 72), u(y + 60))],
              fill=(224, 60, 48))
    d.line([u(x + 8), u(y + 16), u(x + 24), u(y + 25)], fill=(242, 194, 48), width=u(2))


ICONS = {"summit": icon_summit, "culture": icon_culture, "asia": icon_asia,
         "mideast": icon_mideast, "markets": icon_markets}


# ---------------------------------------------------------------- lead art

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lead_art(d, x, y, w, h):
    """Night sky over a river skyline; missile trails arc down to the city."""
    stops = [(0.0, (18, 22, 54)), (0.45, (44, 34, 78)), (0.75, (120, 52, 66)),
             (1.0, (196, 96, 60))]
    for row in range(u(h)):
        t = row / max(1, u(h) - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                col = lerp(c0, c1, (t - t0) / (t1 - t0))
                break
        d.line([u(x), u(y) + row, u(x + w), u(y) + row], fill=col)
    # stars in the upper sky
    for sx, sy in [(60, 12), (180, 22), (300, 8), (470, 16), (560, 26),
                   (760, 10), (880, 20), (660, 6), (240, 30), (820, 32)]:
        d.ellipse([u(x + sx), u(y + sy), u(x + sx + 2), u(y + sy + 2)],
                  fill=(210, 216, 235))
    sil = (13, 16, 28)
    base = y + h
    # skyline
    towers = [(0, 34), (48, 22), (92, 44), (140, 28), (188, 52), (238, 24),
              (700, 40), (748, 26), (792, 50), (842, 30), (884, 44), (928, 24)]
    for tx, th in towers:
        d.rectangle([u(x + tx), u(base - th), u(x + tx + 38), u(base)], fill=sil)
    # bridge across the river gap: deck, two pylons, suspension arcs
    deck_y = base - 12
    d.rectangle([u(x), u(deck_y), u(x + w), u(deck_y + 4)], fill=sil)
    for px in (330, 620):
        d.rectangle([u(x + px), u(base - 44), u(x + px + 7), u(deck_y)], fill=sil)
    for cx, span in ((333, 330), (623, 333)):
        d.arc([u(x + cx - span), u(base - 78), u(x + cx + span), u(base + 30)],
              start=180, end=360, fill=sil, width=u(3))
    d.rectangle([u(x), u(base - 3), u(x + w), u(base)], fill=sil)
    # missile trails: quadratic arcs from the upper sky down to the skyline
    trails = [((90, 2), (240, 26), (372, 66)),
              ((430, 0), (520, 30), (596, 74)),
              ((700, 4), (760, 24), (812, 58)),
              ((880, 0), (872, 26), (838, 62))]
    for (ax, ay), (bx, by), (cx, cy) in trails:
        pts = []
        for i in range(25):
            t = i / 24
            px = (1 - t) ** 2 * ax + 2 * (1 - t) * t * bx + t ** 2 * cx
            py = (1 - t) ** 2 * ay + 2 * (1 - t) * t * by + t ** 2 * cy
            pts.append((u(x + px), u(y + py)))
        d.line(pts, fill=(255, 120, 60), width=u(5))
        d.line(pts, fill=(255, 226, 170), width=u(2))
        d.ellipse([u(x + cx - 5), u(y + cy - 5), u(x + cx + 5), u(y + cy + 5)],
                  fill=(255, 190, 110))
        d.ellipse([u(x + cx - 2), u(y + cy - 2), u(x + cx + 2), u(y + cy + 2)],
                  fill=(255, 244, 214))


# ---------------------------------------------------------------- compose

def main():
    data = json.loads((HERE / "stories.json").read_text(encoding="utf-8"))
    img = Image.new("RGB", (W * S, W * S), PAPER)
    d = ImageDraw.Draw(img)
    mast, lead, panels = data["masthead"], data["lead"], data["panels"]

    # masthead
    draw_tracked(d, W / 2, 22, mast["kicker"], font(DJ_BOLD, 24), INK, 7)
    s1 = fit_size(d, mast["date_line_1"], SERIF_BOLD, 108, CW)
    d.text((u(W / 2), u(50)), mast["date_line_1"], font=font(SERIF_BOLD, s1),
           fill=INK, anchor="ma")
    s2 = fit_size(d, mast["date_line_2"], SERIF_BOLD, 100, CW)
    d.text((u(W / 2), u(156)), mast["date_line_2"], font=font(SERIF_BOLD, s2),
           fill=INK, anchor="ma")
    d.rectangle([u(M), u(244), u(RX), u(250)], fill=INK)
    d.rectangle([u(M), u(254), u(RX), u(256)], fill=INK)

    # lead panel
    lead_art(d, M, 270, CW, 96)
    d.rectangle([u(M), u(270), u(RX), u(366)], outline=INK, width=u(2.5))
    draw_tracked_left(d, M, 376, lead["kicker"], font(DJ_BOLD, 18), RED, 4)
    d.text((u(M), u(396)), lead["headline"], font=font(SANS_BOLD, 44), fill=INK)
    sub_f, sub_lines = fit_wrapped(d, lead["sublabel"], SANS, (21, 20, 19), CW, 3)
    ly = 450
    for line in sub_lines:
        d.text((u(M), u(ly)), line, font=sub_f, fill=BODY)
        ly += 26
    d.rectangle([u(M), u(534), u(RX), u(536)], fill=INK)

    # five story strips
    y = 548
    for panel in panels:
        d.rectangle([u(M), u(y), u(RX), u(y + 88)], fill=CARD)
        d.rectangle([u(M), u(y), u(RX), u(y + 88)], outline=INK, width=u(2))
        ICONS[panel["id"]](d, M, y + 3)
        tx = M + 82 + 16
        tw = RX - tx
        d.text((u(tx), u(y + 5)), panel["kicker"], font=font(DJ_BOLD, 15), fill=RED)
        hf = fit_one_line(d, panel["headline"], SANS_BOLD, 27, tw, minimum=20)
        d.text((u(tx), u(y + 23)), panel["headline"], font=hf, fill=INK)
        sf, slines = fit_wrapped(d, panel["sublabel"], SANS, (17, 16, 15, 14), tw, 2)
        sy = y + 50
        for line in slines:
            d.text((u(tx), u(sy)), line, font=sf, fill=BODY)
            sy += 17
        y += 92

    img = img.resize((W, W), Image.LANCZOS)
    out = HERE / "entry.png"
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
