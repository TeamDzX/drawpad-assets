#!/usr/bin/env python3
"""
Render the dot-to-dot packs from the outlines in shapes_dottodot.py.

    python3 tools/gen_dottodot.py                    # all three packs
    python3 tools/gen_dottodot.py dottodot_animals   # just one

No ComfyUI here: a diffusion model cannot draw legible sequential numbers, and
the dots have to lie on a path that actually closes into the subject. Both are
straightforward in code and impossible to prompt for reliably.
"""
import argparse
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packlib
import shapes_dottodot as shapes

SIZE = packlib.PAGE_PX
BOX = (135, 168, 889, 922)          # drawing area; leaves room for labels
DOT_R = 9
INK = (0, 0, 0)
NUM = (32, 42, 110)
START = (16, 124, 72)
TITLE = (140, 140, 140)
GUIDE = (176, 176, 176)

# PackDownloadManager caches page art at Packs/<packID>/<pageID>.png and never
# revalidates it, so re-cutting the art behind an existing page id would leave
# everyone who has already opened these packs looking at the old drawing
# forever. Bumping the id is the only way to force a refetch without shipping a
# new build. page.id is used for nothing else — not saved projects, not
# entitlement — so this is safe. Bump again if the outlines are ever redrawn.
ART_REV = 2


def page_id(name):
    return name if ART_REV <= 1 else "%s-v%d" % (name, ART_REV)


TITLES = {
    "dottodot_shapes": ("Dot-to-Dot Shapes", "Connect the dots to reveal a picture"),
    "dottodot_animals": ("Dot-to-Dot Animals", "8 animals to connect"),
    "dottodot_vehicles": ("Dot-to-Dot Vehicles", "8 vehicles to connect"),
    "dottodot_sealife": ("Dot-to-Dot Sea Life", "8 sea creatures to connect"),
    "dottodot_treats": ("Dot-to-Dot Treats", "8 tasty things to connect"),
    "dottodot_space": ("Dot-to-Dot Space", "8 space pictures to connect"),
    "dottodot_garden": ("Dot-to-Dot Garden", "8 garden bugs and plants"),
}


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------

def subdivide(path, step):
    """Insert dots along any segment longer than `step`.

    Hand-placed points carry the silhouette; this only fills the straights, so
    a square gets evenly spaced dots down each side without anyone typing them.
    """
    out = []
    n = len(path)
    for i in range(n):
        a, b = path[i], path[(i + 1) % n]
        out.append(a)
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        extra = int(d / step)
        for k in range(1, extra + 1):
            t = k / (extra + 1.0)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def inside(poly, p):
    """Even-odd point-in-polygon, used to aim number labels outward."""
    x, y = p
    hit = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y):
            if x < x1 + (y - y1) / (y2 - y1) * (x2 - x1):
                hit = not hit
    return hit


def outward(poly, i):
    """Unit vector pointing away from the shape at vertex i."""
    p = poly[i]
    a, b = poly[i - 1], poly[(i + 1) % len(poly)]
    tx, ty = b[0] - a[0], b[1] - a[1]
    n = math.hypot(tx, ty) or 1.0
    nx, ny = ty / n, -tx / n
    if inside(poly, (p[0] + nx * 0.02, p[1] + ny * 0.02)):
        nx, ny = -nx, -ny
    return nx, ny


def fit(spec):
    """Scale one page's art to fill the drawing box, aspect preserved.

    Outlines are authored by eye, so a car ends up occupying a wide central
    band and a rocket a tall thin one. Fitting per page rather than trusting the
    raw 0..1 coordinates keeps every subject the same visual size in the grid.
    Detail strokes are included in the bounds so nothing spills outside.
    """
    pts = list(spec["path"]) + [p for st in spec.get("details", []) for p in st]
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    bw = max(max(xs) - min(xs), 1e-6)
    bh = max(max(ys) - min(ys), 1e-6)
    x0, y0, x1, y1 = BOX
    k = min((x1 - x0) / bw, (y1 - y0) / bh)
    ox = x0 + ((x1 - x0) - bw * k) / 2 - min(xs) * k
    oy = y0 + ((y1 - y0) - bh * k) / 2 - min(ys) * k
    return lambda p: (ox + p[0] * k, oy + p[1] * k)


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

def overlaps(box, taken, pad=3):
    for t in taken:
        if not (box[2] + pad < t[0] or box[0] > t[2] + pad or
                box[3] + pad < t[1] or box[1] > t[3] + pad):
            return True
    return False


