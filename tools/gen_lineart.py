#!/usr/bin/env python3
"""
Generate the ComfyUI-backed packs (coloring + mandala) end to end.

    python3 tools/gen_lineart.py                    # every pack in specs_lineart
    python3 tools/gen_lineart.py coloring_ocean     # just these
    python3 tools/gen_lineart.py --page 03 coloring_ocean   # redo one page

Writes pages, thumbs, cover and cover_web, then upserts packs.json. Seeds are
derived from pack+page id, so a rerun reproduces the same art unless you pass
--reseed (use that when a page comes back malformed — an extra limb, a stray
letter — rather than editing the prompt).
"""
import argparse
import importlib.util
import os
import sys
import zlib
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import packlib
import specs_lineart as specs

COMFY = os.path.expanduser("~/.claude/scripts/imagegen/comfy_gen.py")

# The generator lives outside the repo (it holds a personal server token and
# must not be committed here), so load it by path.
_spec = importlib.util.spec_from_file_location("comfy_gen", COMFY)
comfy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(comfy)

# The server renders one job at a time; three in flight just keeps its queue
# fed without piling up timeouts.
CONCURRENCY = 3
RAW = os.path.join(packlib.REPO, ".raw")


def seed_for(pack_id, page_id, bump=0):
    return zlib.crc32(("%s/%s" % (pack_id, page_id)).encode()) % 100000 + bump


def build_page(kind, pack_id, page_id, title, page_prompt, reseed=0):
    """Render one page and write it into the pack directory."""
    from PIL import Image
    os.makedirs(RAW, exist_ok=True)
    raw = os.path.join(RAW, "%s_%s.png" % (pack_id, page_id))
    prompt = specs.prompt_for(kind, page_prompt)
    comfy.generate(raw, prompt, seed_for(pack_id, page_id, reseed),
                   width=1024, height=1024)
    img = packlib.clean_lineart(Image.open(raw))
    if kind == "coloring":
        # Mandalas already fill the frame; cartoon subjects drift off-centre.
        img = packlib.trim_to_square(img, margin=0.08)
    packlib.write_page(img, pack_id, page_id)
    print("  page %s/%s  %s" % (pack_id, page_id, title), flush=True)
    return page_id, img


def build_pack(kind, spec, only_page=None, reseed=0):
    print("pack %s (%s)" % (spec["id"], kind), flush=True)
    pages = [p for p in spec["pages"] if only_page in (None, p[0])]
    done = {}
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        futures = [pool.submit(build_page, kind, spec["id"], pid, title, pr, reseed)
                   for pid, title, pr in pages]
        for f in futures:
            pid, img = f.result()
            done[pid] = img

    cover_src = done.get(spec.get("cover", spec["pages"][0][0]))
    if cover_src is not None:
        packlib.write_cover(cover_src, spec["id"])
    packlib.upsert_pack(packlib.pack_entry(
        spec["id"], spec["title"], spec["subtitle"], kind,
        [(pid, title) for pid, title, _ in spec["pages"]]))
    print("  -> packs.json updated", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("packs", nargs="*", help="pack ids (default: all)")
    ap.add_argument("--page", help="only this page id")
    ap.add_argument("--reseed", type=int, default=0,
                    help="offset the seed to reroll a malformed page")
    a = ap.parse_args()

    all_specs = ([("coloring", s) for s in specs.COLORING_PACKS] +
                 [("mandala", s) for s in specs.MANDALA_PACKS])
    todo = [(k, s) for k, s in all_specs if not a.packs or s["id"] in a.packs]
    if not todo:
        sys.exit("no matching packs; known: " +
                 ", ".join(s["id"] for _, s in all_specs))
    for kind, spec in todo:
        build_pack(kind, spec, a.page, a.reseed)


if __name__ == "__main__":
    main()
