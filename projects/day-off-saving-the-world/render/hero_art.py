"""Vector comic-book hero (cairo): antialiased bezier anatomy, two-tone cel shading,
halftone shadow dots, variable ink line weights and expressive faces.

draw_hero(pose, s, t, tremble, mood, cape_col, expr) -> (PIL RGBA image, (pelvis_x, pelvis_y))
Unit space: pelvis at (0,0), head top ~ -345, soles ~ +232.
"""
import math
import cairo
from PIL import Image

INK = (0.05, 0.05, 0.09)
def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

SUIT = (rgb("1c2557"), rgb("0c1033"), rgb("3c5cb8"))        # base, shadow, highlight
ACC = (rgb("1e8bff"), rgb("0b4fc0"), rgb("8fd4ff"))
GOLDC = (rgb("ffc61a"), rgb("d18a00"), rgb("fff2a8"))
SKINC = (rgb("f2c29c"), rgb("cf8d69"), rgb("ffe0c6"))
HAIRC = (rgb("3d2416"), rgb("1f110a"), rgb("8a5a3a"))
GLOVE = (rgb("1f78ff"), rgb("0d47b8"), rgb("8cc8ff"))
def cape_cols(c):
    c = tuple(v / 255 for v in c)
    return (c, tuple(v * 0.55 for v in c), tuple(min(1, v * 1.25 + 0.12) for v in c))

LIGHT_SH = (13, 9)     # shadow falls lower-right
LIGHT_HI = (-4, -5)

_dots = None
def halftone_pattern():
    global _dots
    if _dots is None:
        n = 9
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, n, n)
        c = cairo.Context(surf); c.set_source_rgba(0, 0, 0, 0.28)
        c.arc(n / 2, n / 2, 1.9, 0, 2 * math.pi); c.fill()
        _dots = cairo.SurfacePattern(surf); _dots.set_extend(cairo.EXTEND_REPEAT)
    return _dots

# ---------------------------------------------------------------- geometry helpers
def catmull(pts, closed=True, n=10):
    out = []; L = len(pts)
    rng = range(L) if closed else range(L - 1)
    for i in rng:
        p0 = pts[(i - 1) % L] if closed or i > 0 else pts[0]
        p1 = pts[i]; p2 = pts[(i + 1) % L]
        p3 = pts[(i + 2) % L] if closed or i + 2 < L else pts[-1]
        for k in range(n):
            t = k / n; t2 = t * t; t3 = t2 * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    if not closed: out.append(pts[-1])
    return out

def limb_pts(a, b, wa, wb, bulge=0.0, side_bias=0.0):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    left, right = [], []
    for i in range(17):
        t = i / 16; w = (wa + (wb - wa) * t) / 2 + bulge * math.sin(math.pi * t) * (1 + side_bias)
        w2 = (wa + (wb - wa) * t) / 2 + bulge * math.sin(math.pi * t) * (1 - side_bias)
        cx, cy = ax + dx * t, ay + dy * t
        left.append((cx + nx * w, cy + ny * w)); right.append((cx - nx * w2, cy - ny * w2))
    cap_b = [(bx + (nx * math.cos(q) + ux * math.sin(q)) * wb / 2, by + (ny * math.cos(q) + uy * math.sin(q)) * wb / 2)
             for q in [i * math.pi / 10 for i in range(1, 10)]]
    cap_a = [(ax + (-nx * math.cos(q) - ux * math.sin(q)) * wa / 2, ay + (-ny * math.cos(q) - uy * math.sin(q)) * wa / 2)
             for q in [i * math.pi / 10 for i in range(1, 10)]]
    return left + cap_b + right[::-1] + cap_a

