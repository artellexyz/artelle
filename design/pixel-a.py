#!/usr/bin/env python3
"""artelle.xyz — pixel "A" mark: cursive capital A whose stem rises into a pixel flower.

Grids are 32x32 ASCII. Legend:
  .  empty            #  ink (letter / stem)
  L  leaf             l  leaf light
  F  flower dark/outline   f  flower mid   h  flower highlight   y  flower centre

Run:  python3 design/pixel-a.py   -> writes assets/brand/pixel/*.svg + design/pixel-a.html
      python3 design/pixel-a.py --png /tmp/px   -> also writes PNG previews for eyeballing
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_SVG = os.path.join(ROOT, "assets", "brand", "pixel")
OUT_HTML = os.path.join(ROOT, "design", "pixel-a.html")

N = 32

def blank():
    return [["."] * N for _ in range(N)]

def put(grid, r, c, ch):
    if 0 <= r < N and 0 <= c < N:
        grid[r][c] = ch

def stamp(grid, sprite, r0, c0):
    for dr, row in enumerate(sprite):
        for dc, ch in enumerate(row):
            if ch != ".":
                put(grid, r0 + dr, c0 + dc, ch)

def hline(grid, r, c1, c2, ch="#"):
    for c in range(min(c1, c2), max(c1, c2) + 1):
        put(grid, r, c, ch)

def vline(grid, c, r1, r2, ch="#"):
    for r in range(min(r1, r2), max(r1, r2) + 1):
        put(grid, r, c, ch)

def ring(grid, cx, cy, rx, ry, inner, ch="#", cmax=None):
    """Elliptical ring, ~2px thick. cmax clips columns to the right (bowl merges into stem)."""
    for r in range(N):
        for c in range(N):
            if cmax is not None and c > cmax:
                continue
            d = ((c - cx) / rx) ** 2 + ((r - cy) / ry) ** 2
            if inner <= d <= 1.0:
                put(grid, r, c, ch)

# ---------------------------------------------------------------- flowers
# Rose: outer blob with two petal tips at the top, one continuous spiral winding in. 11 wide x 10 tall.
ROSE = [
    "..FFF.FFF..",
    ".FfffFfffF.",
    "FffFFFFfffF",
    "FfFffffFffF",
    "FfFfFFfFffF",
    "FfFfFhfFffF",
    "FfFfffFfffF",
    "FffFffffffF",
    ".FffFFFFfF.",
    "..FfffffFF.",
    "...FFFFF...",
]

# Rosebud, side view: three petal tips, cup, two sepals. 9 wide x 10 tall. Reads as "rose" even at 16px.
BUD = [
    "..F..F..F..",
    ".FfFFfFFfF.",
    ".FffFfFffF.",
    ".FfffffffF.",
    "FFffffffhFF",
    "LFffffffhFL",
    ".LFffffhFL.",
    "..LFfffFL..",
    "...LFFFL...",
    "....LLL....",
]

TULIP = [
    ".F....F....F.",
    "FfF..FfF..FfF",
    "FffF.FfF.FffF",
    "FfffFffFFfffF",
    "FfffffffffhfF",
    "FfffffffffhfF",
    ".FffffffffhF.",
    ".FfffffffffF.",
    "..FfffffffF..",
    "...FfffffF...",
    "....FFFFF....",
]

BLOSSOM = [
    "....FFF....",
    "...FfffF...",
    ".FFFfffFFF.",
    "FfffFfFfffF",
    "FffffhffffF",
    "FfffhyhfffF",
    ".FfffhfffF.",
    "..FffFffF..",
    ".FfffFfffF.",
    ".FfffFfffF.",
    "..FFF.FFF..",
]

# ---------------------------------------------------------------- letters

def circle_ring(g, cx, cy, r_out, r_in, cmax, ch="#"):
    for r in range(N):
        for c in range(N):
            if c > cmax: continue
            dx = c + 0.5 - cx; dy = r + 0.5 - cy
            d2 = dx*dx + dy*dy
            if r_in*r_in <= d2 <= r_out*r_out:
                put(g, r, c, ch)

A_ROWS = {
    # row: list of (c1, c2) inclusive spans, ink
    16: [(10,15),(19,20)],
    17: [(8,20)],
    18: [(7,10),(17,20)],
    19: [(6,8),(18,20)],
    20: [(6,7),(19,20)],
    21: [(5,7),(19,20)],
    22: [(5,6),(19,20)],
    23: [(5,6),(19,20)],
    24: [(5,6),(19,20)],
    25: [(5,6),(19,20)],
    26: [(5,7),(19,20)],
    27: [(6,7),(19,20)],
    28: [(6,8),(18,20)],
    29: [(7,10),(17,20)],
    30: [(8,20)],
    31: [(10,15),(19,22)],
}

def cursive_a():
    """Cursive a: hand-drawn 2px circular bowl (cols 5-20, rows 16-31) whose right side is the 2px stem,
    exit tail bottom-right. A 1px stalk grows out of the stem top, leaning right; a leaf hangs off it."""
    g = blank()
    for r, spans in A_ROWS.items():
        for c1, c2 in spans:
            hline(g, r, c1, c2)
    put(g, 30, 23, "#"); put(g, 29, 24, "#")          # exit tail lift
    # stalk: 1px, leaves the stem top at 45 degrees so the letter stays an "a", not a "d"
    for (r, c) in [(15,21),(14,22),(13,23),(12,24),(11,25)]:
        put(g, r, c, "#")
    # leaf off the stalk, pointing up-left
    for (r, c, ch) in [(13,21,"L"),(12,20,"L"),(12,21,"l"),(11,19,"L"),(11,20,"l"),(11,21,"L"),(10,19,"L"),(10,20,"L")]:
        put(g, r, c, ch)
    return g, (11, 25)

def italic_A():
    """Broad-nib italic capital A: heavy 2px right stem (cols 19-20, rows 15-31), thin 1px left leg,
    thin 1px crossbar. The stem continues above the apex as the 1px stalk."""
    g = blank()
    vline(g, 19, 15, 31); vline(g, 20, 15, 31)
    # left leg: from (15,18) to (31,5), 1px diagonal
    for r in range(15, 32):
        c = round(18 - (r - 15) * 13 / 16)
        put(g, r, c, "#")
    # crossbar
    hline(g, 25, 11, 18)
    # foot serifs / exit tail
    for (r, c) in [(31,21),(31,22),(30,23)]:
        put(g, r, c, "#")
    put(g, 31, 4, "#")
    # stalk
    for (r, c) in [(14,20),(13,20),(12,21),(11,22)]:
        put(g, r, c, "#")
    for (r, c, ch) in [(13,19,"L"),(12,18,"L"),(12,19,"l"),(11,17,"L"),(11,18,"l"),(11,19,"L"),(10,17,"L"),(10,18,"L")]:
        put(g, r, c, ch)
    return g, (11, 22)

# ---------------------------------------------------------------- palettes

PAPER = "#F4F1E9"
INK = "#1C1712"
ULTRA = "#33439B"; ULTRA_DEEP = "#273479"; ULTRA_LIGHT = "#8F9AD6"

PALETTES = {
    # name: {char: fill or None}
    "ink":    {"#": INK, "L": INK, "l": None, "F": INK, "f": None, "h": None, "y": INK},
    "ultra":  {"#": INK, "L": ULTRA_DEEP, "l": ULTRA, "F": ULTRA_DEEP, "f": ULTRA, "h": ULTRA_LIGHT, "y": ULTRA_LIGHT},
    "colour": {"#": INK, "L": "#4F7A3F", "l": "#86B26E", "F": "#8E2C3D", "f": "#C9485C", "h": "#F0A3B0", "y": "#E3B04B"},
}
# ink-on-dark (reverse) variants swap ink for paper
REVERSE = {"#": PAPER, "L": PAPER, "l": None, "F": PAPER, "f": None, "h": None, "y": PAPER}
# colour mark for dark grounds: paper letter, same rose, slightly lifted leaves
REVERSE_COLOUR = {"#": PAPER, "L": "#5B8A49", "l": "#9CC585", "F": "#8E2C3D", "f": "#C9485C", "h": "#F0A3B0", "y": "#E3B04B"}

# the mark adopted for the site (2026-09-06): italic capital A, rose, colour
ADOPTED = "italic-rose"
IMG_DIR = os.path.join(ROOT, "assets", "img")
TEMPLATE = os.path.join(ROOT, "templates", "page.html")

# ---------------------------------------------------------------- render

def rects_for(grid, palette):
    rects = []
    # merge horizontal runs of the same fill for a smaller file
    for r in range(N):
        c = 0
        while c < N:
            fill = palette.get(grid[r][c])
            if fill is None:
                c += 1; continue
            c2 = c
            while c2 + 1 < N and palette.get(grid[r][c2 + 1]) == fill:
                c2 += 1
            rects.append(f'<rect x="{c}" y="{r}" width="{c2 - c + 1}" height="1" fill="{fill}"/>')
            c = c2 + 1
    return "".join(rects)

def to_svg(grid, palette, size=None):
    attrs = f' width="{size}" height="{size}"' if size else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {N} {N}"{attrs} '
            f'shape-rendering="crispEdges">' + rects_for(grid, palette) + "</svg>")

def to_png(grid, palette, path, scale=12, bg=PAPER):
    from PIL import Image
    im = Image.new("RGB", (N * scale, N * scale), bg)
    px = im.load()
    for r in range(N):
        for c in range(N):
            fill = palette.get(grid[r][c])
            if not fill:
                continue
            rgb = tuple(int(fill[i:i + 2], 16) for i in (1, 3, 5))
            for y in range(r * scale, (r + 1) * scale):
                for x in range(c * scale, (c + 1) * scale):
                    px[x, y] = rgb
    im.save(path)

def show(grid):
    return "\n".join("".join(row) for row in grid)

# ---------------------------------------------------------------- marks

def place_flower(g, sprite, anchor, bottom_center_col):
    """Stamp sprite so that its bottom-centre lands directly above `anchor` (row, col)."""
    ar, ac = anchor
    h = len(sprite); w = max(len(s) for s in sprite)
    r0 = ar - h
    c0 = ac - bottom_center_col
    stamp(g, sprite, r0, c0)

def build_marks():
    marks = {}
    for lname, letter in (("cursive", cursive_a), ("italic", italic_A)):
        for fname, sprite, bcc in (("rose", ROSE, 5), ("bud", BUD, 5), ("tulip", TULIP, 6), ("blossom", BLOSSOM, 5)):
            g, anchor = letter()
            place_flower(g, sprite, anchor, bcc)
            marks[f"{lname}-{fname}"] = g
    return marks


# ---------------------------------------------------------------- proof sheet

FLOWER_COPY = {
    "rose":    ("Rose", "Two petal lobes and a single spiral winding in. The one she named first; the payoff at the top of the stem."),
    "tulip":   ("Tulip", "Three tips, one cup. Ties straight to the tulip watercolour in the catalogue and reads at 16px."),
    "blossom": ("Blossom", "Five petals and a gold centre, like the red-blossom tree in the Mosque piece. The clearest flower in ink."),
    "bud":     ("Bud", "Side-view rosebud with sepals. The quietest option; leans tulip in one colour."),
}
LETTER_COPY = {
    "italic":  ("Italic A", "Broad-nib capital: heavy 2px stem, hairline left leg and crossbar. The stem runs straight through the apex and becomes the stalk."),
    "cursive": ("Cursive a", "Round 2px bowl with an exit tail, matching the lowercase wordmark. The stalk leaves the shoulder at 45 degrees so it stays an a, not a d."),
}

def img(name, pal, size, label=""):
    alt = f' alt="{label}"' if label else ' alt="" aria-hidden="true"'
    return f'<img src="../assets/brand/pixel/{name}-{pal}.svg" width="{size}" height="{size}"{alt}>'

def write_html(marks):
    plates = []
    n = 0
    roman = ["I","II","III","IV","V","VI","VII","VIII"]
    for lname, fname in [(l, f) for l in ("italic", "cursive") for f in ("rose", "tulip", "blossom", "bud")]:
        g = marks[f"{lname}-{fname}"]
        ltitle, lcopy = LETTER_COPY[lname]; ftitle, fcopy = FLOWER_COPY[fname]
        rec = '<span class="rec">Adopted · site mark</span>' if f"{lname}-{fname}" == ADOPTED else ""
        key = f"{lname}-{fname}"
        trio = "".join(
            f'<figure><div class="tile">{img(key, p, 160, f"{ltitle} {ftitle}, {cap}")}</div><figcaption>{cap}</figcaption></figure>'
            for p, cap in (("ink", "Ink"), ("ultra", "Ultramarine"), ("colour", "Colour"))
        )
        small = "".join(f'<span class="sizebox">{img(key, "colour", s)}{img(key, "ink", s)}</span>' for s in (16, 24, 32, 48))
        insitu = (f'<span class="insitu">{img(key, "colour", 26)}<span class="wm">artelle</span></span>'
                  f'<span class="insitu">{img(key, "ink", 26)}<span class="wm">artelle</span></span>')
        rev = f'<span class="rev">{img(key, "reverse", 44)}</span>'
        files = ", ".join(f'<a href="../assets/brand/pixel/{lname}-{fname}-{p}.svg">{p}</a>' for p in ("ink", "ultra", "colour", "reverse"))
        plates.append(f"""
