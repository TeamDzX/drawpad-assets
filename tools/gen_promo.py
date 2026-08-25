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

# Per-pack marketing art for the landing-page gallery. That gallery renders the
# black-and-white line art from packs/<id>/cover_web.jpg, which is honest about
# what you get but reads as a grid of blank paper at thumbnail size. These give
# each card a colour subject instead. They are NOT App Store assets — promoted
# IAP tiles are per product (see TILES below).
#
# learning_hanzi deliberately shows brush and ink rather than characters: Flux
# garbles hanzi, and a tile with malformed Chinese on it is worse than none.
PACK_TILES = {
    "coloring_dinosaurs": "a cheerful green cartoon dinosaur with a friendly smile standing in tall grass",
    "coloring_ocean": "a happy cartoon dolphin leaping out of bright blue water beside a smiling orange starfish",
    "coloring_space": "a cute cartoon rocket blasting off past a ringed planet and bright stars",
    "coloring_treats": "a cheerful cartoon cupcake with swirled pink frosting and a cherry, beside a rainbow lollipop",
    "coloring_fairytale": "a small friendly cartoon dragon sitting in front of a colourful fairy tale castle",
    "mandala_floral": "an ornate circular flower mandala filled with vivid pinks, purples and greens",
    "mandala_cosmic": "an ornate circular mandala of suns, moons and stars in deep blues, golds and purples",
    "mandala_geometric": "a bold geometric circular mandala of triangles and diamonds in bright primary colours",
    "mandala_animals": "an ornate circular mandala with a decorative elephant head at its centre, warm jewel colours",
    "mandala_celtic": "an ornate circular celtic knotwork mandala in emerald green and gold, interlaced bands",
    "mandala_seasons": "a circular mandala split into four seasons, blossom, sun, autumn leaves and a snowflake",
    "cursive_writing": "a child's hand writing flowing joined-up cursive loops on lined paper with a pencil, no readable words",
    "learning_numbers": "colourful chunky cartoon number shapes one two and three tumbling together on a bright background",
    "learning_hanzi": "a child's hand holding a black calligraphy brush over a red gridded practice square, ink pot beside it, no writing",
    "learning_shapes": "colourful chunky cartoon shapes, a circle a square a triangle and a star, arranged together",
    "learning_letters": "colourful chunky cartoon capital letters A B C tumbling together on a bright background",
    "learning_counting": "five bright red cartoon apples in a row with a chunky colourful number five beside them",
    "learning_lines": "a child's hand drawing a bright wavy zigzag line across paper with a chunky crayon",
    "dottodot_shapes": "a child's hand joining numbered dots with a pencil, the dots forming a bright yellow star",
    "dottodot_animals": "a child's hand joining numbered dots with a pencil, the dots forming a smiling cartoon cat",
    "dottodot_vehicles": "a child's hand joining numbered dots with a pencil, the dots forming a bright red car",
    "dottodot_sealife": "a child's hand joining numbered dots with a pencil, the dots forming a purple cartoon octopus",
    "dottodot_treats": "a child's hand joining numbered dots with a pencil, the dots forming a pink frosted cupcake",
    "dottodot_space": "a child's hand joining numbered dots with a pencil, the dots forming a smiling yellow crescent moon",
    "dottodot_garden": "a child's hand joining numbered dots with a pencil, the dots forming a red ladybird",
    "coloring_farm": "a friendly cartoon cow and a plump pink pig standing together in front of a red barn",
    "coloring_jungle": "a cheeky cartoon monkey hanging from a vine beside a friendly striped tiger",
    "mandala_butterflies": "an ornate circular mandala built from symmetrical butterfly wings in vivid oranges, blues and purples",
    "mandala_lace": "a delicate circular lace doily mandala in soft pinks, creams and gold, fine open scrollwork",
    # The seven below were the original per-pack tiles. They were drawn as
    # rounded-square app-icon art on solid grounds, which reads as a different
    # product beside the pastel-gradient tiles above once they share a gallery
    # row. Re-cut to the house style.
    "coloring_animals": "a friendly cartoon lion cub sitting and smiling, with a soft golden mane",
    "coloring_heroes": "a cheerful cartoon child in an original superhero costume and cape, hands on hips",
    "coloring_nature": "a bright bunch of cartoon garden flowers with green leaves, tied with a ribbon",
    "coloring_unicorns": "a cute cartoon unicorn with a rainbow mane and a golden horn, prancing",
    "coloring_vehicles": "a cheerful red cartoon car with big round headlights, seen three quarters on",
    "mandala_ocean": "an ornate circular mandala of shells, waves and coral in blues, teals and sandy gold",
    "mandala_starter": "a bold simple circular flower mandala with large petals in bright rainbow colours",
}

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


WEB_DIR = os.path.join(PROMO_DIR, "web")
WEB_PX = 500


def _web_version(name):
    """500px JPG for the landing page. The 1024px PNGs are 1-2MB each; a
    28-card gallery of those would be a 40MB page load."""
    from PIL import Image
    os.makedirs(WEB_DIR, exist_ok=True)
    src = os.path.join(PROMO_DIR, name + ".png")
    im = Image.open(src).convert("RGB").resize((WEB_PX, WEB_PX), Image.LANCZOS)
    im.save(os.path.join(WEB_DIR, name + ".jpg"), quality=82, optimize=True)


def build(name, prompts, force=False):
    out = os.path.join(PROMO_DIR, name + ".png")
    if os.path.exists(out) and not force:
        print("  skip %s (already present)" % name)
        return
    seed = zlib.crc32(("promo/" + name).encode()) % 100000
    comfy.generate(out, "%s, %s" % (prompts[name], STYLE), seed,
                   width=1024, height=1024)
    print("  wrote promo/%s.png" % name, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("tiles", nargs="*", help="tile names (default: all)")
    ap.add_argument("--force", action="store_true",
                    help="regenerate even if the tile already exists")
    ap.add_argument("--packs-only", action="store_true",
                    help="only the per-pack landing-page tiles")
    ap.add_argument("--web-only", action="store_true",
                    help="skip generation, just rebuild the 500px web JPGs")
    a = ap.parse_args()

    all_prompts = dict(PACK_TILES)
    all_prompts.update(TILES)
    wanted = a.tiles or (list(PACK_TILES) if a.packs_only
                         else list(TILES) + list(PACK_TILES))
    unknown = [t for t in wanted if t not in all_prompts]
    if unknown:
        sys.exit("unknown tile(s): " + ", ".join(unknown))

    os.makedirs(PROMO_DIR, exist_ok=True)
    if a.web_only:
        # Cover every tile actually on disk, including the legacy per-pack ones
        # that predate PACK_TILES and so have no prompt here.
        wanted = sorted(f[:-4] for f in os.listdir(PROMO_DIR) if f.endswith(".png"))
    for name in wanted:
        if not a.web_only:
            build(name, all_prompts, a.force)
        if os.path.exists(os.path.join(PROMO_DIR, name + ".png")):
            _web_version(name)
