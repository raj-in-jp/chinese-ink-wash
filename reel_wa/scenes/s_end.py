"""The ending.  "Follow for more."  またね！
A recap row fades up — 倭 (OLD NAME, struck through) → 日本 NIHON · 和 HARMONY — then the black brush banner
FOLLOW @raj_in_jp and またね！"""
import numpy as np

import kit
from engine import FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_JP, GREY, H, INK, VERM, W, Cam, StrokeSet, noise, smooth, stroke, \
    text_layer
from scenes.common11 import label
from scenes.kscene import KanjiScene
from timeline import JA, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)
ROW = 620


class Scene(KanjiScene):
    paper_seed = 1106

    def build(self):
        K = lambda c: text_layer(c, FONT_JP, 150)[0]
        self.items = [(K('倭'), label('OLD NAME', 30, FONT_EN_BOLD, 6), GREY, 200),
                      (K('日本'), label('NIHON', 30, FONT_EN_BOLD, 6), INK, 560),
                      (K('和'), label('HARMONY', 30, FONT_EN_BOLD, 6), VERM, 890)]
        self.arrow = label('→', 80)
        self.dot = label('·', 80)
        self.strike = np.ones((8, 190), np.float32)
        m = text_layer('またね！', FONT_BRUSH_JP, 120)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, FONT_EN_BOLD, 10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_follow = at('Follow for more')[0]
        self.t_mt = JA['matane']['start']
        self.t_hit = self.t_mt
        bn = StrokeSet(W, H)
        bn.add(stroke(W, H, [(250, 1196), (540, 1184), (830, 1192)], 118, ink=0.96, dry=0.45,
                      profile=((0, 0.55), (0.06, 1.0), (0.85, 0.95), (1, 0.5)), seed=171), self.t_follow + 0.1, 0.4)
        self.banner = bn

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 5))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        for j, (g, lab, col, x) in enumerate(self.items):
            f = smooth((t - self.t0 - 0.2 - 0.25 * j) / 0.4)
            kit.put(fr, cam, g, x, ROW + 15 * (1 - f), col, f)
            kit.put(fr, cam, lab, x, ROW + 125, GREY if j == 0 else col, f)
        kit.put(fr, cam, self.strike, 200, ROW, VERM, 0.9 * smooth((t - self.t0 - 0.5) / 0.3))
        kit.put(fr, cam, self.arrow, 365, ROW, GREY, smooth((t - self.t0 - 0.35) / 0.3))
        kit.put(fr, cam, self.dot, 745, ROW, GREY, smooth((t - self.t0 - 0.6) / 0.3))
        fb = (t - self.t_follow - 0.1) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1184, IVORY, smooth((t - self.t_follow - 0.25) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1100, INK, smooth(fb))
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 900, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        return fr.img
