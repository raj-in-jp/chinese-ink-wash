"""The hook.  "From clay pots... to bullet trains.  Here's sixteen thousand years of Japan, in two minutes.  Let's go!"
Frame 1 is already the picture: a cord-marked Jōmon pot on the paper, FROM CLAY POTS... over it and the year
c. 14,000 BC.  On "bullet trains" a shinkansen blasts in from the right and races across, wiping the pot away behind
it: Fuji and the viaduct of modern Japan are revealed in its wake while the year counter flies to 2026 and
...TO BULLET TRAINS slams in.  On "Here's sixteen thousand years" the title JAPAN'S ENTIRE HISTORY is brushed in, on
"two minutes" a vermilion ensō stopwatch with 2 MINUTES, and on "Let's go!" the counter rewinds to the start, the
camera punches in and a brushstroke races along the top: the timeline the reel travels on."""
import numpy as np

import hart
import kit
from art import enso
from engine import (FONT_BRUSH_EN, FONT_EN_BOLD, FONT_HEAD, GREY, H, INK, VERM, W, Cam, StrokeSet, cached, ease_in, ease_io,
                    ease_out, lerp, noise, smooth, stroke, text_layer)
from k6art import mist_hills
from scenes.era import BLUE, RIB_X0, RIB_X1, RIB_Y, year_label
from scenes.kscene import SCREEN, KanjiScene
from timeline import at


