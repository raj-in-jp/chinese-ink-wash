"""Painted illustrations for reel 13 (大和), RGBA float images built on draw11's Canvas, ink-wash palette:
    gate_view()     two mountains with a pass between them, a path running through it — "mountain gate" (山門)
    valley_view()   a village of little roofs in a valley ringed by mountains — "the place of the mountains" (山処)
    flame()         a brushed vermilion flame for 大和魂 (alpha only)
    nadeshiko()     a pink fringed nadeshiko (Dianthus superbus) flower, returned petal by petal so it can open
    sun_icon()      a small red sun for 今日
    person(h)       a little ink figure (child / adult sizes for 大人)"""
import cv2
import numpy as np

from draw11 import SS, Canvas, _noise, blur

MOUNT = np.array((0.36, 0.42, 0.40))
MIST = np.array((0.80, 0.83, 0.80))


def _range(c, base, peaks, col, op=1.0, soft=1.5):
    """a mountain silhouette through the given (x, y) peaks, filled down to y = base"""
    pts = [(peaks[0][0], base)] + list(peaks) + [(peaks[-1][0], base)]
    m = c.poly(pts, soft)
    c.lay(col, m, op)
    return m


def gate_view(w=440, h=360, seed=3):
    c = Canvas(w, h)
    sky = c.poly([(0, 0), (w, 0), (w, h), (0, h)], 0)
    c.lay(np.asarray((0.95, 0.93, 0.86))[None, None] * np.ones((1, 1, 3)), sky)
    c.lay((0.98, 0.80, 0.70), blur(c.ell(w / 2, 150, 60, 60), 20), 0.6)           # light through the pass
    _range(c, h, [(0, 170), (60, 120), (120, 60), (170, 110), (205, 230)], MOUNT * 0.9)
    _range(c, h, [(235, 230), (275, 100), (330, 40), (390, 110), (w, 160)], MOUNT * 0.85)
    _range(c, h, [(0, 280), (120, 250), (200, 300), (260, 300), (330, 250), (w, 270)], MOUNT * 0.65)
    path = c.poly([(w / 2 - 6, 235), (w / 2 + 6, 235), (w / 2 + 70, h), (w / 2 - 70, h)], 1)
    c.lay((0.88, 0.80, 0.62), path)
    c.lay(MIST, blur(c.poly([(0, 220), (w, 210), (w, 250), (0, 260)], 0), 12), 0.5)
    return c.out()


def valley_view(w=440, h=360, seed=4):
    c = Canvas(w, h)
    c.lay((0.95, 0.93, 0.86), c.poly([(0, 0), (w, 0), (w, h), (0, h)], 0))
    _range(c, h, [(0, 120), (70, 60), (140, 110), (220, 70), (300, 120), (370, 50), (w, 100)], MOUNT * 0.95)
    _range(c, h, [(0, 200), (60, 170), (110, 230), (330, 230), (380, 160), (w, 190)], MOUNT * 0.75)
    c.lay((0.62, 0.70, 0.46), c.poly([(60, 260), (380, 260), (w, h), (0, h)], 2))      # the valley floor
    r = np.random.default_rng(seed)
    for k in range(9):                                                                  # little roofs
        x, y = 120 + k * 26 + r.uniform(-8, 8), 270 + (k % 3) * 18
        c.lay((0.30, 0.22, 0.18), c.poly([(x - 14, y), (x, y - 12), (x + 14, y)], 0.6))
        c.lay((0.92, 0.88, 0.78), c.poly([(x - 10, y), (x + 10, y), (x + 10, y + 10), (x - 10, y + 10)], 0.6))
    c.lay(MIST, blur(c.poly([(0, 230), (w, 225), (w, 255), (0, 262)], 0), 12), 0.45)
    return c.out()


def flame(w=320, h=440, seed=5):
    """a painted flame: three curling tongues, red outside, orange then yellow at the core; returns (rgb, a)"""
    c = Canvas(w, h)
    def tongue(x0, height, width, curl, ph):
        us = np.linspace(0, 1, 70)
        cx = [x0 + curl * width * np.sin(u * np.pi * 1.3 + ph) * u for u in us]
        hw = [width * (np.sin(np.pi * min(u * 2.2, 1) / 2) ** 0.7) * (1 - u) ** 1.25 for u in us]
        y = [h - 18 - u * height for u in us]
        left = [(x - ww, yy) for x, ww, yy in zip(cx, hw, y)]
        right = [(x + ww, yy) for x, ww, yy in zip(cx, hw, y)][::-1]
        return c.poly(left + right, 1.2)
    outer = np.clip(tongue(w / 2, h * 0.92, w * 0.36, 0.35, 0.3) + tongue(w / 2 - 62, h * 0.55, w * 0.22, -0.4, 1.0)
                    + tongue(w / 2 + 66, h * 0.62, w * 0.22, 0.45, 2.0), 0, 1)
    mid = np.clip(tongue(w / 2, h * 0.66, w * 0.25, 0.3, 0.6) + tongue(w / 2 + 50, h * 0.40, w * 0.14, 0.4, 2.2), 0, 1)
    core = tongue(w / 2, h * 0.40, w * 0.15, 0.25, 0.9)
    n = _noise(c.h, c.w, 10 * SS, seed, 3)
    c.lay(np.asarray((0.80, 0.14, 0.08))[None, None] * (0.9 + 0.2 * n[..., None]), outer)
    c.lay((0.95, 0.42, 0.10), mid * outer)
    c.lay((1.0, 0.82, 0.30), core * outer)
    return c.out()


