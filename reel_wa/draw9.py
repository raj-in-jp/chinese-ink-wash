"""draw9 — the little ink drawings of reel 9: a caravel (Columbus, the Portuguese) with a red cross on its sails, a
camel caravan (the Silk Road), a Chinese junk, Marco Polo's golden palace, and the rising sun.  Each returns float32
density patches (0..1): {'ink', 'red', 'gold', 'wash'} as needed, to be inked with kit.put."""
import cv2
import numpy as np

from engine import blur, noise

S = 4


def _f(a, w, h, soft=1.0, rough=0.2, seed=0):
    m = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    m = blur(m, soft)
    return np.clip(m * (1 - rough + rough * noise(h, w, 5, 2, seed)), 0, 1).astype(np.float32)


def caravel(w=300, h=280, seed=1):
    """a three-masted caravel, sails full, a red cross on the main sail"""
    ink = np.zeros((h * S, w * S), np.uint8)
    red = np.zeros_like(ink)
    wash = np.zeros_like(ink)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    hull = P([(0.06, 0.70), (0.94, 0.66), (0.86, 0.84), (0.16, 0.86)])
    cv2.fillPoly(ink, [hull], 255, cv2.LINE_AA)
    cv2.fillPoly(ink, [P([(0.70, 0.66), (0.94, 0.58), (0.94, 0.68)])], 255, cv2.LINE_AA)         # raised stern
    lw = 3 * S
    for x, top in ((0.30, 0.18), (0.52, 0.08), (0.74, 0.22)):
        cv2.line(ink, (int(x * w * S), int(0.70 * h * S)), (int(x * w * S), int(top * h * S)), 255, lw, cv2.LINE_AA)
    sails = [(0.30, 0.24, 0.13, 0.20), (0.52, 0.14, 0.16, 0.26), (0.74, 0.28, 0.11, 0.18)]
    for j, (x, y, sw, sh) in enumerate(sails):
        pts = P([(x - sw, y), (x + sw, y), (x + sw * 0.9, y + sh), (x - sw * 0.9, y + sh)])
        cv2.fillPoly(wash, [pts], 255, cv2.LINE_AA)
        cv2.polylines(ink, [pts], True, 255, 2 * S, cv2.LINE_AA)
        if j == 1:                                       # the red cross on the main sail
            cx, cy = int(x * w * S), int((y + sh / 2) * h * S)
            a = int(sw * 0.45 * w * S)
            cv2.line(red, (cx - a, cy), (cx + a, cy), 255, 6 * S, cv2.LINE_AA)
            cv2.line(red, (cx, cy - a), (cx, cy + a), 255, 6 * S, cv2.LINE_AA)
    cv2.line(ink, (int(0.52 * w * S), int(0.08 * h * S)), (int(0.58 * w * S), int(0.03 * h * S)), 255, 2 * S, cv2.LINE_AA)
    return {'ink': _f(ink, w, h, 0.8, 0.15, seed), 'red': _f(red, w, h, 0.8, 0.2, seed + 1), 'wash': _f(wash, w, h, 1.5, 0.3, seed + 2)}


def junk(w=260, h=240, seed=3):
    """a Chinese junk with its battened sails"""
    ink = np.zeros((h * S, w * S), np.uint8)
    wash = np.zeros_like(ink)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    cv2.fillPoly(ink, [P([(0.05, 0.66), (0.95, 0.62), (0.84, 0.82), (0.18, 0.84)])], 255, cv2.LINE_AA)
    for x, top, sw in ((0.38, 0.12, 0.17), (0.66, 0.24, 0.13)):
        pts = P([(x - sw, top + 0.04), (x + sw * 0.8, top), (x + sw, 0.60), (x - sw * 0.9, 0.62)])
        cv2.fillPoly(wash, [pts], 255, cv2.LINE_AA)
        cv2.polylines(ink, [pts], True, 255, 2 * S, cv2.LINE_AA)
        for k in range(1, 5):                            # battens
            yy = top + (0.6 - top) * k / 5
            cv2.line(ink, (int((x - sw) * w * S), int(yy * h * S)), (int((x + sw) * w * S), int(yy * h * S)), 255, int(1.5 * S), cv2.LINE_AA)
        cv2.line(ink, (int(x * w * S), int(0.66 * h * S)), (int(x * w * S), int((top - 0.04) * h * S)), 255, 3 * S, cv2.LINE_AA)
    return {'ink': _f(ink, w, h, 0.8, 0.15, seed), 'wash': _f(wash, w, h, 1.5, 0.3, seed + 1)}


