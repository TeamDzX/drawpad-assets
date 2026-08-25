"""Contact sheet of every dot-to-dot path, drawn connected, to eyeball shape quality."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import packlib, shapes_dottodot as S, gen_dottodot as G

CELL = 300
items = [(pid, name, spec) for pid, pack in S.PACKS.items() for name, spec in pack.items()]
cols = 8
rows = (len(items) + cols - 1) // cols
sheet = Image.new("RGB", (cols * CELL, rows * CELL), "white")
sd = ImageDraw.Draw(sheet)
f = packlib.font(packlib.FONT_BOLD, 20)

G.BOX = (30, 46, CELL - 30, CELL - 20)
for i, (pid, name, spec) in enumerate(items):
    cell = Image.new("RGB", (CELL, CELL), "white")
    d = ImageDraw.Draw(cell)
    tx = G.fit(spec)
    for stroke in spec.get("details", []):
        d.line([tx(p) for p in stroke], fill=(180, 180, 180), width=2, joint="curve")
    poly = G.subdivide(spec["path"], spec.get("step", 0.16))
    pts = [tx(p) for p in poly]
    d.line(pts + [pts[0]], fill=(0, 0, 0), width=3, joint="curve")
    for p in pts:
        d.ellipse([p[0]-3, p[1]-3, p[0]+3, p[1]+3], fill=(200, 30, 30))
    d.text((CELL/2, 18), "%s/%s" % (pid.split('_')[1], name), font=f,
           fill=(90, 90, 90), anchor="mm")
    d.rectangle([0, 0, CELL-1, CELL-1], outline=(225, 225, 225))
    sheet.paste(cell, ((i % cols) * CELL, (i // cols) * CELL))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_solutions.png")
sheet.save(out)
print("wrote", out, sheet.size, len(items), "shapes")
