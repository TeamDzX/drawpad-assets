"""
Shared helpers for building DrawPad content packs.

Every pack on the CDN follows the same on-disk contract, and the app reads it
straight from packs.json (see PackModels.swift):

    packs/<pack_id>/<page_id>.png          1024x1024  full-res line art
    packs/<pack_id>/<page_id>_thumb.png     320x320    grid preview
    packs/<pack_id>/cover.png               600x600    store tile
    packs/<pack_id>/cover_web.jpg           500x500    landing-page gallery

Filenames are the contract — the manifest points at them by path, so add
variants rather than renaming.
"""
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

PAGE_PX = 1024
THUMB_PX = 320
COVER_PX = 600
COVER_WEB_PX = 500

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS_DIR = os.path.join(REPO, "packs")
MANIFEST = os.path.join(PACKS_DIR, "packs.json")

FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_ROUND = "/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# --------------------------------------------------------------------------
# line-art cleanup
# --------------------------------------------------------------------------

def clean_lineart(img, lo=50, hi=200):
    """Snap a diffusion-model line drawing to true black-on-white.

    Flux returns near-white paper (245-252) with grey wash in the large flat
    areas. That reads as dirty on screen and, more importantly, seeds the
    canvas with off-white pixels. A levels curve fixes it without the jagged
    edges a hard threshold would give: everything above `hi` becomes pure
    white, everything below `lo` pure black, and the band between is rescaled
    so line antialiasing survives.
    """
    g = img.convert("L")
    span = max(hi - lo, 1)
    lut = [0 if v <= lo else 255 if v >= hi else int((v - lo) * 255 / span)
           for v in range(256)]
    return g.point(lut).convert("RGB")


def trim_to_square(img, margin=0.06, bg=255):
    """Centre the drawing in a square with an even margin.

    Flux composes most subjects well but drifts off-centre often enough that a
    grid of eight pages looks untidy. Ignored when the art already fills the
    frame (mandalas), since the bbox is then the whole image.
    """
    g = img.convert("L")
    box = g.point(lambda v: 0 if v > 240 else 255).getbbox()
    if not box:
        return img
    w, h = box[2] - box[0], box[3] - box[1]
    side = int(max(w, h) * (1 + 2 * margin))
    out = Image.new("RGB", (side, side), (bg, bg, bg))
    out.paste(img.crop(box), ((side - w) // 2, (side - h) // 2))
    return out


def _square(img, px):
    if img.size != (px, px):
        img = img.resize((px, px), Image.LANCZOS)
    return img


# --------------------------------------------------------------------------
# writing a pack to disk
# --------------------------------------------------------------------------

def pack_dir(pack_id):
    d = os.path.join(PACKS_DIR, pack_id)
    os.makedirs(d, exist_ok=True)
    return d


def write_page(img, pack_id, page_id):
    """Save one page plus its thumbnail. Returns the manifest page paths."""
    d = pack_dir(pack_id)
    page = _square(img.convert("RGB"), PAGE_PX)
    page.save(os.path.join(d, page_id + ".png"), optimize=True)
    _square(page.copy(), THUMB_PX).save(
        os.path.join(d, page_id + "_thumb.png"), optimize=True)
    return {"image": "%s/%s.png" % (pack_id, page_id),
            "thumb": "%s/%s_thumb.png" % (pack_id, page_id)}


def write_cover(img, pack_id):
    """Cover tile (PNG for the app) and web JPG (for the landing gallery)."""
    d = pack_dir(pack_id)
    cover = _square(img.convert("RGB"), COVER_PX)
    cover.save(os.path.join(d, "cover.png"), optimize=True)
    _square(cover.copy(), COVER_WEB_PX).save(
        os.path.join(d, "cover_web.jpg"), quality=82, optimize=True)
    return "%s/cover.png" % pack_id


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------

def load_manifest():
    with open(MANIFEST) as f:
        return json.load(f)


def upsert_pack(entry):
    """Add or replace one pack in packs.json, preserving the existing order.

    Entitlement is per category (PackCategory.unlockProductID), so a new pack
    needs no new IAP — it goes live the moment the CDN serves the manifest.
    """
    m = load_manifest()
    for i, p in enumerate(m["packs"]):
        if p["id"] == entry["id"]:
            m["packs"][i] = entry
            break
    else:
        m["packs"].append(entry)
    with open(MANIFEST, "w") as f:
        json.dump(m, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return m


def pack_entry(pack_id, title, subtitle, category, pages):
    """Build a manifest entry. `pages` is [(page_id, title), ...]."""
    return {
        "id": pack_id,
        "productID": "TeamDzX.Drawing-App.pack.%s" % pack_id,
        "title": title,
        "subtitle": subtitle,
        "category": category,
        "thumb": "%s/cover.png" % pack_id,
        "pages": [
            {"id": pid, "title": ptitle,
             "image": "%s/%s.png" % (pack_id, pid),
             "thumb": "%s/%s_thumb.png" % (pack_id, pid)}
            for pid, ptitle in pages
        ],
    }
