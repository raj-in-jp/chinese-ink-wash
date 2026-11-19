"""Today.  "You still hear it today.  The Japanese spirit… やまとだましい.  And… やまとなでしこ, named after a delicate pink
flower."
YOU STILL HEAR IT TODAY.  Left: 大和魂 brushed in over a flickering painted flame, YAMATO-DAMASHII · JAPANESE SPIRIT.
Right: 大和撫子 over a pink nadeshiko that opens petal by petal and sways, YAMATO NADESHIKO · A DELICATE PINK FLOWER."""
import numpy as np

import kit
from draw13 import flame, nadeshiko
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_EN_BOLD, GREY, INK, VERM, Cam, cached, ease_out, smooth, text_layer
from glyphs import typeset
from scenes.common12 import drop_y, label, paint, pulse
from scenes.kscene import KanjiScene
from timeline import JA, at


def _flame():
    rgb, a = flame()
    return {'rgb': rgb, 'a': a}


def _flower():
    petals, centre = nadeshiko()
    d = {}
    for k, (rgb, a) in enumerate(petals):
        d[f'p{k}rgb'], d[f'p{k}a'] = rgb, a
    d['crgb'], d['ca'] = centre
    return d


class Scene(KanjiScene):
    paper_seed = 1306

    def build(self):
        self.head = text_layer('YOU STILL HEAR IT TODAY', FONT_BOLD, 84, tracking=3)[0]
        self.fl = cached('r13_flame_v2', _flame)
        self.fw = cached('r13_flower_v1', _flower)
        self.k1 = [typeset(c, 130, font=FONT_BRUSH_JP, seed=1360 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('大和魂')]
        self.k2 = [typeset(c, 130, font=FONT_BRUSH_JP, seed=1370 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('大和撫子')]
        self.l1 = [label('YAMATO-DAMASHII', 40, FONT_BOLD, 6), label('THE JAPANESE SPIRIT', 30, FONT_EN_BOLD, 6)]
        self.l2 = [label('YAMATO NADESHIKO', 40, FONT_BOLD, 6), label('A DELICATE PINK FLOWER', 30, FONT_EN_BOLD, 6)]
        self.t_hear = at('still hear')[0]
        self.t_d = JA['damashii']['start']
        self.t_n = JA['nadeshiko']['start']
        self.t_hit = self.t_d

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 9))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.head, 540, 270, INK, smooth((t - self.t_hear + 0.1) / 0.3), pulse(t, self.t_hear, 0.12))
        # 大和魂 + flame (left)
        f = (t - self.t_d + 0.6) / 0.5
        if f > 0:
            fl = self.fl
            flick = 1 + 0.05 * np.sin(t * 13) + 0.03 * np.sin(t * 21)
            paint(fr, cam, fl['rgb'], fl['a'], 280, 900 - 30 * (flick - 1) * 10, smooth(f), 0.95 * flick, 0.03 * np.sin(t * 9))
            for j, g in enumerate(self.k1):
                kit.put(fr, cam, g.at((t - self.t_d + 0.2) / 0.5 - 0.35 * j, soft=0.05), 140 + 140 * j, 560, INK, 1.0)
            fl_ = smooth((t - self.t_d - 0.4) / 0.3)
            kit.put(fr, cam, self.l1[0], 280, 1180, VERM, fl_)
            kit.put(fr, cam, self.l1[1], 280, 1235, GREY, fl_)
        # 大和撫子 + nadeshiko opening (right)
        f2 = (t - self.t_n + 0.4) / 0.4
        if f2 > 0:
            fw = self.fw
            sway = 0.06 * np.sin(t * 1.8)
            for k in range(5):
                o = ease_out(np.clip((t - self.t_n + 0.2 - 0.12 * k) / 0.45, 0, 1))
                if o > 0:
                    paint(fr, cam, fw[f'p{k}rgb'], fw[f'p{k}a'], 800, 900, o, 0.95 * (0.4 + 0.6 * o), sway)
            paint(fr, cam, fw['crgb'], fw['ca'], 800, 900, smooth(f2), 0.95, sway)
            for j, g in enumerate(self.k2):
                kit.put(fr, cam, g.at((t - self.t_n + 0.1) / 0.45 - 0.3 * j, soft=0.05), 610 + 126 * j, 560, INK, 1.0, 0.92)
            fl_ = smooth((t - self.t_n - 0.4) / 0.3)
            kit.put(fr, cam, self.l2[0], 800, 1180, VERM, fl_)
            kit.put(fr, cam, self.l2[1], 800, 1235, GREY, fl_)
        return fr.img