class Scene(KanjiScene):
    paper_seed = 299
    paper_stains = 0.1

    def build(self):
        b = lambda s, n, seed: (lambda d: d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed)))(text_layer(s, FONT_BRUSH_EN, n)[0])
        self.hills = cached('h7_hookhills_v1', lambda: mist_hills(1330, seed=17))['ink']
        self.pot = cached('h7_jomon_v1', hart.jomon)
        self.now = cached('h7_showa_v1', hart.showa)
        self.bt = cached('h7_bullet_v1', lambda: dict(zip(('ink', 'blue'), hart.bullet_train())))
        self.from_, _ = text_layer('FROM CLAY POTS...', FONT_HEAD, 66)
        self.to_ = b('...to bullet trains!', 120, 4)
        self.l1, _ = text_layer("JAPAN'S ENTIRE", FONT_HEAD, 78)
        self.l2 = b('HISTORY', 200, 1)
        self.n2 = b('2', 150, 3)
        self.mins, _ = text_layer('MINUTES', FONT_EN_BOLD, 28, tracking=8)
        self.t_bt = at('bullet trains')[0] - 0.15
        self.t_here = at('sixteen thousand')[0] - 0.2
        self.t_two = at('two minutes')[0]
        self.t_go = at('go')[0]
        ss = StrokeSet(W, H)
        enso(ss, 540, 1185, 130, 14, self.t_two - 0.1, 0.5, seed=5, red=True)
        self.ring = ss
        rb = StrokeSet(W, 260)
        rb.add(stroke(W, 260, [(RIB_X0 - 30, 130), (540, 126), (RIB_X1 + 30, 130)], 5, ink=0.6, dry=0.5,
                      profile=((0, 0.3), (0.1, 1), (0.9, 1), (1, 0.3)), seed=7), self.t_go, 0.45)
        self.rib = rb
        self._years = {}
        self.t_hit = self.t_go

    def train_x(self, t):
        """the shinkansen's nose: in from the right edge, out past the left"""
        u = (t - self.t_bt) / 1.1
        return lerp(1700, -900, ease_in(np.clip(u, 0, 1)) * 0.35 + np.clip(u, 0, 1) * 0.65)

    def year(self, t):
        if t < self.t_go - 0.1:
            u = ease_io(np.clip((t - self.t_bt) / 1.1, 0, 1))
            y = lerp(-14000, 2026, u)
        else:
            y = lerp(2026, -14000, ease_out(np.clip((t - self.t_go + 0.1) / 0.5, 0, 1)))
        y = int(round(y))
        s = year_label(round(y / 1000) * 1000 if y < -2000 else round(y / 100) * 100 if y < 300 else y)
        if s not in self._years:
            self._years[s] = text_layer(s, FONT_HEAD, 84)[0]
        return self._years[s]

    def cam(self, t):
        punch = 0.06 * np.exp(-max(t - self.t_go, 0) * 5) * (t > self.t_go) + 0.03 * np.exp(-max(t - self.t_bt - 0.2, 0) * 4) * (t > self.t_bt + 0.2)
        q = t - self.t_bt - 0.2
        rumble = 6 * np.exp(-q * 3) * np.sin(q * 60) * (q > 0)
        return Cam(540 + rumble, 960, 1.0 + 0.04 * smooth(t / 7) + punch)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        self.layer(fr, cam, self.hills, opacity=0.55)
        # the past on the left of the train, the present on the right of it
        tx = self.train_x(t)
        xx = np.arange(W, dtype=np.float32)[None, :]
        past = np.clip((tx - 120 - xx) / 60, 0, 1)                 # ahead of the nose
        now = 1 - past
        fade = 1 - smooth((t - self.t_here) / 0.5) * 0.65          # the pictures step back under the title
        for c, col in (('ink', INK),):
            self.layer(fr, cam, self.pot[c] * past, 0, 60, opacity=0.95 * fade)
        if t > self.t_bt:
            self.layer(fr, cam, self.now['red'] * now, 0, 40, color=VERM, opacity=0.8 * fade)
            self.layer(fr, cam, self.now['ink'] * now, 0, 40, opacity=0.95 * fade)
        if -900 < tx < 1700 and t > self.t_bt:
            for j in range(5):                                       # speed lines behind it
                kit.put(fr, cam, kit.box(4, 260, 1.0), tx + 640 + 120 * j, 1150 + 18 * (j - 2), GREY, 0.5 * (1 - j / 5))
            kit.put(fr, cam, self.bt['blue'], tx + 430, 1215, BLUE, 1.0, -1.25, 1.25)
            kit.put(fr, cam, self.bt['ink'], tx + 430, 1215, INK, 1.0, -1.25, 1.25)
        # the words
        ff = 1 - smooth((t - self.t_here + 0.25) / 0.25)
        kit.put(fr, cam, self.from_, 540, 330, INK, ff)
        ft = (t - self.t_bt - 0.45) / 0.25
        if ft > 0:
            kit.put(fr, cam, self.to_, 540, 455, VERM, smooth(ft) * (1 - smooth((t - self.t_here + 0.25) / 0.25)), 1 + 0.25 * np.exp(-ft * 3), rot=-0.03)
        fh = smooth((t - self.t_here - 0.05) / 0.35)
        kit.put(fr, cam, self.l1, 540, 330 + 20 * (1 - fh), INK, fh)
        kit.put(fr, cam, self.l2, 540, 475, VERM, smooth((t - self.t_here - 0.25) / 0.35), 1.1 - 0.1 * fh, rot=-0.03)
        kit.put(fr, cam, self.year(t), 540, 650, INK, 1.0, 1 + 0.08 * np.exp(-max(t - self.t_go, 0) * 6) * (t > self.t_go))
        # the two-minute stopwatch
        f2 = (t - self.t_two) / 0.3
        if f2 > 0:
            self.plate(fr, cam, 540, 1185, 300, 300, smooth(f2) * 0.9)
            self.layer(fr, cam, self.ring.render(t, red=True), color=VERM, opacity=0.95)
            kit.put(fr, cam, self.n2, 540, 1165, INK, smooth(f2), 1 + 0.3 * np.exp(-f2 * 3))
            kit.put(fr, cam, self.mins, 540, 1245, GREY, smooth(f2 - 1))
        if t > self.t_go - 0.05:
            kit.put(fr, SCREEN, self.rib.render(t), 540, RIB_Y, INK, 0.75)
        return fr.img
