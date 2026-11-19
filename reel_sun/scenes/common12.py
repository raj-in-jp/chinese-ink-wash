"""Shared by the scenes of reel 11: labels, the paper colour, a paper card with a soft shadow, a brushed X, the
vertical scroll of classical text, and timed stamps."""
import numpy as np

import kit
from engine import FONT_EN_BOLD, FONT_JP, INK, VERM, W, Cam, StrokeSet, smooth, stroke, text_layer

SCREEN = Cam(540, 960, 1.0)
PAPER = np.array([0.97, 0.95, 0.89], np.float32)
SCROLL = np.array([0.94, 0.90, 0.80], np.float32)
_cache = {}


def label(s, size, font=FONT_EN_BOLD, tracking=6):
    k = (s, size, font, tracking)
    if k not in _cache:
        _cache[k] = text_layer(s, font, size, tracking=tracking)[0]
    return _cache[k]


def card(fr, cam, x, y, w, h, op, sc=1.0, color=PAPER, rim=True):
    if op <= 0:
        return
    kit.put(fr, cam, kit.box(h, w, 10), x + 8, y + 12, INK, 0.22 * op, sc)
    kit.put(fr, cam, kit.box(h, w, 4), x, y, color, op, sc, over=True)
    if rim:
        kit.put(fr, cam, kit.rim(h, w, inset=8, t=3), x, y, VERM, 0.75 * op, sc)


def chip(fr, cam, g, x, y, op, color=VERM, sc=1.0):
    card(fr, cam, x, y, g.shape[1] + 60, g.shape[0] + 34, op, sc, rim=False)
    kit.put(fr, cam, g, x, y, color, op, sc)


def brush_x(cx, cy, r, t0, seed=11, width=24):
    x = StrokeSet(W, 1920)
    prof = ((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2))
    x.add(stroke(W, 1920, [(cx - r, cy - r * 0.8), (cx, cy), (cx + r, cy + r * 0.8)], width, ink=0.95, dry=0.35, profile=prof, seed=seed),
          t0, 0.2)
    x.add(stroke(W, 1920, [(cx + r, cy - r * 0.8), (cx, cy), (cx - r, cy + r * 0.8)], width, ink=0.95, dry=0.35, profile=prof,
                 seed=seed + 1), t0 + 0.16, 0.2)
    return x


def vertical(text, size, font=FONT_JP):
    """a column of characters, top to bottom"""
    gs = [label(c, size, font, 0) for c in text]
    h = int(size * 1.08 * len(gs))
    w = max(g.shape[1] for g in gs)
    out = np.zeros((h, w), np.float32)
    for j, g in enumerate(gs):
        y = int(j * size * 1.08)
        x = (w - g.shape[1]) // 2
        hh = min(g.shape[0], h - y)
        out[y:y + hh, x:x + g.shape[1]] = np.maximum(out[y:y + hh, x:x + g.shape[1]], g[:hh])
    return out


def mixed(parts, gap=18):
    """one line from several fonts: parts = [(text, size, font, tracking), ...], centred vertically on each other"""
    gs = [label(*p) for p in parts]
    h = max(g.shape[0] for g in gs)
    w = sum(g.shape[1] for g in gs) + gap * (len(gs) - 1)
    out = np.zeros((h, w), np.float32)
    x = 0
    for g in gs:
        y = (h - g.shape[0]) // 2
        out[y:y + g.shape[0], x:x + g.shape[1]] = g
        x += g.shape[1] + gap
    return out


# ---------------------------------------------------------------- reel 12: tiles, letters, bubbles, motion
from engine import FONT_KANA, FONT_PLAY, FONT_ROUND, H as _H, blur

IVORY = np.array([0.99, 0.96, 0.89], np.float32)
INDIGO = np.array([0.18, 0.27, 0.52], np.float32)
GOLD = np.array([0.88, 0.62, 0.16], np.float32)
TEAL = np.array([0.13, 0.47, 0.46], np.float32)
PALETTE = (VERM, INDIGO, TEAL, GOLD)


def ease_back(x, s=1.7):
    x = float(np.clip(x, 0, 1)) - 1
    return 1 + x * x * ((s + 1) * x + s)


def pulse(t, t0, amp=0.25, rate=6.0, wob=0.0):
    """a pop: 1 + amp right at t0, decaying (optionally wobbling)"""
    q = t - t0
    if q < 0:
        return 1.0
    return 1 + amp * np.exp(-q * rate) * (np.cos(q * wob) if wob else 1)


def rbox(h, w, r=22, soft=1.2):
    import cv2
    m = np.zeros((h, w), np.float32)
    cv2.rectangle(m, (r, 0), (w - r, h), 1.0, -1)
    cv2.rectangle(m, (0, r), (w, h - r), 1.0, -1)
    for cx, cy in ((r, r), (w - r, r), (r, h - r), (w - r, h - r)):
        cv2.circle(m, (cx, cy), r, 1.0, -1, cv2.LINE_AA)
    return blur(m, soft) if soft else m


