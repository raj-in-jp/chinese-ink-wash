"""Painted, near-realistic illustrations for reel 11, as RGBA float images (premultiplied-free: rgb + alpha):

    washoku()  a full ichijū-sansai meal on a lacquer tray: a bowl of glossy rice, miso soup with tofu, wakame and
               spring onion in a red lacquer bowl, a grilled salmon fillet with grated daikon and shiso, takuan
               pickles, chopsticks on a rest — on a dark wooden table.  Its steam is animated separately (steam()).
    washi()    a hand-made sheet of washi: deckle edges, kōzo fibres, translucency.
    plum_branch()  a branch of plum blossom (Reiwa comes from the Man'yōshū preface about plum blossoms).
Everything is drawn at 2x and downsampled, lit from the upper left."""
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


def _bowl(c, cx, cy, rw, depth, glaze, glaze_dark, rim_col, band=None, foot=True):
    """a bowl seen from slightly above: body below the rim ellipse, shaded round, with a highlight"""
    ry = rw * 0.3
    body = c.ell(cx, cy, rw, depth, 0, 180) * (c.Y >= cy - 1)
    body = np.maximum(body, c.ell(cx, cy, rw, ry))
    if foot:
        body = np.maximum(body, c.poly([(cx - rw * 0.36, cy + depth * 0.92), (cx + rw * 0.36, cy + depth * 0.92),
                                         (cx + rw * 0.32, cy + depth * 1.08), (cx - rw * 0.32, cy + depth * 1.08)]))
    # cast shadow on the tray
    c.lay((0, 0, 0), blur(c.ell(cx + rw * 0.18, cy + depth * 1.02, rw * 1.02, ry * 0.9), 10), 0.45)
    u = np.clip((c.X - cx) / rw, -1, 1)
    v = np.clip((c.Y - cy) / depth, 0, 1)
    col = np.asarray(glaze, np.float32)[None, None] * (1 - 0.55 * ((u + 0.35).clip(0) ** 1.4)[..., None]) * \
        (1 - 0.35 * v[..., None])
    c.lay(col, body)
    c.lay(glaze_dark, body * np.clip((u - 0.25) * 1.4, 0, 1) * (c.Y > cy), 0.55)
    if band is not None:
        b = c.ell(cx, cy + depth * 0.18, rw * 0.99, ry * 1.0, 0, 180, soft=0.5) - c.ell(cx, cy + depth * 0.18 - 6, rw * 0.99,
                                                                                         ry, 0, 180, soft=0.5)
        c.lay(band, np.clip(b, 0, 1) * body * (c.Y > cy), 0.8)
        for k in range(-5, 6):                                   # little brushed motifs on the band
            x = cx + k * rw * 0.17
            c.lay(band, c.ell(x, cy + depth * 0.45, 5, 9) * body * (c.Y > cy), 0.6 * (1 - abs(k) / 6))
    # specular streak
    hl = blur(c.poly([(cx - rw * 0.72, cy + depth * 0.15), (cx - rw * 0.6, cy + depth * 0.12), (cx - rw * 0.42, cy + depth * 0.7),
                      (cx - rw * 0.52, cy + depth * 0.72)]), 3)
    c.lay((1, 1, 1), hl * body, 0.55)
    # rim
    rim = np.clip(c.ell(cx, cy, rw, ry) - c.ell(cx, cy + 1, rw - 7, ry - 4), 0, 1)
    c.lay(rim_col, rim, 1.0)
    return c.ell(cx, cy + 1, rw - 7, ry - 4)                     # the opening, for the contents