<section class="plate" id="{lname}-{fname}">
  <div class="fieldname"><span class="plate-no">Plate {roman[n]} · {ltitle} · {ftitle}</span>{rec}</div>
  <div class="fieldwrap">
    <i class="crop c1"></i><i class="crop c2"></i><i class="crop c3"></i><i class="crop c4"></i>
    <div class="field">{trio}</div>
  </div>
  <div class="plate-body">
    <h2 class="pname">{ltitle} <em>&amp;</em> {ftitle}</h2>
    <p class="prat">{lcopy} {fcopy}</p>
  </div>
  <div class="strip">
    <div class="chipset"><span>16 / 24 / 32 / 48</span>{small}</div>
    <div class="chipset"><span>Header</span>{insitu}</div>
    <div class="chipset"><span>Reverse</span>{rev}</div>
    <div class="chipset"><span>SVG</span><span class="files">{files}</span></div>
  </div>
</section>""")
        n += 1

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Artelle Pixel A Proofs</title>
<meta name="description" content="Pixel A mark proofs for artelle.xyz: a capital A whose stem rises into a pixel flower.">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400&family=Cormorant+Garamond:wght@600&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root{{--paper:#F3F0E7;--field:#FAF8F1;--ink:#1C1712;--ink-2:#6B6353;--hair:#D8D1BF}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--paper);color:var(--ink);font-family:"Instrument Sans",-apple-system,"Helvetica Neue",sans-serif;font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}}
  a{{color:inherit}}
  .wrap{{max-width:880px;margin:0 auto;padding:0 28px}}
  header{{padding:44px 0 30px;border-bottom:2px solid var(--ink)}}
  .mast{{display:flex;justify-content:space-between;align-items:flex-end;gap:24px}}
  .brand{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:2rem;letter-spacing:.01em}}
  .ticket{{text-align:right;font-size:.66rem;font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:var(--ink-2)}}
  .intro{{margin:26px 0 0;font-family:Fraunces,Georgia,serif;font-style:italic;font-weight:400;font-size:1.25rem;max-width:40ch;text-wrap:balance}}
  .toc{{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:22px;font-size:.72rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-2)}}
  .toc a{{text-decoration:none;border-bottom:1px solid var(--hair)}}
  .plate{{padding:58px 0 10px}}
  .plate + .plate{{border-top:1px solid var(--hair)}}
  .fieldname{{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:16px}}
  .plate-no{{font-size:.68rem;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--ink-2)}}
  .rec{{font-size:.62rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--paper);background:var(--ink);padding:5px 11px;border-radius:2px}}
  .fieldwrap{{position:relative;padding:22px}}
  .crop{{position:absolute;width:16px;height:16px;border-color:var(--ink-2);border-style:solid;border-width:0;opacity:.75}}
  .c1{{top:0;left:0;border-top-width:1px;border-left-width:1px}} .c2{{top:0;right:0;border-top-width:1px;border-right-width:1px}}
  .c3{{bottom:0;left:0;border-bottom-width:1px;border-left-width:1px}} .c4{{bottom:0;right:0;border-bottom-width:1px;border-right-width:1px}}
  .field{{background:var(--field);border:1px solid var(--hair);display:grid;grid-template-columns:repeat(3,1fr);gap:0;padding:40px 24px 28px}}
  .field figure{{display:flex;flex-direction:column;align-items:center;gap:14px}}
  .field figure + figure{{border-left:1px solid var(--hair)}}
  .tile img{{display:block;image-rendering:pixelated}}
  img{{display:block}}
  figcaption{{font-size:.64rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-2)}}
  .plate-body{{display:grid;grid-template-columns:minmax(140px,2fr) 3fr;gap:20px 36px;padding:20px 0 8px}}
  .pname{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:1.45rem;line-height:1.15}}
  .pname em{{font-weight:400;color:var(--ink-2)}}
  .prat{{font-size:.92rem;color:var(--ink-2);max-width:52ch}}
  .strip{{display:flex;align-items:center;gap:26px;padding:14px 0 34px;flex-wrap:wrap}}
  .chipset{{display:flex;align-items:center;gap:12px}}
  .chipset > span:first-child{{font-size:.64rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-2)}}
  .sizebox{{display:inline-flex;align-items:center;gap:4px;margin-right:6px}}
  .insitu{{display:inline-flex;align-items:center;gap:8px;margin-right:10px}}
  .wm{{font-family:"Cormorant Garamond",Georgia,serif;font-weight:600;font-size:1.42rem;line-height:1;letter-spacing:.005em}}
  .rev{{background:var(--ink);border-radius:3px;padding:9px 11px;display:inline-flex}}
  .files{{font-size:.72rem;color:var(--ink-2)}}
  .files a{{text-decoration:none;border-bottom:1px solid var(--hair);margin-right:2px}}
  footer{{border-top:2px solid var(--ink);margin-top:40px;padding:26px 0 60px;display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}}
  footer p{{font-size:.68rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--ink-2)}}
  @media (max-width:640px){{
    .plate-body{{grid-template-columns:1fr}} .mast{{flex-direction:column;align-items:flex-start}} .ticket{{text-align:left}}
    .field{{grid-template-columns:1fr;gap:28px}} .field figure + figure{{border-left:0;border-top:1px solid var(--hair);padding-top:24px}}
    .tile svg{{width:120px;height:120px}}
  }}
</style>
</head>
<body>
<div class="wrap">

<header>
  <div class="mast">
    <div class="brand">artelle</div>
    <div class="ticket">Mark proofs · Sheet 2 · Pixel A · Sep 2026</div>
  </div>
  <p class="intro">A capital A drawn on a 32-pixel grid. The stem keeps going past the letter and opens into a flower. Two letterforms, four flowers, three colourways each.</p>
  <nav class="toc">{" ".join(f'<a href="#{l}-{f}">{roman[i]} {LETTER_COPY[l][0]} · {FLOWER_COPY[f][0]}</a>' for i,(l,f) in enumerate([(l,f) for l in ("italic","cursive") for f in ("rose","tulip","blossom","bud")]))}</nav>
</header>
{"".join(plates)}
<footer>
  <p>Proofed for artelle.xyz</p>
  <p>32 × 32 grid · crisp-edge SVG · source design/pixel-a.py</p>
</footer>

</div>
</body>
</html>
"""
    with open(OUT_HTML, "w") as f:
        f.write(html)
    print(f"wrote {OUT_HTML}")


