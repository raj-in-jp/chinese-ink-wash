"""What the map scenes of reel 9 share: the world chart seen through a moving camera (centre lon/lat + zoom, eased
between keyframes), the routes the name travelled (dashed vermilion lines that draw themselves), place pins and
labels, and the paper name tag that rides along a route and changes its word at each stop."""
import cv2
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_JP, GREY, H, INK, VERM, W, cached, ease_io, smooth, spline, text_layer
from worldmap import chart_xy, world_chart

GOLD = np.array([0.80, 0.60, 0.16], np.float32)
PAPER = np.array([0.97, 0.95, 0.89], np.float32)

# the routes, as (lon, lat) waypoints
R_CHINA = [(135.8, 35.0), (131.5, 33.9), (128.5, 34.4), (125.0, 36.5), (121.5, 38.6), (116.4, 39.9)]
R_SILK = [(116.4, 39.9), (108.9, 34.3), (101.5, 36.6), (94.7, 40.1), (82.5, 41.8), (76.0, 39.5), (67.0, 39.7),
          (59.5, 37.6), (51.4, 35.7), (46.3, 38.1), (39.0, 40.5), (29.0, 41.0), (23.5, 37.6), (18.5, 40.0), (12.3, 45.4)]
R_COLUMBUS = [(-6.9, 37.2), (-12.0, 31.0), (-17.0, 28.1), (-35.0, 26.0), (-55.0, 25.5), (-70.0, 24.5), (-75.5, 23.6), (-79.0, 22.3)]
R_PORTUGAL = [(102.2, 2.2), (96.0, 5.0), (86.0, 5.5), (79.0, 5.0), (68.0, 0.0), (55.0, -6.0), (43.0, -15.0), (37.0, -25.0),
              (30.0, -33.0), (19.0, -35.5), (10.0, -28.0), (2.0, -15.0), (-8.0, -2.0), (-17.0, 10.0), (-17.5, 21.0),
              (-12.5, 31.0), (-9.1, 38.7)]
R_ENGLAND = [(-9.1, 38.7), (-10.0, 43.0), (-6.5, 48.0), (-2.5, 50.2), (-0.1, 51.5)]
PLACES = {'japan': (138.0, 36.0), 'beijing': (116.4, 39.9), 'venice': (12.3, 45.4), 'palos': (-6.9, 37.2),
          'caribbean': (-77.0, 21.5), 'malacca': (102.2, 2.2), 'lisbon': (-9.1, 38.7), 'london': (-0.1, 51.5)}


def chart():
    return cached('r9_world_v1', world_chart)['rgb'].astype(np.float32)


def path_px(route, n=30):
    return np.array(spline([tuple(chart_xy(x, y)) for x, y in route], n), np.float32)