def _rice(c, cx, cy, rw, seed=5):
    ry = rw * 0.3
    mound = c.ell(cx, cy - rw * 0.05, rw - 8, rw * 0.46, 180, 360) + c.ell(cx, cy, rw - 8, ry - 4)
    mound = np.clip(mound, 0, 1)
    shade = np.clip((c.X - cx) / rw * 0.5 + (c.Y - (cy - rw * 0.3)) / rw * 0.4, 0, 1)
    c.lay(np.asarray((0.97, 0.96, 0.92))[None, None] * (1 - 0.22 * shade[..., None]), mound)
    r = np.random.default_rng(seed)
    grains = np.zeros((c.h, c.w), np.float32)
    hi = np.zeros((c.h, c.w), np.float32)
    for k in range(900):
        x, y = r.uniform(cx - rw, cx + rw), r.uniform(cy - rw * 0.5, cy + ry)
        if mound[int(y * SS), int(x * SS)] < 0.9:
            continue
        a = r.uniform(0, 180)
        cv2.ellipse(grains, (int(x * SS), int(y * SS)), (int(6.5 * SS), int(3 * SS)), a, 0, 360, 1.0, 1, cv2.LINE_AA)
        cv2.ellipse(hi, (int((x - 1.4) * SS), int((y - 1.2) * SS)), (int(3 * SS), int(1.1 * SS)), a, 0, 360, 1.0, -1, cv2.LINE_AA)
    c.lay((0.70, 0.68, 0.62), blur(grains, 0.5) * mound, 0.55)
    c.lay((1, 1, 1), blur(hi, 0.6) * mound, 0.9)
    c.shade(mound * np.clip((c.X - cx) / rw, 0, 1), 0.18)


def _miso(c, inner, cx, cy, rw, seed=9):
    ry = rw * 0.3
    n = _noise(c.h, c.w, 40 * SS, seed)
    soup = np.asarray((0.74, 0.53, 0.29))[None, None] * (0.86 + 0.28 * n[..., None])
    c.lay(soup, inner)
    c.lay((0.86, 0.70, 0.46), inner * np.clip((n - 0.55) * 4, 0, 1), 0.5)       # cloudy miso
    r = np.random.default_rng(seed)
    for k in range(6):                                                          # tofu cubes
        x, y = cx + r.uniform(-rw * 0.6, rw * 0.6), cy + r.uniform(-ry * 0.5, ry * 0.5)
        s = r.uniform(13, 18)
        top = c.poly([(x - s, y - s * 0.4), (x + s * 0.2, y - s * 0.7), (x + s, y - s * 0.3), (x - s * 0.2, y)])
        side = c.poly([(x - s, y - s * 0.4), (x - s * 0.2, y), (x - s * 0.2, y + s * 0.5), (x - s, y + s * 0.1)])
        side2 = c.poly([(x - s * 0.2, y), (x + s, y - s * 0.3), (x + s, y + s * 0.2), (x - s * 0.2, y + s * 0.5)])
        c.lay((0.98, 0.97, 0.90), top * inner)
        c.lay((0.90, 0.88, 0.80), side * inner)
        c.lay((0.82, 0.79, 0.70), side2 * inner)
    for k in range(5):                                                          # wakame
        x, y = cx + r.uniform(-rw * 0.7, rw * 0.7), cy + r.uniform(-ry * 0.6, ry * 0.6)
        pts = [(x + 26 * np.cos(a) * r.uniform(0.5, 1.1), y + 11 * np.sin(a) * r.uniform(0.5, 1.1)) for a in np.linspace(0, 2 * np.pi, 9)]
        m = c.poly(pts, 1.2) * inner
        c.lay((0.16, 0.30, 0.14), m, 0.9)
        c.lay((0.35, 0.52, 0.25), m * blur(c.line(pts[:4], 2), 1), 0.5)
    for k in range(12):                                                         # spring onion rings
        x, y = cx + r.uniform(-rw * 0.75, rw * 0.75), cy + r.uniform(-ry * 0.7, ry * 0.7)
        ring = np.clip(c.ell(x, y, 6, 4, soft=0.4) - c.ell(x, y, 3.2, 2, soft=0.4), 0, 1)
        c.lay((0.45, 0.70, 0.25), ring * inner)
    c.lay((1, 1, 1), blur(c.ell(cx - rw * 0.35, cy - ry * 0.35, rw * 0.3, ry * 0.18), 4) * inner, 0.35)  # sheen


