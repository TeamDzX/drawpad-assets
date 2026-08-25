#!/usr/bin/env python3
"""
Check packs.json against what is actually on disk before pushing.

The manifest is the contract between this repo and the shipped app: a page whose
PNG is missing renders as a broken tile in the Store and there is no way to fix
it without another CDN round trip. Run this before every commit.

    python3 tools/validate.py
"""
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packlib

# House sizes for anything generated from tools/. The launch packs predate
# these (256px thumbs, 1024px covers, and coloring_heroes is 1216x832
# landscape) and the app scales whatever it is given, so a mismatch is a
# warning about consistency, not a breakage.
HOUSE = {"page": (packlib.PAGE_PX, packlib.PAGE_PX),
         "thumb": (packlib.THUMB_PX, packlib.THUMB_PX),
         "cover": (packlib.COVER_PX, packlib.COVER_PX)}
CATEGORIES = {"coloring", "mandala", "learning", "dottodot"}

errors = []
warnings = []


sizes = {}

# Flux sometimes renders a toucan's plumage or a monarch's wing markings as
# solid black. Those areas cannot be coloured in, which defeats the page.
#
# Total ink coverage does NOT detect this: dense fine linework (lace mandalas)
# scores as high as a filled silhouette. Downsampling hard is what separates
# them — a solid region stays black through a box filter, while hatching and
# thin outlines average out to grey. Measured across the shipped packs, clean
# line art scores under 0.004 and genuine fills score 0.06-0.12.
#
# Set to catch only the egregious cases. Plenty of good pages carry small
# deliberate dark areas — a donut's sprinkles, a cookie's chocolate chips, an
# animal's eyes — and score 0.01-0.05, so a tighter limit buries the real
# problems in noise. This is a coarse net, not a substitute for looking at the
# contact sheet.
BLOB_LIMIT = 0.060


def solid_blob_ratio(path, size=48, thr=70):
    """Fraction of the page held by large contiguous dark areas."""
    g = Image.open(path).convert("L").resize((size, size), Image.BOX)
    px = list(g.getdata())
    return sum(1 for v in px if v < thr) / float(len(px))


def check(rel, kind):
    """A missing file is fatal — it renders as a broken tile in the Store with
    no way to fix it short of another CDN round trip. An off-house size is not."""
    path = os.path.join(packlib.PACKS_DIR, rel)
    if not os.path.exists(path):
        errors.append("missing %s: %s" % (kind, rel))
        return
    w, h = Image.open(path).size
    sizes[rel] = (w, h)
    if (w, h) != HOUSE[kind]:
        warnings.append("%s %s is %dx%d, house size is %dx%d"
                        % (kind, rel, w, h, *HOUSE[kind]))


m = packlib.load_manifest()
ids = set()
for p in m["packs"]:
    if p["id"] in ids:
        errors.append("duplicate pack id: " + p["id"])
    ids.add(p["id"])
    if p["category"] not in CATEGORIES:
        errors.append("%s: unknown category %r (PackCategory would fail to decode)"
                      % (p["id"], p["category"]))
    if p.get("thumb"):
        check(p["thumb"], "cover")
    if not p["pages"]:
        errors.append(p["id"] + ": no pages")
    page_ids = set()
    for pg in p["pages"]:
        if pg["id"] in page_ids:
            errors.append("%s: duplicate page id %s" % (p["id"], pg["id"]))
        page_ids.add(pg["id"])
        check(pg["image"], "page")
        if p["category"] in ("coloring", "mandala"):
            full = os.path.join(packlib.PACKS_DIR, pg["image"])
            if os.path.exists(full):
                blob = solid_blob_ratio(full)
                if blob > BLOB_LIMIT:
                    warnings.append("%s: solid black areas (%.3f) — reroll, "
                                    "they cannot be coloured in" % (pg["image"], blob))
        if pg.get("thumb"):
            check(pg["thumb"], "thumb")
            # A "thumbnail" the size of the page defeats the point of having one.
            full, small = sizes.get(pg["image"]), sizes.get(pg["thumb"])
            if full and small and small[0] >= full[0]:
                errors.append("%s: thumb %s is not smaller than the page"
                              % (p["id"], pg["thumb"]))
    web = os.path.join(packlib.PACKS_DIR, p["id"], "cover_web.jpg")
    if not os.path.exists(web):
        warnings.append(p["id"] + ": no cover_web.jpg (landing-page gallery tile)")

# Files on disk that nothing in the manifest points at.
listed = {p["id"] for p in m["packs"]}
for d in sorted(os.listdir(packlib.PACKS_DIR)):
    if os.path.isdir(os.path.join(packlib.PACKS_DIR, d)) and d not in listed:
        warnings.append("directory not in manifest: " + d)

house = [w for w in warnings if "house size is" in w]
other = [w for w in warnings if "house size is" not in w]
for w in other:
    print("warn  " + w)
if house:
    packs_off = sorted({w.split()[1].split("/")[0] for w in house})
    print("warn  %d files differ from the house size, in: %s"
          % (len(house), ", ".join(packs_off)))
for e in errors:
    print("ERROR " + e)
print("\n%d packs, %d pages, %d errors, %d warnings"
      % (len(m["packs"]), sum(len(p["pages"]) for p in m["packs"]),
         len(errors), len(warnings)))
sys.exit(1 if errors else 0)