def lerp(a, b, t): return a + (b - a) * t
def band_pts(a, b, t0, t1, w0, w1):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay; L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    p0 = (ax + dx * t0, ay + dy * t0); p1 = (ax + dx * t1, ay + dy * t1)
    return [(p0[0] + nx * w0 / 2, p0[1] + ny * w0 / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
            (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w0 / 2, p0[1] - ny * w0 / 2)]
def lerp2(p, q, t): return (lerp(p[0], q[0], t), lerp(p[1], q[1], t))

# ---------------------------------------------------------------- shading core
class Painter:
    def __init__(self, ctx, s):
        self.c = ctx; self.s = s
    def path(self, pts):
        c = self.c; c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        c.close_path()
    def shape(self, pts, cols, ink=5.5, shade=True, hi=True, dots=True, sh=LIGHT_SH):
        c = self.c; base, dark, light = cols
        c.save(); self.path(pts); c.clip()
        c.set_source_rgb(*base); c.paint()
        if shade:
            c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            self.path(pts); c.save(); c.translate(-sh[0], -sh[1]); self.path(pts); c.restore()
            c.set_source_rgb(*dark)
            if dots:
                c.fill_preserve(); c.set_source(halftone_pattern())
                # pattern in device space so dot size is stable regardless of scale
            c.fill()
            c.set_fill_rule(cairo.FILL_RULE_WINDING)
        if hi:
            c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
            self.path(pts); c.save(); c.translate(-LIGHT_HI[0], -LIGHT_HI[1]); self.path(pts); c.restore()
            c.set_source_rgba(*light, 0.9); c.fill()
            c.set_fill_rule(cairo.FILL_RULE_WINDING)
        c.restore()
        if ink:
            self.path(pts); c.set_source_rgb(*INK); c.set_line_width(ink)
            c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    def line(self, pts, w=3, col=INK, smooth=True, cap=cairo.LINE_CAP_ROUND):
        c = self.c
        if smooth and len(pts) > 2: pts = catmull(pts, closed=False, n=6)
        c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        c.set_source_rgb(*col) if len(col) == 3 else c.set_source_rgba(*col)
        c.set_line_width(w); c.set_line_cap(cap); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
    def fill(self, pts, col, ink=0):
        self.path(pts); c = self.c
        c.set_source_rgb(*col) if len(col) == 3 else c.set_source_rgba(*col)
        if ink:
            c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(ink); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke()
        else:
            c.fill()

def ellipse_pts(cx, cy, rx, ry, n=36, rot=0):
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return out

# ---------------------------------------------------------------- poses
POSES = {
    #        elbowL       handL        elbowR       handR       kneeL      ankleL      kneeR     ankleR   handL,handR kinds
    "hips":  ((-118, -112), (-60, -34), (118, -112), (60, -34), (-46, 112), (-62, 198), (46, 112), (62, 198), "fist", "fist"),
    "stand": ((-88, -98), (-84, 0), (88, -98), (84, 0), (-34, 112), (-40, 200), (34, 112), (40, 200), "fist", "fist"),
    "lift":  ((-112, -292), (-80, -392), (112, -292), (80, -392), (-50, 108), (-66, 196), (50, 108), (66, 196), "palm_up", "palm_up"),
    "thumb": ((-118, -112), (-60, -34), (128, -150), (146, -262), (-40, 112), (-52, 198), (40, 112), (52, 198), "fist", "thumb"),
    "point": ((-118, -112), (-60, -34), (104, -104), (22, -150), (-40, 112), (-52, 198), (40, 112), (52, 198), "fist", "point"),
    "shrug": ((-126, -118), (-170, -200), (126, -118), (170, -200), (-38, 112), (-48, 198), (38, 112), (48, 198), "palm_up", "palm_up"),
    "slump": ((-80, -90), (-74, 6), (80, -90), (74, 6), (-30, 112), (-36, 200), (30, 112), (36, 200), "fist", "fist"),
}

# ---------------------------------------------------------------- body parts
def draw_cape(P, sh_l, sh_r, t, mood, cols, spread):
    wv = math.sin(t * 5.2) * 26 * (1 - 0.6 * mood); wv2 = math.sin(t * 5.2 + 1.3) * 22 * (1 - 0.6 * mood)
    drop = 40 * mood
    hem_y = 175 + drop
    pts = [(sh_l[0] + 6, sh_l[1] + 6), (sh_l[0] - 40 * spread, sh_l[1] + 80),
           (-118 * spread + wv, hem_y - 30), (-90 * spread + wv, hem_y + 10), (-40 + wv2, hem_y - 10),
           (10 + wv, hem_y + 22), (60 + wv2, hem_y - 6), (112 * spread + wv, hem_y + 14), (132 * spread + wv2, hem_y - 26),
           (sh_r[0] + 40 * spread, sh_r[1] + 80), (sh_r[0] - 6, sh_r[1] + 6)]
    cp = catmull(pts, closed=True, n=8)
    P.shape(cp, cols, ink=6, sh=(18, 4))
    # inner-fold lines
    for fx in (-60, -10, 45):
        P.line([(fx * 0.4, sh_l[1] + 40), (fx * 0.8 + wv * 0.5, 60), (fx + wv * 0.8, hem_y - 4)], 3, (*cols[1], 0.9))

def draw_leg(P, hip, knee, ankle, side):
    # thigh, shin (suit), boot (glove blue + gold band), foot
    P.shape(limb_pts(hip, knee, 58, 44, 9, 0.2 * side), SUIT, ink=5.5)
    P.shape(limb_pts(knee, ankle, 44, 36, 7, -0.1 * side), SUIT, ink=5.5)
    boot_top = lerp2(knee, ankle, 0.42)
    P.shape(limb_pts(boot_top, ankle, 46, 40, 3), GLOVE, ink=5.5)
    P.shape(band_pts(knee, ankle, 0.40, 0.48, 47, 46), GOLDC, ink=3.5, dots=False, sh=(5, 3))
    ax, ay = ankle
    o = 8 * side
    foot = catmull([(ax - 20, ay - 6), (ax + 20, ay - 6), (ax + 27 + o, ay + 20), (ax + 24 + o, ay + 33),
                    (ax - 24 + o, ay + 33), (ax - 27 + o, ay + 20)], True, 6)
    P.shape(foot, GLOVE, ink=5.5)
    P.line([(ax - 20 + o, ay + 30), (ax + 20 + o, ay + 30)], 4, GOLDC[1], smooth=False)

def draw_torso(P, slump, breathe):
    y0 = -202 + slump
    pts = [(-74, y0 + 6), (-56, y0 - 6), (-20, y0 - 12), (20, y0 - 12), (56, y0 - 6), (74, y0 + 6),
           (78, y0 + 40), (64, y0 + 90), (46, -40), (44, -6), (48, 14), (0, 22), (-48, 14), (-44, -6), (-46, -40),
           (-64, y0 + 90), (-78, y0 + 40)]
    pts = [(x * (1 + breathe), y) for x, y in pts]
    tp = catmull(pts, True, 7)
    P.shape(tp, SUIT, ink=6.5)
    c = P.c
    c.save(); P.path(tp); c.clip()
    # electric-blue angular side accents
    for sgn in (-1, 1):
        acc = [(sgn * 80, y0 + 10), (sgn * 50, y0 + 6), (sgn * 30, y0 + 70), (sgn * 44, -2), (sgn * 66, -2), (sgn * 90, y0 + 60)]
        P.shape(acc, ACC, ink=3.5, dots=False)
    # pec + ab detail
    P.line([(-52, y0 + 58), (-26, y0 + 70), (-4, y0 + 62)], 3)
    P.line([(52, y0 + 58), (26, y0 + 70), (4, y0 + 62)], 3)
    for yy in (-95, -62):
        P.line([(-20, yy + slump * 0.5), (-4, yy + 4 + slump * 0.5)], 2.5, (*SUIT[2], 0.8))
        P.line([(20, yy + slump * 0.5), (4, yy + 4 + slump * 0.5)], 2.5, (*SUIT[1], 1.0))
    P.line([(0, y0 + 74), (0, -30)], 2.5, SUIT[1], smooth=False)
    c.restore()
    # belt
    belt = catmull([(-48, -12), (0, -6), (48, -12), (50, 8), (0, 16), (-50, 8)], True, 6)
    P.shape(belt, GOLDC, ink=4.5, dots=False)
    P.shape(ellipse_pts(0, 4, 15, 12), GOLDC, ink=4, dots=False)
    P.line([(-6, 4), (6, 4)], 2.5)
    # emblem: angular shield with lightning bolt
    ey = y0 + 72
    shield = [(0, ey - 46), (40, ey - 30), (34, ey + 14), (0, ey + 44), (-34, ey + 14), (-40, ey - 30)]
    P.shape(shield, GOLDC, ink=5, dots=False, sh=(8, 6))
    inner = [(0, ey - 34), (29, ey - 22), (25, ey + 10), (0, ey + 32), (-25, ey + 10), (-29, ey - 22)]
    P.shape(inner, ((0.85, 0.08, 0.2), (0.55, 0.03, 0.12), (1, 0.4, 0.45)), ink=3, dots=False, sh=(6, 4))
    bolt = [(6, ey - 28), (-14, ey + 2), (-1, ey + 2), (-9, ey + 28), (16, ey - 6), (2, ey - 6), (10, ey - 28)]
    P.shape(bolt, GOLDC, ink=2.5, dots=False, sh=(3, 3))
    # cape clasps
    for sx in (-50, 50):
        P.shape(ellipse_pts(sx, y0 + 6, 13, 13), GOLDC, ink=4, dots=False, sh=(4, 4))

def draw_hand(P, elbow, hand, kind, side):
    ex, ey = elbow; hx, hy = hand
    ang = math.atan2(hy - ey, hx - ex)
    ux, uy = math.cos(ang), math.sin(ang); nx, ny = -uy, ux
    def T(a, b): return (hx + ux * a + nx * b * side, hy + uy * a + ny * b * side)
    if kind == "palm_up":
        palm = catmull([T(-8, -20), T(14, -24), T(30, -18), T(34, 0), T(30, 18), T(10, 24), T(-8, 20)], True, 6)
        P.shape(palm, GLOVE, ink=5)
        for k, off in enumerate((-15, -5, 5, 15)):
            ln = 22 - abs(off) * 0.4
            P.shape(limb_pts(T(26, off), T(26 + ln, off * 1.25), 10, 9, 0), GLOVE, ink=4, dots=False)
        P.shape(limb_pts(T(6, -20), T(20, -36), 11, 9, 0), GLOVE, ink=4, dots=False)
    else:
        fist = catmull([T(-10, -18), T(12, -22), T(30, -16), T(34, 2), T(30, 18), T(10, 22), T(-10, 18)], True, 6)
        P.shape(fist, GLOVE, ink=5)
        for off in (-9, 1, 11):
            P.line([T(22, off), T(33, off + 1)], 2.5)
        if kind == "thumb":
            P.shape(limb_pts((hx - 4, hy - 8), (hx - 2, hy - 46), 15, 12, 0), GLOVE, ink=4.5, dots=False)
        elif kind == "point":
            P.shape(limb_pts(T(26, -10), T(56, -12), 12, 10, 0), GLOVE, ink=4.5, dots=False)

def draw_arm(P, sh, el, hand, kind, side):
    P.shape(limb_pts(sh, el, 46, 38, 10, 0.3), SUIT, ink=5.5)
    # deltoid cap
    P.shape(ellipse_pts(sh[0], sh[1] + 4, 30, 26), SUIT, ink=5.5)
    P.shape(limb_pts(el, hand, 40, 32, 6), GLOVE, ink=5.5)
    P.shape(band_pts(el, hand, 0.30, 0.40, 40, 38), GOLDC, ink=3.5, dots=False, sh=(5, 3))
    draw_hand(P, el, hand, kind, side)

def draw_head(P, hx, hy, tilt, mood, expr, t):
    c = P.c
    c.save(); c.translate(hx, hy); c.rotate(tilt)
    # neck
    neck = [(-17, 18), (17, 18), (20, 58), (-20, 58)]
    P.shape(neck, SKINC, ink=5, sh=(10, 0), dots=False)
    P.fill([(-17, 30), (17, 30), (17, 40), (-17, 40)], (*SKINC[1], 0.8))
    collar = catmull([(-34, 50), (0, 60), (34, 50), (30, 66), (0, 72), (-30, 66)], True, 6)
    P.shape(collar, SUIT, ink=4.5, dots=False)
    # ears
    for sx in (-1, 1):
        P.shape(ellipse_pts(sx * 33, 2, 8, 13), SKINC, ink=4, dots=False, sh=(4 * sx, 2))
    # face shape: square-ish approachable jaw
    face = catmull([(-31, -36), (0, -44), (31, -36), (34, -6), (31, 14), (20, 32), (8, 40), (-8, 40), (-20, 32), (-31, 14), (-34, -6)], True, 7)
    P.shape(face, SKINC, ink=5.5, sh=(9, 4), dots=False)
    # cheek shadow under hair line
    # eyes
    lid = min(1, mood) * 6
    eye_y = -4
    for sx in (-1, 1):
        ex = sx * 14
        if expr == "strain":
            P.line([(ex - 9, eye_y), (ex, eye_y + 2 * 1), (ex + 9, eye_y)], 3.5)
            continue
        white = ellipse_pts(ex, eye_y, 9, 6.5)
        P.fill(white, (1, 1, 1), ink=2.6)
        P.c.save(); P.path(white); P.c.clip()
        look = 1.5 * sx * 0 + (1 if expr == "grin" else 0)
        P.fill(ellipse_pts(ex + look, eye_y + 0.5, 5, 5.5), rgb("6b3f22"))
        P.fill(ellipse_pts(ex + look, eye_y + 0.5, 2.6, 3), INK)
        P.fill(ellipse_pts(ex + look - 1.6, eye_y - 1.8, 1.4, 1.4), (1, 1, 1))
        if lid > 0:
            P.fill([(ex - 12, eye_y - 9), (ex + 12, eye_y - 9), (ex + 12, eye_y - 7 + lid), (ex - 12, eye_y - 7 + lid)], SKINC[1])
        P.c.restore()
        P.line([(ex - 9, eye_y + 1), (ex - 3, eye_y - 6.5), (ex + 9, eye_y - 1)], 2.8)
        if mood > 0.6:
            P.line([(ex - 6, eye_y + 9), (ex + 5, eye_y + 10)], 1.8, (*SKINC[1], 1))
    # eyebrows
    for sx in (-1, 1):
        ex = sx * 14
        if expr in ("tired",) or mood > 0.6:
            inner_y, outer_y = -18, -12        # worried: inner raised
        elif expr in ("shout", "strain", "determined"):
            inner_y, outer_y = -11, -19        # angry/effort: inner lowered
        else:
            inner_y, outer_y = -16, -18
        brow = [(ex - sx * 4 - sx * 0, inner_y), (ex + sx * 6, (inner_y + outer_y) / 2 - 2), (ex + sx * 12, outer_y)]
        bp = limb_pts(brow[0], brow[2], 6, 4, 1.5)
        P.fill(bp, HAIRC[1])
    # nose
    P.line([(2, 2), (5, 14), (0, 17)], 2.6)
    P.fill([(2, 4), (6, 14), (2, 16)], (*SKINC[1], 0.7))
    # mouth
    if expr == "grin":
        m = catmull([(-13, 23), (0, 25), (13, 23), (8, 32), (0, 34), (-8, 32)], True, 6)
        P.fill(m, rgb("5a1414"), ink=2.8)
        P.fill([(-11, 23.5), (11, 23.5), (9, 27), (-9, 27)], (1, 1, 1))
    elif expr == "shout":
        m = catmull([(-11, 21), (0, 19), (11, 21), (9, 33), (0, 37), (-9, 33)], True, 6)
        P.fill(m, rgb("5a1414"), ink=2.8)
        P.fill([(-8, 21), (8, 21), (7, 24), (-7, 24)], (1, 1, 1))
        P.fill(ellipse_pts(0, 33, 5, 2.5), rgb("d9535b"))
    elif expr == "strain":
        m = [(-13, 23), (13, 23), (11, 31), (-11, 31)]
        P.fill(m, (1, 1, 1), ink=2.8)
        P.line([(-12, 27), (12, 27)], 1.8)
        for xx in (-6, 0, 6): P.line([(xx, 23), (xx, 31)], 1.5, smooth=False)
    elif expr == "tired" or mood > 0.6:
        P.line([(-10, 29), (0, 26), (10, 29)], 3)
    else:  # smile
        P.line([(-11, 24), (0, 29), (11, 24)], 3)
        P.line([(-13, 22), (-10, 25)], 2)
    # hair: messy, spiky, layered with highlight streaks
    sway = math.sin(t * 3) * 1.5
    back = [(-38, -6), (-40, -30), (-30, -50), (-8, -60), (20, -58), (38, -44), (40, -20), (36, -6), (30, -26), (12, -34), (-14, -32), (-30, -22)]
    P.shape(catmull(back, True, 6), HAIRC, ink=5, sh=(6, 3))
    spikes = [(-40, -18), (-50, -40 + sway), (-34, -44), (-36, -66 + sway), (-16, -54), (-8, -78 + sway), (6, -58),
              (22, -76 + sway), (24, -54), (44, -60 + sway), (36, -40), (48, -26 + sway), (34, -26),
              (24, -40), (14, -28), (2, -40), (-10, -26), (-18, -38), (-28, -24)]
    P.shape(spikes, HAIRC, ink=5, sh=(7, 4))
    for a, b in [((-24, -52), (-14, -40)), ((0, -60), (6, -46)), ((22, -60), (26, -48))]:
        P.line([a, b], 3, HAIRC[2])
    if mood > 0.6 and expr != "strain":
        P.shape(catmull([(40, -30), (46, -18), (44, -10), (38, -12), (37, -22)], True, 5), ((0.75, 0.9, 1), (0.45, 0.7, 0.95), (1, 1, 1)), ink=2.5, dots=False)
    if expr == "strain":
        for sx, yy in ((-44, -36), (46, -10)):
            P.shape(catmull([(sx, yy), (sx + 5, yy + 12), (sx, yy + 17), (sx - 5, yy + 12)], True, 4), ((0.75, 0.9, 1), (0.45, 0.7, 0.95), (1, 1, 1)), ink=2.2, dots=False)
    c.restore()

# ---------------------------------------------------------------- main entry
_cache = {}
def draw_hero(pose="stand", s=1.0, t=0.0, tremble=0.0, mood=0.0, cape_col=(214, 24, 52), expr=None):
    if expr is None:
        if pose == "lift" and tremble > 0.35: expr = "strain"
        elif mood > 0.6: expr = "tired"
        elif pose == "shrug": expr = "shout"
        elif pose in ("thumb", "hips"): expr = "grin"
        elif pose == "point": expr = "shout"
        else: expr = "smile"
    Wd, Hd = int(620 * s), int(760 * s)
    ox, oy = 310 * s, 470 * s
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, max(1, Wd), max(1, Hd))
    ctx = cairo.Context(surf); ctx.set_antialias(cairo.ANTIALIAS_BEST)
    jx = math.sin(t * 61) * tremble * 5; jy = math.cos(t * 47) * tremble * 3
    ctx.translate(ox + jx * s, oy + jy * s); ctx.scale(s, s)
    P = Painter(ctx, s)
    el_l, ha_l, el_r, ha_r, kn_l, an_l, kn_r, an_r, hk_l, hk_r = POSES[pose]
    slump = 22 * mood
    breathe = 0.012 * math.sin(t * 2.4)
    sh_l, sh_r = (-70, -184 + slump), (70, -184 + slump)
    def tr(p, amt=1.0):  # tremble on raised hands
        return (p[0] + math.sin(t * 57 + p[0]) * tremble * 4 * amt, p[1] + math.cos(t * 43 + p[1]) * tremble * 3 * amt)
    el_l, ha_l, el_r, ha_r = tr(el_l, .5), tr(ha_l), tr(el_r, .5), tr(ha_r)
    spread = 1.15 if pose in ("lift", "shrug") else 1.0
    draw_cape(P, sh_l, sh_r, t, mood, cape_cols(cape_col), spread)
    draw_leg(P, (-28, 4), kn_l, an_l, -1)
    draw_leg(P, (28, 4), kn_r, an_r, 1)
    draw_torso(P, slump, breathe)
    head_y = -252 + slump * 1.5
    tilt = 0.10 * mood + (0.04 * math.sin(t * 2) if pose != "lift" else -0.02)
    raised = pose in ("lift", "shrug", "thumb")
    if raised:
        draw_head(P, 0, head_y, tilt, mood, expr, t)
    draw_arm(P, sh_l, el_l, ha_l, hk_l, -1)
    draw_arm(P, sh_r, el_r, ha_r, hk_r, 1)
    if not raised:
        draw_head(P, 0, head_y, tilt, mood, expr, t)
    surf.flush()
    img = Image.frombuffer("RGBA", (Wd, Hd), bytes(surf.get_data()), "raw", "BGRa", surf.get_stride(), 1)
    return img, (ox, oy)