def _salmon(c, cx, cy, s=1.0, seed=3):
    # white rectangular plate in perspective
    pw, ph = 190 * s, 70 * s
    plate = c.poly([(cx - pw, cy - ph * 0.6), (cx + pw * 0.92, cy - ph * 0.75), (cx + pw, cy + ph), (cx - pw * 0.95, cy + ph * 1.1)], 1.5)
    c.lay((0, 0, 0), blur(c.poly([(cx - pw + 12, cy - ph * 0.4), (cx + pw + 12, cy - ph * 0.5), (cx + pw + 16, cy + ph * 1.35),
                                   (cx - pw * 0.9, cy + ph * 1.45)]), 9), 0.4)
    c.lay((0.93, 0.93, 0.90), plate)
    c.lay((0.80, 0.80, 0.78), plate * np.clip((c.Y - cy) / ph, 0, 1), 0.4)
    inner = c.poly([(cx - pw + 16, cy - ph * 0.45), (cx + pw * 0.92 - 14, cy - ph * 0.58), (cx + pw - 16, cy + ph * 0.8),
                    (cx - pw * 0.95 + 16, cy + ph * 0.9)], 3)
    c.lay((0.98, 0.98, 0.96), inner, 0.6)
    # the fillet: a thick wedge, skin along the bottom
    pts = [(cx - 150 * s, cy + 10 * s), (cx - 120 * s, cy - 42 * s), (cx + 30 * s, cy - 58 * s), (cx + 120 * s, cy - 40 * s),
           (cx + 140 * s, cy + 5 * s), (cx + 110 * s, cy + 40 * s), (cx - 110 * s, cy + 45 * s)]
    f = c.poly(pts, 1.2)
    c.lay((0, 0, 0), blur(f, 6) * (c.Y > cy), 0.25)
    sh = np.clip((c.Y - (cy - 50 * s)) / (95 * s), 0, 1)
    c.lay(np.asarray((0.96, 0.52, 0.33))[None, None] * (1 - 0.25 * sh[..., None]), f)
    for k in range(-4, 5):                                       # white fat lines
        x0 = cx + k * 28 * s
        c.lay((0.99, 0.84, 0.72), c.line([(x0 - 16 * s, cy - 50 * s), (x0 + 6 * s, cy - 8 * s), (x0 - 4 * s, cy + 38 * s)], 2.4 * s, 1.4) * f, 0.5)
    skin = c.poly([(cx - 150 * s, cy + 10 * s), (cx - 110 * s, cy + 45 * s), (cx + 110 * s, cy + 40 * s), (cx + 140 * s, cy + 5 * s),
                   (cx + 120 * s, cy + 22 * s), (cx - 100 * s, cy + 28 * s)], 1)
    c.lay((0.38, 0.36, 0.36), skin)
    c.lay((0.75, 0.75, 0.78), skin * np.clip(_noise(c.h, c.w, 6 * SS, seed) - 0.4, 0, 1) * 2, 0.6)
    n = _noise(c.h, c.w, 18 * SS, seed + 1)
    char = f * np.clip((n - 0.52) * 3, 0, 1)                     # grilled, charred patches
    c.lay((0.42, 0.18, 0.08), char, 0.7)
    for k in range(3):                                           # grill marks
        x0 = cx - 70 * s + k * 60 * s
        c.lay((0.30, 0.12, 0.05), c.line([(x0, cy - 50 * s), (x0 + 30 * s, cy + 30 * s)], 7 * s, 2) * f, 0.55)
    c.lay((1, 1, 1), blur(c.line([(cx - 90 * s, cy - 36 * s), (cx + 40 * s, cy - 48 * s)], 5 * s), 3) * f, 0.45)
    # shiso leaf + grated daikon
    lx, ly = cx + 150 * s, cy + 35 * s
    leaf = c.poly([(lx - 50 * s, ly + 10 * s), (lx - 10 * s, ly - 26 * s), (lx + 45 * s, ly - 20 * s), (lx + 55 * s, ly + 5 * s),
                   (lx + 10 * s, ly + 26 * s)], 1.2)
    c.lay((0.20, 0.45, 0.18), leaf)
    c.lay((0.42, 0.66, 0.30), leaf * c.line([(lx - 45 * s, ly + 8 * s), (lx + 50 * s, ly - 2 * s)], 2.5, 0.8), 0.9)
    d = c.ell(lx + 5 * s, ly - 6 * s, 30 * s, 18 * s)
    c.lay((0.95, 0.94, 0.90), d)
    c.lay((0.75, 0.74, 0.70), d * np.clip(_noise(c.h, c.w, 3 * SS, seed + 2) - 0.45, 0, 1) * 2, 0.7)


