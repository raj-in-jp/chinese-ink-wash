"""Vowels.  "So when English puts consonants together, Japanese adds a little vowel to each one.  Test becomes テスト.
Christmas becomes クリスマス.  Which vowel?  Usually 'u'.  But after 't' and 'd', it's 'o'."
TEST in chunky letters; the stuck-together S and T jiggle in vermilion (CONSONANTS TOGETHER!); the letters spread
apart and little vowel bubbles u / o drop into the gaps; then it snaps into tiles テ ス ト (te SU TO, added vowels red).
CHRISTMAS below over a twinkling painted tree, bursting into ク リ ス マ ス.  Then the rule: a big +U bubble (ス ク ル)
and AFTER T & D: +O (ト ド)."""
import cv2
import numpy as np

import kit
from draw12 import xmas_tree
from engine import FONT_BOLD, FONT_EN_BOLD, GREY, INK, VERM, Cam, cached, ease_io, ease_out, smooth, text_layer
from scenes.common12 import GOLD, INDIGO, PALETTE, Bubble, Tile, Word, chip, drop_y, label, paint, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

TEST_Y, XM_Y = 560, 900


def _tree():
    rgb, a, lights = xmas_tree()
    return {'rgb': rgb, 'a': a, 'lights': lights}


class Scene(KanjiScene):
    paper_seed = 1203

    def build(self):
        self.head = text_layer('CONSONANTS TOGETHER?', FONT_BOLD, 96, tracking=4)[0]
        self.test = Word('TEST', 180)
        self.bu, self.bo = Bubble('u', 96), Bubble('o', 96)
        self.ttiles = [Tile(k, 160, PALETTE[j], romaji=r, hot=h) for j, (k, r, h) in enumerate(zip('テスト', ('te', 'su', 'to'), ((), (1,), (1,))))]
        self.txs = tile_row('テスト', 540, 160, 18)
        self.xmas = Word('CHRISTMAS', 120)
        self.xtiles = [Tile(k, 124, PALETTE[(j + 1) % 4], romaji=r, hot=h) for j, (k, r, h) in
                       enumerate(zip('クリスマス', ('ku', 'ri', 'su', 'ma', 'su'), ((1,), (), (1,), (), (1,))))]
        self.xxs = tile_row('クリスマス', 540, 124, 14)
        self.tree = cached('r12_tree_v1', _tree)
        dot = np.zeros((40, 40), np.float32)
        cv2.circle(dot, (20, 20), 9, 1.0, -1, cv2.LINE_AA)
        self.dot = cv2.GaussianBlur(dot, (0, 0), 4)
        self.which = text_layer('WHICH VOWEL?', FONT_BOLD, 130, tracking=4)[0]
        self.U = Bubble('u', 220)
        self.O = Bubble('o', 200)
        self.usually = label('USUALLY', 44, FONT_EN_BOLD, 10)
        self.after = label('AFTER  T  &  D', 44, FONT_EN_BOLD, 10)
        self.ex_u = [Tile(k, 110, INDIGO, romaji=r, hot=(1,)) for k, r in zip('スクル', ('su', 'ku', 'ru'))]
        self.ex_o = [Tile(k, 120, VERM, romaji=r, hot=(1,)) for k, r in zip('トド', ('to', 'do'))]
        self.t_cons = at('consonants together')[0]
        self.t_add = at('adds a little')[0]
        self.t_test = at('Test')[0]
        self.t_tes = JA['tesuto']['start']
        self.t_xm = at('Christmas')[0]
        self.t_kur = JA['kurisumasu']['start']
        self.t_which = at('Which vowel')[0]
        self.t_u = at('Usually')[0]
        self.t_after = at('But after')[0]
        self.t_o = at('its o')[0] + 0.25
        r = np.random.default_rng(5)
        self.burst = [(r.uniform(-1, 1) * 400, r.uniform(-1, -0.3) * 400, r.uniform(-1.5, 1.5)) for _ in self.xmas.letters]
        self.t_hit = self.t_tes

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 15))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        part1 = 1 - smooth((t - self.t_which + 0.2) / 0.35)
        if part1 > 0:
            kit.put(fr, cam, self.head, 540, 270, INK, smooth((t - self.t_cons + 0.1) / 0.3) * part1, pulse(t, self.t_cons, 0.15))
            # TEST: S T jiggle, the letters spread, vowels drop in, then it snaps into テ ス ト
            spread = ease_io((t - self.t_add) / 0.6)
            snap = np.clip((t - self.t_tes + 0.05) / 0.25, 0, 1)
            if snap < 1:
                jig = (self.t_cons < t < self.t_add + 0.6) * 6 * np.sin(t * 40)
                offs = [(-110 * spread, 0), (-110 * spread, 0), (jig, 0), (160 * spread - jig, 0)]
                cols = [INK, INK, VERM if t > self.t_cons else INK, VERM if t > self.t_cons else INK]
                ops = [smooth((t - self.t0 - 0.2 - 0.06 * k) / 0.15) * (1 - snap) for k in range(4)]
                self.test.draw(fr, cam, 540 - 55 * spread, TEST_Y, INK, part1, 1.0, offs, ops, cols)
                xs = self.test.xs
                for bub, k, dx in ((self.bu, 2, 105), (self.bo, 3, 115)):
                    tb = self.t_add + 0.5 + 0.25 * (k - 2)
                    if t > tb:
                        bx = 540 - 55 * spread + xs[k] + offs[k][0] + dx
                        bub.draw(fr, cam, bx, TEST_Y + 20 + drop_y(t, tb, 320, 0.45), smooth((t - tb) / 0.1) * (1 - snap) * part1,
                                 pulse(t, tb + 0.4, 0.2))
            for k, (tile, x) in enumerate(zip(self.ttiles, self.txs)):
                t0 = self.t_tes + 0.15 * k
                if t > t0:
                    tile.draw(fr, cam, x, TEST_Y + drop_y(t, t0, 120, 0.35), smooth((t - t0) / 0.1) * part1, pulse(t, t0 + 0.3, 0.15))
                    tile.draw_rom(fr, cam, x, TEST_Y + 125, smooth((t - t0 - 0.25) / 0.2) * part1)
            # CHRISTMAS over a twinkling tree
            fx = smooth((t - self.t_xm + 0.2) / 0.3) * part1
            if fx > 0:
                tr = self.tree
                paint(fr, cam, tr['rgb'], tr['a'], 540, 1265, fx, 0.85)
                b = np.clip((t - self.t_kur + 0.1) / 0.45, 0, 1)
                if b < 1:
                    offs, ops, rots = [], [], []
                    for k, (dx, dy, rr) in enumerate(self.burst):
                        e = ease_out(b)
                        offs.append((dx * e, drop_y(t, self.t_xm - 0.1 + 0.04 * k, 160, 0.35) + dy * e + 700 * e * e))
                        ops.append(smooth((t - self.t_xm + 0.1 - 0.04 * k) / 0.12) * (1 - b) * part1)
                        rots.append(rr * e)
                    self.xmas.draw(fr, cam, 540, XM_Y, INK, 1.0, 1.0, offs, ops, None, rots)
                for k, (tile, x) in enumerate(zip(self.xtiles, self.xxs)):
                    t0 = self.t_kur + 0.13 * k
                    if t > t0:
                        tile.draw(fr, cam, x, XM_Y + drop_y(t, t0, 260, 0.4), smooth((t - t0) / 0.1) * part1, pulse(t, t0 + 0.3, 0.15))
                        tile.draw_rom(fr, cam, x, XM_Y + 102, smooth((t - t0 - 0.25) / 0.2) * part1)
                # twinkling lights, additive
                for k, (lx, ly) in enumerate(tr['lights']):
                    tw = max(0.0, np.sin(t * 4 + k * 1.7))
                    if tw > 0.05:
                        x = 540 + (lx - tr['a'].shape[1] / 2) * 0.85
                        y = 1265 + (ly - tr['a'].shape[0] / 2) * 0.85
                        M = kit.affine(cam, x, y, 40, 40)
                        A = cv2.warpAffine(self.dot, M, (fr.img.shape[1], fr.img.shape[0]))
                        fr.img += A[..., None] * np.array([1.0, 0.85, 0.45], np.float32) * 0.6 * tw * fx
        # the rule
        f2 = smooth((t - self.t_which + 0.1) / 0.35)
        if f2 > 0:
            kit.put(fr, cam, self.which, 540, 290, INK, f2, pulse(t, self.t_which, 0.15))
            fu = (t - self.t_u + 0.05) / 0.3
            if fu > 0:
                self.U.draw(fr, cam, 300, 680 + drop_y(t, self.t_u - 0.05, 300, 0.45), smooth(fu * 2), pulse(t, self.t_u + 0.4, 0.2))
                kit.put(fr, cam, self.usually, 300, 850, INK, smooth(fu))
                for k, tl in enumerate(self.ex_u):
                    t0 = self.t_u + 0.4 + 0.15 * k
                    if t > t0:
                        tl.draw(fr, cam, 590 + 125 * k, 680, smooth((t - t0) / 0.1), pulse(t, t0, 0.3))
                        tl.draw_rom(fr, cam, 590 + 125 * k, 760, smooth((t - t0 - 0.2) / 0.2))
            fo = (t - self.t_after + 0.05) / 0.3
            if fo > 0:
                kit.put(fr, cam, self.after, 540, 1010, INK, smooth(fo))
                self.O.draw(fr, cam, 300, 1200 + drop_y(t, self.t_o - 0.2, 300, 0.45), smooth((t - self.t_o + 0.2) / 0.1),
                            pulse(t, self.t_o + 0.2, 0.2))
                for k, tl in enumerate(self.ex_o):
                    t0 = self.t_o + 0.1 + 0.15 * k
                    if t > t0:
                        tl.draw(fr, cam, 620 + 140 * k, 1200, smooth((t - t0) / 0.1), pulse(t, t0, 0.3))
                        tl.draw_rom(fr, cam, 620 + 140 * k, 1280, smooth((t - t0 - 0.2) / 0.2))
        return fr.img
