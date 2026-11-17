"""和 everywhere.  "And that kanji is still everywhere today.  Washoku, Japanese food.  Washi, Japanese paper.  Even Reiwa,
the name of this era."
和 IS EVERYWHERE at the top.  Then three full painted panels, each sliding in as Raj names it, with its word above it
(和 always in vermilion):
  和食 WASHOKU   a whole ichijū-sansai meal on a lacquer tray, steam curling off the rice and the miso soup;
  和紙 WASHI     a hand-made sheet of washi drifting down, light sweeping across its fibres, a brush writing 和 on it;
  令和 REIWA     a hinoki board with 令和 brushed on it, a plum branch over it and petals falling — the name comes from a
                 Man'yōshū preface about plum blossoms; 2019 —"""
import cv2
import numpy as np

import kit
from draw11 import board, plum_branch, steam, washi, washoku
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_EN_ITALIC, FONT_JP, FONT_JP_ANTIQUE, GREY, H, INK, VERM, W, Cam, cached, ease_io, \
    ease_out, smooth
from glyphs import typeset
from scenes.common11 import label, mixed
from scenes.kscene import KanjiScene
from timeline import JA, at

PY = 960                                                     # panel centre


def paint(fr, cam, rgb, a, x, y, op=1.0, sc=1.0, rot=0.0):
    """composite a painted RGBA image, centred at (x, y)"""
    if op <= 0:
        return
    h, w = a.shape
    M = kit.affine(cam, x, y, w, h, sc, sc, rot)
    A = cv2.warpAffine(a, M, (W, H))
    if A.max() <= 0:
        return
    C = cv2.warpAffine(rgb, M, (W, H))
    fr.over(C, A, op)


def _rgba(fn):
    def go():
        out = fn()
        return {'rgb': out[0].astype(np.float32), 'a': out[1].astype(np.float32)}
    return go


def _washoku():
    rgb, a, src = washoku()
    return {'rgb': rgb.astype(np.float32), 'a': a.astype(np.float32), 'src': np.asarray(src, np.float32)}