# ---------------------------------------------------------------- adopt: site assets + template header

def write_adopted(marks):
    g = marks[ADOPTED]
    head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" shape-rendering="crispEdges" role="img" aria-label="{label}">'
    with open(os.path.join(IMG_DIR, "logo.svg"), "w") as f:
        f.write(head.format(label="Artelle mark") + "<!-- Pixel A: italic capital A, stem rising into a rose. Source: design/pixel-a.py -->"
                + rects_for(g, PALETTES["colour"]) + "</svg>\n")
    with open(os.path.join(IMG_DIR, "logo-reverse.svg"), "w") as f:
        f.write(head.format(label="Artelle mark, reversed") + "<!-- Pixel A for dark grounds -->"
                + rects_for(g, REVERSE_COLOUR) + "</svg>\n")
    # favicon: paper rounded square with a 2px margin so the ink letter survives dark tab bars
    with open(os.path.join(IMG_DIR, "favicon.svg"), "w") as f:
        f.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" shape-rendering="crispEdges">'
                f'<rect width="36" height="36" rx="6" fill="{PAPER}"/><g transform="translate(2 2)">'
                + rects_for(g, PALETTES["colour"]) + "</g></svg>\n")
    # header mark, inline in the shared template between <!-- mark --> ... <!-- /mark -->
    tpl = open(TEMPLATE).read()
    inline = ('<svg viewBox="0 0 32 32" shape-rendering="crispEdges" aria-hidden="true">'
              + rects_for(g, PALETTES["colour"]) + "</svg>")
    new = re.sub(r"<!-- mark -->.*?<!-- /mark -->", f"<!-- mark -->{inline}<!-- /mark -->", tpl, flags=re.S)
    if new == tpl and "<!-- mark -->" not in tpl:
        raise SystemExit("templates/page.html has no <!-- mark --> markers; add them around the brand svg")
    open(TEMPLATE, "w").write(new)
    print(f"adopted {ADOPTED}: logo.svg, logo-reverse.svg, favicon.svg, template header")

