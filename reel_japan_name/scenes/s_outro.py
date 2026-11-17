"""The whole chain.  "So 'Japan' is really 'Nihon', passed from mouth to mouth, halfway around the world."
JAPAN = 日本 at the top; the whole world chart, every route the name travelled drawn on it, a little paper chip at
each stop with the word it had there; under the chart the chain 日本 → JIH-PEN-KUO → CIPANGU → JAPANG → JAPÃO → JAPAN,
each word lighting up in turn (and its chip on the map bouncing) as Raj says "from mouth to mouth"."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_JP, GREY, INK, VERM, Cam, smooth, text_layer
from scenes.common9 import (PAPER, PLACES, R_CHINA, R_ENGLAND, R_PORTUGAL, R_SILK, MapCam, chart, draw_map, draw_route, label,
                            path_px)
from scenes.kscene import KanjiScene
from timeline import at
from worldmap import chart_xy

SCREEN = Cam(540, 960, 1.0)
CHAIN = [('日本', 'japan', True), ('JIH-PEN-KUO', 'beijing', False), ('CIPANGU', 'venice', False), ('JAPANG', 'malacca', False),
         ('JAPÃO', 'lisbon', False), ('JAPAN', 'london', False)]


class Scene(KanjiScene):
    paper_seed = 904

    def build(self):
        self.img = chart()
        self.cam_ = MapCam([(self.t0, 27.0, 22.0, 0.178), (self.t1, 27.0, 22.0, 0.18)], cy=900)
        self.paths = [path_px(r) for r in (R_CHINA, R_SILK, R_PORTUGAL, R_ENGLAND)]
        self.title = text_layer('JAPAN =', FONT_BOLD, 150, tracking=4)[0]
        self.title_j = text_layer('日本', FONT_JP, 140)[0]
        self.t_eq = at('is really')[0]
        self.t_m = at('mouth to')[0]
        self.chips = [label(w, 26, FONT_JP if jp else FONT_EN_BOLD, 0 if jp else 3) for w, _, jp in CHAIN]
        self.chain = [label(w, 44, FONT_JP if jp else FONT_EN_BOLD, 0 if jp else 3) for w, _, jp in CHAIN]
        self.arrow = label('→', 40, FONT_EN_BOLD, 0)
        self.t_hit = self.t_eq

    def render(self, t):
        fr = self.frame(SCREEN)
        M, z = self.cam_.matrix(t)
        draw_map(fr, self.img, M, smooth((t - self.t0) / 0.4))
        for P in self.paths:
            draw_route(fr, M, P, 1.0, width=6, dash=(12, 7))
        fe = smooth((t - self.t_eq) / 0.35)
        kit.put(fr, SCREEN, self.title, 400, 380, INK, fe)
        fj = smooth((t - self.t_eq - 0.35) / 0.3)
        kit.put(fr, SCREEN, self.title_j, 740, 375, VERM, fj, 1 + 0.35 * np.exp(-max(t - self.t_eq - 0.35, 0) * 4))
        # chips at each stop, and the chain under the map, lit in turn
        rows = [CHAIN[:3], CHAIN[3:]]
        for j, ((w, key, jp), chip, big) in enumerate(zip(CHAIN, self.chips, self.chain)):
            ts = self.t_m + 0.32 * j
            q = t - ts
            lit = smooth(q / 0.2)
            bounce = 1 + 0.4 * np.exp(-max(q, 0) * 6) * (q > 0)
            p = np.array(chart_xy(*PLACES[key])) * M[0, 0] + M[:, 2]
            dy = -42 if key in ('japan', 'beijing', 'london') else 42
            kit.put(fr, SCREEN, kit.box(chip.shape[0] + 14, chip.shape[1] + 22, 3), p[0], p[1] + dy, PAPER, 0.9 * smooth((t - self.t0 - 0.2) / 0.4), bounce, over=True)
            kit.put(fr, SCREEN, chip, p[0], p[1] + dy, VERM if lit > 0.5 else INK, smooth((t - self.t0 - 0.2) / 0.4), bounce)
            r, i = (0, j) if j < 3 else (1, j - 3)
            widths = [self.chain[k].shape[1] for k in (range(3) if r == 0 else range(3, 6))]
            tot = sum(widths) + 2 * 70
            x = 540 - tot / 2 + sum(widths[:i]) + 70 * i + widths[i] / 2
            y = 1270 + 90 * r
            kit.put(fr, SCREEN, big, x, y, VERM if lit > 0.5 else GREY, 0.35 + 0.65 * lit, bounce)
            if i < 2:
                kit.put(fr, SCREEN, self.arrow, x + widths[i] / 2 + 35, y, GREY, 0.8)
        return fr.img
