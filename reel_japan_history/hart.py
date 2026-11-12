"""hart — the paintings of the history reel, one per era, in the same brush as the other reels (poly_ink strokes and
washes).  Each returns float32 densities on the full 1080x1920 page, keyed by colour: 'ink' (sumi), 'red'
(vermilion), 'gold', 'blue' (indigo), 'grey' (a pale wash).  The painting sits in the band y 840-1360, between the
era title above it and the captions below it.  Moving parts (trains, ships, smoke, the bubble, petals) are drawn by
the scenes from the small sprites at the bottom of this file."""
import numpy as np

from art import blossom_cluster, cherry_branch, granary, pagoda, pit_dwelling
from engine import H, W, StrokeSet, blur, noise, spline, stroke
from k6art import fields, mist_hills
from poly_ink.brush import BLUNT, PRESS_DOWN, SWEEP, wash as pwash
from r5art import junk

GROUND = 1340


def _f(a):
    return np.clip(np.asarray(a, np.float32), 0, 1)


def _ground(ss, y=GROUND, x0=90, x1=990, seed=0, ink=0.55):
    ss.add(stroke(W, H, spline([(x0, y + 4), ((x0 + x1) / 2, y - 2), (x1, y + 4)], 8), 6, ink=ink, dry=0.55, profile=SWEEP, seed=seed), 0, 1)


def _hills(y0=1180, seed=3, op=0.7):
    return mist_hills(y0, seed=seed)['ink'] * op


def _ring(cx, cy, r, w=10, ink=0.9, seed=0, start=-1.9, sweep=5.9, wobble=0.02):
    pts = [(cx + r * (1 + wobble * np.sin(5 * a)) * np.cos(a), cy + r * (1 + wobble * np.cos(4 * a)) * np.sin(a))
           for a in np.linspace(start, start + sweep, 40)]
    return stroke(W, H, spline(pts, 4), w, ink=ink, dry=0.45, profile=((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2)), seed=seed)


# ------------------------------------------------------------------ 縄文: a flame-rimmed cord-marked pot, a pit dwelling
def jomon():
    ss, red = StrokeSet(W, H), StrokeSet(W, H)
    cx, base, top = 600, 1330, 900
    prof = [(0.0, 120), (0.15, 150), (0.45, 175), (0.7, 160), (0.88, 150), (1.0, 190)]   # (height 0..1, half-width)
    left = [(cx - w, base - u * (base - top)) for u, w in prof]
    right = [(cx + w, base - u * (base - top)) for u, w in prof][::-1]
    ss.add(pwash(W, H, left + right, ink=0.32, soft=2.5, seed=1, grain=0.45), 0, 1)
    for side, pts in ((-1, left), (1, right)):
        ss.add(stroke(W, H, spline(pts, 8), 8, ink=0.85, dry=0.4, profile=BLUNT, seed=2 + side), 0, 1)
    # the flame-like rim: four lobes curling up
    for k, dx in enumerate((-150, -50, 50, 150)):
        ss.add(stroke(W, H, spline([(cx + dx - 35, top + 5), (cx + dx - 20, top - 70), (cx + dx + 15, top - 85), (cx + dx + 25, top - 40),
                                    (cx + dx + 5, top - 30)], 10), 12, ink=0.85, dry=0.4, profile=SWEEP, seed=10 + k), 0, 1)
    # cord marks: bands of short slanted ticks
    r = np.random.default_rng(4)
    for band in range(7):
        y = base - 40 - band * 52
        hw = np.interp((base - y) / (base - top), [u for u, _ in prof], [w for _, w in prof]) - 14
        for j in range(int(hw / 9)):
            x = cx - hw + j * 18 + (band % 2) * 9
            sl = 1 if band % 2 else -1
            ss.add(stroke(W, H, [(x, y - 12), (x + 8 * sl, y + 12)], 3, ink=r.uniform(0.45, 0.7), dry=0.6, profile=SWEEP,
                          seed=100 + band * 50 + j), 0, 1)
    pit_dwelling(ss, 220, base, 1.25, 0, 7, dur=0.01)
    _ground(ss, base + 4, seed=9)
    return {'ink': _f(np.maximum(ss.render(9), _hills(1200, 2, 0.45))), 'red': _f(red.render(9))}


# ------------------------------------------------------------------ 弥生: rice paddies and a raised-floor granary
def yayoi():
    ss = StrokeSet(W, H)
    granary(ss, 760, 1180, 1.7, 0, 21, dur=0.01)
    F = fields()['ink']
    F[:1060] = 0
    return {'ink': _f(np.maximum(ss.render(9), F * 0.85))}


