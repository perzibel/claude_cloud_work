#!/usr/bin/env python3
"""Procedural comic-book 9:16 lyric clip renderer for "Day Off Saving The World".

Usage: python3 render_clip.py <timeline.json> <song.mp3> <out.mp4> [--preview SECONDS] [--frames t1,t2,...]

Everything is drawn programmatically (PIL + numpy): halftone backgrounds, speed lines,
impact bursts, comic panels, a stylised hero, SFX lettering and word-by-word lyric captions.
Timing comes from the JSON timeline (song-time seconds), so lyric timing can be tweaked
and re-rendered without touching code.
"""
import json, math, random, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "..", "assets", "fonts", "Bangers-Regular.ttf")
W, H, FPS = 1080, 1920, 30

INK = (12, 12, 20); CREAM = (255, 244, 214); GOLD = (255, 196, 20); CRIMSON = (214, 24, 52)
NAVY = (16, 24, 66); BLUE = (20, 120, 255); ELEC = (60, 200, 255); WHITE = (255, 255, 255)
ORANGE = (255, 140, 40); VIOLET = (90, 60, 170); SKIN = (236, 186, 150); HAIR = (60, 36, 22)

_fonts = {}
def font(sz):
    sz = max(8, int(sz))
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(FONT, sz)
    return _fonts[sz]

