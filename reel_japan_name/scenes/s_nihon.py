"""日本.  "In Japan, it's Nihon.  Written with the kanji for 'sun', and 'origin'.  The land where the sun rises."
日本 is brushed in big, stroke by stroke, with にほん over it and NIHON under it as Raj says it.  On "sun" 日 turns
vermilion and SUN is tagged under it; on "origin" 本 gets ORIGIN.  On "the land where the sun rises" an ink sea opens
along the bottom with a row of islands on the horizon, and a big vermilion sun rises behind them, its light spreading
up the page: THE LAND OF THE RISING SUN."""
import numpy as np

import kit
from draw9 import sun
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_JP, GREY, INK, VERM, Cam, StrokeSet, cached, ease_out, smooth, stroke, text_layer
from glyphs import typeset
from k6art import mist_hills
from scenes.common9 import label
from scenes.kscene import KanjiScene
from timeline import JA, at

INDIGO = np.array([0.20, 0.25, 0.45], np.float32)
HORIZON = 1360


class Scene(KanjiScene):
    paper_seed = 902

    def build(self):
        self.g = [typeset(c, 300, font=FONT_BRUSH_JP, seed=910 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('日本')]
        self.furi = text_layer('にほん', FONT_JP, 58)[0]
        self.rom = label('NIHON', 64, FONT_EN_BOLD, 14)
        self.top = text_layer("IN JAPAN, IT'S", FONT_BOLD, 80, tracking=4)[0]
        self.sunl, self.orl = label('SUN', 52, FONT_BOLD, 6), label('ORIGIN', 52, FONT_BOLD, 6)
        self.rising = text_layer('THE LAND OF THE RISING SUN', FONT_BOLD, 76, tracking=3)[0]
        self.sun = sun(190)
        self.hills = cached('r9_hills_v1', lambda: mist_hills(HORIZON, seed=23))['ink']
        sea = StrokeSet(1080, 1920)
        r = np.random.default_rng(3)
        for j in range(16):                                    # wave strokes on the sea
            y = HORIZON + 30 + j * 26
            x0 = r.uniform(-60, 400)
            sea.add(stroke(1080, 1920, [(x0, y), (x0 + 260, y - 6), (x0 + 520, y + 3), (x0 + 760, y - 4)], 3 + j * 0.25, ink=0.5,
                           dry=0.5, profile=((0, 0.2), (0.3, 1), (1, 0.2)), seed=40 + j), 0, 1)
        self.sea = sea.render(9)
        self.t_n = JA['nihon']['start']
        self.t_sun = at('for "sun"')[0] if False else at('kanji for')[1]
        self.t_or = at('origin')[0]
        self.t_rise = at('land where')[0]
        self.t_hit = self.t_n

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.04 * smooth((t - self.t0) / 8))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # the rising sun, the sea and the islands on the horizon
        fs = (t - self.t_rise + 0.3) / 1.6
        if fs > 0:
            u = ease_out(min(fs, 1))
            glow = np.clip(1 - np.abs(np.linspace(0, 1, 1920) - HORIZON / 1920) * 3, 0, 1)
            fr.img *= (1 - 0.12 * u * glow[:, None, None] * (1 - np.array([0.98, 0.72, 0.55], np.float32)))
            kit.put(fr, cam, self.sun, 540, HORIZON + 180 - 210 * u, VERM, 0.9 * smooth(fs * 3))
            fr.img[HORIZON + 4:] = fr.img[HORIZON + 4:] * 0.0 + self.frame(cam).img[HORIZON + 4:]      # the sea hides the sun's lower half
            self.layer(fr, cam, self.sea, opacity=0.6 * smooth(fs * 2))
            self.layer(fr, cam, self.hills, opacity=0.55 * smooth(fs * 2))
            kit.put(fr, cam, self.rising, 540, 1095, INK, smooth((fs - 0.15) * 2.5), 1 + 0.15 * np.exp(-max(fs - 0.5, 0) * 4))
        kit.put(fr, cam, self.top, 540, 300, INK, smooth((t - self.t0 - 0.1) / 0.3))
        # 日本, brushed in
        for j, g in enumerate(self.g):
            fk = (t - self.t_n + 0.35 - 0.25 * j) / 0.45
            if fk > 0:
                hot = smooth((t - (self.t_sun if j == 0 else self.t_or)) / 0.3)
                col = INK * (1 - hot) + VERM * hot
                kit.put(fr, cam, g.at(fk, soft=0.05), 375 + 330 * j, 720, col, 1.0, 1 + 0.12 * np.exp(-fk * 3) + 0.08 * hot * np.exp(-max(t - (self.t_sun if j == 0 else self.t_or), 0) * 4))
        kit.put(fr, cam, self.furi, 540, 480, INDIGO, smooth((t - self.t_n) / 0.3))
        kit.put(fr, cam, self.rom, 540, 995, GREY, smooth((t - self.t_n - 0.3) / 0.3))
        for x, lb, ts in ((375, self.sunl, self.t_sun), (705, self.orl, self.t_or)):
            f = smooth((t - ts) / 0.3)
            if f > 0:
                kit.put(fr, cam, kit.box(8, 120, 1.0), x, 878, VERM, f)
                kit.put(fr, cam, lb, x, 925 + 12 * (1 - f), VERM, f)
        return fr.img
