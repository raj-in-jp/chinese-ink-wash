"""Painted illustrations for reel 12 (RGBA float images, lit from the upper left), built on draw11's Canvas:
    burger()          a generic burger: sesame bun, lettuce, cheese, patty (no brand marks)
    xmas_tree()       a little Christmas tree with baubles and a star; light positions for twinkling
    rice_bowl()       a bowl of glossy rice (draw11's bowl + rice)
    louse()           a tiny cartoon louse, cute not gross
    violin()          a violin: varnished body, f-holes, fingerboard, strings, scroll
    eiffel()          the Eiffel Tower in ink (alpha only)"""
import cv2
import numpy as np

from draw11 import SS, Canvas, _bowl, _noise, _rice, blur


def burger(w=620, h=520, seed=2):
    c = Canvas(w, h)
    cx = w / 2
    c.lay((0, 0, 0), blur(c.ell(cx + 14, h - 40, 270, 34), 12), 0.35)                                   # shadow
    # bottom bun
    bb = c.poly([(cx - 250, h - 120), (cx + 250, h - 120), (cx + 236, h - 70), (cx + 200, h - 50), (cx - 200, h - 50),
                 (cx - 236, h - 70)], 2)
    c.lay((0.86, 0.58, 0.28), bb)
    c.lay((0.70, 0.42, 0.18), bb * np.clip((c.Y - (h - 110)) / 60, 0, 1), 0.5)
    # patty
    pt = c.ell(cx, h - 150, 268, 52, soft=2)
    n = _noise(c.h, c.w, 5 * SS, seed)
    c.lay(np.asarray((0.36, 0.20, 0.12))[None, None] * (0.8 + 0.4 * n[..., None]), pt)
    c.lay((0.22, 0.11, 0.06), pt * np.clip((c.Y - (h - 150)) / 50, 0, 1), 0.6)
    for k in range(-4, 5):                                                                               # grill lines
        c.lay((0.18, 0.08, 0.04), c.line([(cx + k * 50 - 20, h - 190), (cx + k * 50 + 20, h - 120)], 6, 2) * pt, 0.5)
    # cheese: a square slice draping over the patty
    ch = c.poly([(cx - 250, h - 205), (cx + 250, h - 205), (cx + 240, h - 180), (cx + 150, h - 150), (cx + 110, h - 112),
                 (cx + 70, h - 152), (cx - 120, h - 160), (cx - 160, h - 118), (cx - 196, h - 168), (cx - 246, h - 182)], 1.5)
    c.lay((0.98, 0.76, 0.18), ch)
    c.lay((1.0, 0.92, 0.55), ch * np.clip(1 - (c.Y - (h - 205)) / 25, 0, 1), 0.6)
    # lettuce: a wavy green frill
    xs = np.linspace(cx - 280, cx + 280, 40)
    top = [(x, h - 220 + 10 * np.sin(k * 1.3)) for k, x in enumerate(xs)]
    bot = [(x, h - 196 + 14 * np.sin(k * 1.7 + 1)) for k, x in enumerate(xs[::-1])]
    lt = c.poly(top + bot, 1.5)
    c.lay((0.36, 0.66, 0.22), lt)
    c.lay((0.58, 0.82, 0.36), lt * np.clip(1 - (c.Y - (h - 222)) / 18, 0, 1), 0.6)
    # top bun: a dome with sesame seeds and a shine
    tb = np.clip(c.ell(cx, h - 222, 262, 200, 180, 360, 2) + c.poly([(cx - 262, h - 232), (cx + 262, h - 232), (cx + 255, h - 214),
                                                                       (cx - 255, h - 214)], 2), 0, 1)
    shade = np.clip((c.X - cx) / 260 * 0.5 + (c.Y - (h - 420)) / 200 * 0.5, 0, 1)
    c.lay(np.asarray((0.92, 0.62, 0.28))[None, None] * (1.05 - 0.35 * shade[..., None]), tb)
    c.lay((1.0, 0.88, 0.62), blur(c.ell(cx - 90, h - 360, 90, 40), 14) * tb, 0.55)
    r = np.random.default_rng(seed)
    for k in range(34):
        x, y = r.uniform(cx - 220, cx + 220), r.uniform(h - 410, h - 250)
        if tb[int(y * SS), int(x * SS)] < 0.9:
            continue
        a = r.uniform(0, 180)
        m = np.zeros((c.h, c.w), np.uint8)
        cv2.ellipse(m, (int(x * SS), int(y * SS)), (int(9 * SS), int(4.5 * SS)), a, 0, 360, 255, -1, cv2.LINE_AA)
        c.lay((0.99, 0.95, 0.82), m.astype(np.float32) / 255)
    return c.out()


