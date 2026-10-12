"""Builds the GenQuest Games wordmark logo (SVG) with letters converted to outlines.

Usage: python3 build_logo.py  ->  writes genquest-games-logo.svg next to this script.
"""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONT = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"
OUT = Path(__file__).with_name("genquest-games-logo.svg")

font = TTFont(FONT)
gs = font.getGlyphSet()
cmap = font.getBestCmap()
UPM = font["head"].unitsPerEm
INK = "#0b0418"


def glyph(ch, size, x, baseline):
    """Return (svg path d, advance, bbox) for a character at a position/size."""
    name = cmap[ord(ch)]
    s = size / UPM
    t = (s, 0, 0, -s, x, baseline)
    pen = SVGPathPen(gs)
    gs[name].draw(TransformPen(pen, t))
    bp = BoundsPen(gs)
    gs[name].draw(TransformPen(bp, t))
    return pen.getCommands(), gs[name].width * s, bp.bounds


def layout(text, sizes, baseline, tracking):
    """Lay out text left-to-right; sizes maps index -> font size."""
    x, items = 0.0, []
    for i, ch in enumerate(text):
        size = sizes(i, ch)
        if ch == " ":
            x += size * 0.38
            continue
        d, adv, bb = glyph(ch, size, x, baseline)
        items.append(dict(ch=ch, d=d, bb=bb, hero=size > 200))
        x += adv + tracking
    return items, x - tracking


# ---- Wordmark: the two G's are the heroes inside the full name -------------
NAME = "GenQuest Games"
HERO, BODY, BASE = 300, 168, 0
hero_idx = {0, 9}
items, width = layout(NAME, lambda i, ch: HERO if i in hero_idx else BODY, BASE, 2)

W, H = 1200, 600
target_w = 960
scale = target_w / width
ox = (W - target_w) / 2
oy = 330  # baseline in canvas coords
wordmark_tf = f"translate({ox:.1f} {oy}) scale({scale:.4f})"

# ---- Tagline -----------------------------------------------------------------
TAG = "MOBILE GAMES"
tag_items, tag_w = layout(TAG, lambda i, ch: 40, 0, 7)

defs, shadow, outline, fill, gloss = [], [], [], [], []
palettes = [("#ffe14d", "#ff8a1f", "#ff2e63"), ("#5ff8ff", "#2fa8ff", "#8a3dff")]
hero_n = 0
for it in items:
    d = it["d"]
    shadow.append(f'<path d="{d}"/>')
    outline.append(f'<path d="{d}"/>')
    if it["hero"]:
        x0, y0, x1, y1 = it["bb"]
        a, b, c = palettes[hero_n]
        gid = f"hero{hero_n}"
        defs.append(
            f'<linearGradient id="{gid}" x1="{x0:.0f}" y1="{y0:.0f}" x2="{x1:.0f}" y2="{y1:.0f}" '
            f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="{a}"/>'
            f'<stop offset="0.5" stop-color="{b}"/><stop offset="1" stop-color="{c}"/></linearGradient>'
        )
        defs.append(f'<clipPath id="clip{hero_n}"><path d="{d}"/></clipPath>')
        fill.append(f'<path d="{d}" fill="url(#{gid})"/>')
        # glossy highlight across the upper part of each hero G
        gy = y0 + (y1 - y0) * 0.42
        gloss.append(
            f'<g clip-path="url(#clip{hero_n})"><path d="M {x0-20:.0f} {y0-20:.0f} H {x1+20:.0f} '
            f'V {gy-30:.0f} Q {(x0+x1)/2:.0f} {gy+10:.0f} {x0-20:.0f} {gy-10:.0f} Z" fill="#fff" opacity="0.28"/></g>'
        )
        hero_n += 1
    else:
        fill.append(f'<path d="{d}" fill="#ffffff"/>')

tag_paths = "".join(f'<path d="{it["d"]}"/>' for it in tag_items)
pill_w = tag_w + 120
sparkle = "M0 -26 L7 -7 L26 0 L7 7 L0 26 L-7 7 L-26 0 L-7 -7 Z"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
  <title>GenQuest Games</title>
  <defs>
    <linearGradient id="screen" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#4a1f96"/><stop offset="1" stop-color="#1a0b3a"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="45%" r="55%">
      <stop offset="0" stop-color="#b14dff" stop-opacity="0.55"/><stop offset="1" stop-color="#b14dff" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="pill" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ff3d7f"/><stop offset="1" stop-color="#c2185b"/>
    </linearGradient>
    {"".join(defs)}
  </defs>

  <!-- Landscape smartphone frame: the "mobile" in mobile games -->
  <rect x="62" y="46" width="1076" height="460" rx="78" fill="{INK}"/>
  <rect x="300" y="38" width="90" height="14" rx="7" fill="{INK}"/>
  <rect x="410" y="38" width="60" height="14" rx="7" fill="{INK}"/>
  <rect x="86" y="70" width="1028" height="412" rx="58" fill="url(#screen)"/>
  <rect x="86" y="70" width="1028" height="412" rx="58" fill="url(#glow)"/>
  <rect x="96" y="232" width="14" height="88" rx="7" fill="#2b1556"/>

  <!-- Screen decorations: d-pad, action buttons, sparkles -->
  <g opacity="0.22" fill="#ffffff">
    <rect x="148" y="400" width="22" height="58" rx="5"/><rect x="130" y="418" width="58" height="22" rx="5"/>
    <circle cx="1032" cy="412" r="13"/><circle cx="1060" cy="438" r="13"/><circle cx="1004" cy="438" r="13"/><circle cx="1032" cy="464" r="13" opacity="0"/>
  </g>
  <g fill="#fff6c2" stroke="{INK}" stroke-width="4" stroke-linejoin="round">
    <path transform="translate(160 128)" d="{sparkle}"/>
    <path transform="translate(1048 132) scale(0.75)" d="{sparkle}"/>
    <path transform="translate(1000 300) scale(0.5)" d="{sparkle}"/>
  </g>

  <!-- Wordmark: full company name, the two G's highlighted -->
  <g transform="{wordmark_tf}" stroke-linejoin="round">
    <g fill="{INK}" stroke="{INK}" stroke-width="34" transform="translate(9 13)">{"".join(shadow)}</g>
    <g fill="{INK}" stroke="{INK}" stroke-width="30">{"".join(outline)}</g>
    {"".join(fill)}
    {"".join(gloss)}
  </g>

  <!-- Tagline pill -->
  <g transform="translate({W/2:.1f} 520)">
    <rect x="{-pill_w/2:.1f}" y="-38" width="{pill_w:.1f}" height="76" rx="38" fill="url(#pill)" stroke="{INK}" stroke-width="8"/>
    <g transform="translate({-tag_w/2:.1f} 15)" fill="#ffffff" stroke="{INK}" stroke-width="5" paint-order="stroke" stroke-linejoin="round">{tag_paths}</g>
  </g>
</svg>
'''
OUT.write_text(svg)
print("wrote", OUT)
