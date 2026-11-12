"""The ending.  "Which era would you live in?  Tell me in the comments, and follow for more."  またね！
WHICH ERA WOULD YOU LIVE IN? is set at the top and the fifteen era names fall into a 3 x 5 grid of small washi
cards, in order.  A vermilion ring runs round the grid like a roulette, slowing, while Raj asks; on "comments"
TELL ME IN THE COMMENTS ↓ comes in, on "follow" the black banner FOLLOW @raj_in_jp sweeps in, and またね！ is brushed
in vermilion as Raj says it."""
import numpy as np

import kit
from cards import INDIGO
from engine import (FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_HEAD, FONT_JP, GREY, H, INK, VERM, W, Cam, StrokeSet, ease_io,
                    noise, smooth, stroke, text_layer)
from scenes.era import ERAS
from scenes.kscene import KanjiScene
from timeline import ERA_KEYS, JA, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)
CARD = np.array([0.96, 0.93, 0.86], np.float32)
KEYS = [k for k in ERA_KEYS if k != 'ships']
XS, Y0, DY = (230, 540, 850), 520, 132
CW, CH = 270, 116


class Scene(KanjiScene):
    paper_seed = 330

    def build(self):
        self.q1, _ = text_layer('WHICH ERA', FONT_HEAD, 70)
        b = text_layer('would you live in?', FONT_BRUSH_EN, 96)[0]
        self.q2 = b * (0.86 + 0.14 * noise(*b.shape, 6, 2, 2))
        self.cells = [(text_layer(ERAS[k][0], FONT_JP, 66)[0], text_layer(ERAS[k][2].split(' ')[0], FONT_EN_BOLD, 22, tracking=4)[0])
                      for k in KEYS]
        self.box, self.rim = kit.box(CH, CW, 2.5), kit.rim(CH, CW, inset=6, t=3)
        self.sel = kit.rim(CH + 16, CW + 16, inset=4, t=6)
        self.cm, _ = text_layer('TELL ME IN THE COMMENTS ↓', FONT_EN_BOLD, 36, tracking=4)
        m = text_layer('またね！', FONT_BRUSH_JP, 100)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow, _ = text_layer('FOLLOW', FONT_EN_BOLD, 40, tracking=10)
        self.handle, _ = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)
        self.t_q = at('Which era')[0]
        self.t_cm = at('comments')[0]
        self.t_follow = at('follow for')[0]
        self.t_mt = JA['matane']['start']
        self.t_hit = self.t_mt
        bn = StrokeSet(W, H)
        bn.add(stroke(W, H, [(250, 1336), (540, 1324), (830, 1332)], 118, ink=0.96, dry=0.45,
                      profile=((0, 0.55), (0.06, 1.0), (0.85, 0.95), (1, 0.5)), seed=171), self.t_follow - 0.05, 0.4)
        self.banner = bn

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 6))

    def cell_xy(self, j):
        return XS[j % 3], Y0 + DY * (j // 3)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fq = smooth((t - self.t_q + 0.2) / 0.35)
        kit.put(fr, cam, self.q1, 540, 270 + 15 * (1 - fq), INK, fq)
        kit.put(fr, cam, self.q2, 540, 375, VERM, smooth((t - self.t_q - 0.2) / 0.35), rot=-0.03)
        for j, (g, lab) in enumerate(self.cells):
            f = (t - self.t0 - 0.25 - 0.06 * j) / 0.3
            if f <= 0:
                continue
            x, y = self.cell_xy(j)
            o = smooth(f)
            dy = -30 * (1 - ease_io(min(f, 1)))
            kit.card(fr, cam, self.box, self.rim, x, y + dy, o, color=CARD)
            kit.put(fr, cam, g, x, y - 14 + dy, INK, o)
            kit.put(fr, cam, lab, x, y + 38 + dy, INDIGO, o)
        # the roulette ring, slowing down, gone by "comments"
        u = (t - self.t_q) / (self.t_cm - self.t_q)
        if 0 < u < 1.1:
            pos = 22 * (1 - (1 - min(u, 1)) ** 2)
            j = int(pos) % len(KEYS)
            x, y = self.cell_xy(j)
            kit.put(fr, cam, self.sel, x, y, VERM, 0.95 * (1 - smooth((u - 0.9) / 0.2)))
        fc = smooth((t - self.t_cm + 0.1) / 0.3) * (1 - smooth((t - self.t_mt + 0.3) / 0.3))
        kit.put(fr, cam, self.cm, 540, 1195, INK, fc)
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 1172, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow + 0.05) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1324, IVORY, smooth((t - self.t_follow - 0.15) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1252, INK, smooth(fb))
        return fr.img