def _pickles(c, cx, cy, seed=4):
    d = c.ell(cx, cy, 82, 30)
    c.lay((0, 0, 0), blur(c.ell(cx + 10, cy + 12, 84, 30), 7), 0.35)
    c.lay((0.86, 0.89, 0.92), d)
    c.lay((0.20, 0.32, 0.55), np.clip(c.ell(cx, cy, 82, 30) - c.ell(cx, cy, 76, 26), 0, 1), 0.8)   # indigo rim
    for k, (dx, dy) in enumerate(((-34, -2), (0, -8), (32, -1))):
        s = c.ell(cx + dx, cy + dy, 26, 17, soft=0.6)
        c.lay((0.96, 0.80, 0.25), s)
        c.lay((0.88, 0.62, 0.12), s * np.clip((c.Y - (cy + dy)) / 14, 0, 1), 0.6)
        c.lay((1, 0.95, 0.7), np.clip(c.ell(cx + dx, cy + dy - 3, 20, 11, soft=0.6) - c.ell(cx + dx, cy + dy - 3, 17, 9, soft=0.6), 0, 1), 0.6)


def washoku(w=960, h=760):
    """the meal on a lacquer tray over a wooden table; returns (rgb, alpha) and the steam sources"""
    c = Canvas(w, h)
    table = c.poly([(30, 30), (w - 30, 30), (w - 30, h - 30), (30, h - 30)], 0)
    table = blur(c.mask(lambda m, s: cv2.rectangle(m, (30 * s, 30 * s), ((w - 30) * s, (h - 30) * s), 255, -1)), 1.5)
    grain = _noise(c.h, c.w, 3 * SS, 1, 3)
    streak = cv2.resize(np.random.default_rng(2).random((c.h // 3, 6)).astype(np.float32), (c.w, c.h), interpolation=cv2.INTER_CUBIC)
    wood = np.stack([0.36, 0.22, 0.13])[None, None] * (0.75 + 0.35 * streak[..., None] + 0.08 * grain[..., None])
    c.lay(wood, table)
    vign = np.clip(1 - ((c.X - w / 2) / (w * 0.6)) ** 2 - ((c.Y - h / 2) / (h * 0.7)) ** 2, 0, 1)
    c.shade(table, 0.45 * (1 - vign))
    # lacquer tray (oshiki), black with a vermilion inner edge
    tray = [(110, 165), (w - 110, 165), (w - 55, h - 85), (55, h - 85)]
    c.lay((0, 0, 0), blur(c.poly([(x + 14, y + 22) for x, y in tray]), 12), 0.55)
    c.lay((0.09, 0.07, 0.06), c.poly(tray, 1))
    inner = [(130, 180), (w - 130, 180), (w - 78, h - 102), (78, h - 102)]
    c.lay((0.55, 0.10, 0.06), np.clip(c.poly(tray, 1) - c.poly(inner, 1), 0, 1), 0.8)
    c.lay((0.13, 0.10, 0.09), c.poly(inner, 1))
    c.lay((1, 1, 1), blur(c.poly([(160, 190), (w * 0.55, 190), (w * 0.45, 260), (150, 260)]), 18), 0.07)
    # back row: salmon, pickles; front row: rice, miso; chopsticks along the front
    _salmon(c, 330, 330, 0.95)
    _pickles(c, 720, 330)
    rx, ry_, rw = 285, 520, 125
    op = _bowl(c, rx, ry_, rw, 120, (0.93, 0.91, 0.86), (0.55, 0.52, 0.48), (0.80, 0.77, 0.70), band=(0.18, 0.28, 0.55))
    _rice(c, rx, ry_, rw)
    mx, my, mw = 670, 525, 128
    op2 = _bowl(c, mx, my, mw, 105, (0.55, 0.08, 0.05), (0.18, 0.02, 0.02), (0.12, 0.04, 0.03))
    _miso(c, op2, mx, my, mw)
    rest = c.ell(470, h - 128, 28, 10)
    c.lay((0.85, 0.85, 0.82), rest)
    for k, dy in enumerate((-4, 5)):
        st = c.line([(250, h - 120 + dy), (780, h - 142 + dy * 1.3)], 9 - k, 0.8)
        c.lay((0.62, 0.42, 0.22), st)
        c.lay((0.85, 0.66, 0.42), st * blur(c.line([(250, h - 123 + dy), (780, h - 145 + dy * 1.3)], 2), 1), 0.6)
    rgb, a = c.out()
    return rgb, a, [(rx, ry_ - 60, rw * 0.8), (mx, my - 20, mw * 0.8)]


def steam(t, w, h, sources, seed=0):
    """animated steam over the meal: soft rising wisps; returns an alpha (white) layer the size of the panel"""
    out = np.zeros((h, w), np.float32)
    r = np.random.default_rng(seed)
    for (sx, sy, sw) in sources:
        for k in range(5):
            ph = r.uniform(0, 6.28)
            x0 = sx + r.uniform(-sw * 0.6, sw * 0.6)
            sp = r.uniform(35, 55)
            off = ((t * sp + k * 60) % 260)                      # wisps keep rising and fading
            pts = []
            for j in range(26):
                y = sy - off - j * 9
                x = x0 + 9 * np.sin(j * 0.25 + t * 1.4 + ph) * (j / 26 + 0.3) + 5 * np.sin(t * 0.8 + k)
                pts.append((x, y))
            p = np.asarray(pts, np.int32)
            lay = np.zeros((h, w), np.float32)
            cv2.polylines(lay, [p], False, 1.0, int(r.uniform(8, 14)), cv2.LINE_AA)
            fade = np.clip(1 - off / 260, 0, 1) * np.clip(off / 40, 0, 1)
            out = np.maximum(out, cv2.GaussianBlur(lay, (0, 0), 7) * 0.55 * fade)
    return out


def washi(w=640, h=780, seed=21):
    c = Canvas(w, h)
    edge = _noise(c.h, c.w, 5 * SS, seed, 2)
    base = c.poly([(40, 40), (w - 40, 40), (w - 40, h - 40), (40, h - 40)], 0)
    d = cv2.distanceTransform((base > 0.5).astype(np.uint8), cv2.DIST_L2, 5) / SS
    sheet = np.clip((d - 6 * edge) / 6, 0, 1)                     # torn, feathered deckle edge
    c.lay((0, 0, 0), blur(np.roll(np.roll(sheet, 14 * SS, 0), 10 * SS, 1), 14), 0.25)
    n = _noise(c.h, c.w, 30 * SS, seed + 1)
    c.lay(np.asarray((0.97, 0.94, 0.86))[None, None] * (0.94 + 0.08 * n[..., None]), sheet)
    r = np.random.default_rng(seed)
    fib = np.zeros((c.h, c.w), np.float32)
    for k in range(650):                                          # long kōzo fibres, curling
        x, y = r.uniform(40, w - 40), r.uniform(40, h - 40)
        a = r.uniform(0, np.pi)
        L = r.uniform(20, 90)
        pts = [(x + np.cos(a + 0.6 * np.sin(u * 3)) * u * L, y + np.sin(a + 0.6 * np.sin(u * 3)) * u * L) for u in np.linspace(0, 1, 8)]
        cv2.polylines(fib, [(np.asarray(pts) * SS).astype(np.int32)], False, r.uniform(0.3, 1.0), max(1, int(r.uniform(0.6, 1.6) * SS)), cv2.LINE_AA)
    c.lay((0.80, 0.74, 0.62), blur(fib, 0.4) * sheet, 0.45)
    c.lay((1, 1, 1), blur(np.roll(fib, 2, 1), 0.6) * sheet, 0.25)
    c.lay((0.86, 0.80, 0.68), sheet * np.clip((_noise(c.h, c.w, 12 * SS, seed + 3) - 0.6) * 3, 0, 1), 0.35)  # cloudy thickness
    return c.out()


def plum_branch(w=520, h=520, seed=31):
    c = Canvas(w, h)
    r = np.random.default_rng(seed)
    main = [(w - 10, 30), (w - 120, 110), (w - 210, 150), (w - 300, 250), (w - 360, 280), (w - 470, 400)]
    c.lay((0.20, 0.13, 0.10), c.line(main, 16, 1.0))
    twigs = [[(w - 120, 110), (w - 150, 210), (w - 175, 260)], [(w - 210, 150), (w - 250, 80), (w - 300, 55)],
             [(w - 300, 250), (w - 300, 340), (w - 330, 400)], [(w - 360, 280), (w - 430, 250)]]
    for tw in twigs:
        c.lay((0.24, 0.16, 0.12), c.line(tw, 7, 0.8))
    spots = [p for tw in twigs for p in tw[1:]] + main[1:-1] + [(w - 470, 400)]
    for (x, y) in spots:                                          # five-petal plum blossoms
        x, y = x + r.uniform(-10, 10), y + r.uniform(-10, 10)
        R = r.uniform(17, 24)
        for k in range(5):
            a = k * 2 * np.pi / 5 + r.uniform(0, 0.3)
            p = c.ell(x + np.cos(a) * R * 0.75, y + np.sin(a) * R * 0.75, R * 0.62, R * 0.62)
            c.lay((0.98, 0.86, 0.88), p)
            c.lay((0.92, 0.55, 0.62), p * np.clip(1 - np.hypot(c.X - x, c.Y - y) / (R * 1.2), 0, 1), 0.6)
        c.lay((0.85, 0.30, 0.20), c.ell(x, y, R * 0.28, R * 0.28))
        for k in range(8):
            a = k * np.pi / 4
            c.lay((0.95, 0.80, 0.25), c.ell(x + np.cos(a) * R * 0.45, y + np.sin(a) * R * 0.45, 2.2, 2.2))
    return c.out()


def board(w=520, h=760, seed=41):
    """a plain hinoki board, the kind a new era name is shown on"""
    c = Canvas(w, h)
    b = c.poly([(20, 20), (w - 20, 20), (w - 20, h - 20), (20, h - 20)], 1.0)
    c.lay((0, 0, 0), blur(np.roll(np.roll(b, 16 * SS, 0), 12 * SS, 1), 14), 0.3)
    streak = cv2.resize(np.random.default_rng(seed).random((8, c.w // 6)).astype(np.float32), (c.w, c.h), interpolation=cv2.INTER_CUBIC)
    n = _noise(c.h, c.w, 4 * SS, seed, 2)
    c.lay(np.stack([0.90, 0.78, 0.58])[None, None] * (0.9 + 0.12 * streak.T.mean() * 0 + 0.12 * streak[..., None] + 0.04 * n[..., None]), b)
    vg = cv2.resize(np.random.default_rng(seed + 1).random((c.h // 40, 30)).astype(np.float32), (c.w, c.h), interpolation=cv2.INTER_CUBIC)
    c.lay((0.74, 0.58, 0.38), b * np.clip((vg - 0.6) * 2, 0, 1), 0.18)        # vertical grain
    c.lay((0.55, 0.40, 0.25), np.clip(b - c.poly([(30, 30), (w - 30, 30), (w - 30, h - 30), (30, h - 30)], 1.0), 0, 1), 0.6)
    return c.out()