class MapCam:
    """camera keyframes [(t, lon, lat, zoom)], eased; zoom = screen px per chart px"""

    def __init__(self, keys, cy=960):
        self.keys = keys
        self.cy = cy

    def at(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            k = ks[0]
            return chart_xy(k[1], k[2]), k[3]
        for a, b in zip(ks[:-1], ks[1:]):
            if t <= b[0]:
                u = ease_io((t - a[0]) / max(b[0] - a[0], 1e-3))
                ca, cb = chart_xy(a[1], a[2]), chart_xy(b[1], b[2])
                za, zb = a[3], b[3]
                z = np.exp(np.log(za) + (np.log(zb) - np.log(za)) * u)       # zoom eases in log space
                return ca + (cb - ca) * u, z
        k = ks[-1]
        return chart_xy(k[1], k[2]), k[3]

    def matrix(self, t, extra_zoom=1.0, center=None):
        c, z = self.at(t)
        if center is not None:
            c = center
        z *= extra_zoom
        tx, ty = 540 - z * c[0], self.cy - z * c[1]
        ch = 3011 * z
        if ch >= H:                                   # never show past the top or bottom of the chart when it fills the screen
            ty = min(0.0, max(H - ch, ty))
        return np.array([[z, 0, tx], [0, z, ty]], np.float32), z

    def to_screen(self, p, t):
        M, _ = self.matrix(t)
        return np.array([M[0, 0] * p[0] + M[0, 2], M[1, 1] * p[1] + M[1, 2]], np.float32)


def draw_map(fr, img, M, op=1.0):
    """the chart through the camera; where the camera sees past the chart's edge, the paper shows, with a soft ink
    frame round the chart like a sheet laid on the desk"""
    m = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    h, w = img.shape[:2]
    if not hasattr(draw_map, 'ones') or draw_map.ones.shape != (h, w):
        draw_map.ones = np.ones((h, w), np.float32)
    a = cv2.warpAffine(draw_map.ones, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    if a.min() < 0.999:
        sh = cv2.GaussianBlur(a, (0, 0), 14)
        fr.img *= (1 - 0.35 * op * sh * (1 - a))[..., None]          # a soft shadow round the sheet
        edge = np.clip(a - cv2.erode(a, np.ones((5, 5), np.uint8)), 0, 1)
        m = m * (1 - 0.7 * edge[..., None]) + INK * 0.7 * edge[..., None]
    k = (a * op)[..., None]
    fr.img = fr.img * (1 - k) + m * k


def route_at(P, u):
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
    L = seg[-1] * np.clip(u, 0, 1)
    n = int(np.searchsorted(seg, L))
    tip = np.array([np.interp(L, seg, P[:, 0]), np.interp(L, seg, P[:, 1])], np.float32)
    k = max(n - 1, 0)
    d = P[min(k + 1, len(P) - 1)] - P[k]
    return tip, n, d / (np.hypot(*d) + 1e-6)


def draw_route(fr, M, P, u, op=1.0, width=6, dash=(18, 12), color=VERM):
    """the route drawn from its start up to fraction u, as a dashed line in screen space"""
    if u <= 0 or op <= 0:
        return None
    Q = P * M[0, 0] + M[:, 2]
    tip, n, _ = route_at(Q, u)
    pts = np.vstack([Q[:n], tip])
    d = np.zeros((H, W), np.float32)
    acc = 0.0
    on, off = dash
    for a_, b_ in zip(pts[:-1], pts[1:]):
        ln = float(np.hypot(*(b_ - a_)))
        q = 0.0
        while q < ln:
            ph = acc % (on + off)
            step = min(ln - q, (on - ph) if ph < on else (on + off - ph))
            if ph < on:
                p0, p1 = a_ + (b_ - a_) * q / ln, a_ + (b_ - a_) * (q + step) / ln
                cv2.line(d, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), 1.0, width, cv2.LINE_AA, shift=2)
            q += max(step, 1e-3)
            acc += max(step, 1e-3)
    fr.ink(d, color, 0.95 * op)
    return tip


_cache = {}


def label(s, size, font=FONT_EN_BOLD, tracking=6):
    k = (s, size, font, tracking)
    if k not in _cache:
        _cache[k] = text_layer(s, font, size, tracking=tracking)[0]
    return _cache[k]


def pin(fr, cam, x, y, op, scale=1.0):
    if not hasattr(pin, 'd'):
        from art import soft_disc
        pin.d = soft_disc(40, 40, 20, 20, 12, edge=2).astype(np.float32)
        pin.r = (soft_disc(60, 60, 30, 30, 22, edge=1.5) - soft_disc(60, 60, 30, 30, 18, edge=1.5)).clip(0, 1).astype(np.float32)
    kit.put(fr, cam, pin.d, x, y, VERM, op, scale)
    kit.put(fr, cam, pin.r, x, y, VERM, 0.6 * op, scale)


def place_label(fr, cam, s, x, y, op, size=34, color=INK):
    g = label(s, size, tracking=6)
    kit.put(fr, cam, kit.box(g.shape[0] + 18, g.shape[1] + 30, 4.0), x, y, PAPER, 0.85 * op, over=True)
    kit.put(fr, cam, g, x, y, color, op)


class Tag:
    """the paper name tag: a list of (t_from, text, kanji or None); at each change the old word squeezes out and the
    new one pops in"""

    def __init__(self, words, size=58):
        self.words = words
        self.g = [(label(s, size, FONT_EN_BOLD, 6), label(k, int(size * 0.62), FONT_JP, 0) if k else None) for _, s, k in words]

    def draw(self, fr, cam, t, x, y, op=1.0, scale=1.0):
        if op <= 0:
            return
        idx = max([i for i, (ts, _, _) in enumerate(self.words) if t >= ts] or [0])
        q = t - self.words[idx][0]
        pop = 1 + 0.35 * np.exp(-max(q, 0) * 6) * (q > 0) * (idx > 0)
        g, k = self.g[idx]
        w = g.shape[1] + (k.shape[1] + 20 if k is not None else 0) + 60
        h = 110
        sx = scale * pop
        kit.put(fr, cam, kit.box(int(h * 0.98) + 14, int(w) + 14, 10.0), x + 8, y + 12, INK, 0.25 * op, sx)
        kit.put(fr, cam, kit.box(h, int(w), 3.0), x, y, PAPER, op, sx, over=True)
        kit.put(fr, cam, kit.rim(h, int(w), inset=8, t=3), x, y, VERM, 0.8 * op, sx)
        if k is not None:
            kx = x - (w / 2 - 30 - k.shape[1] / 2) * sx
            kit.put(fr, cam, k, kx, y, INK, op, sx)
            kit.put(fr, cam, g, x + (k.shape[1] + 20) / 2 * sx, y + 2, VERM, op, sx)
        else:
            kit.put(fr, cam, g, x, y + 2, VERM, op, sx)
        # a little flash ring on every change
        if idx > 0 and 0 < q < 0.5:
            r = kit.rim(int(h + 60 * q * 2), int(w + 60 * q * 2), inset=6, t=4)
            kit.put(fr, cam, r, x, y, VERM, 0.6 * (1 - q / 0.5), sx)