if __name__ == "__main__":
    marks = build_marks()
    png_dir = None
    if "--png" in sys.argv:
        png_dir = sys.argv[sys.argv.index("--png") + 1]
        os.makedirs(png_dir, exist_ok=True)
    os.makedirs(OUT_SVG, exist_ok=True)
    for name, g in marks.items():
        if "--ascii" in sys.argv:
            print(f"--- {name}\n{show(g)}\n")
        for pal_name, pal in PALETTES.items():
            with open(os.path.join(OUT_SVG, f"{name}-{pal_name}.svg"), "w") as f:
                f.write(to_svg(g, pal))
            if png_dir:
                to_png(g, pal, os.path.join(png_dir, f"{name}-{pal_name}.png"))
        with open(os.path.join(OUT_SVG, f"{name}-reverse.svg"), "w") as f:
            f.write(to_svg(g, REVERSE))
    print(f"wrote {len(marks) * 4} svgs to {OUT_SVG}")
    write_html(marks)
    write_adopted(marks)
    if png_dir:
        from PIL import Image
        names = list(marks); pals = list(PALETTES)
        tile = N * 12; pad = 20
        W = pad + len(pals) * (tile + pad) + 2 * (16 + 32 + 48 + 20)
        sheet = Image.new("RGB", (W, pad + len(names) * (tile + pad)), PAPER)
        for i, n in enumerate(names):
            for j, p in enumerate(pals):
                sheet.paste(Image.open(os.path.join(png_dir, f"{n}-{p}.png")), (pad + j * (tile + pad), pad + i * (tile + pad)))
            x = pad + len(pals) * (tile + pad); y = pad + i * (tile + pad) + tile // 2
            for p in ("colour", "ink"):
                for s in (16, 32, 48):
                    im = Image.open(os.path.join(png_dir, f"{n}-{p}.png")).resize((s, s), Image.NEAREST)
                    sheet.paste(im, (x, y - s // 2)); x += s + 8
                x += 12
        sheet.save(os.path.join(png_dir, "sheet.png")); print("sheet", sheet.size)
