"""draw10 — the ink drawings of reel 10: Tokyo's skyline with its tower, the empty marsh that was there before,
Edo Castle's keep, a little Edo house (repeated to grow the city), the imperial chrysanthemum, and a closed law book.
Each returns float32 density patches (0..1) to ink with kit.put."""
import cv2
import numpy as np

from engine import blur, noise

S = 4


def _f(a, w, h, soft=1.0, rough=0.2, seed=0):
    m = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return np.clip(blur(m, soft) * (1 - rough + rough * noise(h, w, 5, 2, seed)), 0, 1).astype(np.float32)


def skyline(w=1080, h=700, seed=1):
    """towers of different heights, a lattice tower in the middle; {'ink', 'lights'}"""
    ink = np.zeros((h * S, w * S), np.uint8)
    lit = np.zeros_like(ink)
    r = np.random.default_rng(seed)
    x = 0
    while x < w:
        bw = int(r.uniform(60, 130))
        bh = int(r.uniform(0.25, 0.75) * h)
        if 440 < x < 600:
            bh = int(bh * 0.6)
        cv2.rectangle(ink, (x * S, (h - bh) * S), ((x + bw - 6) * S, h * S), 255, -1)
        for wy in range(h - bh + 16, h - 10, 26):            # windows
            for wx in range(x + 10, x + bw - 18, 20):
                if r.random() < 0.55:
                    cv2.rectangle(lit, (wx * S, wy * S), ((wx + 8) * S, (wy + 12) * S), 255, -1)
        x += bw
    # the tower: a tall lattice A
    cx, top, base = 540, int(h * 0.02), h
    pts = np.array([[cx * S, top * S], [(cx + 70) * S, base * S], [(cx - 70) * S, base * S]], np.int32)
    cv2.polylines(ink, [pts], True, 255, 5 * S, cv2.LINE_AA)
    for k in range(1, 14):                                   # cross bracing
        y = top + (base - top) * k / 14
        half = 70 * k / 14
        cv2.line(ink, (int((cx - half) * S), int(y * S)), (int((cx + half) * S), int(y * S)), 255, 2 * S, cv2.LINE_AA)
        y2 = top + (base - top) * (k + 1) / 14
        h2 = 70 * (k + 1) / 14
        cv2.line(ink, (int((cx - half) * S), int(y * S)), (int((cx + h2) * S), int(y2 * S)), 255, int(1.5 * S), cv2.LINE_AA)
        cv2.line(ink, (int((cx + half) * S), int(y * S)), (int((cx - h2) * S), int(y2 * S)), 255, int(1.5 * S), cv2.LINE_AA)
    for yy in (0.35, 0.6):                                   # observation decks
        y = top + (base - top) * yy
        hw = 70 * yy + 22
        cv2.rectangle(ink, (int((cx - hw) * S), int((y - 12) * S)), (int((cx + hw) * S), int((y + 12) * S)), 255, -1)
    lit = cv2.bitwise_and(lit, ink)
    return {'ink': _f(ink, w, h, 0.7, 0.1, seed), 'lights': _f(lit, w, h, 0.8, 0.2, seed + 1)}


def reeds(w=1080, h=420, seed=3):
    """an empty marsh: reeds and water lines"""
    m = np.zeros((h * S, w * S), np.uint8)
    r = np.random.default_rng(seed)
    for k in range(70):
        x = r.uniform(0, w)
        hh = r.uniform(0.3, 0.9) * h
        bend = r.uniform(-30, 30)
        pts = np.array([[x * S, h * S], [(x + bend * 0.4) * S, (h - hh * 0.5) * S], [(x + bend) * S, (h - hh) * S]], np.int32)
        cv2.polylines(m, [pts], False, 255, int(r.uniform(2, 4) * S), cv2.LINE_AA)
    for k in range(6):
        y = h - 10 - k * 14
        cv2.line(m, (int(r.uniform(0, 300) * S), y * S), (int(r.uniform(700, 1080) * S), y * S), 160, 2 * S, cv2.LINE_AA)
    return _f(m, w, h, 0.8, 0.2, seed)


