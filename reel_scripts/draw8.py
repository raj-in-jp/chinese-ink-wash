"""draw8 — the little ink drawings of reel 8: a steaming coffee cup on its saucer (the sentence is 'I drink coffee'),
the steam itself (drawn fresh every frame so it curls upward), a small brushed figure for 私 'I', and the Dutch flag
for コーヒー < koffie.  Each returns float32 density patches (0..1) to be inked with kit.put."""
import cv2
import numpy as np

from engine import blur, noise


def _ink(m, rough=0.18, seed=0, soft=1.2):
    """turn a hard mask into an ink stroke: soft edge, uneven density"""
    m = blur(m.astype(np.float32), soft)
    return np.clip(m * (1 - rough + rough * noise(*m.shape, 5, 2, seed)), 0, 1).astype(np.float32)


def cup(w=560, h=460, seed=3):
    """a coffee cup on a saucer, ink outline + a pale wash inside; returns {'ink', 'wash', 'coffee'}"""
    S = 4
    o = np.zeros((h * S, w * S), np.uint8)
    wash = np.zeros_like(o)
    cof = np.zeros_like(o)
    cx = w * S // 2
    top, bot = int(h * 0.16 * S), int(h * 0.74 * S)
    rw_top, rw_bot = int(w * 0.30 * S), int(w * 0.22 * S)
    # body: a tapered bowl
    body = np.array([[cx - rw_top, top], [cx + rw_top, top], [cx + rw_bot, bot], [cx - rw_bot, bot]], np.int32)
    cv2.fillPoly(wash, [body], 255, cv2.LINE_AA)
    cv2.ellipse(wash, (cx, bot), (rw_bot, int(h * 0.05 * S)), 0, 0, 180, 255, -1, cv2.LINE_AA)
    lw = 9 * S
    cv2.line(o, (cx - rw_top, top), (cx - rw_bot, bot), 255, lw, cv2.LINE_AA)
    cv2.line(o, (cx + rw_top, top), (cx + rw_bot, bot), 255, lw, cv2.LINE_AA)
    cv2.ellipse(o, (cx, bot), (rw_bot, int(h * 0.05 * S)), 0, 0, 180, 255, lw, cv2.LINE_AA)
    # the rim and the coffee in it
    cv2.ellipse(o, (cx, top), (rw_top, int(h * 0.06 * S)), 0, 0, 360, 255, lw, cv2.LINE_AA)
    cv2.ellipse(cof, (cx, top + 4 * S), (rw_top - 14 * S, int(h * 0.045 * S)), 0, 0, 360, 255, -1, cv2.LINE_AA)
    # the handle
    cv2.ellipse(o, (cx + rw_top - 6 * S, int(h * 0.40 * S)), (int(w * 0.11 * S), int(h * 0.13 * S)), 0, -80, 95, 255, lw, cv2.LINE_AA)
    # the saucer
    sy = int(h * 0.80 * S)
    cv2.ellipse(o, (cx, sy), (int(w * 0.46 * S), int(h * 0.075 * S)), 0, 0, 180, 255, lw, cv2.LINE_AA)
    cv2.ellipse(o, (cx, sy), (int(w * 0.46 * S), int(h * 0.075 * S)), 0, 180, 360, 255, int(lw * 0.6), cv2.LINE_AA)
    cv2.ellipse(wash, (cx, sy), (int(w * 0.46 * S), int(h * 0.075 * S)), 0, 0, 360, 120, -1, cv2.LINE_AA)
    f = lambda a: cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return {'ink': _ink(f(o), 0.25, seed), 'wash': _ink(f(wash), 0.4, seed + 1, 6) * 0.35,
            'coffee': _ink(f(cof), 0.3, seed + 2, 2)}


def steam(t, w=360, h=380, n=3):
    """three wisps curling up from the cup, moving with t"""
    m = np.zeros((h, w), np.float32)
    for j in range(n):
        x0 = w * (0.3 + 0.2 * j)
        ys = np.linspace(h - 10, 20, 60)
        u = (h - ys) / h
        xs = x0 + 26 * np.sin(u * 7 - t * 3.2 + j * 2.1) * (0.4 + u)
        pts = np.stack([xs, ys], 1).astype(np.int32)
        seg = np.zeros_like(m)
        cv2.polylines(seg, [pts], False, 1.0, 9, cv2.LINE_AA)
        fade = np.clip(np.linspace(0, 1, h)[:, None] * 1.6 - 0.15, 0, 1)    # thin out towards the top
        pulse = 0.6 + 0.4 * np.sin(t * 2 + j)
        m = np.maximum(m, seg * fade * pulse)
    return blur(m, 4)


def person(h=150, seed=7):
    """a small brushed figure (head + body + arms)"""
    w = int(h * 0.8)
    S = 4
    o = np.zeros((h * S, w * S), np.uint8)
    cx = w * S // 2
    cv2.circle(o, (cx, int(h * 0.18 * S)), int(h * 0.13 * S), 255, -1, cv2.LINE_AA)
    body = np.array([[cx - int(w * 0.30 * S), h * S - 4], [cx + int(w * 0.30 * S), h * S - 4],
                     [cx + int(w * 0.17 * S), int(h * 0.36 * S)], [cx - int(w * 0.17 * S), int(h * 0.36 * S)]], np.int32)
    cv2.fillPoly(o, [body], 255, cv2.LINE_AA)
    m = cv2.resize(o, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return _ink(m, 0.2, seed)


def dutch_flag(w=150, h=100):
    """the Dutch flag as three bands (red, white, blue) + an outline; returns (rgb, alpha)"""
    rgb = np.zeros((h, w, 3), np.float32)
    rgb[:h // 3] = (0.68, 0.11, 0.16)
    rgb[h // 3:2 * h // 3] = (0.97, 0.96, 0.93)
    rgb[2 * h // 3:] = (0.13, 0.27, 0.55)
    a = np.ones((h, w), np.float32)
    rgb[:3], rgb[-3:], rgb[:, :3], rgb[:, -3:] = 0.15, 0.15, 0.15, 0.15
    return rgb, a
