"""Painted (full-colour, near-realistic) art for reel 10's hook: Tokyo at night with Tokyo Tower.
    tokyo_night()  -> layers: sky gradient, far towers, Tokyo Tower, near towers (rgb + alpha each) + window light masks
    Tokyo Tower: 333 m lattice tower (1958), international-orange and white bands, Main Deck (150 m) and Top Deck (250 m)."""
import cv2
import numpy as np

SS = 2


def _noise(h, w, scale, seed, octaves=4):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        g = r.random((h // s + 2, w // s + 2)).astype(np.float32)
        out += amp * cv2.resize(g, (w + s * 2, h + s * 2), interpolation=cv2.INTER_CUBIC)[:h, :w]
        tot += amp
        amp *= 0.5
    return out / tot


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w * SS, h * SS
        self.rgb = np.zeros((self.h, self.w, 3), np.float32)
        self.a = np.zeros((self.h, self.w), np.float32)
        yy, xx = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.X, self.Y = xx / SS, yy / SS

    def lay(self, col, m, op=1.0):
        """paint colour (rgb tuple or HxWx3) through mask m"""
        m = np.clip(m * op, 0, 1)
        c = np.asarray(col, np.float32)
        self.rgb = self.rgb * (1 - m[..., None]) + (c if c.ndim == 3 else c[None, None]) * m[..., None]
        self.a = np.maximum(self.a, m)

    def shade(self, m, amount, dark=(0, 0, 0)):
        """darken (amount>0) or lighten (amount<0) inside m"""
        if np.isscalar(amount):
            amount = np.full(m.shape, amount, np.float32)
        k = np.clip(m * np.abs(amount), 0, 1)[..., None]
        tgt = np.asarray(dark, np.float32) if np.mean(amount) > 0 else np.ones(3, np.float32)
        self.rgb = self.rgb * (1 - k) + tgt * k

    def mask(self, fn):
        m = np.zeros((self.h, self.w), np.uint8)
        fn(m, SS)
        return m.astype(np.float32) / 255

    def ell(self, cx, cy, rx, ry, a0=0, a1=360, soft=0.8):
        m = self.mask(lambda m, s: cv2.ellipse(m, (int(cx * s), int(cy * s)), (int(rx * s), int(ry * s)), 0, a0, a1, 255, -1,
                                               cv2.LINE_AA))
        return cv2.GaussianBlur(m, (0, 0), soft * SS) if soft else m

    def poly(self, pts, soft=0.8):
        p = (np.asarray(pts, np.float32) * SS).astype(np.int32)
        m = self.mask(lambda m, s: cv2.fillPoly(m, [p], 255, cv2.LINE_AA))
        return cv2.GaussianBlur(m, (0, 0), soft * SS) if soft else m

    def line(self, pts, width, soft=0.6):
        p = (np.asarray(pts, np.float32) * SS).astype(np.int32)
        m = self.mask(lambda m, s: cv2.polylines(m, [p], False, 255, max(1, int(width * s)), cv2.LINE_AA))
        return cv2.GaussianBlur(m, (0, 0), soft * SS) if soft else m

    def out(self):
        rgb = cv2.resize(self.rgb, (self.w // SS, self.h // SS), interpolation=cv2.INTER_AREA)
        a = cv2.resize(self.a, (self.w // SS, self.h // SS), interpolation=cv2.INTER_AREA)
        return np.clip(rgb, 0, 1), np.clip(a, 0, 1)


def blur(m, s):
    return cv2.GaussianBlur(m, (0, 0), s * SS)




def tower(h=980, seed=0):
    """Tokyo Tower: four splayed legs with an arch, a concave tapering lattice in orange / white bands, two decks, mast"""
    w = int(h * 0.42)
    c = Canvas(w, h)
    cx = w / 2
    H_LAT = h * 0.80                                  # lattice top (the mast continues above)
    top_y = h - H_LAT
    def half(y):                                      # half-width at height y (image coords), concave like the real tower
        f = np.clip((h - y) / H_LAT, 0, 1)
        return 8 + (w * 0.47 - 8) * (1 - f) ** 2.3
    ys = np.linspace(top_y, h, 400)
    left = [(cx - half(y), y) for y in ys]
    right = [(cx + half(y), y) for y in ys[::-1]]
    sil = c.poly(left + right, 0.6)
    arch = c.ell(cx, h, half(h) * 0.62, h * 0.13, 180, 360, 0.6)           # the arch between the legs
    sil = np.clip(sil - arch, 0, 1)
    # bands: international orange and white, ~ every 1/9 of the lattice, from the base up
    f = np.clip((h - c.Y) / H_LAT, 0, 1)
    band = (np.floor(f * 9) % 2 == 1)
    ORANGE, WHITE = np.array((0.95, 0.36, 0.12)), np.array((0.95, 0.93, 0.90))
    col = np.where(band[..., None], WHITE[None, None], ORANGE[None, None])
    # lit from the left, the right side in shadow; the night lighting makes it glow warm
    shade = np.clip((c.X - cx) / (half(c.Y) + 1e-3), -1, 1)
    col = col * (1 - 0.30 * np.clip(shade, 0, 1)[..., None]) * (1 + 0.08 * np.clip(-shade, 0, 1)[..., None])
    # lattice: the silhouette is see-through between the members
    lat = np.zeros((c.h, c.w), np.uint8)
    nseg = 26
    for k in range(nseg):
        y0 = top_y + H_LAT * (k / nseg) ** 1.0
        y1 = top_y + H_LAT * ((k + 1) / nseg) ** 1.0
        for side in (-1, 1):
            xa0, xa1 = cx + side * half(y0), cx + side * half(y1)
            xb0, xb1 = cx + side * half(y0) * 0.35, cx + side * half(y1) * 0.35
            P = lambda x, y: (int(x * SS), int(y * SS))
            cv2.line(lat, P(xa0, y0), P(xb1, y1), 255, max(1, int(1.6 * SS)), cv2.LINE_AA)
            cv2.line(lat, P(xb0, y0), P(xa1, y1), 255, max(1, int(1.6 * SS)), cv2.LINE_AA)
        cv2.line(lat, P(cx - half(y1), y1), P(cx + half(y1), y1), 255, max(1, int(1.8 * SS)), cv2.LINE_AA)
    for side in (-1, 1):                                                   # the four corner legs (two seen)
        pts = np.array([(int((cx + side * half(y)) * SS), int(y * SS)) for y in ys], np.int32)
        cv2.polylines(lat, [pts], False, 255, int(4.5 * SS), cv2.LINE_AA)
        pts = np.array([(int((cx + side * half(y) * 0.35) * SS), int(y * SS)) for y in ys], np.int32)
        cv2.polylines(lat, [pts], False, 255, int(2.5 * SS), cv2.LINE_AA)
    lat = cv2.GaussianBlur(lat.astype(np.float32) / 255, (0, 0), 0.5 * SS)
    body = np.clip(sil * (0.42 + 0.58 * lat), 0, 1)
    c.lay(col, body)
    # the decks: Main Deck (150 m) and Top Deck (250 m), with lit window bands
    for hm, dh, wf in ((150, 34, 1.35), (250, 18, 1.5)):
        y = h - H_LAT * hm / 333 * 1.0
        hw = half(y) * wf + 6
        deck = c.poly([(cx - hw, y - dh / 2), (cx + hw, y - dh / 2), (cx + hw * 0.92, y + dh / 2), (cx - hw * 0.92, y + dh / 2)], 0.6)
        c.lay((0.20, 0.18, 0.20), deck)
        win = c.poly([(cx - hw + 3, y - dh * 0.28), (cx + hw - 3, y - dh * 0.28), (cx + hw * 0.92 - 4, y + dh * 0.12), (cx - hw * 0.92 + 4, y + dh * 0.12)], 0.6)
        c.lay((1.0, 0.92, 0.70), win)
        c.lay((0.95, 0.36, 0.12), c.poly([(cx - hw, y + dh / 2 - 3), (cx + hw, y + dh / 2 - 3), (cx + hw * 0.92, y + dh / 2), (cx - hw * 0.92, y + dh / 2)], 0.4))
    # the mast
    mast = c.poly([(cx - 5, top_y + 2), (cx + 5, top_y + 2), (cx + 2, 4), (cx - 2, 4)], 0.5)
    c.lay(ORANGE * 0.9, mast)
    for k in range(4):
        y = top_y - (top_y - 4) * (k + 0.5) / 4
        c.lay(WHITE, c.poly([(cx - 4, y - 8), (cx + 4, y - 8), (cx + 4, y + 8), (cx - 4, y + 8)], 0.4) * mast)
    rgb, a = c.out()
    return rgb, a, (cx, 4, h - H_LAT * 150 / 333, h - H_LAT * 250 / 333)


def towers(w=1080, h=1100, seed=1, far=False):
    """a row of skyscrapers: rgb, alpha, window-light mask, list of roof tops (x, y) for aviation lights"""
    c = Canvas(w, h)
    r = np.random.default_rng(seed)
    lights = np.zeros((c.h, c.w), np.float32)
    tops = []
    x = -20
    base_col = np.array((0.20, 0.24, 0.36)) if far else np.array((0.07, 0.08, 0.14))
    while x < w + 20:
        bw = r.uniform(70, 150) if not far else r.uniform(50, 110)
        bh = r.uniform(0.30, 0.70) * h if far else r.uniform(0.15, 0.48) * h
        if 330 < x + bw / 2 < 750:
            bh *= 0.32 if not far else 0.45                                            # keep the tower clear
        y0 = h - bh
        m = c.poly([(x, y0), (x + bw - 4, y0), (x + bw - 4, h), (x, h)], 0.4)
        grad = (0.85 + 0.25 * (c.Y - y0) / max(bh, 1))[..., None]
        c.lay(base_col[None, None] * grad, m)
        c.lay(base_col * 1.6, m * (c.X < x + 4), 0.6)              # lit edge
        if r.random() < 0.4 and not far:                          # a stepped crown
            c.lay(base_col, c.poly([(x + bw * 0.2, y0 - 26), (x + bw * 0.8 - 4, y0 - 26), (x + bw * 0.8 - 4, y0), (x + bw * 0.2, y0)], 0.4))
            y0 -= 26
        tops.append((x + bw / 2, y0 - 4))
        gx, gy = (14, 20) if not far else (10, 14)
        for wy in np.arange(h - bh + 18, h - 8, gy):
            for wx in np.arange(x + 8, x + bw - 14, gx):
                if r.random() < (0.45 if not far else 0.3):
                    cv2.rectangle(lights, (int(wx * SS), int(wy * SS)), (int((wx + gx * 0.5) * SS), int((wy + gy * 0.55) * SS)),
                                  r.uniform(0.5, 1.0), -1)
        x += bw + r.uniform(-6, 8)
    rgb, a = c.out()
    L = cv2.resize(lights, (w, h), interpolation=cv2.INTER_AREA)
    return rgb, a, L * a, tops


def edo_town(w=1080, h=760, seed=3):
    """Edo in 1866, as ink density on paper: snow-capped Fuji far off, the castle's stone wall and a corner turret with
    pines (the main keep burned in 1657 and was never rebuilt), and rows of tiled roofs and white storehouses, drawn back
    to front so nearer houses hide the ones behind"""
    c = Canvas(w, h)
    ink = np.zeros((c.h, c.w), np.float32)
    def over(m, v):
        nonlocal ink
        ink = ink * (1 - m) + v * m
    n = _noise(c.h, c.w, 6 * SS, seed, 3)
    over(c.poly([(60, 330), (250, 150), (285, 138), (320, 150), (520, 330)], 3.0), 0.22)          # Fuji
    over(c.poly([(225, 175), (250, 150), (285, 138), (320, 150), (345, 175), (320, 186), (300, 172), (282, 190), (262, 176), (245, 190)], 1.2), 0.05)
    # the castle: battered stone wall, a two-storey corner turret, pines
    over(c.poly([(600, 380), (1000, 380), (1040, 470), (560, 470)], 1.0), 0.5)
    for k in range(6):
        over(c.line([(590 - k * 5, 392 + k * 14), (1010 + k * 5, 392 + k * 14)], 1.2, 0.5), 0.75)
    tx, ty = 820, 330
    over(c.poly([(tx - 90, ty + 50), (tx + 90, ty + 50), (tx + 70, ty + 8), (tx - 70, ty + 8)], 0.8), 0.9)   # lower roof
    over(c.poly([(tx - 60, ty + 52), (tx + 60, ty + 52), (tx + 60, ty + 80), (tx - 60, ty + 80)], 0.8), 0.08)  # white wall
    over(c.poly([(tx - 58, ty + 10), (tx + 58, ty + 10), (tx + 40, ty - 26), (tx - 40, ty - 26)], 0.8), 0.9)   # upper roof
    over(c.poly([(tx - 36, ty + 10), (tx + 36, ty + 10), (tx + 36, ty - 4), (tx - 36, ty - 4)], 0.8), 0.08)
    for k in range(3):
        over(c.poly([(tx - 40 + k * 32, ty + 60), (tx - 30 + k * 32, ty + 60), (tx - 30 + k * 32, ty + 72), (tx - 40 + k * 32, ty + 72)], 0.5), 0.8)
    r = np.random.default_rng(seed)
    for px in (640, 700, 960):
        for k in range(4):
            over(c.ell(px + r.uniform(-20, 20), 360 - k * 16, 34 - k * 6, 12, soft=1.5), 0.7)
    # rows of houses, back to front
    rows = np.linspace(470, h + 10, 9)
    for row, y in enumerate(rows):
        s_ = 0.5 + 0.16 * row
        x = r.uniform(-60, 0)
        while x < w + 60:
            bw = r.uniform(80, 150) * s_
            rh = r.uniform(24, 34) * s_
            yy = y + r.uniform(-6, 6) * s_
            kura = r.random() < 0.15
            wall_h = rh * (1.5 if kura else 1.0)
            over(c.poly([(x - bw * 0.02, yy), (x + bw * 1.02, yy), (x + bw * 1.02, yy + wall_h), (x - bw * 0.02, yy + wall_h)], 0.6),
                 0.06 if kura else 0.22)
            if not kura:
                for k in range(int(bw / (14 * s_))):                                                # lattice front
                    xx = x + bw * 0.1 + k * 14 * s_
                    if xx < x + bw * 0.9:
                        over(c.line([(xx, yy + 3), (xx, yy + wall_h - 2)], 1.0, 0.4), 0.45)
            over(c.poly([(x - bw * 0.04, yy + 2), (x + bw * 0.12, yy - rh), (x + bw * 0.88, yy - rh), (x + bw * 1.04, yy + 2)], 0.6), 0.85)
            over(c.line([(x + bw * 0.12, yy - rh), (x + bw * 0.88, yy - rh)], 2.5, 0.5), 1.0)              # ridge
            for k in range(1, 4):                                                                       # tile rows
                t_ = k / 4
                over(c.line([(x + bw * 0.12 * (1 - t_) - bw * 0.04 * t_, yy - rh * (1 - t_)),
                             (x + bw * (0.88 + 0.16 * t_), yy - rh * (1 - t_))], 1.0, 0.5), 0.55)
            x += bw + r.uniform(-4, 10) * s_
    ink = np.clip(ink * (0.85 + 0.3 * n), 0, 1)
    ink = cv2.resize(ink, (w, h), interpolation=cv2.INTER_AREA)
    return ink.astype(np.float32)