class Tile:
    """a katakana tile: a rounded colour block with the kana in ivory and an optional romaji line under it"""
    def __init__(self, kana, size=150, color=VERM, romaji=None, hot=None):
        self.box = rbox(size, size, int(size * 0.16))
        self.shadow = blur(rbox(size, size, int(size * 0.16)), 7)
        self.g = text_layer(kana, FONT_KANA, int(size * (0.62 if len(kana) == 1 else 0.40)))[0]
        g = np.zeros((size * 2, size * 2), np.float32)
        import cv2
        cv2.circle(g, (size, size), int(size * 0.62), 1.0, -1, cv2.LINE_AA)
        self.glowm = blur(g, size * 0.22)
        self.size, self.color = size, np.asarray(color, np.float32)
        self.rom = None
        if romaji:
            # romaji with the added vowel (hot = index of characters) in vermilion
            self.rom = [(label(ch, int(size * 0.3), FONT_ROUND, 0), (hot is not None and k in hot)) for k, ch in enumerate(romaji)]

    def draw(self, fr, cam, x, y, op=1.0, s=1.0, sy=None, rot=0.0, glow=0.0):
        if op <= 0:
            return
        sy = s if sy is None else sy
        kit.put(fr, cam, self.shadow, x + 8, y + 12, INK, 0.28 * op, s, sy, rot)
        if glow > 0:
            kit.put(fr, cam, self.glowm, x, y, GOLD, 0.55 * glow * op, s, sy)
        kit.put(fr, cam, self.box, x, y, self.color, op, s, sy, rot, over=True)
        kit.put(fr, cam, self.g, x, y, IVORY, op, s, sy, rot, over=True)

    def draw_rom(self, fr, cam, x, y, op=1.0):
        if self.rom is None or op <= 0:
            return
        ws = [g.shape[1] for g, _ in self.rom]
        x0 = x - (sum(ws) + 2 * (len(ws) - 1)) / 2
        for (g, hot), w in zip(self.rom, ws):
            kit.put(fr, cam, g, x0 + w / 2, y, VERM if hot else INK, op, 1 + 0.25 * hot * 0)
            x0 += w + 2


def tile_row(kanas, xc, size, gap=14):
    """x centres of a row of tiles"""
    n = len(kanas)
    step = size + gap
    return [xc + (k - (n - 1) / 2) * step for k in range(n)]


class Word:
    """an English word as separate letters on one baseline, so they can jump, scatter and regroup"""
    def __init__(self, text, size=170, font=None, tracking=6):
        from PIL import Image, ImageDraw, ImageFont
        font = font or FONT_PLAY
        f = ImageFont.truetype(font, size)
        H = int(size * 1.5)
        self.letters, xs, x = [], [], 0.0
        for ch in text:
            w = f.getlength(ch)
            if ch != ' ':
                im = Image.new('L', (int(w) + 24, H), 0)
                ImageDraw.Draw(im).text((12, H * 0.78), ch, font=f, fill=255, anchor='ls')
                self.letters.append((ch, np.asarray(im, np.float32) / 255))
                xs.append(x + w / 2)
            x += w + tracking
        self.width = x - tracking
        self.xs = [v - self.width / 2 for v in xs]

    def draw(self, fr, cam, x, y, color=INK, op=1.0, s=1.0, offsets=None, ops=None, colors=None, rots=None):
        for k, (ch, g) in enumerate(self.letters):
            dx, dy = offsets[k] if offsets is not None else (0, 0)
            o = op * (ops[k] if ops is not None else 1.0)
            c = colors[k] if colors is not None else color
            r = rots[k] if rots is not None else 0.0
            kit.put(fr, cam, g, x + self.xs[k] * s + dx, y + dy, c, o, s, rot=r, over=True)


class Bubble:
    """a little vowel in a vermilion circle, dropping in"""
    def __init__(self, ch, size=90):
        import cv2
        m = np.zeros((size, size), np.float32)
        cv2.circle(m, (size // 2, size // 2), size // 2 - 3, 1.0, -1, cv2.LINE_AA)
        self.disc = blur(m, 1.0)
        self.sh = blur(self.disc, 5)
        self.g = text_layer(ch, FONT_ROUND, int(size * 0.62))[0]

    def draw(self, fr, cam, x, y, op=1.0, s=1.0):
        if op <= 0:
            return
        kit.put(fr, cam, self.sh, x + 5, y + 8, INK, 0.25 * op, s)
        kit.put(fr, cam, self.disc, x, y, VERM, op, s, over=True)
        kit.put(fr, cam, self.g, x, y + 2, IVORY, op, s, over=True)


def paint(fr, cam, rgb, a, x, y, op=1.0, sc=1.0, rot=0.0):
    """composite a painted RGBA image centred at (x, y)"""
    import cv2
    from engine import W
    if op <= 0:
        return
    h, w = a.shape
    M = kit.affine(cam, x, y, w, h, sc, sc, rot)
    A = cv2.warpAffine(a, M, (W, _H))
    if A.max() > 0:
        fr.over(cv2.warpAffine(rgb, M, (W, _H)), A, op)


def drop_y(t, t0, dist=260, dur=0.45):
    """y offset of something dropping in with an overshoot"""
    return -dist * (1 - ease_back((t - t0) / dur))