def xmas_tree(w=420, h=560, seed=4):
    c = Canvas(w, h)
    cx = w / 2
    c.lay((0, 0, 0), blur(c.ell(cx + 10, h - 22, 150, 18), 10), 0.3)
    c.lay((0.45, 0.28, 0.16), c.poly([(cx - 26, h - 110), (cx + 26, h - 110), (cx + 26, h - 30), (cx - 26, h - 30)], 1))  # trunk
    c.lay((0.70, 0.14, 0.10), c.poly([(cx - 70, h - 70), (cx + 70, h - 70), (cx + 56, h - 24), (cx - 56, h - 24)], 1))  # pot
    lights = []
    for k, (y0, hw, hh) in enumerate(((h - 110, 190, 150), (h - 200, 150, 140), (h - 290, 112, 130), (h - 370, 76, 110))):
        tier = c.poly([(cx - hw, y0), (cx, y0 - hh), (cx + hw, y0)], 1.2)
        g = np.asarray((0.12, 0.46, 0.24))[None, None] * (0.85 + 0.3 * np.clip((cx - c.X) / hw, -1, 1)[..., None] * 0.5)
        c.lay(g, tier)
        c.lay((0.06, 0.30, 0.14), tier * np.clip((c.Y - (y0 - 18)) / 18, 0, 1), 0.6)
        for j in range(5):                                                                              # garland dots
            u = (j + 0.5) / 5
            lights.append((cx - hw * 0.8 + 2 * hw * 0.8 * u, y0 - 12 - 18 * np.sin(u * np.pi)))
    r = np.random.default_rng(seed)
    cols = [(0.86, 0.16, 0.12), (0.98, 0.78, 0.20), (0.22, 0.42, 0.85), (0.95, 0.95, 0.92)]
    for k, (x, y) in enumerate(lights):
        col = cols[k % 4]
        c.lay(col, c.ell(x, y, 9, 9, soft=0.8))
        c.lay((1, 1, 1), c.ell(x - 3, y - 3, 3, 3, soft=0.6), 0.8)
    star = [(cx + (30 if k % 2 == 0 else 13) * np.cos(-np.pi / 2 + k * np.pi / 5),
             h - 485 + (30 if k % 2 == 0 else 13) * np.sin(-np.pi / 2 + k * np.pi / 5)) for k in range(10)]
    c.lay((0.98, 0.80, 0.20), c.poly(star, 1))
    rgb, a = c.out()
    return rgb, a, np.asarray(lights + [(cx, h - 485)], np.float32)


def rice_bowl(w=440, h=400):
    c = Canvas(w, h)
    op = _bowl(c, w / 2, 150, 165, 150, (0.93, 0.91, 0.86), (0.55, 0.52, 0.48), (0.80, 0.77, 0.70), band=(0.18, 0.28, 0.55))
    _rice(c, w / 2, 150, 165)
    return c.out()


def louse(w=300, h=300):
    """a cute cartoon louse: oval body with segments, six little legs, big eyes"""
    c = Canvas(w, h)
    cx, cy = w / 2, h / 2 + 20
    for side in (-1, 1):
        for k in range(3):
            y = cy - 30 + k * 32
            c.lay((0.30, 0.22, 0.18), c.line([(cx + side * 40, y), (cx + side * 92, y - 18 + k * 10), (cx + side * 110, y + 8 + k * 6)], 7, 1))
    body = c.ell(cx, cy + 10, 62, 82)
    c.lay((0.86, 0.72, 0.56), body)
    c.lay((0.70, 0.54, 0.38), body * np.clip((c.X - cx) / 62, 0, 1), 0.5)
    for k in range(4):
        c.lay((0.62, 0.46, 0.32), c.line([(cx - 52 + abs(k - 1.5) * 4, cy + 10 + k * 22), (cx + 52 - abs(k - 1.5) * 4, cy + 10 + k * 22)], 3, 1)
              * body, 0.7)
    head = c.ell(cx, cy - 78, 44, 38)
    c.lay((0.86, 0.72, 0.56), head)
    for side in (-1, 1):
        c.lay((1, 1, 1), c.ell(cx + side * 18, cy - 84, 14, 16))
        c.lay((0.12, 0.10, 0.10), c.ell(cx + side * 18 + 3, cy - 82, 7, 9))
        c.lay((1, 1, 1), c.ell(cx + side * 18 + 5, cy - 86, 2.5, 2.5))
        c.lay((0.30, 0.22, 0.18), c.line([(cx + side * 14, cy - 112), (cx + side * 36, cy - 142), (cx + side * 46, cy - 136)], 5, 1))
    c.lay((0.75, 0.30, 0.30), c.ell(cx, cy - 62, 8, 4, 0, 180), 0.9)                                    # smile
    return c.out()


