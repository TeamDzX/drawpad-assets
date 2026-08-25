#!/usr/bin/env python3
"""
Render the code-generated Learning packs.

    python3 tools/gen_learning.py                     # all
    python3 tools/gen_learning.py learning_counting   # just one

Three packs, all built on the ruled-row worksheet that learning_numbers and
cursive_writing already use, so the Learning tab stays visually of a piece:

  learning_letters   Aa-Zz print letters (the app had cursive but no print)
  learning_counting  count the apples, then trace the numeral
  learning_lines     pre-writing pencil warm-ups (waves, zigzags, loops)

Like the dot-to-dot packs this is deliberately not ComfyUI work: Flux cannot
render dependable letterforms, and a tracing sheet is worthless if the glyph is
subtly wrong.
"""
import argparse
import math
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packlib

SIZE = packlib.PAGE_PX
L, R = 72, 952                      # text column
RULE = (221, 221, 221)
GREY = (153, 153, 153)
BLUE = (150, 178, 214)
BLUE_FAINT = (191, 209, 232)
GREEN = (16, 124, 72)
# Each successive row is fainter, so the child traces then writes unaided.
FADE = [(51, 51, 51), (102, 102, 102), (153, 153, 153),
        (204, 204, 204), (232, 232, 232)]

ROW_TOP = 322
ROW_H = 90
ROW_PITCH = 135


def dashed(d, pts, fill, width=2, dash=12, gap=9):
    """PIL has no dash support, so walk the polyline and stamp segments.

    Phase comes from the distance travelled rather than a running carry: the
    carry version could drive `step` negative once the leftover exceeded the
    gap length, and the walk would then loop forever without advancing.
    """
    period = float(dash + gap)
    travelled = 0.0
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        seg = math.hypot(x2 - x1, y2 - y1)
        if seg <= 0:
            continue
        steps = max(1, int(seg / 2.0))
        for k in range(steps):
            if (travelled + seg * k / steps) % period < dash:
                d.line([(x1 + (x2 - x1) * k / steps, y1 + (y2 - y1) * k / steps),
                        (x1 + (x2 - x1) * (k + 1) / steps,
                         y1 + (y2 - y1) * (k + 1) / steps)],
                       fill=fill, width=width)
        travelled += seg


def header(d, glyph, word, glyph_font, word_font):
    d.text((L, 66), glyph, font=glyph_font, fill=(20, 20, 20))
    w = d.textlength(glyph, font=glyph_font)
    d.text((L + w + 46, 122), word, font=word_font, fill=GREY)
    d.line([(L, 250), (R, 250)], fill=RULE, width=2)


def ruled_row(d, top):
    d.line([(L, top), (R, top)], fill=BLUE, width=2)
    dashed(d, [(L, top + ROW_H / 2), (R, top + ROW_H / 2)], BLUE_FAINT, 2)
    d.line([(L, top + ROW_H), (R, top + ROW_H)], fill=BLUE, width=2)


def trace_rows(d, rows, font, per_row=7, colors=None):
    """`rows` is a list of the string to repeat on each successive line."""
    colors = colors or FADE
    for i, text in enumerate(rows):
        top = ROW_TOP + i * ROW_PITCH
        ruled_row(d, top)
        pitch = (R - L - 32) / per_row
        for k in range(per_row):
            d.text((L + 16 + pitch * (k + 0.5), top + ROW_H),
                   text, font=font, fill=colors[i], anchor="ms")


# --------------------------------------------------------------------------
# learning_letters
# --------------------------------------------------------------------------

def page_letter(ch):
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    header(d, ch.upper() + ch.lower(), "%s / %s" % (ch.upper(), ch.lower()),
           packlib.font(packlib.FONT_BOLD, 118),
           packlib.font(packlib.FONT_REG, 40))
    # Three lines of the capital, then two of the lowercase — capitals are the
    # ones children are taught to form first.
    trace_rows(d, [ch.upper()] * 3 + [ch.lower()] * 2,
               packlib.font(packlib.FONT_BOLD, 86),
               colors=[FADE[0], FADE[1], FADE[2], FADE[0], FADE[2]])
    return img


# --------------------------------------------------------------------------
# learning_counting
# --------------------------------------------------------------------------

WORDS = ["one", "two", "three", "four", "five",
         "six", "seven", "eight", "nine", "ten"]


def apple(d, cx, cy, r):
    d.ellipse([cx - r, cy - r * 0.92, cx + r, cy + r], outline=(40, 40, 40), width=5)
    d.line([(cx - r * 0.04, cy - r * 0.90), (cx - r * 0.10, cy - r * 1.46)],
           fill=(40, 40, 40), width=5)
    d.ellipse([cx + r * 0.06, cy - r * 1.40, cx + r * 0.72, cy - r * 1.04],
              outline=(40, 40, 40), width=4)


def page_count(n):
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    header(d, str(n), WORDS[n - 1],
           packlib.font(packlib.FONT_BOLD, 118),
           packlib.font(packlib.FONT_REG, 40))

    # Count the apples, then trace the numeral that says how many.
    per = 5
    r = 34
    step = 116
    for i in range(n):
        col, row = i % per, i // per
        in_row = min(n - row * per, per)
        cx = SIZE / 2 - (in_row - 1) * step / 2 + col * step
        cy = 344 + row * 112
        apple(d, cx, cy, r)

    rows = 3
    base = 560 if n > 5 else 500
    f = packlib.font(packlib.FONT_BOLD, 86)
    for i in range(rows):
        top = base + i * ROW_PITCH
        ruled_row(d, top)
        pitch = (R - L - 32) / 7
        for k in range(7):
            d.text((L + 16 + pitch * (k + 0.5), top + ROW_H),
                   str(n), font=f, fill=FADE[i], anchor="ms")
    return img