def camel(w=170, h=150, seed=5):
    """a camel walking, in silhouette"""
    a = np.zeros((h * S, w * S), np.uint8)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    cv2.fillPoly(a, [P([(0.20, 0.50), (0.30, 0.30), (0.42, 0.42), (0.52, 0.26), (0.66, 0.40), (0.72, 0.56), (0.25, 0.62)])], 255, cv2.LINE_AA)
    cv2.fillPoly(a, [P([(0.68, 0.46), (0.82, 0.18), (0.94, 0.16), (0.95, 0.24), (0.86, 0.26), (0.76, 0.52)])], 255, cv2.LINE_AA)
    for x0, x1 in ((0.26, 0.22), (0.34, 0.38), (0.60, 0.56), (0.68, 0.72)):
        cv2.line(a, (int(x0 * w * S), int(0.58 * h * S)), (int(x1 * w * S), int(0.95 * h * S)), 255, int(3.2 * S), cv2.LINE_AA)
    cv2.ellipse(a, (int(0.47 * w * S), int(0.22 * h * S)), (int(0.07 * w * S), int(0.10 * h * S)), 0, 0, 360, 255, -1, cv2.LINE_AA)   # rider
    return _f(a, w, h, 0.8, 0.15, seed)


def palace(w=420, h=330, seed=7):
    """Marco Polo's golden palace on its island: a sweeping roof in gold over an ink hall, on a gold-washed island"""
    ink = np.zeros((h * S, w * S), np.uint8)
    gold = np.zeros_like(ink)
    P = lambda pts: np.array([[int(x * w * S), int(y * h * S)] for x, y in pts], np.int32)
    cv2.ellipse(gold, (int(0.5 * w * S), int(0.86 * h * S)), (int(0.46 * w * S), int(0.1 * h * S)), 0, 0, 360, 160, -1, cv2.LINE_AA)
    for y0, half, hh in ((0.18, 0.30, 0.14), (0.44, 0.38, 0.14)):          # two roofs, curving up at the ends
        roof = P([(0.5 - half, y0 + hh), (0.5 - half * 0.7, y0 + hh * 0.55), (0.5, y0), (0.5 + half * 0.7, y0 + hh * 0.55), (0.5 + half, y0 + hh)])
        cv2.fillPoly(gold, [roof], 255, cv2.LINE_AA)
        cv2.polylines(ink, [roof], False, 255, 2 * S, cv2.LINE_AA)
    cv2.rectangle(ink, (int(0.28 * w * S), int(0.32 * h * S)), (int(0.72 * w * S), int(0.44 * h * S)), 255, 2 * S, cv2.LINE_AA)
    cv2.rectangle(ink, (int(0.20 * w * S), int(0.58 * h * S)), (int(0.80 * w * S), int(0.80 * h * S)), 255, 2 * S, cv2.LINE_AA)
    for k in range(6):
        x = 0.24 + k * 0.104
        cv2.line(ink, (int(x * w * S), int(0.58 * h * S)), (int(x * w * S), int(0.80 * h * S)), 255, 2 * S, cv2.LINE_AA)
    return {'ink': _f(ink, w, h, 0.8, 0.15, seed), 'gold': _f(gold, w, h, 1.2, 0.25, seed + 1)}


def sun(r=170, seed=9):
    s = 2 * r + 40
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.hypot(xx - s / 2, yy - s / 2)
    m = np.clip((r - d) / 3, 0, 1)
    return (m * (0.88 + 0.12 * noise(s, s, 8, 3, seed))).astype(np.float32)
