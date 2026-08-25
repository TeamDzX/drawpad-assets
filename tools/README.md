# Pack generation tools

Everything that builds a DrawPad content pack lives here. The first sixteen
packs were generated ad hoc and the scripts were never kept, so re-cutting a
pack meant re-inventing the prompt and the post-processing. That is what these
scripts exist to prevent — **the prompt is part of the asset**.

## What builds what

| Pack category | Built by | Why |
|---|---|---|
| `coloring`, `mandala` | `gen_lineart.py` (ComfyUI / Flux 2 Klein) | Flux draws clean closed line art; this is what it is good at. |
| `dottodot` | `gen_dottodot.py` (code) | A diffusion model cannot render legible sequential numbers, and the dots must lie on a path that closes into the subject. |
| `learning` | `gen_learning.py` (code) | A tracing sheet is worthless if the letterform is subtly wrong. Flux also garbles hanzi outright. |

## Usage

```sh
python3 tools/gen_lineart.py                      # every ComfyUI pack
python3 tools/gen_lineart.py coloring_ocean       # one pack
python3 tools/gen_lineart.py --page 03 --reseed 7 coloring_ocean   # reroll a bad page

python3 tools/gen_dottodot.py [pack_id ...]
python3 tools/gen_learning.py [pack_id ...]
```

Each script writes pages, `_thumb`s, `cover.png` and `cover_web.jpg`, then
upserts its entry into `packs/packs.json`. Entitlement is per *category*
(`PackCategory.unlockProductID` in the app), so a new pack ships the moment the
CDN serves the updated manifest — no new IAP, no app resubmission.

## Adding a pack

- **Coloring / mandala** — add a dict to `COLORING_PACKS` or `MANDALA_PACKS` in
  `specs_lineart.py` and run `gen_lineart.py <id>`. Keep the shared style
  strings alone; they are what makes a pack cut a year from now sit next to the
  launch packs.
- **Dot-to-dot** — add an entry to `shapes_dottodot.py`. Points are normalised
  0..1 with y down, listed in connection order, and **are** the dots. Place them
  by hand at the corners and inflections that carry the silhouette; `step`
  controls how long a straight run may get before the renderer fills it in.
  Details are grey finishing marks (eyes, wheels) and are never numbered.
- **Learning** — add a page builder in `gen_learning.py` and reuse
  `header()` / `ruled_row()` / `trace_rows()` so the Learning tab stays uniform.

## Checking your work before you push

Dots alone are hard to judge. Render the paths connected:

```sh
python3 tools/preview_dottodot.py     # writes tools/_solutions.png
```

Every subject should be recognisable at thumbnail size. Four of the original
eight animals were not, and it only showed up once they were drawn connected.

## After generating

1. `python3 tools/validate.py` — every manifest path must resolve.
2. `python3 tools/preview_dottodot.py` if you touched a dot-to-dot outline.
3. Refresh the app's offline fallback so a first launch without network still
   lists the full catalog (it is a copy of this manifest, and it had drifted
   five packs behind before anyone noticed):

   ```sh
   cp packs/packs.json "../Drawing App/Drawing App/packs.json"
   ```

   Only the manifest is bundled — the images always come from the CDN.
4. Commit and push, then purge the jsDelivr cache (see below).

## Notes

- `comfy_gen.py` lives at `~/.claude/scripts/imagegen/comfy_gen.py` and holds a
  personal server token — it is loaded by path and deliberately **not** vendored
  into this repo.
- Seeds derive from `pack_id/page_id`, so reruns reproduce. Use `--reseed N` for
  a malformed page rather than editing a prompt that is fine.
- `.raw/` holds the pre-cleanup ComfyUI output and is gitignored.
- jsDelivr caches `@main` for ~12h. After pushing, purge the manifest:
  `https://purge.jsdelivr.net/gh/TeamDzX/drawpad-assets@main/packs/packs.json`
