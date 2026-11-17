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
