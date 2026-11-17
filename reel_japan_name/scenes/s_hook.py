"""The hook.  "Japanese people never call their country 'Japan'.  So where did that word come from?  It travelled ten
thousand kilometres to get here."
Frame 1: the sea chart close on Japan, JAPAN slammed over it in huge letters.  On "never call" a vermilion brush X
slashes through it and 日本 is stamped beside it; on "where did that word come from?" WHO NAMED IT? drops in; on
"travelled ten thousand kilometres" the camera flies out to the whole world while the route of the name snakes from
Japan through China, along the Silk Road to Venice, round Africa and up to London, a glowing dot racing ahead of it,
and a counter runs up to 10,000 KM."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_JP, INK, VERM, W, Cam, StrokeSet, ease_io, ease_out, noise, smooth, stroke, text_layer
from scenes.common9 import (GOLD, R_CHINA, R_ENGLAND, R_PORTUGAL, R_SILK, MapCam, chart, draw_map, draw_route, label, path_px,
                            route_at)
from scenes.kscene import KanjiScene
from timeline import at

SCREEN = Cam(540, 960, 1.0)


class Scene(KanjiScene):
    paper_seed = 901

    def build(self):
        self.img = chart()
        self.t_x = at('never call')[0]
        self.t_who = at('where did')[0]
        self.t_fly = at('travelled ten')[0]
        self.cam_ = MapCam([(0.0, 134.0, 36.5, 1.35), (self.t_fly - 0.2, 133.5, 37.0, 1.25), (self.t_fly + 1.6, 60.0, 22.0, 0.19),
                            (self.t1, 60.0, 22.0, 0.185)], cy=1060)
        self.japan = text_layer('JAPAN', FONT_BOLD, 250, tracking=6)[0]
        self.nihon = text_layer('日本', FONT_JP, 190)[0]
        b = lambda s, n, seed: (lambda d: d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed)))(text_layer(s, FONT_BOLD, n, tracking=4)[0])
        self.who = b('WHO NAMED IT?', 150, 2)
        self.km = {}
        self.isnt = text_layer("ISN'T JAPANESE", FONT_BOLD, 96, tracking=4)[0]
        x = StrokeSet(W, 1920)
        x.add(stroke(W, 1920, [(190, 540), (540, 760), (890, 960)], 26, ink=0.95, dry=0.35,
                     profile=((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2)), seed=11), self.t_x, 0.22)
        x.add(stroke(W, 1920, [(890, 560), (540, 760), (200, 950)], 26, ink=0.95, dry=0.35,
                     profile=((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2)), seed=12), self.t_x + 0.18, 0.22)
        self.slash = x
        self.routes = [path_px(r) for r in (R_CHINA, R_SILK, R_PORTUGAL[::-1], R_ENGLAND)]
        self.t_hit = self.t_x

    def kmpatch(self, n):
        s = f'{n:,} KM'
        if s not in self.km:
            self.km[s] = text_layer(s, FONT_BOLD, 120, tracking=4)[0]
        return self.km[s]

    def render(self, t):
        fr = self.frame(SCREEN)
        q = t - self.t_x
        shake = 10 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        M, z = self.cam_.matrix(t)
        M = M.copy()
        M[0, 2] += shake
        draw_map(fr, self.img, M, 1.0)
        # JAPAN, slammed in, then slashed
        out = smooth((t - self.t_fly) / 0.4)
        sl = (t + 0.1) / 0.3
        kit.put(fr, SCREEN, self.japan, 540 + shake, 760, INK, smooth(sl * 2) * (1 - out), 1 + 0.5 * np.exp(-max(sl, 0) * 3) * (sl < 2),
                rot=-0.03)
        if t > self.t_x - 0.02:
            kit.put(fr, SCREEN, self.slash.render(t), 540 + shake, 960, VERM, 0.95 * (1 - out))
            fn = (t - self.t_x - 0.45) / 0.2
            if fn > 0:
                kit.put(fr, SCREEN, kit.box(260, 420, 6), 540, 1080, np.array([0.97, 0.95, 0.89], np.float32), 0.9 * smooth(fn) * (1 - out),
                        over=True)
                kit.put(fr, SCREEN, self.nihon, 540, 1080, INK, smooth(fn) * (1 - out), 1 + 0.4 * np.exp(-fn * 2.5))
                kit.put(fr, SCREEN, self.isnt, 540, 1250, VERM, smooth(fn - 1.5) * (1 - out))
        # WHO NAMED IT?
        fw = (t - self.t_who + 0.05) / 0.25
        if fw > 0:
            kit.put(fr, SCREEN, self.who, 540, 420, VERM, smooth(fw), 1 + 0.4 * np.exp(-fw * 2.5), rot=-0.03)
        # the flight: the whole route of the name snakes round the world, the counter runs up
        u = ease_io((t - self.t_fly - 0.3) / 2.2)
        if u > 0:
            tot = [0.18, 0.45, 0.82, 1.0]
            prev = 0.0
            for P, e in zip(self.routes, tot):
                v = np.clip((u - prev) / (e - prev), 0, 1)
                tip = draw_route(fr, M, P, v, width=9, dash=(14, 8))
                if 0 < v < 1 and tip is not None:
                    kit.put(fr, SCREEN, kit.box(30, 30, 8), tip[0], tip[1], GOLD, 0.9)
                prev = e
            n = int(round(10000 * u / 100.0)) * 100
            kit.put(fr, SCREEN, self.kmpatch(n), 540, 1430, VERM, smooth(u * 4), 1 + 0.08 * np.sin(t * 14) * (u < 1))
        return fr.img
