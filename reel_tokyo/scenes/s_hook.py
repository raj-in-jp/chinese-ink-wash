"""The hook.  "Tokyo is one of the biggest cities on Earth.  But a hundred and sixty years ago, there was no Tokyo!"
Frame 1: TOKYO 東京 slams in over a night skyline (windows twinkling, the tower in the middle).  On "a hundred and
sixty years ago" a year counter rewinds 2026 → 1866 while the skyline sinks into the ground and a marsh of reeds grows
up in its place; on "no Tokyo!" the title is slashed with a vermilion X and NO TOKYO?! is stamped."""
import numpy as np

import kit
from draw10 import reeds, skyline
from engine import FONT_BOLD, FONT_JP, INK, VERM, W, Cam, StrokeSet, cached, ease_io, ease_out, smooth, stroke, text_layer
from scenes.common10 import label
from scenes.kscene import KanjiScene
from timeline import JA, at

SCREEN = Cam(540, 960, 1.0)
LIGHT = np.array([0.90, 0.68, 0.22], np.float32)
DUSK = np.array([0.36, 0.40, 0.52], np.float32)


class Scene(KanjiScene):
    paper_seed = 1001

    def build(self):
        self.sky = cached('r10_skyline_v1', skyline)
        self.reeds = cached('r10_reeds_v1', lambda: {'d': reeds()})['d']
        self.tokyo = text_layer('TOKYO', FONT_BOLD, 240, tracking=8)[0]
        self.kanji = text_layer('東京', FONT_JP, 150)[0]
        self.big = label('ONE OF THE BIGGEST CITIES ON EARTH', 34)
        self.no = text_layer('NO TOKYO?!', FONT_BOLD, 170, tracking=4)[0]
        self.years = {}
        self.t_big = at('biggest')[0]
        self.t_back = at('hundred and sixty')[0]
        self.t_no = JA['tokyo2']['start']
        x = StrokeSet(W, 1920)
        x.add(stroke(W, 1920, [(220, 260), (540, 420), (860, 560)], 24, ink=0.95, dry=0.35,
                     profile=((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2)), seed=11), self.t_no - 0.1, 0.2)
        x.add(stroke(W, 1920, [(860, 260), (540, 420), (230, 560)], 24, ink=0.95, dry=0.35,
                     profile=((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2)), seed=12), self.t_no + 0.06, 0.2)
        self.slash = x
        self.t_hit = self.t_no

    def year(self, y):
        if y not in self.years:
            self.years[y] = text_layer(str(y), FONT_BOLD, 150, tracking=6)[0]
        return self.years[y]

    def cam(self, t):
        q = t - self.t_no
        shake = 10 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.04 * smooth(t / 7.5))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        back = ease_io((t - self.t_back) / 1.8)
        # dusk wash behind the city, fading with it
        sky = np.clip(np.linspace(0, 1, 1920) * 1.6 - 0.45, 0, 1)[:, None, None]
        fr.img *= 1 - 0.18 * (1 - back) * sky * (1 - DUSK)
        # the skyline sinks; the marsh grows in its place
        sink = 700 * back
        if back < 1:
            kit.put(fr, cam, self.sky['ink'], 540, 1350 + sink, INK, 0.95 * (1 - smooth((back - 0.7) / 0.3)))
            tw = 0.7 + 0.3 * np.sin(t * 7)
            kit.put(fr, cam, self.sky['lights'], 540, 1350 + sink, LIGHT, tw * (1 - back))
        if back > 0:
            kit.put(fr, cam, self.reeds, 540, 1490 + 200 * (1 - ease_out(back)), INK, 0.8 * smooth(back * 2))
        # the title
        sl = (t + 0.1) / 0.3
        kit.put(fr, cam, self.tokyo, 540, 360, VERM, smooth(sl * 2), 1 + 0.5 * np.exp(-max(sl, 0) * 3), rot=-0.02)
        kit.put(fr, cam, self.kanji, 540, 560, INK, smooth((t - 0.25) / 0.3))
        kit.put(fr, cam, self.big, 540, 690, INK, smooth((t - self.t_big) / 0.3) * (1 - smooth((t - self.t_back) / 0.3)))
        # the year rewinding
        if t > self.t_back - 0.1:
            y = int(round(2026 - 160 * back))
            kit.put(fr, cam, self.year(y), 540, 780, INK, smooth((t - self.t_back + 0.1) / 0.2), 1 + 0.06 * np.sin(t * 30) * (back < 1))
        if t > self.t_no - 0.15:
            kit.put(fr, cam, self.slash.render(t), 540, 960, VERM, 0.95)
            fn = (t - self.t_no - 0.35) / 0.18
            if fn > 0:
                kit.put(fr, cam, self.no, 540, 1000, VERM, smooth(fn), 1 + 0.5 * np.exp(-fn * 2.5), rot=-0.05)
        return fr.img