def ease_out_back(x, k=1.70158):
    x = min(max(x, 0), 1); x -= 1
    return x * x * ((k + 1) * x + k) + 1
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x
def mix(c1, c2, x): return tuple(int(lerp(a, b, min(max(x, 0), 1))) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- backgrounds
def halftone_bg(c_in, c_out, dot, cx=0.5, cy=0.45, spacing=26, seed=0, w=W + 160, h=H + 240):
    """Radial gradient with comic halftone dots, oversized for camera moves."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - cx * w) / w) ** 2 + ((yy - cy * h) / h) ** 2) / 0.75
    d = np.clip(d, 0, 1)[..., None]
    arr = (np.array(c_in) * (1 - d) + np.array(c_out) * d).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")
    dr = ImageDraw.Draw(img)
    for j, y in enumerate(range(0, h, spacing)):
        off = spacing // 2 if j % 2 else 0
        for x in range(off, w, spacing):
            r = (math.hypot((x - cx * w) / w, (y - cy * h) / h) / 0.75) * spacing * 0.42
            if r > 1.2: dr.ellipse([x - r, y - r, x + r, y + r], fill=dot)
    return img

def starfield(img, n=140, seed=3):
    rnd = random.Random(seed); dr = ImageDraw.Draw(img)
    for _ in range(n):
        x, y = rnd.randrange(img.width), rnd.randrange(img.height); r = rnd.choice([1, 2, 2, 3, 4])
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 220))
    return img

def skyline(img, base_y, color, seed=5, win=None):
    rnd = random.Random(seed); dr = ImageDraw.Draw(img); x = -20
    while x < img.width:
        bw = rnd.randint(70, 150); bh = rnd.randint(160, 520)
        dr.rectangle([x, base_y - bh, x + bw, img.height], fill=color, outline=INK, width=5)
        if win:
            for wy in range(base_y - bh + 24, base_y - 20, 44):
                for wx in range(x + 16, x + bw - 20, 34):
                    if rnd.random() < 0.55: dr.rectangle([wx, wy, wx + 14, wy + 20], fill=win)
        x += bw - 4
    return img

# ---------------------------------------------------------------- primitives
def speed_lines(dr, cx, cy, t, color=WHITE, n=46, inner=260, seed=1, width=1.0):
    rnd = random.Random(seed + int(t * 12))
    for i in range(n):
        a = rnd.random() * 2 * math.pi; da = rnd.uniform(0.006, 0.02) * width
        r0 = inner + rnd.uniform(0, 260); r1 = 2400
        pts = [(cx + math.cos(a) * r0, cy + math.sin(a) * r0),
               (cx + math.cos(a - da) * r1, cy + math.sin(a - da) * r1),
               (cx + math.cos(a + da) * r1, cy + math.sin(a + da) * r1)]
        dr.polygon(pts, fill=color)

def burst(dr, cx, cy, r, color, spikes=16, jag=0.38, rot=0.0, outline=INK, ow=10, seed=0):
    rnd = random.Random(seed); pts = []
    for i in range(spikes * 2):
        a = rot + i * math.pi / spikes
        rr = r if i % 2 == 0 else r * (1 - jag * rnd.uniform(0.7, 1.2))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    if outline: dr.polygon(pts, fill=outline)
    s = [(cx + (x - cx) * (1 - ow / max(r, 1)), cy + (y - cy) * (1 - ow / max(r, 1))) for x, y in pts]
    dr.polygon(s, fill=color)

def rays(dr, cx, cy, t, c1, c2, n=18, spin=0.25):
    for i in range(n):
        a0 = t * spin + i * 2 * math.pi / n; a1 = a0 + math.pi / n
        dr.polygon([(cx, cy), (cx + math.cos(a0) * 2600, cy + math.sin(a0) * 2600),
                    (cx + math.cos(a1) * 2600, cy + math.sin(a1) * 2600)], fill=c1 if i % 2 else c2)

def panel(img, box, fill, border=12, angle=0):
    x0, y0, x1, y1 = box
    dr = ImageDraw.Draw(img)
    dr.rectangle([x0 - border, y0 - border, x1 + border, y1 + border], fill=INK)
    dr.rectangle([x0, y0, x1, y1], fill=fill)
    return dr

def text_layer(txt, size, fill, stroke=10, stroke_fill=INK, shadow=8):
    f = font(size)
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    w, h = r - l + shadow + 4, b - t + shadow + 4
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if shadow: d.text((-l + shadow, -t + shadow), txt, font=f, fill=INK, stroke_width=stroke, stroke_fill=INK)
    d.text((-l, -t), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def put(img, layer, cx, cy, scale=1.0, angle=0.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01: return
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    if angle: layer = layer.rotate(angle, resample=Image.BILINEAR, expand=True)
    if alpha < 1.0:
        a = layer.getchannel("A").point(lambda v: int(v * alpha)); layer.putalpha(a)
    img.paste(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)), layer)

def sfx(img, txt, cx, cy, size, fill, t_in, t, angle=-8, burst_col=None, seed=0):
    """Pop-in comic sound effect with overshoot."""
    k = ease_out_back((t - t_in) / 0.22, 2.6)
    if k <= 0: return
    if burst_col:
        burst(ImageDraw.Draw(img), cx, cy, size * 1.25 * k, burst_col, seed=seed, rot=seed * 0.3)
    put(img, text_layer(txt, size, fill), cx, cy, k, angle)

# ---------------------------------------------------------------- hero (stylised comic figure)
def hero(img, cx, cy, s, pose="stand", t=0.0, tremble=0.0, mood=0.0, cape_col=CRIMSON):
    """cx,cy = pelvis. s = scale (1 ~ 520px tall). mood 0=happy, 1=exhausted."""
    dr = ImageDraw.Draw(img); ow = max(3, int(7 * s))
    jx = math.sin(t * 61) * tremble * 6 * s; jy = math.cos(t * 47) * tremble * 4 * s
    cx += jx; cy += jy
    P = lambda x, y: (cx + x * s, cy + y * s)
    def poly(pts, fill): dr.polygon([P(*p) for p in pts], fill=fill, outline=INK, width=ow)
    def limb(a, b, wdt, fill):
        (x0, y0), (x1, y1) = P(*a), P(*b)
        ang = math.atan2(y1 - y0, x1 - x0); nx, ny = -math.sin(ang) * wdt * s / 2, math.cos(ang) * wdt * s / 2
        q = [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny), (x0 - nx, y0 - ny)]
        dr.polygon(q, fill=fill, outline=INK, width=ow)
        r = wdt * s / 2 + ow / 2; dr.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=fill, outline=INK, width=ow)
    slump = 26 * mood
    # cape
    wv = math.sin(t * 5.5) * 30 * (1 - 0.7 * mood)
    poly([(-58, -205 + slump), (58, -205 + slump), (110 + wv, 120 + 40 * mood), (20 + wv * .5, 150), (-80 + wv, 135), (-120 + wv, 110 + 40 * mood)], cape_col)
    # legs
    limb((-30, 0), (-48, 120), 46, NAVY); limb((30, 0), (48, 120), 46, NAVY)
    limb((-48, 120), (-52, 205), 44, NAVY); limb((48, 120), (52, 205), 44, NAVY)
    poly([(-80, 190), (-24, 190), (-24, 222), (-86, 222)], BLUE); poly([(24, 190), (80, 190), (86, 222), (24, 222)], BLUE)
    # torso
    poly([(-66, -200 + slump), (66, -200 + slump), (44, 0), (-44, 0)], NAVY)
    poly([(-44, -8), (44, -8), (46, 10), (-46, 10)], GOLD)  # belt
    dr.line([P(-60, -190 + slump), P(-40, -20)], fill=BLUE, width=max(2, int(8 * s)))
    dr.line([P(60, -190 + slump), P(40, -20)], fill=BLUE, width=max(2, int(8 * s)))
    # emblem
    ey = -130 + slump
    poly([(0, ey - 40), (38, ey), (0, ey + 40), (-38, ey)], GOLD)
    dr.polygon([P(6, ey - 26), P(-12, ey + 4), P(2, ey + 4), P(-6, ey + 28), P(14, ey - 6), P(0, ey - 6)], fill=CRIMSON)
    # arms
    sh_l, sh_r = (-70, -185 + slump), (70, -185 + slump)
    if pose == "lift":
        el_l, ha_l, el_r, ha_r = (-110, -290), (-80, -390), (110, -290), (80, -390)
    elif pose == "hips":
        el_l, ha_l, el_r, ha_r = (-130, -110), (-62, -40), (130, -110), (62, -40)
    elif pose == "point":
        el_l, ha_l, el_r, ha_r = (-120, -110), (-62, -40), (60, -120), (8, -140 + slump)
    elif pose == "shrug":
        el_l, ha_l, el_r, ha_r = (-130, -120), (-170, -210), (130, -120), (170, -210)
    elif pose == "thumb":
        el_l, ha_l, el_r, ha_r = (-100, -90), (-70, -20), (130, -140), (150, -250)
    else:  # slump
        el_l, ha_l, el_r, ha_r = (-90, -90), (-80, 10), (90, -90), (80, 10)
    limb(sh_l, el_l, 40, NAVY); limb(el_l, ha_l, 36, BLUE); limb(sh_r, el_r, 40, NAVY); limb(el_r, ha_r, 36, BLUE)
    if pose == "thumb":
        hx, hy = P(*ha_r); dr.rounded_rectangle([hx - 10 * s, hy - 70 * s, hx + 12 * s, hy - 14 * s], radius=10 * s, fill=BLUE, outline=INK, width=ow)
    # head
    hy0 = -250 + slump * 1.4
    hx = 0; hcx, hcy = P(hx, hy0)
    r = 46 * s
    dr.rectangle([hcx - 18 * s, hcy + 30 * s, hcx + 18 * s, hcy + 60 * s], fill=SKIN, outline=INK, width=ow)
    dr.ellipse([hcx - r, hcy - r * 1.1, hcx + r, hcy + r], fill=SKIN, outline=INK, width=ow)
    dr.chord([hcx - r - 4 * s, hcy - r * 1.25, hcx + r + 4 * s, hcy + r * 0.2], 180, 360, fill=HAIR, outline=INK, width=ow)
    for k in (-1, 0, 1):
        dr.polygon([(hcx + (k * 24 - 14) * s, hcy - 40 * s), (hcx + (k * 24 + 6) * s, hcy - 64 * s), (hcx + (k * 24 + 14) * s, hcy - 36 * s)], fill=HAIR)
    # face
    e_y = hcy + 2 * s
    lid = mood * 9 * s
    for ex in (-17, 17):
        dr.ellipse([hcx + ex * s - 6 * s, e_y - 7 * s + lid, hcx + ex * s + 6 * s, e_y + 7 * s], fill=INK)
        dr.line([hcx + ex * s - 13 * s, e_y - 18 * s + mood * 6 * s * (1 if ex < 0 else -1), hcx + ex * s + 13 * s, e_y - 18 * s - mood * 6 * s * (1 if ex < 0 else -1)], fill=HAIR, width=max(2, int(6 * s)))
    m_y = hcy + 26 * s
    if mood < 0.5:
        dr.arc([hcx - 18 * s, m_y - 14 * s, hcx + 18 * s, m_y + 12 * s], 10, 170, fill=INK, width=max(2, int(5 * s)))
    else:
        dr.arc([hcx - 16 * s, m_y, hcx + 16 * s, m_y + 22 * s], 200, 340, fill=INK, width=max(2, int(5 * s)))
    return P

def earth(dr, cx, cy, r, t):
    dr.ellipse([cx - r - 10, cy - r - 10, cx + r + 10, cy + r + 10], fill=INK)
    dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 130, 230))
    rnd = random.Random(9)
    for _ in range(7):
        a = rnd.random() * 6.28 + t * 0.4; d = rnd.uniform(0.1, 0.65) * r
        bx, by = cx + math.cos(a) * d, cy + math.sin(a) * d * 0.8; br = rnd.uniform(0.18, 0.32) * r
        if math.hypot(bx - cx, by - cy) + br < r * 0.98:
            dr.ellipse([bx - br, by - br * .7, bx + br, by + br * .7], fill=(70, 190, 90), outline=INK, width=4)
    dr.chord([cx - r, cy - r, cx + r, cy + r], 200, 290, fill=(120, 190, 255))

def pizza(dr, cx, cy, s):
    pts = [(cx, cy + 120 * s), (cx - 90 * s, cy - 90 * s), (cx + 90 * s, cy - 90 * s)]
    dr.polygon(pts, fill=(255, 205, 90), outline=INK, width=8)
    dr.rounded_rectangle([cx - 100 * s, cy - 120 * s, cx + 100 * s, cy - 80 * s], radius=18 * s, fill=(200, 120, 50), outline=INK, width=8)
    for px, py in [(-30, -50), (25, -40), (0, 10), (-8, 60)]:
        dr.ellipse([cx + px * s - 16 * s, cy + py * s - 16 * s, cx + px * s + 16 * s, cy + py * s + 16 * s], fill=CRIMSON, outline=INK, width=4)

# ---------------------------------------------------------------- scenes
class Ctx:
    pass

def scene_dayoff(img, c):
    dr = ImageDraw.Draw(img)
    rays(dr, W / 2, 760, c.lt, (200, 20, 45), (235, 60, 40), 20, 0.4)
    speed_lines(dr, W / 2, 760, c.t, (255, 230, 150), 30, 380)
    # emergency mini-panels orbiting
    labels = [("FIRE!", ORANGE), ("FLOOD!", ELEC), ("ROBOT!", (180, 180, 200)), ("CAT IN TREE!", GOLD), ("CRASH!", CRIMSON), ("HELP!", WHITE)]
    for i, (lb, col) in enumerate(labels):
        k = ease_out_back((c.lt - 0.12 * i - 0.2) / 0.3)
        if k <= 0: continue
        a = i * 1.047 + c.lt * 0.6; R = 430 * k
        x, y = W / 2 + math.cos(a) * R, 760 + math.sin(a) * R * 1.05
        lay = Image.new("RGBA", (300, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rectangle([0, 0, 299, 149], fill=INK); d.rectangle([9, 9, 290, 140], fill=col)
        tl = text_layer(lb, 54 if len(lb) < 8 else 40, WHITE, 6, INK, 4); lay.paste(tl, ((300 - tl.width) // 2, (150 - tl.height) // 2), tl)
        put(img, lay, x, y, 0.9, math.sin(i * 2.1) * 12)
    hero(img, W / 2 - 60, 1010, 0.95, "shrug", c.t, 0.2 * c.pulse, 0.15)
    k = ease_out_back((c.lt - 0.9) / 0.25, 2.8)
    if k > 0:
        dr = ImageDraw.Draw(img)
        sz = 1 + 0.06 * c.pulse
        bx, by = W / 2 + 150, 560
        dr.ellipse([bx - 330 * k * sz, by - 150 * k * sz, bx + 330 * k * sz, by + 150 * k * sz], fill=INK)
        dr.ellipse([bx - 316 * k * sz, by - 136 * k * sz, bx + 316 * k * sz, by + 136 * k * sz], fill=WHITE)
        dr.polygon([(bx - 150 * k, by + 110 * k), (bx - 70 * k, by + 120 * k), (bx - 230 * k, by + 250 * k)], fill=WHITE, outline=INK, width=10)
        put(img, text_layer("DAY OFF!", 150, CRIMSON, 10, INK, 6), bx, by, k * sz, -5)

def scene_catch(img, c):
    img.paste(c.bg["sky"].crop((40, 60, 40 + W, 60 + H)))
    dr = ImageDraw.Draw(img)
    # building + ladder
    panel(img, (560, 380, 1010, 1130), (250, 238, 214), 12)
    for wy in range(430, 1100, 120):
        for wx in (600, 790):
            dr.rectangle([wx, wy, wx + 150, wy + 80], fill=ELEC, outline=INK, width=6)
    dr.rectangle([560, 520, 760, 540], fill=INK)
    lad = ease_out((c.lt - 0.2) / 0.8)
    x0, y0 = 120, 1180; x1, y1 = lerp(x0, 640, lad), lerp(y0, 560, lad)
    for off in (0, 70):
        dr.line([(x0 + off, y0), (x1 + off, y1)], fill=(220, 40, 40), width=16)
    for i in range(1, 12):
        f = i / 12
        if f > lad: break
        dr.line([(lerp(x0, x1, f / max(lad, 1e-3) * lad), lerp(y0, y1, f / max(lad, 1e-3) * lad)),
                 (lerp(x0, x1, f / max(lad, 1e-3) * lad) + 70, lerp(y0, y1, f / max(lad, 1e-3) * lad))], fill=WHITE, width=8)
    # hero relaxed on left giving thumbs up
    hero(img, 290, 900, 0.82, "thumb", c.t, 0, 0.0)
    if c.lt > 1.1: sfx(img, "PHEW!", 330, 380, 120, GOLD, 1.1, c.lt, -10, CRIMSON, 4)
    if c.lt > 0.5: sfx(img, "GOT HER!", 800, 300, 80, WHITE, 0.5, c.lt, 6, BLUE, 2)

def scene_sky(img, c):
    img.paste(c.bg["night"].crop((80 + int(c.lt * 10), 100, 80 + int(c.lt * 10) + W, 100 + H)))
    dr = ImageDraw.Draw(img)
    sh = math.sin(c.t * 40) * 6 * (0.5 + c.pulse)
    # sky dome
    dr.ellipse([-260, -560 + sh, W + 260, 640 + sh], fill=INK)
    dr.ellipse([-245, -545 + sh, W + 245, 625 + sh], fill=(40, 70, 170))
    starfield_dome = random.Random(11)
    for _ in range(70):
        x = starfield_dome.uniform(0, W); y = starfield_dome.uniform(40, 560)
        r = starfield_dome.choice([2, 3, 4])
        dr.ellipse([x - r, y - r + sh, x + r, y + r + sh], fill=(255, 245, 200))
    dr.ellipse([720, 140 + sh, 860, 280 + sh], fill=GOLD, outline=INK, width=8)  # sun/planet
    dr.ellipse([180, 260 + sh, 260, 340 + sh], fill=(255, 140, 120), outline=INK, width=6)
    # lightning crackle
    if int(c.t * 8) % 3 == 0:
        x = 120 + (int(c.t * 8) * 137) % 800
        dr.line([(x, 560), (x + 30, 610), (x - 10, 650), (x + 40, 720)], fill=(255, 255, 160), width=8)
    hero(img, W / 2, 1000, 1.0, "lift", c.t, 0.6 + 0.8 * c.lt / 3, 0.4)
    if c.lt > 1.3: sfx(img, "NNGH!", 230, 820, 110, GOLD, 1.3, c.lt, -12, None)

def scene_friday(img, c):
    dr = ImageDraw.Draw(img)
    split = ease_out(c.lt / 0.3)
    # left warm panel
    panel(img, (30, 300, int(lerp(W / 2, 520, split)), 1150), (255, 170, 70), 12)
    halfx = int(lerp(W / 2, 520, split))
    dr.ellipse([90, 360, 300, 570], fill=CREAM, outline=INK, width=10)
    a = -math.pi / 2 + math.pi * 0.66
    dr.line([(195, 465), (195, 395)], fill=INK, width=10); dr.line([(195, 465), (195 + 60 * math.cos(a), 465 + 60 * math.sin(a))], fill=INK, width=8)
    put(img, text_layer("FRIDAY 8:00 PM", 58, WHITE, 6, INK, 4), 275, 640, 1, -4)
    pizza(dr, 280, 880, 1.1 + 0.05 * c.pulse)
    # right blue panel with hero holding the sky
    panel(img, (halfx + 30, 300, W - 30, 1150), (40, 70, 150), 12)
    clip = Image.new("RGB", (W - 60 - halfx, 850), (40, 70, 150)); cd = ImageDraw.Draw(clip)
    cd.ellipse([-200, -500, clip.width + 200, 260], fill=INK); cd.ellipse([-188, -488, clip.width + 188, 248], fill=(70, 100, 200))
    hero(clip, clip.width / 2, 600, 0.68, "lift", c.t, 0.9, 0.55)
    img.paste(clip, (halfx + 30, 300))
    if c.lt > 1.2: sfx(img, "SIGH...", 780, 1050, 80, WHITE, 1.2, c.lt, 4, None)

def scene_oneman(img, c):
    dr = ImageDraw.Draw(img)
    rays(dr, W / 2, 740, c.lt, (30, 60, 160), (20, 40, 120), 16, 0.3)
    collapse = ease_out((c.lt - 1.6) / 0.35)
    cols = [CRIMSON, BLUE, GOLD, ORANGE, ELEC, VIOLET]
    tags = ["RESCUER", "PROTECTOR", "FIGHTER", "FRIEND", "TENANT", "CELEB"]
    pw, ph = 470, 270
    for i in range(6):
        gx, gy = 30 + (i % 2) * (pw + 80), 300 + (i // 2) * (ph + 30)
        tx, ty = W / 2 - pw / 2, 740 - ph / 2
        x, y = lerp(gx, tx, collapse), lerp(gy, ty, collapse)
        appear = ease_out_back((c.lt - 0.08 * i) / 0.25)
        if appear <= 0: continue
        lay = Image.new("RGB", (pw, ph), cols[i])
        hero(lay, pw / 2 + 60, ph - 10, 0.33, ["hips", "point", "lift", "thumb", "shrug", "stand"][i], c.t + i, 0, 0.2)
        tl = text_layer(tags[i], 44, WHITE, 5, INK, 3); lay.paste(tl, (14, 12), tl)
        lay = lay.resize((max(1, int(pw * appear)), max(1, int(ph * appear))))
        dr.rectangle([x - 10, y - 10, x + lay.width + 10, y + lay.height + 10], fill=INK)
        img.paste(lay, (int(x), int(y)))
    if collapse > 0.9:
        burst(dr, W / 2, 740, 420, GOLD, 18, 0.35, c.lt, INK, 12, 3)
        hero(img, W / 2, 860, 0.85, "point", c.t, 0.2, 0.3)
    sfx(img, "HEY!", 250, 440, 170, GOLD, 0.0, c.lt, -12, CRIMSON, 6)

def scene_montage(img, c):
    beat_i = int(c.lt / 0.393)
    rnd = random.Random(beat_i * 7 + 1)
    pal = [(CRIMSON, GOLD), (BLUE, ELEC), (ORANGE, GOLD), (VIOLET, ELEC), (GOLD, CRIMSON)]
    a, b = pal[beat_i % len(pal)]
    dr = ImageDraw.Draw(img)
    img.paste(a, [0, 0, W, H])
    speed_lines(dr, W / 2 + rnd.randint(-120, 120), 760, c.t, b, 40, 300, beat_i)
    words = ["CRASH!", "WHOOSH!", "SPLASH!", "KRAK!", "BAM!", "ZOOM!", "POW!", "SAVED!"]
    poses = ["lift", "point", "hips", "thumb", "lift", "shrug", "point", "hips"]
    ang = rnd.uniform(-10, 10)
    # tilted panel
    lay = Image.new("RGB", (900, 760), b); d = ImageDraw.Draw(lay)
    speed_lines(d, 450, 380, c.t, WHITE, 26, 200, beat_i + 3)
    hero(lay, 450 + rnd.randint(-80, 80), 560, 0.9, poses[beat_i % 8], c.t, 0.1, min(1, c.lt / 3.0))
    fr = Image.new("RGBA", (920, 780), INK + (255,)); fr.paste(lay, (10, 10))
    put(img, fr, W / 2, 760, 1 + 0.04 * c.pulse, ang)
    sfx(img, words[beat_i % 8], W / 2 + rnd.randint(-200, 200), 430 + rnd.randint(-30, 30), 150, WHITE, beat_i * 0.393, c.lt, rnd.uniform(-14, 14), CRIMSON if a != CRIMSON else NAVY, beat_i)

def scene_world(img, c):
    dr = ImageDraw.Draw(img)
    img.paste(c.bg["cosmic"].crop((80, 100, 80 + W, 100 + H)))
    rays(dr, W / 2, 520, c.lt, (255, 200, 60), (255, 150, 40), 22, 0.2) if c.lt < 1.8 else rays(dr, W / 2, 520, c.lt, mix((255, 200, 60), (60, 70, 160), (c.lt - 1.8) / 1.2), mix((255, 150, 40), (40, 50, 130), (c.lt - 1.8) / 1.2), 22, 0.2)
    rise = ease_out(c.lt / 0.6)
    trem = max(0, (c.lt - 1.4)) * 1.4
    ex, ey = W / 2 + math.sin(c.t * 50) * trem * 5, lerp(780, 450, rise)
    hero(img, W / 2, 1080, 1.0, "lift", c.t, trem, min(1, max(0, c.lt - 1.5) / 1.2))
    earth(dr, ex, ey, 210, c.lt)
    if c.lt > 0.3: sfx(img, "HUP!", 860, 900, 100, GOLD, 0.3, c.lt, 10, CRIMSON, 8)

def scene_carry(img, c):
    dr = ImageDraw.Draw(img)
    fade = min(1, c.lt / 1.6)
    img.paste(mix((40, 50, 130), (14, 22, 70), fade), [0, 0, W, H])
    starfield(img, 90, 21)
    dr.ellipse([W / 2 - 300, 1000, W / 2 + 300, 1080], fill=(30, 40, 100), outline=INK, width=8)
    hero(img, W / 2, 820 + 40 * fade, 0.95, "slump", c.t, 0, 1.0, mix(CRIMSON, (110, 40, 70), fade))
    # notebook pull-back at the end
    nb = ease_out((c.lt - 2.1) / 0.9)
    if nb > 0:
        paper = Image.new("RGBA", (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(paper)
        m = int(lerp(-200, 60, nb))
        a = int(255 * nb)
        pd.rectangle([0, 0, W, H], fill=(245, 240, 225, a))
        for y in range(300, 1500, 54): pd.line([(0, y), (W, y)], fill=(150, 180, 230, a), width=3)
        pd.line([(110, 0), (110, H)], fill=(230, 120, 120, a), width=4)
        pd.rectangle([m + 40, 300 + m, W - 40 - m, 1150 - m], fill=(0, 0, 0, 0), outline=(12, 12, 20, a), width=10)
        pd.rectangle([m + 50, 310 + m, W - 50 - m, 1140 - m], fill=(0, 0, 0, 0))
        img.paste(paper, (0, 0), paper)
        # pencil
        px, py = lerp(W + 200, 860, nb), lerp(200, 520, nb)
        dr = ImageDraw.Draw(img)
        dr.polygon([(px, py), (px + 300, py - 420), (px + 360, py - 380), (px + 60, py + 40)], fill=GOLD, outline=INK, width=8)
        dr.polygon([(px, py), (px + 60, py + 40), (px - 20, py + 70)], fill=CREAM, outline=INK, width=6)
        if c.lt > 2.6:
            put(img, text_layer("BUT WHAT ABOUT REAL LIFE?", 64, GOLD, 6, INK, 4), W / 2, 400, 1, -2, min(1, (c.lt - 2.6) / 0.4))

SCENES = {"dayoff": scene_dayoff, "catch": scene_catch, "sky": scene_sky, "friday": scene_friday,
          "oneman": scene_oneman, "montage": scene_montage, "world": scene_world, "carry": scene_carry}

# ---------------------------------------------------------------- captions
def wrap(words, f, maxw):
    lines, cur = [], []
    for w in words:
        test = " ".join(cur + [w])
        if cur and f.getlength(test) > maxw: lines.append(cur); cur = [w]
        else: cur.append(w)
    if cur: lines.append(cur)
    return lines

def caption(img, text, lt, dur, pulse):
    words = text.split(); f = font(84); maxw = 880
    lines = wrap(words, f, maxw)
    reveal = max(1, dur * 0.62)
    n_vis = min(len(words), int(lt / reveal * len(words)) + 1)
    lh = 92; boxh = lh * len(lines) + 50
    k = 0.6 + 0.4 * ease_out_back(lt / 0.18, 2.0)
    y_mid = 1330
    lay = Image.new("RGBA", (980, boxh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rectangle([10, 10, 979, boxh + 19], fill=INK); d.rectangle([0, 0, 968, boxh + 8], fill=INK)
    d.rectangle([10, 10, 958, boxh - 2], fill=(255, 236, 120))
    idx = 0
    for li, ln in enumerate(lines):
        lw = f.getlength(" ".join(ln)); x = (968 - lw) / 2; y = 30 + li * lh
        for w in ln:
            col = INK if idx < n_vis - 1 else (CRIMSON if idx == n_vis - 1 else (0, 0, 0, 0))
            if idx < n_vis:
                d.text((x, y), w, font=f, fill=col)
            x += f.getlength(w + " "); idx += 1
    put(img, lay, W / 2, y_mid, k * (1 + 0.015 * pulse), -1.5)

# ---------------------------------------------------------------- main
def main():
    tl = json.load(open(sys.argv[1])); song = sys.argv[2]; out = sys.argv[3]
    preview = None; stills = None
    if "--preview" in sys.argv: preview = float(sys.argv[sys.argv.index("--preview") + 1])
    if "--frames" in sys.argv: stills = [float(x) for x in sys.argv[sys.argv.index("--frames") + 1].split(",")]
    c0, c1 = tl["clip"]["start"], tl["clip"]["end"]
    dur = c1 - c0 if not preview else min(preview, c1 - c0)
    beats = [b - c0 for b in tl["beats"]]
    lines = [dict(l, t=l["t"] - c0) for l in tl["lines"]]
    for i, l in enumerate(lines): l["end"] = lines[i + 1]["t"] if i + 1 < len(lines) else (c1 - c0)

    c = Ctx(); c.bg = {
        "sky": skyline(halftone_bg((120, 200, 255), (40, 110, 220), (150, 215, 255), cy=0.3), 1500, (70, 90, 150), 2, (255, 230, 140)),
        "night": skyline(starfield(halftone_bg((40, 50, 120), (10, 14, 40), (60, 70, 150))), 1550, (22, 28, 70), 7, (255, 200, 90)),
        "cosmic": starfield(halftone_bg((80, 50, 150), (14, 16, 50), (110, 80, 180), cy=0.3), 160, 4),
        "base": halftone_bg((240, 70, 60), (150, 10, 40), (255, 120, 90))}

    def frame(t):
        c.t = t
        lb = max([b for b in beats if b <= t], default=-9); c.pulse = math.exp(-(t - lb) * 7)
        li = max([i for i, l in enumerate(lines) if l["t"] <= t + 0.05], default=0)
        L = lines[li]; c.lt = max(0.0, t - L["t"])
        img = c.bg["base"].crop((80, 120, 80 + W, 120 + H))
        SCENES[L["scene"]](img, c)
        # paper/halftone grain overlay & vignette are baked in bg; add ink frame
        dr = ImageDraw.Draw(img)
        # line-change slam flash
        if c.lt < 0.07 and t > 0.1: img.paste((255, 250, 230), [0, 0, W, H]) if c.lt < 0.035 else None
        # top branding / hook
        if t < 3.0:
            k = 1.0 + 0.05 * c.pulse  # hook is fully visible from frame 0 (first-second hook)
            lay = text_layer(tl["hook"], 74, WHITE, 9, INK, 6)
            if lay.width > 980: lay = lay.resize((980, int(lay.height * 980 / lay.width)))
            bw, bh = lay.width + 60, lay.height + 40
            box = Image.new("RGBA", (bw + 10, bh + 10), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
            bd.rectangle([10, 10, bw + 9, bh + 9], fill=INK); bd.rectangle([0, 0, bw, bh], fill=INK); bd.rectangle([8, 8, bw - 8, bh - 8], fill=CRIMSON)
            box.paste(lay, (30, 20), lay)
            put(img, box, W / 2, 270, k, 2)
        else:
            put(img, text_layer(f"{tl['artist'].upper()}  ·  {tl['song'].upper()}", 46, GOLD, 6, INK, 4), W / 2, 250, 1, 0, min(1, (t - 3) / 0.3))
        caption(img, L["text"], c.lt, L["end"] - L["t"], c.pulse)
        # beat zoom + shake
        z = 1 + 0.018 * c.pulse
        if z > 1.001:
            zw, zh = int(W * z), int(H * z)
            img = img.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2, (zw - W) // 2 + W, (zh - H) // 2 + H))
        return img

    if stills:
        for s in stills:
            frame(s - c0 if s > c0 else s).save(f"{out}_{s:.2f}.png")
        return
    n = int(round(dur * FPS))
    ff = subprocess.Popen(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-ss", f"{c0:.3f}", "-t", f"{dur:.3f}", "-i", song,
        "-map", "0:v", "-map", "1:a",
        "-af", f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=in:d=0.04,afade=t=out:st={dur - 0.25:.3f}:d=0.25",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(n):
        ff.stdin.write(frame(i / FPS).tobytes())
        if i % 60 == 0: print(f"frame {i}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    print("wrote", out)

if __name__ == "__main__":
    main()