def castle(w=300, h=300, seed=5):
    """Edo Castle's keep: stacked roofs on a stone base; {'ink', 'wash'}"""
    ink = np.zeros((h * S, w * S), np.uint8)
    wash = np.zeros_like(ink)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    cv2.fillPoly(wash, [P([(0.18, 0.78), (0.82, 0.78), (0.9, 0.98), (0.1, 0.98)])], 200, cv2.LINE_AA)
    cv2.polylines(ink, [P([(0.18, 0.78), (0.82, 0.78), (0.9, 0.98), (0.1, 0.98)])], True, 255, 2 * S, cv2.LINE_AA)
    for k, (y0, half) in enumerate(((0.62, 0.38), (0.44, 0.3), (0.26, 0.22), (0.1, 0.14))):
        roof = P([(0.5 - half, y0 + 0.08), (0.5 - half * 0.6, y0 + 0.02), (0.5, y0 - 0.02), (0.5 + half * 0.6, y0 + 0.02), (0.5 + half, y0 + 0.08)])
        cv2.polylines(ink, [roof], False, 255, 3 * S, cv2.LINE_AA)
        cv2.rectangle(wash, (int((0.5 - half * 0.7) * w * S), int((y0 + 0.08) * h * S)), (int((0.5 + half * 0.7) * w * S), int((y0 + 0.18) * h * S)), 255, -1)
        cv2.rectangle(ink, (int((0.5 - half * 0.7) * w * S), int((y0 + 0.08) * h * S)), (int((0.5 + half * 0.7) * w * S), int((y0 + 0.18) * h * S)), 255, 2 * S, cv2.LINE_AA)
    return {'ink': _f(ink, w, h, 0.8, 0.15, seed), 'wash': _f(wash, w, h, 1.2, 0.3, seed + 1)}


def house(w=60, h=48, seed=7):
    m = np.zeros((h * S, w * S), np.uint8)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    cv2.fillPoly(m, [P([(0.02, 0.45), (0.5, 0.05), (0.98, 0.45)])], 255, cv2.LINE_AA)
    cv2.rectangle(m, (int(0.15 * w * S), int(0.45 * h * S)), (int(0.85 * w * S), int(0.98 * h * S)), 150, -1)
    return _f(m, w, h, 0.6, 0.2, seed)


def crest(r=90, seed=9):
    """a 16-petal chrysanthemum"""
    s = 2 * r + 20
    m = np.zeros((s * S, s * S), np.uint8)
    c = (s * S // 2, s * S // 2)
    for k in range(16):
        a = k * np.pi / 8
        cv2.ellipse(m, (int(c[0] + np.cos(a) * r * 0.55 * S), int(c[1] + np.sin(a) * r * 0.55 * S)), (int(r * 0.42 * S), int(r * 0.14 * S)),
                    np.degrees(a), 0, 360, 255, 2 * S, cv2.LINE_AA)
    cv2.circle(m, c, int(r * 0.2 * S), 255, -1, cv2.LINE_AA)
    cv2.circle(m, c, int(r * S), 255, 2 * S, cv2.LINE_AA)
    return _f(m, s, s, 0.7, 0.1, seed)


def book(w=520, h=380, seed=11):
    """an open law book; {'ink', 'wash'}"""
    ink = np.zeros((h * S, w * S), np.uint8)
    wash = np.zeros_like(ink)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    for side in (-1, 1):
        page = P([(0.5, 0.12), (0.5 + side * 0.46, 0.06), (0.5 + side * 0.46, 0.9), (0.5, 0.96)])
        cv2.fillPoly(wash, [page], 255, cv2.LINE_AA)
        cv2.polylines(ink, [page], True, 255, 3 * S, cv2.LINE_AA)
        for k in range(9):
            y = 0.2 + k * 0.075
            x0, x1 = (0.08, 0.44) if side < 0 else (0.56, 0.92)
            cv2.line(ink, (int(x0 * w * S), int(y * h * S)), (int(x1 * w * S), int((y - 0.01 * side) * h * S)), 150, int(1.5 * S), cv2.LINE_AA)
    return {'ink': _f(ink, w, h, 0.8, 0.15, seed), 'wash': _f(wash, w, h, 1.0, 0.2, seed + 1)}