class Scene(KanjiScene):
    paper_seed = 1105

    def build(self):
        self.head = mixed([('和', 96, FONT_JP, 0), ('IS EVERYWHERE', 104, FONT_BOLD, 4)], 20)
        d = cached('r11_washoku_v2', _washoku)
        self.food = (d['rgb'], d['a'], [tuple(r) for r in d['src']])
        self.sheet = cached('r11_washi_v1', _rgba(washi))
        self.board = cached('r11_board_v1', _rgba(board))
        self.plum = cached('r11_plum_v1', _rgba(plum_branch))
        K = lambda c: label(c, 120, FONT_JP_ANTIQUE, 0)
        self.items = [
            (K('和'), K('食'), 0, label('WASHOKU', 80, FONT_BOLD, 6), label('Japanese food', 40, FONT_EN_ITALIC, 0), JA['washoku']['start']),
            (K('和'), K('紙'), 0, label('WASHI', 80, FONT_BOLD, 6), label('Japanese paper', 40, FONT_EN_ITALIC, 0), JA['washi']['start']),
            (K('令'), K('和'), 1, label('REIWA', 80, FONT_BOLD, 6), label('this era, 2019 —', 40, FONT_EN_ITALIC, 0), JA['reiwa']['start'])]
        self.wa_brush = typeset('和', 330, font=FONT_BRUSH_JP, seed=1150, medians=False, sweep=(0.7, 1))
        self.rei = [typeset(c, 250, font=FONT_BRUSH_JP, seed=1160 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('令和')]
        self.poem = label('from a poem about plum blossoms (Man’yōshū)', 34, FONT_EN_ITALIC, 0)
        r = np.random.default_rng(5)
        self.petals = [(r.uniform(150, 1000), r.uniform(0, 1), r.uniform(0.6, 1.2), r.uniform(0, 6.28)) for _ in range(14)]
        pet = np.zeros((26, 26), np.float32)
        cv2.ellipse(pet, (13, 13), (11, 7), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        self.pet = cv2.GaussianBlur(pet, (0, 0), 0.8)
        yy, xx = np.mgrid[0:H, 0:W]
        self.diag = (xx + 0.5 * yy).astype(np.float32)
        self.t_ev = at('everywhere')[0]
        self.t_hit = JA['washoku']['start']

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 10))

    def slide(self, t, j):
        """x offset of panel j and whether it is on screen: in from the right, out to the left when the next comes"""
        ts = self.items[j][-1] - 0.3
        x = 1150 * (1 - ease_io(np.clip((t - ts) / 0.5, 0, 1)))
        if j + 1 < len(self.items):
            x -= 1150 * ease_io(np.clip((t - self.items[j + 1][-1] + 0.3) / 0.5, 0, 1))
        return x, t > ts and abs(x) < 1100

    def word(self, fr, cam, j, x, t):
        a, b, hot, name, gloss, ts = self.items[j]
        pop = 1 + 0.15 * np.exp(-max(t - ts, 0) * 5)
        kit.put(fr, cam, a, x - 330, 470, VERM if hot == 0 else INK, 1.0, pop)
        kit.put(fr, cam, b, x - 200, 470, VERM if hot == 1 else INK, 1.0, pop)
        kit.put(fr, cam, name, x + 110, 445, INK, 1.0)
        kit.put(fr, cam, gloss, x + 110, 515, GREY, 1.0)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fh = (t - self.t_ev + 0.2) / 0.3
        kit.put(fr, cam, self.head, 540, 280, VERM, smooth(fh), 1 + 0.2 * np.exp(-max(fh, 0) * 3))
        # 1. washoku: the meal, steaming
        x, on = self.slide(t, 0)
        if on:
            rgb, a, src = self.food
            sc = 0.94 + 0.03 * smooth((t - self.items[0][-1]) / 2.5)
            paint(fr, cam, rgb, a, 540 + x, PY, 1.0, sc, -0.012 * x / 1150)
            st = steam(t, a.shape[1], a.shape[0], src)
            kit.put(fr, cam, st, 540 + x, PY, np.array([1, 1, 1], np.float32), 0.85, sc, over=True)
            self.word(fr, cam, 0, 540 + x, t)
        # 2. washi: the sheet drifts down, light sweeps over it, a brush writes 和
        x, on = self.slide(t, 1)
        if on:
            ts = self.items[1][-1]
            u = ease_out(np.clip((t - ts + 0.3) / 0.9, 0, 1))
            rot = -0.10 * (1 - u) - 0.02 + 0.01 * np.sin(t * 1.3)
            py = PY - 60 * (1 - u)
            pa_ = self.sheet['a']
            paint(fr, cam, self.sheet['rgb'], pa_, 540 + x, py, 1.0, 0.95, rot)
            cx = -300 + 1900 * np.clip((t - ts) / 1.8, 0, 1)
            sweep = np.clip(1 - np.abs(self.diag - cx - 300) / 170, 0, 1)
            pa = cv2.warpAffine(pa_, kit.affine(cam, 540 + x, py, pa_.shape[1], pa_.shape[0], 0.95, 0.95, rot), (W, H))
            fr.over(np.array([1, 1, 1], np.float32), sweep * pa, 0.35)
            fb = (t - ts - 0.2) / 1.0
            if fb > 0:
                kit.put(fr, cam, self.wa_brush.at(fb, soft=0.05), 540 + x, py - 10, INK, 0.92, 1.0, rot=rot)
            self.word(fr, cam, 1, 540 + x, t)
        # 3. Reiwa: the board, 令和 brushed, plum blossom and falling petals
        x, on = self.slide(t, 2)
        if on:
            ts = self.items[2][-1]
            paint(fr, cam, self.board['rgb'], self.board['a'], 540 + x, PY + 20, 1.0, 0.95)
            for j, g in enumerate(self.rei):
                kit.put(fr, cam, g.at((t - ts - 0.1) / 0.7 - 0.45 * j, soft=0.05), 540 + x, PY - 130 + 280 * j, INK, 0.95)
            paint(fr, cam, self.plum['rgb'], self.plum['a'], 830 + x, PY - 250, smooth((t - ts) / 0.5), 0.72)
            for (px, ph, sp, rr) in self.petals:
                q = ((t - ts) * 0.25 * sp + ph) % 1
                kit.put(fr, cam, self.pet, px + x + 40 * np.sin(t * 1.5 + rr), 560 + q * 900, np.array([0.93, 0.60, 0.66], np.float32),
                        0.8 * smooth((t - ts) / 0.6) * smooth((1 - q) * 8), 1.0, rot=t * 2 + rr, over=True)
            self.word(fr, cam, 2, 540 + x, t)
            kit.put(fr, cam, self.poem, 540 + x, PY + 440, GREY, smooth((t - ts - 0.9) / 0.4))
        return fr.img
