#!/usr/bin/env python3
"""
Promoted in-app purchase tiles for App Store Connect (1024x1024, full colour).

    python3 tools/gen_promo.py            # any category tile not already present
    python3 tools/gen_promo.py --force coloring mandala

One tile per *product*, not per pack. Entitlement is a single non-consumable
per category (PackCategory.unlockProductID), so there are exactly four
promotable products no matter how many packs ship. The per-pack tiles still in
promo/ (coloring_animals.png and friends) predate that change and App Store
Connect has nowhere to attach them — they are kept only because the landing
page and store listings reuse them as marketing art.

Apple renders these small and alongside the product's own display name, so the
art carries the idea on its own: one clear subject, no lettering.
"""
import argparse
import importlib.util
import os
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packlib

COMFY = os.path.expanduser("~/.claude/scripts/imagegen/comfy_gen.py")
_spec = importlib.util.spec_from_file_location("comfy_gen", COMFY)
comfy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comfy)

PROMO_DIR = os.path.join(packlib.REPO, "promo")

# Matches the tiles already in promo/: saturated flat cartoon, dark outlines,
# soft gradient ground, subject centred with room around it.
STYLE = ("vivid full colour children's cartoon illustration, thick dark "
         "outlines, flat cel shading, soft pastel gradient background, single "
         "centred subject, cheerful, clean and uncluttered, square composition, "
         "no text, no lettering, no words, no watermark")

TILES = {
    "coloring": "a happy child's hand holding a fat crayon colouring in a "
                "half-finished picture of a smiling cartoon animal, bright "
                "crayons scattered around",
    "mandala":  "a single ornate circular mandala filled in with vivid rainbow "
                "colours, symmetrical petals radiating outward, a few coloured "
                "pencils resting beside it",
    "learning": "a smiling young child writing letters in an open exercise book "
                "with a big colourful pencil",
    "dottodot": "a child's hand drawing a line between numbered dots on a page, "
                "the dots forming a friendly cartoon animal",
}


def build(name, force=False):
    out = os.path.join(PROMO_DIR, name + ".png")
    if os.path.exists(out) and not force:
        print("  skip %s (already present)" % name)
        return
    seed = zlib.crc32(("promo/" + name).encode()) % 100000
    comfy.generate(out, "%s, %s" % (TILES[name], STYLE), seed,
                   width=1024, height=1024)
    print("  wrote promo/%s.png" % name, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles", nargs="*",
                    help="category names (default: all four): " + ", ".join(TILES))
    ap.add_argument("--force", action="store_true",
                    help="regenerate even if the tile already exists")
    a = ap.parse_args()
    unknown = [t for t in a.tiles if t not in TILES]
    if unknown:
        sys.exit("unknown tile(s): %s; choose from %s"
                 % (", ".join(unknown), ", ".join(TILES)))
    os.makedirs(PROMO_DIR, exist_ok=True)
    for name in (a.tiles or TILES):
        build(name, a.force)