# ------------------------------------------------------------------ 古墳: a keyhole tomb seen from above, in its moat
def kofun():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy, r = 540, 1000, 165
    circ = np.hypot(xx - cx, yy - cy) < r
    u = np.clip((yy - (cy + 60)) / 300, 0, 1)
    trap = (yy > cy + 60) & (yy < cy + 360) & (np.abs(xx - cx) < 90 + 150 * u)
    mound = (circ | trap).astype(np.float32)
    m = blur(mound, 3)
    tree = 0.55 + 0.45 * noise(H, W, 9, 3, 5)
    body = m * tree * 0.6
    edge = np.clip(blur(mound, 2) - blur(mound, 9), 0, None) * 1.4
    import cv2
    dist = cv2.distanceTransform((mound < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    moat = ((dist > 18) & (dist < 62)).astype(np.float32)
    moat = blur(moat, 2) * 0.55 * (0.8 + 0.2 * np.sin(yy / 4 + noise(H, W, 30, 2, 6) * 4))
    shore = np.exp(-((dist - 64) / 3) ** 2) + np.exp(-((dist - 16) / 2.5) ** 2) * 0.6
    dabs = (noise(H, W, 6, 2, 8) > 0.62) * m * 0.5
    ink = np.maximum.reduce([body * 0.7, dabs, edge, shore * 0.7])
    return {'ink': _f(ink), 'blue': _f(moat)}


# ------------------------------------------------------------------ 飛鳥: a five-storey pagoda on misty hills
def asuka():
    ss = StrokeSet(W, H)
    pagoda(ss, 560, GROUND - 10, 1.85, 0, 0.01, seed=31)
    _ground(ss, GROUND - 6, seed=32, ink=0.45)
    return {'ink': _f(np.maximum(ss.render(9), _hills(1180, 4, 0.55)))}


# ------------------------------------------------------------------ 奈良: the Great Buddha, seated, with a vermilion halo
def nara():
    ss, red, gold = StrokeSet(W, H), StrokeSet(W, H), StrokeSet(W, H)
    cx = 540
    red.add(_ring(cx, 980, 150, w=12, seed=41), 0, 1)
    red.add(_ring(cx, 1070, 255, w=8, seed=42, start=-2.9, sweep=2.75), 0, 1)
    # head with the curled-hair bump (ushnisha), long ears
    head = [(cx + 62 * np.cos(a), 985 + 74 * np.sin(a)) for a in np.linspace(0, 2 * np.pi, 30, endpoint=False)]
    gold.add(pwash(W, H, head, ink=0.55, soft=2, seed=43, grain=0.4), 0, 1)
    gold.add(pwash(W, H, [(cx + 40 * np.cos(a), 905 + 26 * np.sin(a)) for a in np.linspace(np.pi, 2 * np.pi, 14)] + [(cx + 40, 915), (cx - 40, 915)],
                   ink=0.6, soft=2, seed=44), 0, 1)
    for s in (-1, 1):
        ss.add(stroke(W, H, [(cx + s * 64, 975), (cx + s * 70, 1020), (cx + s * 62, 1050)], 9, ink=0.6, dry=0.4, profile=SWEEP, seed=45 + s), 0, 1)
    # robed body: shoulders, arms resting in the lap, crossed legs
    body = [(cx - 70, 1060), (cx - 190, 1100), (cx - 230, 1190), (cx - 250, 1260), (cx - 300, 1300), (cx - 290, 1330),
            (cx + 290, 1330), (cx + 300, 1300), (cx + 250, 1260), (cx + 230, 1190), (cx + 190, 1100), (cx + 70, 1060)]
    gold.add(pwash(W, H, body, ink=0.5, soft=2.5, seed=46, grain=0.45), 0, 1)
    for k, pts in enumerate(([(cx - 70, 1062), (cx - 190, 1102), (cx - 232, 1192), (cx - 252, 1262), (cx - 300, 1302)],
                             [(cx + 70, 1062), (cx + 190, 1102), (cx + 232, 1192), (cx + 252, 1262), (cx + 300, 1302)],
                             [(cx - 160, 1240), (cx, 1210), (cx + 160, 1240)], [(cx - 270, 1300), (cx, 1280), (cx + 270, 1300)],
                             [(cx - 40, 1100), (cx - 10, 1180), (cx + 30, 1220)], [(cx + 60, 1090), (cx + 80, 1170)])):
        ss.add(stroke(W, H, spline(pts, 8), 7 if k < 2 else 4, ink=0.8 if k < 2 else 0.5, dry=0.4, profile=SWEEP, seed=50 + k), 0, 1)
    # the raised hand (mudra) and the lotus base
    ss.add(stroke(W, H, [(cx + 150, 1150), (cx + 165, 1080), (cx + 160, 1040)], 16, ink=0.7, dry=0.4, profile=BLUNT, seed=58), 0, 1)
    for k in range(7):
        x = cx - 270 + k * 90
        ss.add(stroke(W, H, spline([(x - 40, 1350), (x, 1325), (x + 40, 1350)], 6), 5, ink=0.6, dry=0.5, profile=SWEEP, seed=60 + k), 0, 1)
    return {'ink': _f(ss.render(9)), 'red': _f(red.render(9)), 'gold': _f(gold.render(9))}


# ------------------------------------------------------------------ 平安: an unrolled handscroll and a court fan
def heian():
    ss, red = StrokeSet(W, H), StrokeSet(W, H)
    # a folding fan (hiōgi) open on the left
    fx, fy = 300, 1300
    for k, a in enumerate(np.linspace(-2.55, -0.6, 13)):
        ss.add(stroke(W, H, [(fx, fy), (fx + 290 * np.cos(a), fy + 290 * np.sin(a))], 3, ink=0.6, dry=0.5, profile=SWEEP, seed=70 + k), 0, 1)
    arc = [(fx + 290 * np.cos(a), fy + 290 * np.sin(a)) for a in np.linspace(-2.55, -0.6, 20)]
    arc_in = [(fx + 120 * np.cos(a), fy + 120 * np.sin(a)) for a in np.linspace(-0.6, -2.55, 12)]
    red.add(pwash(W, H, arc + arc_in, ink=0.5, soft=2, seed=85, grain=0.5), 0, 1)
    ss.add(stroke(W, H, spline(arc, 6), 5, ink=0.8, dry=0.4, profile=BLUNT, seed=86), 0, 1)
    # silk cords
    ss.add(stroke(W, H, spline([(fx, fy), (fx - 30, fy + 40), (fx - 10, fy + 60)], 6), 3, ink=0.6, dry=0.5, profile=SWEEP, seed=87), 0, 1)
    return {'ink': _f(np.maximum(ss.render(9), _hills(1250, 6, 0.4))), 'red': _f(red.render(9))}


# ------------------------------------------------------------------ 鎌倉: a samurai helmet over a stormy sea of junks
def kamakura():
    ss, red, gold = StrokeSet(W, H), StrokeSet(W, H), StrokeSet(W, H)
    cx, cy = 540, 1010
    bowl = [(cx + 150 * np.cos(a), cy + 120 * np.sin(a)) for a in np.linspace(np.pi, 2 * np.pi, 24)]
    ss.add(pwash(W, H, bowl + [(cx + 150, cy + 10), (cx - 150, cy + 10)], ink=0.85, soft=1.6, seed=101, grain=0.3), 0, 1)
    for k in range(9):                                       # ridges on the bowl
        a = np.pi + (k + 1) * np.pi / 10
        ss.add(stroke(W, H, [(cx, cy - 115), (cx + 148 * np.cos(a), cy + 118 * np.sin(a) + 6)], 2.5, ink=0.35, dry=0.5,
                      profile=SWEEP, seed=110 + k), 0, 1)
    for j in range(4):                                       # the flared neck guard, lames stepping out
        y = cy + 18 + j * 34
        hw = 175 + j * 32
        ss.add(pwash(W, H, [(cx - hw, y), (cx + hw, y), (cx + hw + 30, y + 32), (cx - hw - 30, y + 32)], ink=0.65 - 0.08 * j, soft=1.6,
                     seed=120 + j), 0, 1)
        red.add(stroke(W, H, [(cx - hw - 20, y + 30), (cx + hw + 20, y + 30)], 4, ink=0.8, dry=0.4, profile=BLUNT, seed=130 + j), 0, 1)
    for s in (-1, 1):                                        # the golden horns (kuwagata)
        gold.add(stroke(W, H, spline([(cx + s * 20, cy - 70), (cx + s * 90, cy - 160), (cx + s * 150, cy - 230)], 8), 22, ink=0.9, dry=0.35,
                        profile=((0, 1), (0.7, 0.8), (1, 0.15)), seed=140 + s), 0, 1)
    gold.add(pwash(W, H, [(cx - 22, cy - 20), (cx + 22, cy - 20), (cx + 14, cy - 70), (cx - 14, cy - 70)], ink=0.85, soft=1.5, seed=143), 0, 1)
    # the sea and the storm
    for k in range(6):
        y = 1290 + k * 14
        ss.add(stroke(W, H, spline([(80, y), (300, y - 12), (540, y + 6), (780, y - 10), (1000, y)], 10), 3, ink=0.5, dry=0.6,
                      profile=SWEEP, seed=150 + k), 0, 1)
    for k in range(5):
        y0 = 870 + k * 26
        ss.add(stroke(W, H, spline([(60 + 30 * k, y0), (300, y0 - 30), (520, y0 - 10)], 8), 3, ink=0.3, dry=0.7, profile=SWEEP,
                      seed=160 + k), 0, 1)
    return {'ink': _f(ss.render(9)), 'red': _f(red.render(9)), 'gold': _f(gold.render(9))}


# ------------------------------------------------------------------ 室町: the Golden Pavilion over its pond
def muromachi():
    ss, gold = StrokeSet(W, H), StrokeSet(W, H)
    cx, base = 540, 1235
    tiers = [(300, 105, 0.0), (260, 95, 0.0), (190, 85, 1.0)]       # (width, height, gold)
    y = base
    for k, (w, h, g) in enumerate(tiers):
        body = [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2, y - h), (cx - w / 2, y - h)]
        (gold if g or k == 1 else ss).add(pwash(W, H, body, ink=0.75 if (g or k == 1) else 0.18, soft=1.5, seed=170 + k, grain=0.35), 0, 1)
        for j in range(5):
            x = cx - w / 2 + (j + 0.5) * w / 5
            ss.add(stroke(W, H, [(x, y), (x, y - h + 6)], 3, ink=0.55, dry=0.4, profile=BLUNT, seed=175 + k * 5 + j), 0, 1)
        y -= h
        rw = w / 2 + 60
        ss.add(pwash(W, H, [(cx - rw, y + 4), (cx + rw, y + 4), (cx + rw * 0.55, y - 38), (cx - rw * 0.55, y - 38)], ink=0.8, soft=1.5,
                     seed=190 + k), 0, 1)
        ss.add(stroke(W, H, spline([(cx - rw - 12, y - 6), (cx, y + 6), (cx + rw + 12, y - 6)], 8), 6, ink=0.9, dry=0.3, profile=BLUNT,
                      seed=195 + k), 0, 1)
        y -= 38
    gold.add(pwash(W, H, [(cx - 18, y), (cx + 18, y), (cx + 26, y - 40), (cx, y - 60), (cx - 26, y - 40)], ink=0.9, soft=1.2, seed=199), 0, 1)
    top = ss.render(9)
    g = gold.render(9)
    # reflections in the pond, broken by ripples
    yy = np.arange(H)[:, None]
    rip = 0.6 + 0.4 * np.sin(yy / 2.5 + noise(H, W, 40, 2, 7) * 3)
    def mirror(a):
        m = np.zeros_like(a)
        n = min(H - base - 6, base - 700)
        m[base + 6:base + 6 + n] = np.flipud(a[base - n:base]) * 0.3
        return m * rip * np.clip((base + 260 - yy) / 260, 0, 1)
    pine = StrokeSet(W, H)
    for k, (x, s) in enumerate(((150, 1), (930, -1))):
        pine.add(stroke(W, H, spline([(x, base), (x + 20 * s, base - 120), (x - 10 * s, base - 220)], 8), 14, ink=0.8, dry=0.4,
                        profile=BLUNT, seed=210 + k), 0, 1)
        for j in range(4):
            yb = base - 110 - j * 40
            pine.add(pwash(W, H, [(x - 70 + j * 10, yb), (x + 70 - j * 10, yb), (x, yb - 34)], ink=0.55, soft=3, seed=220 + k * 5 + j,
                           grain=0.5), 0, 1)
    pn = pine.render(9)
    shore = StrokeSet(W, H)
    shore.add(stroke(W, H, [(70, base + 6), (1010, base + 4)], 5, ink=0.6, dry=0.5, profile=SWEEP, seed=230), 0, 1)
    return {'ink': _f(np.maximum.reduce([top, mirror(top), pn, mirror(pn), shore.render(9)])), 'gold': _f(np.maximum(g, mirror(g)))}


# ------------------------------------------------------------------ 戦国: a castle keep between war banners
def sengoku():
    ss, red = StrokeSet(W, H), StrokeSet(W, H)
    cx, base = 540, 1330
    ss.add(pwash(W, H, [(cx - 300, base), (cx + 300, base), (cx + 240, base - 110), (cx - 240, base - 110)], ink=0.5, soft=2, seed=240,
                 grain=0.55), 0, 1)
    r = np.random.default_rng(3)
    for j in range(4):                                       # stone courses
        y = base - 25 - j * 28
        ss.add(stroke(W, H, [(cx - 290 + j * 14, y), (cx + 290 - j * 14, y)], 2, ink=0.4, dry=0.6, profile=SWEEP, seed=241 + j), 0, 1)
    y = base - 110
    for k, (w, h) in enumerate(((360, 90), (290, 80), (210, 70), (140, 60))):
        ss.add(pwash(W, H, [(cx - w / 2, y), (cx + w / 2, y), (cx + w / 2, y - h), (cx - w / 2, y - h)], ink=0.06, soft=1.2, seed=250 + k), 0, 1)
        for s in (-1, 1):
            ss.add(stroke(W, H, [(cx + s * w / 2, y), (cx + s * w / 2, y - h)], 4, ink=0.7, dry=0.3, profile=BLUNT, seed=255 + k * 2 + s), 0, 1)
        for j in range(3):                                   # windows
            x = cx - w / 3 + j * w / 3
            ss.add(pwash(W, H, [(x - 9, y - h * 0.35), (x + 9, y - h * 0.35), (x + 9, y - h * 0.65), (x - 9, y - h * 0.65)], ink=0.8, soft=1,
                         seed=260 + k * 3 + j), 0, 1)
        y -= h
        rw = w / 2 + 55
        ss.add(pwash(W, H, [(cx - rw, y + 4), (cx + rw, y + 4), (cx + rw * 0.6, y - 28), (cx - rw * 0.6, y - 28)], ink=0.85, soft=1.4,
                     seed=270 + k), 0, 1)
        ss.add(stroke(W, H, spline([(cx - rw - 18, y - 12), (cx, y + 4), (cx + rw + 18, y - 12)], 8), 6, ink=0.95, dry=0.3, profile=BLUNT,
                      seed=275 + k), 0, 1)
        y -= 28
    # the war banners (nobori), three on each side
    for k, x in enumerate((110, 190, 270, 810, 890, 970)):
        h0 = base - 330 - 40 * (k % 3)
        ss.add(stroke(W, H, [(x, base + 10), (x, h0 - 20)], 4, ink=0.85, dry=0.3, profile=BLUNT, seed=280 + k), 0, 1)
        red.add(pwash(W, H, [(x + 4, h0), (x + 58, h0 + 8), (x + 56, h0 + 240), (x + 4, h0 + 236)], ink=0.8, soft=1.5, seed=290 + k, grain=0.5), 0, 1)
        ss.add(_ring(x + 31, h0 + 70, 16, w=4, ink=0.8, seed=300 + k, sweep=6.2), 0, 1)
    return {'ink': _f(ss.render(9)), 'red': _f(red.render(9))}


# ------------------------------------------------------------------ 江戸: a great wave with Fuji beyond it
def edo():
    blue, ss = StrokeSet(W, H), StrokeSet(W, H)
    # Fuji, small, in the trough
    fuji = [(620, 1260), (700, 1190), (760, 1185), (840, 1260)]
    ss.add(pwash(W, H, fuji, ink=0.5, soft=2, seed=310), 0, 1)
    ss.add(pwash(W, H, [(700, 1190), (760, 1185), (775, 1205), (745, 1200), (730, 1212), (712, 1200), (688, 1206)], ink=0.0, soft=1, seed=311), 0, 1)
    # the big wave: a curling crest with a hollow, claws of foam along its lip
    outer = [(80, 1340), (110, 1150), (200, 990), (330, 900), (470, 880), (560, 930), (560, 990), (505, 960), (450, 965), (420, 1010),
             (430, 1080), (480, 1140), (560, 1200), (650, 1300), (700, 1340)]
    blue.add(pwash(W, H, outer, ink=0.7, soft=2.5, seed=312, grain=0.4), 0, 1)
    for k in range(9):                                       # lines inside the body of the wave
        off = k * 22
        blue.add(stroke(W, H, spline([(120 + off, 1330), (150 + off, 1170), (240 + off * 0.8, 1020), (360 + off * 0.5, 940 + off * 0.3)], 8),
                        3, ink=0.6, dry=0.5, profile=SWEEP, seed=313 + k), 0, 1)
    for k in range(10):                                      # foam claws on the lip
        a = np.pi * (0.95 + 0.07 * k)
        x0, y0 = 470 + 95 * np.cos(a + np.pi), 960 + 80 * np.sin(a + np.pi)
        ss.add(stroke(W, H, spline([(x0, y0), (x0 + 22, y0 + 26), (x0 + 6, y0 + 46)], 6), 5, ink=0.85, dry=0.4, profile=SWEEP,
                      seed=330 + k), 0, 1)
    # a second, smaller wave and the boats
    blue.add(pwash(W, H, [(640, 1340), (720, 1270), (820, 1230), (920, 1250), (1000, 1300), (1010, 1340)], ink=0.5, soft=2.5, seed=345), 0, 1)
    for k, x in enumerate((300, 790)):
        ss.add(stroke(W, H, spline([(x - 90, 1240 + 60 * k), (x, 1262 + 60 * k), (x + 90, 1236 + 60 * k)], 6), 12, ink=0.8, dry=0.35,
                      profile=BLUNT, seed=350 + k), 0, 1)
    sky = np.zeros((H, W), np.float32)
    return {'ink': _f(ss.render(9)), 'blue': _f(blue.render(9)), 'grey': sky}


# ------------------------------------------------------------------ 黒船: steam frigates with smoke
def ships():
    ss, red = StrokeSet(W, H), StrokeSet(W, H)
    for k, (x, y, s) in enumerate(((560, 1250, 1.0), (230, 1170, 0.55), (880, 1150, 0.45))):
        hull = [(x - 260 * s, y - 40 * s), (x + 300 * s, y - 50 * s), (x + 250 * s, y + 30 * s), (x - 230 * s, y + 30 * s)]
        ss.add(pwash(W, H, hull, ink=0.92, soft=1.5, seed=360 + k), 0, 1)
        ss.add(pwash(W, H, [(x - 30 * s, y - 40 * s), (x + 10 * s, y - 40 * s), (x + 10 * s, y - 150 * s), (x - 30 * s, y - 150 * s)],
                     ink=0.9, soft=1.2, seed=365 + k), 0, 1)              # funnel
        ss.add(_ring(x - 120 * s, y - 25 * s, 50 * s, w=5 * s, ink=0.6, seed=368 + k, start=np.pi, sweep=np.pi), 0, 1)   # paddle box
        for j, mx in enumerate((-180, 120, 230)):
            ss.add(stroke(W, H, [(x + mx * s, y - 40 * s), (x + mx * s, y - 330 * s)], 4 * s, ink=0.85, dry=0.3, profile=BLUNT,
                          seed=370 + k * 3 + j), 0, 1)
            for yy in (-150, -250):
                ss.add(stroke(W, H, [(x + mx * s - 60 * s, y + yy * s), (x + mx * s + 60 * s, y + yy * s)], 3 * s, ink=0.7, dry=0.4,
                              profile=BLUNT, seed=380 + k * 6 + j * 2 + (yy > -200)), 0, 1)
        red.add(stroke(W, H, [(x - 250 * s, y - 20 * s), (x + 290 * s, y - 28 * s)], 6 * s, ink=0.7, dry=0.4, profile=BLUNT, seed=390 + k), 0, 1)
    for k in range(5):
        y = 1300 + k * 12
        ss.add(stroke(W, H, spline([(60, y), (400, y - 8), (700, y + 4), (1020, y - 4)], 8), 2.5, ink=0.45, dry=0.6, profile=SWEEP,
                      seed=395 + k), 0, 1)
    return {'ink': _f(ss.render(9)), 'red': _f(red.render(9))}


# ------------------------------------------------------------------ 明治 / 大正 / 昭和 / 平成 / 令和
def meiji():
    """the backdrop for the steam train: rails, telegraph poles, a factory with chimneys on the horizon"""
    ss = StrokeSet(W, H)
    for y in (1300, 1322):
        ss.add(stroke(W, H, [(40, y), (1040, y)], 4, ink=0.8, dry=0.35, profile=BLUNT, seed=400 + y), 0, 1)
    for k in range(24):
        x = 40 + k * 44
        ss.add(stroke(W, H, [(x, 1296), (x - 8, 1330)], 6, ink=0.5, dry=0.4, profile=BLUNT, seed=410 + k), 0, 1)
    ss.add(pwash(W, H, [(700, 1150), (980, 1150), (980, 1060), (900, 1090), (900, 1060), (820, 1090), (820, 1060), (740, 1090), (700, 1090)],
                 ink=0.35, soft=1.5, seed=440), 0, 1)
    for k, x in enumerate((760, 860)):
        ss.add(pwash(W, H, [(x, 1060), (x + 22, 1060), (x + 18, 940), (x + 4, 940)], ink=0.45, soft=1.2, seed=445 + k), 0, 1)
    for k, x in enumerate((140, 400, 660)):
        ss.add(stroke(W, H, [(x, 1290), (x, 1060)], 5, ink=0.6, dry=0.4, profile=BLUNT, seed=450 + k), 0, 1)
        ss.add(stroke(W, H, [(x - 30, 1080), (x + 30, 1080)], 4, ink=0.6, dry=0.4, profile=BLUNT, seed=455 + k), 0, 1)
    ss.add(stroke(W, H, spline([(140, 1084), (270, 1100), (400, 1084), (530, 1100), (660, 1084), (1040, 1090)], 10), 2, ink=0.4, dry=0.5,
                  profile=SWEEP, seed=460), 0, 1)
    return {'ink': _f(np.maximum(ss.render(9), _hills(1220, 8, 0.35)))}


def taisho():
    """a streetcar under its wire, Western-style brick front behind; the earthquake crack is a separate layer"""
    ss, red = StrokeSet(W, H), StrokeSet(W, H)
    # a brick building with a clock tower
    ss.add(pwash(W, H, [(620, 1260), (980, 1260), (980, 1000), (620, 1000)], ink=0.2, soft=1.5, seed=470), 0, 1)
    ss.add(pwash(W, H, [(760, 1000), (840, 1000), (840, 880), (800, 840), (760, 880)], ink=0.3, soft=1.5, seed=471), 0, 1)
    ss.add(_ring(800, 920, 22, w=4, ink=0.8, seed=472, sweep=6.2), 0, 1)
    for j in range(3):
        for i in range(5):
            x, y = 650 + i * 66, 1040 + j * 70
            ss.add(pwash(W, H, [(x, y), (x + 30, y), (x + 30, y + 40), (x, y + 40)], ink=0.6, soft=1, seed=480 + j * 5 + i), 0, 1)
    # the streetcar
    x0, y0 = 120, 1290
    body = [(x0, y0), (x0 + 430, y0), (x0 + 440, y0 - 170), (x0 - 10, y0 - 170)]
    red.add(pwash(W, H, body, ink=0.55, soft=1.8, seed=500, grain=0.4), 0, 1)
    ss.add(pwash(W, H, [(x0 - 20, y0 - 170), (x0 + 450, y0 - 170), (x0 + 420, y0 - 200), (x0 + 10, y0 - 200)], ink=0.85, soft=1.5, seed=501), 0, 1)
    for i in range(5):
        x = x0 + 30 + i * 80
        ss.add(pwash(W, H, [(x, y0 - 150), (x + 55, y0 - 150), (x + 55, y0 - 90), (x, y0 - 90)], ink=0.0, soft=1, seed=505 + i), 0, 1)
        ss.add(stroke(W, H, [(x, y0 - 150), (x + 55, y0 - 150), (x + 55, y0 - 90), (x, y0 - 90), (x, y0 - 150)], 3, ink=0.85, dry=0.3,
                      profile=BLUNT, seed=510 + i), 0, 1)
    for x in (x0 + 80, x0 + 350):
        ss.add(_ring(x, y0 + 4, 26, w=7, ink=0.9, seed=520 + x, sweep=6.2), 0, 1)
    ss.add(stroke(W, H, [(x0 + 220, y0 - 200), (x0 + 300, y0 - 330)], 4, ink=0.8, dry=0.3, profile=BLUNT, seed=530), 0, 1)
    ss.add(stroke(W, H, [(40, 958), (1040, 952)], 2, ink=0.6, dry=0.5, profile=SWEEP, seed=531), 0, 1)
    ss.add(stroke(W, H, [(40, y0 + 30), (1040, y0 + 30)], 5, ink=0.7, dry=0.4, profile=BLUNT, seed=532), 0, 1)
    return {'ink': _f(ss.render(9)), 'red': _f(red.render(9))}


def crack():
    """the earthquake: a jagged crack splitting the street from left to right, with branches"""
    ss = StrokeSet(W, H)
    r = np.random.default_rng(9)
    x, y, pts = 60, 1330, []
    while x < 1040:
        pts.append((x, y))
        x += r.uniform(40, 80)
        y = 1330 + r.uniform(-24, 24)
    ss.add(stroke(W, H, pts, 10, ink=0.95, dry=0.35, profile=((0, 0.3), (0.2, 1), (0.8, 1), (1, 0.3)), seed=540), 0, 1)
    for k in range(6):
        px, py = pts[2 + k * 2]
        ss.add(stroke(W, H, [(px, py), (px + r.uniform(-30, 30), py + r.uniform(25, 45)), (px + r.uniform(-50, 50), py + r.uniform(50, 80))],
                      4, ink=0.85, dry=0.4, profile=SWEEP, seed=550 + k), 0, 1)
    return _f(ss.render(9))


def showa():
    """Fuji in the distance over a viaduct: the bullet train is a sprite that crosses it"""
    ss, red = StrokeSet(W, H), StrokeSet(W, H)
    xs = np.arange(W, dtype=np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None]
    ridge = 900 + 330 * (1 - np.exp(-np.clip(np.abs(xs - 600) - 40, 0, None) / 260))
    depth = yy - ridge[None]
    snow = (depth > 0) & (depth < 90 - 0.25 * np.abs(xs - 600)[None])
    fuji = (depth > 0) * (0.35 * np.exp(-np.clip(depth, 0, None) / 300)) * (1 - snow) * (0.7 + 0.3 * noise(H, W, 40, 3, 11))
    fuji[1180:] = 0
    from art import sun_disc
    sun = sun_disc(H, W, 860, 900, 80, seed=12)
    ss.add(pwash(W, H, [(0, 1250), (1080, 1250), (1080, 1268), (0, 1268)], ink=0.85, soft=1.2, seed=560), 0, 1)
    for k in range(8):
        x = 60 + k * 140
        ss.add(pwash(W, H, [(x, 1268), (x + 26, 1268), (x + 32, 1350), (x - 6, 1350)], ink=0.7, soft=1.2, seed=565 + k), 0, 1)
        ss.add(stroke(W, H, spline([(x + 26, 1290), (x + 83, 1318), (x + 140, 1290)], 8), 4, ink=0.6, dry=0.4, profile=BLUNT, seed=575 + k), 0, 1)
    return {'ink': _f(np.maximum(ss.render(9), fuji)), 'red': _f(sun)}


def heisei():
    """a city skyline: the bubble, the wave and the globe are drawn by the scene"""
    ss = StrokeSet(W, H)
    r = np.random.default_rng(14)
    x = 60
    while x < 1020:
        w = r.uniform(50, 110)
        h = r.uniform(80, 200)
        ss.add(pwash(W, H, [(x, 1330), (x + w, 1330), (x + w, 1330 - h), (x, 1330 - h)], ink=r.uniform(0.15, 0.4), soft=1.5,
                     seed=int(r.integers(1e6))), 0, 1)
        for j in range(int(h / 40)):
            ss.add(stroke(W, H, [(x + 10, 1310 - j * 40), (x + w - 10, 1310 - j * 40)], 2, ink=0.3, dry=0.6, profile=SWEEP,
                          seed=int(r.integers(1e6))), 0, 1)
        x += w + r.uniform(4, 16)
    _ground(ss, 1334, seed=600)
    return {'ink': _f(ss.render(9))}


def reiwa():
    """a plum branch in flower reaching across a rising sun: the Reiwa poem is about plum blossoms"""
    ss = StrokeSet(W, H)
    centres = cherry_branch(ss, [(-40, 1290), (180, 1220), (380, 1170), (560, 1120), (760, 1040), (900, 990)], 24, 0, 1, seed=61)
    bl = np.zeros((H, W), np.float32)
    r = np.random.default_rng(71)
    path = spline([(-40, 1290), (180, 1220), (380, 1170), (560, 1120), (760, 1040), (900, 990)], 40)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    centre = np.zeros((H, W), np.float32)
    for k in range(30):
        px, py = path[int(r.uniform(4, len(path) - 1))] if k < 24 else centres[k % len(centres)]
        cx, cy = px + r.normal(0, 36), py + r.normal(-10, 30)
        rad = r.uniform(14, 24)
        rot = r.uniform(0, 2 * np.pi)
        y0, y1, x0, x1 = int(cy - 3 * rad), int(cy + 3 * rad), int(cx - 3 * rad), int(cx + 3 * rad)
        if y0 < 0 or x0 < 0 or x1 >= W or y1 >= H:
            continue
        X, Y = xx[y0:y1, x0:x1] - cx, yy[y0:y1, x0:x1] - cy
        f = np.zeros_like(X)
        for j in range(5):                               # five round petals
            a_ = rot + j * 2 * np.pi / 5
            f = np.maximum(f, np.clip(1 - np.hypot(X - rad * np.cos(a_), Y - rad * np.sin(a_)) / (rad * 0.75), 0, 1) ** 0.6)
        bl[y0:y1, x0:x1] = np.maximum(bl[y0:y1, x0:x1], f * r.uniform(0.75, 0.95))
        centre[y0:y1, x0:x1] = np.maximum(centre[y0:y1, x0:x1], np.clip(1 - np.hypot(X, Y) / (rad * 0.28), 0, 1))
    ss.add(stroke(W, H, [(0, 0), (1, 1)], 1, ink=0.0, seed=1), 0, 1)
    from art import sun_disc
    sun = sun_disc(H, W, 640, 1080, 210, seed=13)
    return {'ink': _f(np.maximum.reduce([ss.render(9), _hills(1250, 15, 0.4), centre * 0.8])), 'red': _f(sun * 0.85), 'bloss': _f(bl)}


# ------------------------------------------------------------------ sprites the scenes move
def steam_train(w=760, h=300):
    """a steam locomotive and tender, facing right, on its own canvas; returns (ink, red)"""
    ss, red = StrokeSet(w, h), StrokeSet(w, h)
    y = h - 40
    ss.add(pwash(w, h, [(300, y - 30), (640, y - 30), (650, y - 140), (300, y - 140)], ink=0.92, soft=1.4, seed=1), 0, 1)     # boiler
    ss.add(pwash(w, h, [(160, y - 30), (300, y - 30), (300, y - 210), (160, y - 210)], ink=0.92, soft=1.4, seed=2), 0, 1)     # cab
    ss.add(pwash(w, h, [(140, y - 210), (320, y - 210), (310, y - 236), (150, y - 236)], ink=0.95, soft=1.2, seed=3), 0, 1)
    ss.add(pwash(w, h, [(185, y - 180), (235, y - 180), (235, y - 120), (185, y - 120)], ink=0.0, soft=1, seed=4), 0, 1)
    ss.add(pwash(w, h, [(560, y - 140), (600, y - 140), (612, y - 230), (548, y - 230)], ink=0.95, soft=1.2, seed=5), 0, 1)   # chimney
    ss.add(pwash(w, h, [(640, y - 30), (720, y - 30), (680, y - 80), (650, y - 80)], ink=0.8, soft=1.2, seed=6), 0, 1)       # cowcatcher
    ss.add(pwash(w, h, [(10, y - 30), (150, y - 30), (150, y - 150), (10, y - 150)], ink=0.85, soft=1.4, seed=7), 0, 1)       # tender
    for k, (x, r) in enumerate(((60, 30), (115, 30), (230, 52), (350, 52), (470, 52), (600, 34))):
        ss.add(_ring_s(w, h, x, y - r + 10, r, 6, 10 + k), 0, 1)
    red.add(stroke(w, h, [(300, y - 60), (640, y - 60)], 6, ink=0.85, dry=0.4, profile=BLUNT, seed=20), 0, 1)
    red.add(stroke(w, h, [(230, y - 20), (470, y - 20)], 5, ink=0.85, dry=0.4, profile=BLUNT, seed=21), 0, 1)
    return _f(ss.render(9)), _f(red.render(9))


def bullet_train(w=1100, h=170):
    """the 0-series shinkansen facing right: white body, blue band, rounded nose; returns (ink, blue)"""
    ss, blue = StrokeSet(w, h), StrokeSet(w, h)
    top, bot = 30, 140
    nose = [(w - 210 + 200 * np.sin(a), (top + bot) / 2 - (bot - top) / 2 * np.cos(a)) for a in np.linspace(0, np.pi, 20)]
    outline = [(20, bot), (w - 210, bot)] + nose[::-1] + [(20, top)]
    ss.add(pwash(w, h, outline, ink=0.07, soft=1.2, seed=1), 0, 1)
    ss.add(stroke(w, h, outline + [(20, bot)], 4, ink=0.85, dry=0.3, profile=BLUNT, seed=2), 0, 1)
    blue.add(pwash(w, h, [(20, 92), (w - 140, 92), (w - 90, 110), (w - 120, 124), (20, 124)], ink=0.85, soft=1.2, seed=3), 0, 1)
    for k in range(14):
        x = 50 + k * 62
        ss.add(pwash(w, h, [(x, 48), (x + 40, 48), (x + 40, 74), (x, 74)], ink=0.6, soft=1, seed=10 + k), 0, 1)
    ss.add(pwash(w, h, [(w - 200, 48), (w - 110, 52), (w - 125, 74), (w - 200, 74)], ink=0.75, soft=1, seed=30), 0, 1)
    return _f(ss.render(9)), _f(blue.render(9))


def _ring_s(w, h, cx, cy, r, width, seed):
    pts = [(cx + r * np.cos(a), cy + r * np.sin(a)) for a in np.linspace(0, 2 * np.pi * 1.02, 30)]
    return stroke(w, h, spline(pts, 4), width, ink=0.9, dry=0.35, profile=BLUNT, seed=seed)


def smoke_puff(s=140, seed=0):
    """one soft grey puff of smoke"""
    yy, xx = np.mgrid[0:s, 0:s] - s / 2
    d = np.clip(1 - np.hypot(xx, yy) / (s / 2), 0, 1) ** 1.5 * (0.6 + 0.4 * noise(s, s, 14, 3, seed))
    return _f(blur(d, 2))


def bubble(s=420):
    """a soap bubble: a thin ring with a highlight (the bubble economy)"""
    yy, xx = np.mgrid[0:s, 0:s] - s / 2
    r = np.hypot(xx, yy) / (s / 2 - 10)
    ring = np.exp(-((r - 0.97) / 0.03) ** 2)
    hl = np.exp(-(((xx + s * 0.18) / (s * 0.08)) ** 2 + ((yy + s * 0.2) / (s * 0.04)) ** 2))
    return _f(ring * 0.8 + hl * 0.5 + (r < 1) * 0.04)


def globe(s=300):
    """a globe in ink: outline, meridians and parallels"""
    ss = StrokeSet(s, s)
    c, r = s / 2, s / 2 - 12
    ss.add(_ring_s(s, s, c, c, r, 5, 1), 0, 1)
    for k, f in enumerate((0.35, 0.75)):
        pts = [(c + r * f * np.sin(a), c - r * np.cos(a)) for a in np.linspace(0, np.pi, 16)]
        ss.add(stroke(s, s, spline(pts, 4), 2.5, ink=0.7, dry=0.4, profile=SWEEP, seed=2 + k), 0, 1)
        ss.add(stroke(s, s, spline([(2 * c - x, y) for x, y in pts], 4), 2.5, ink=0.7, dry=0.4, profile=SWEEP, seed=4 + k), 0, 1)
    for k, yy in enumerate((-0.5, 0, 0.5)):
        hw = r * np.sqrt(1 - yy ** 2)
        ss.add(stroke(s, s, [(c - hw, c + yy * r), (c + hw, c + yy * r)], 2.5, ink=0.7, dry=0.4, profile=SWEEP, seed=8 + k), 0, 1)
    return _f(ss.render(9))


def wave_line(w=1080, h=260, seed=0):
    """a rolling wave crest for the tsunami line, kept restrained: one indigo swell"""
    ss = StrokeSet(w, h)
    for k in range(5):
        y = 120 + k * 22
        ss.add(stroke(w, h, spline([(0, y + 30), (250, y - 50 + k * 8), (520, y + 10), (780, y - 40), (1080, y + 20)], 10), 8 - k, ink=0.8 - 0.1 * k,
                      dry=0.5, profile=SWEEP, seed=seed + k), 0, 1)
    return _f(ss.render(9))


def junks():
    """three small junks for the Mongol fleet; each (ink, red)"""
    return [junk() for _ in range(3)]