def violin(w=300, h=760, seed=6):
    c = Canvas(w, h)
    cx = w / 2
    c.lay((0, 0, 0), blur(c.ell(cx + 18, h * 0.62 + 20, 120, 230), 18), 0.25)
    up = c.ell(cx, h * 0.47, 92, 105, soft=1.2)
    lo = c.ell(cx, h * 0.72, 118, 132, soft=1.2)
    waist = np.clip(c.ell(cx - 118, h * 0.60, 52, 48, soft=1.2) + c.ell(cx + 118, h * 0.60, 52, 48, soft=1.2), 0, 1)
    body = np.clip(np.maximum(up, lo) + c.poly([(cx - 66, h * 0.52), (cx + 66, h * 0.52), (cx + 66, h * 0.68), (cx - 66, h * 0.68)], 1)
                   - waist, 0, 1)
    n = _noise(c.h, c.w, 4 * SS, seed, 3)
    grain = cv2.resize(np.random.default_rng(seed).random((c.h // 30, 4)).astype(np.float32), (c.w, c.h), interpolation=cv2.INTER_CUBIC)
    var = np.asarray((0.66, 0.30, 0.10))[None, None] * (0.85 + 0.2 * grain[..., None] + 0.05 * n[..., None])
    c.lay(var, body)
    c.lay((0.36, 0.13, 0.04), body * np.clip((c.X - cx) / 110, 0, 1), 0.55)
    c.lay((1.0, 0.82, 0.55), blur(c.ell(cx - 50, h * 0.70, 26, 80), 10) * body, 0.45)                   # varnish shine
    edge = np.clip(body - blur(body, 3) * 1.0, 0, 1)
    c.lay((0.20, 0.08, 0.03), np.clip(body - np.clip(blur(body, 2.5) - 0.5, 0, 1) * 2, 0, 1) * 0.0 + edge * 2, 0.7)
    for side in (-1, 1):                                                                                 # f-holes
        x = cx + side * 46
        c.lay((0.12, 0.05, 0.02), c.line([(x, h * 0.56), (x - side * 8, h * 0.62), (x, h * 0.68)], 4, 0.7))
        c.lay((0.12, 0.05, 0.02), c.ell(x, h * 0.56, 5, 5, soft=0.6))
        c.lay((0.12, 0.05, 0.02), c.ell(x, h * 0.68, 5, 5, soft=0.6))
    c.lay((0.10, 0.08, 0.07), c.poly([(cx - 14, h * 0.12), (cx + 14, h * 0.12), (cx + 22, h * 0.66), (cx - 22, h * 0.66)], 1))  # board
    c.lay((0.88, 0.80, 0.62), c.poly([(cx - 34, h * 0.735), (cx + 34, h * 0.735), (cx + 30, h * 0.75), (cx - 30, h * 0.75)], 0.6))  # bridge
    c.lay((0.10, 0.08, 0.07), c.poly([(cx - 30, h * 0.80), (cx + 30, h * 0.80), (cx + 18, h * 0.93), (cx - 18, h * 0.93)], 1))  # tailpiece
    c.lay((0.50, 0.22, 0.08), c.poly([(cx - 12, h * 0.03), (cx + 12, h * 0.03), (cx + 12, h * 0.13), (cx - 12, h * 0.13)], 1))  # pegbox
    c.lay((0.50, 0.22, 0.08), c.ell(cx, h * 0.03, 18, 18, soft=1))                                       # scroll
    c.lay((0.30, 0.12, 0.04), c.ell(cx + 2, h * 0.03, 8, 8, soft=0.8))
    for side in (-1, 1):
        for k in range(2):
            c.lay((0.20, 0.08, 0.03), c.ell(cx + side * 22, h * 0.06 + k * 26, 10, 6, soft=0.8))
    for k in range(4):                                                                                   # strings
        x0 = cx - 9 + k * 6
        c.lay((0.92, 0.90, 0.82), c.line([(x0, h * 0.10), (cx - 15 + k * 10, h * 0.80)], 1.2, 0.3))
    return c.out()


def eiffel(w=420, h=900):
    """the Eiffel Tower in ink (density 0..1): four curved legs, the big arch, three platforms, the lattice, the top"""
    S = 3
    m = np.zeros((h * S, w * S), np.uint8)
    cx = w / 2
    base, top = h - 10, 30
    def half(y):
        f = np.clip((base - y) / (base - top), 0, 1)
        return 8 + (w * 0.46 - 8) * (1 - f) ** 3.2
    ys = np.linspace(top + 40, base, 300)
    for side in (-1, 1):
        pts = np.array([[(cx + side * half(y)) * S, y * S] for y in ys], np.int32)
        cv2.polylines(m, [pts], False, 255, 7 * S, cv2.LINE_AA)
        pts = np.array([[(cx + side * half(y) * 0.55) * S, y * S] for y in ys], np.int32)
        cv2.polylines(m, [pts], False, 255, 4 * S, cv2.LINE_AA)
    for k in range(40):                                                                                  # lattice
        y0 = top + 40 + (base - top - 40) * k / 40
        y1 = top + 40 + (base - top - 40) * (k + 1) / 40
        for side in (-1, 1):
            cv2.line(m, (int((cx + side * half(y0)) * S), int(y0 * S)), (int((cx + side * half(y1) * 0.55) * S), int(y1 * S)), 255, 2 * S,
                     cv2.LINE_AA)
            cv2.line(m, (int((cx + side * half(y0) * 0.55) * S), int(y0 * S)), (int((cx + side * half(y1)) * S), int(y1 * S)), 255, 2 * S,
                     cv2.LINE_AA)
    ay = base - 0.17 * (base - top)
    cv2.ellipse(m, (int(cx * S), int(base * S)), (int(half(ay) * 0.75 * S), int((base - ay) * 0.95 * S)), 0, 180, 360, 255, 6 * S,
                cv2.LINE_AA)
    cv2.ellipse(m, (int(cx * S), int(base * S)), (int(half(ay) * 0.62 * S), int((base - ay) * 0.80 * S)), 0, 180, 360, 0, -1, cv2.LINE_AA)
    for f, th in ((0.18, 16), (0.38, 12), (0.80, 10)):                                                   # platforms
        y = base - f * (base - top)
        hw = half(y) + 14
        cv2.rectangle(m, (int((cx - hw) * S), int((y - th / 2) * S)), (int((cx + hw) * S), int((y + th / 2) * S)), 255, -1)
    cv2.line(m, (int(cx * S), int(top * S)), (int(cx * S), int((top + 60) * S)), 255, 4 * S, cv2.LINE_AA)  # spire
    out = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return out


def ice_cream(w=360, h=620, seed=8):
    """a waffle cone with two scoops (strawberry on vanilla) and a cherry"""
    c = Canvas(w, h)
    cx = w / 2
    cone = c.poly([(cx - 110, 300), (cx + 110, 300), (cx, h - 20)], 1)
    c.lay((0.86, 0.62, 0.32), cone)
    c.lay((0.66, 0.42, 0.18), cone * np.clip((c.X - cx) / 110, 0, 1), 0.5)
    for k in range(-6, 7):                                                   # waffle lines
        c.lay((0.62, 0.38, 0.16), c.line([(cx + k * 34 - 60, 300), (cx + k * 34 + 120, h - 40)], 3, 0.8) * cone, 0.7)
        c.lay((0.62, 0.38, 0.16), c.line([(cx + k * 34 + 60, 300), (cx + k * 34 - 120, h - 40)], 3, 0.8) * cone, 0.7)
    van = np.clip(c.ell(cx, 280, 128, 92) + c.poly([(cx - 128, 280), (cx + 128, 280), (cx + 120, 312), (cx - 120, 312)], 1), 0, 1)
    c.lay((0.98, 0.94, 0.80), van)
    c.lay((0.86, 0.80, 0.62), van * np.clip((c.X - cx) / 128, 0, 1), 0.5)
    for k in range(7):                                                       # drippy rim
        x = cx - 110 + k * 36
        c.lay((0.98, 0.94, 0.80), c.ell(x, 312, 20, 18 + 10 * (k % 2)))
    st = c.ell(cx + 6, 170, 108, 92)
    c.lay((0.97, 0.62, 0.70), st)
    c.lay((0.86, 0.42, 0.52), st * np.clip((c.X - cx) / 108, 0, 1), 0.5)
    r = np.random.default_rng(seed)
    for k in range(18):                                                      # sprinkles
        x, y = r.uniform(cx - 80, cx + 90), r.uniform(110, 230)
        a = r.uniform(0, np.pi)
        col = [(0.2, 0.5, 0.9), (0.98, 0.85, 0.2), (0.3, 0.75, 0.4), (1, 1, 1)][k % 4]
        c.lay(col, c.line([(x, y), (x + 12 * np.cos(a), y + 12 * np.sin(a))], 4, 0.6) * st)
    c.lay((1, 1, 1), blur(c.ell(cx - 40, 140, 30, 18), 6) * st, 0.6)
    c.lay((0.80, 0.08, 0.12), c.ell(cx + 10, 72, 28, 28))                    # cherry
    c.lay((1, 1, 1), c.ell(cx + 2, 64, 7, 6), 0.7)
    c.lay((0.30, 0.45, 0.15), c.line([(cx + 14, 46), (cx + 30, 10)], 4, 0.6))
    return c.out()