# --------------------------------------------------------------------------
# learning_lines — pre-writing pencil control
# --------------------------------------------------------------------------

def _samples(fn, x0, x1, n=260):
    return [(x0 + (x1 - x0) * i / (n - 1.0), fn(i / (n - 1.0))) for i in range(n)]


def pattern(name, x0, x1, mid, amp):
    if name == "straight":
        return _samples(lambda t: mid, x0, x1, 2)
    if name == "wave":
        return _samples(lambda t: mid - amp * math.sin(t * 8 * math.pi), x0, x1)
    if name == "zigzag":
        return _samples(lambda t: mid - amp * (4 * abs(((t * 4) % 1) - 0.5) - 1),
                        x0, x1, 200)
    if name == "hills":
        return _samples(lambda t: mid - amp * abs(math.sin(t * 5 * math.pi)), x0, x1)
    if name == "bumps":
        return _samples(lambda t: mid - amp * max(0.0, math.sin(t * 9 * math.pi)) ** 0.4,
                        x0, x1)
    if name == "valleys":
        return _samples(lambda t: mid + amp * abs(math.sin(t * 5 * math.pi)), x0, x1)
    if name == "loops":
        # Prolate cycloid (b > a), so the curve actually crosses itself — this
        # is the motion behind cursive e and l, which is the point of the page.
        turns = 5
        b = 1.7
        raw = [(t - b * math.sin(t), math.cos(t))
               for t in (i / 419.0 * turns * 2 * math.pi for i in range(420))]
        lo = min(x for x, _ in raw)
        hi = max(x for x, _ in raw)
        return [(x0 + (x1 - x0) * (x - lo) / (hi - lo), mid + amp * y)
                for x, y in raw]
    if name == "spirals":
        pts = []
        count = 5
        span = (x1 - x0) / count
        for c in range(count):
            cx = x0 + span * (c + 0.5)
            for i in range(90):
                a = i / 89.0 * 3.2 * 2 * math.pi
                rr = amp * (1 - i / 89.0 * 0.92)
                pts.append((cx + rr * math.cos(a), mid + rr * math.sin(a)))
            pts.append((cx, mid))
        return pts
    raise ValueError(name)


LINE_PAGES = [
    ("straight", "Straight Lines"), ("wave", "Waves"),
    ("zigzag", "Zigzags"), ("hills", "Hills"),
    ("valleys", "Valleys"), ("bumps", "Bumps"),
    ("loops", "Loops"), ("spirals", "Spirals"),
]


def page_lines(name, title):
    img = Image.new("RGB", (SIZE, SIZE), "white")
    d = ImageDraw.Draw(img)
    d.text((SIZE / 2, 84), title, font=packlib.font(packlib.FONT_BOLD, 52),
           fill=(120, 120, 120), anchor="mm")
    d.text((SIZE / 2, 140), "Start at the green dot and follow the path",
           font=packlib.font(packlib.FONT_REG, 30), fill=GREY, anchor="mm")

    # First row solid to copy from, the rest dashed and fading out.
    for i in range(4):
        mid = 268 + i * 178
        amp = 52
        pts = pattern(name, L + 40, R - 20, mid, amp)
        d.line([(L, mid + amp + 34), (R, mid + amp + 34)], fill=RULE, width=2)
        if i == 0:
            d.line(pts, fill=(70, 70, 70), width=6, joint="curve")
        else:
            dashed(d, pts, FADE[min(i, 3)], width=5, dash=16, gap=13)
        d.ellipse([L + 40 - 9, mid - 9, L + 40 + 9, mid + 9], fill=GREEN)
    return img


# --------------------------------------------------------------------------

def build(pack_id):
    if pack_id == "learning_letters":
        pages = []
        first = None
        for ch in "abcdefghijklmnopqrstuvwxyz":
            img = page_letter(ch)
            packlib.write_page(img, pack_id, ch)
            pages.append((ch, "%s %s" % (ch.upper(), ch.lower())))
            first = first or img
        packlib.write_cover(first, pack_id)
        packlib.upsert_pack(packlib.pack_entry(
            pack_id, "Print Letters", "Trace Aa to Zz", "learning", pages))
    elif pack_id == "learning_counting":
        pages = []
        first = None
        for n in range(1, 11):
            img = page_count(n)
            packlib.write_page(img, pack_id, "%02d" % n)
            pages.append(("%02d" % n, "%d — %s" % (n, WORDS[n - 1])))
            first = first or img
        packlib.write_cover(first, pack_id)
        packlib.upsert_pack(packlib.pack_entry(
            pack_id, "Count & Trace", "Count the apples, trace the number",
            "learning", pages))
    elif pack_id == "learning_lines":
        pages = []
        first = None
        for name, title in LINE_PAGES:
            img = page_lines(name, title)
            packlib.write_page(img, pack_id, name)
            pages.append((name, title))
            first = first or img
        packlib.write_cover(first, pack_id)
        packlib.upsert_pack(packlib.pack_entry(
            pack_id, "Pencil Warm-Ups", "8 pre-writing patterns to trace",
            "learning", pages))
    else:
        raise SystemExit("unknown pack " + pack_id)
    print("  %s -> %d pages" % (pack_id, len(pages)), flush=True)


ALL = ["learning_letters", "learning_counting", "learning_lines"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("packs", nargs="*")
    a = ap.parse_args()
    for pid in (a.packs or ALL):
        build(pid)