def place_label(draw, font, text, anchor, direction, taken):
    """Put a number beside its dot without landing on a neighbour.

    Tries the outward normal first, then fans out to either side and further
    away. Dense corners are exactly where a wrongly placed number makes the
    ordering ambiguous, so it is worth the search.
    """
    w = draw.textlength(text, font=font)
    h = font.size
    ax, ay = anchor
    dx, dy = direction
    base = math.atan2(dy, dx)
    for radius in (30, 42, 56):
        for off in (0, 26, -26, 52, -52, 78, -78, 104, -104, 140, -140, 180):
            a = base + math.radians(off)
            cx = ax + math.cos(a) * radius
            cy = ay + math.sin(a) * radius
            box = (cx - w / 2 - 2, cy - h / 2 - 2, cx + w / 2 + 2, cy + h / 2 + 2)
            if box[0] < 4 or box[1] < 4 or box[2] > SIZE - 4 or box[3] > SIZE - 4:
                continue
            if not overlaps(box, taken):
                draw.text((cx, cy), text, font=font, fill=NUM, anchor="mm")
                taken.append(box)
                return (cx, cy)
    draw.text((ax + 26, ay - 26), text, font=font, fill=NUM, anchor="mm")
    return (ax + 26, ay - 26)


def render(title, spec):
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)

    f_title = packlib.font(packlib.FONT_BOLD, 46)
    f_num = packlib.font(packlib.FONT_BOLD, 36)
    f_start = packlib.font(packlib.FONT_BOLD, 26)

    d.text((SIZE / 2, 74), title, font=f_title, fill=TITLE, anchor="mm")

    # Grey finishing marks (eyes, wheels, windows) sit under the dots and are
    # never numbered — connecting the black dots is the whole puzzle.
    tx = fit(spec)
    for stroke in spec.get("details", []):
        d.line([tx(p) for p in stroke], fill=GUIDE, width=3, joint="curve")

    poly = subdivide(spec["path"], spec.get("step", 0.16))
    pts = [tx(p) for p in poly]

    taken = [(p[0] - DOT_R - 4, p[1] - DOT_R - 4,
              p[0] + DOT_R + 4, p[1] + DOT_R + 4) for p in pts]
    for p in pts:
        d.ellipse([p[0] - DOT_R, p[1] - DOT_R, p[0] + DOT_R, p[1] + DOT_R], fill=INK)

    for i, p in enumerate(pts):
        place_label(d, f_num, str(i + 1), p, outward(poly, i), taken)

    sx, sy = pts[0]
    d.text((sx, sy + 34), "start", font=f_start, fill=START, anchor="mm")
    return img, len(pts)


def render_cover(title, spec):
    """Cover tile: the finished picture, not the puzzle.

    At 600px a field of numbered dots reads as noise in the Store grid, and a
    shopper cannot tell a crab from a car. Showing the connected result is also
    what they are actually buying.
    """
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    d.text((SIZE / 2, 74), title, font=packlib.font(packlib.FONT_BOLD, 46),
           fill=TITLE, anchor="mm")
    tx = fit(spec)
    for stroke in spec.get("details", []):
        d.line([tx(p) for p in stroke], fill=GUIDE, width=4, joint="curve")
    pts = [tx(p) for p in subdivide(spec["path"], spec.get("step", 0.16))]
    d.line(pts + [pts[0]], fill=INK, width=7, joint="curve")
    for p in pts:
        d.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=INK)
    return img


def build(pack_id, only=None):
    entries = shapes.PACKS[pack_id]
    title, subtitle = TITLES[pack_id]
    pages = []
    first = None
    for name, spec in entries.items():
        pid = page_id(name)
        title_text = name.replace("_", " ").title()
        pages.append((pid, title_text))
        if only and name != only:
            continue
        img, n = render(title_text, spec)
        packlib.write_page(img, pack_id, pid)
        if first is None:
            first = render_cover(title_text, spec)
        print("  %s/%s  %d dots" % (pack_id, pid, n), flush=True)
    if first is not None:
        packlib.write_cover(first, pack_id)
    packlib.upsert_pack(packlib.pack_entry(
        pack_id, title, subtitle, "dottodot", pages))
    print("  -> packs.json updated", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("packs", nargs="*")
    ap.add_argument("--page")
    a = ap.parse_args()
    for pack_id in (a.packs or shapes.PACKS.keys()):
        print("pack %s" % pack_id, flush=True)
        build(pack_id, a.page)


if __name__ == "__main__":
    main()