def nadeshiko(w=420, h=420, seed=6):
    """a pink nadeshiko seen from the front: five deeply fringed petals, a darker eye, stamens;
    returns a list of 5 petal layers (rgb, a) plus the centre (rgb, a), all the same size"""
    cx, cy = w / 2, h / 2
    petals = []
    for k in range(5):
        c = Canvas(w, h)
        a0 = -np.pi / 2 + k * 2 * np.pi / 5
        pts = []
        for u in np.linspace(-1, 1, 41):                     # the fringed outer edge
            ang = a0 + u * 0.55
            fr_ = 1 - 0.28 * (np.abs(np.sin(u * 11 * np.pi)) ** 0.6)   # deep comb-like fringe
            R = 175 * fr_ * (1 - 0.12 * u * u)
            pts.append((cx + R * np.cos(ang), cy + R * np.sin(ang)))
        base = [(cx + 22 * np.cos(a0 + 0.9), cy + 22 * np.sin(a0 + 0.9)), (cx, cy), (cx + 22 * np.cos(a0 - 0.9), cy + 22 * np.sin(a0 - 0.9))]
        m = c.poly(pts + base, 0.8)
        d = np.hypot(c.X - cx, c.Y - cy)
        col = np.stack([0.98 - 0.05 * (d / 175), 0.74 - 0.22 * (d / 175), 0.84 - 0.10 * (d / 175)], -1)
        c.lay(np.clip(col, 0, 1), m)
        for j in range(5):                                   # veins
            ang = a0 + (j - 2) * 0.16
            c.lay((0.86, 0.42, 0.56), c.line([(cx + 30 * np.cos(ang), cy + 30 * np.sin(ang)),
                                              (cx + 120 * np.cos(ang), cy + 120 * np.sin(ang))], 1.6, 0.6) * m, 0.5)
        petals.append(c.out())
    c = Canvas(w, h)
    c.lay((0.70, 0.18, 0.34), c.ell(cx, cy, 46, 46, soft=4), 0.85)                    # the eye
    for j in range(10):
        ang = j * 2 * np.pi / 10
        c.lay((0.96, 0.94, 0.96), c.line([(cx, cy), (cx + 36 * np.cos(ang), cy + 36 * np.sin(ang))], 2.2, 0.5))
        c.lay((0.98, 0.98, 0.98), c.ell(cx + 38 * np.cos(ang), cy + 38 * np.sin(ang), 4, 4, soft=0.6))
    return petals, c.out()


def sun_icon(r=70):
    s = int(r * 2 + 110)
    c = Canvas(s, s)
    c.lay((0.86, 0.22, 0.14), c.ell(s / 2, s / 2, r, r))
    c.lay((1, 1, 1), blur(c.ell(s / 2 - r * 0.35, s / 2 - r * 0.35, r * 0.3, r * 0.2), 4), 0.35)
    return c.out()


def person(h=220):
    """a simple ink figure (alpha): head, body, arms, legs"""
    w = int(h * 0.6)
    S = 3
    m = np.zeros((h * S, w * S), np.uint8)
    P = lambda x, y: (int(x * w * S), int(y * h * S))
    cv2.circle(m, P(0.5, 0.13), int(0.11 * h * S), 255, -1, cv2.LINE_AA)
    cv2.line(m, P(0.5, 0.26), P(0.5, 0.62), 255, int(0.08 * h * S), cv2.LINE_AA)
    cv2.line(m, P(0.5, 0.34), P(0.18, 0.52), 255, int(0.055 * h * S), cv2.LINE_AA)
    cv2.line(m, P(0.5, 0.34), P(0.82, 0.52), 255, int(0.055 * h * S), cv2.LINE_AA)
    cv2.line(m, P(0.5, 0.60), P(0.3, 0.97), 255, int(0.065 * h * S), cv2.LINE_AA)
    cv2.line(m, P(0.5, 0.60), P(0.7, 0.97), 255, int(0.065 * h * S), cv2.LINE_AA)
    return cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
