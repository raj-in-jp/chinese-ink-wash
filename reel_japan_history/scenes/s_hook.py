"""The hook.  "Sixteen thousand years of Japan, in two minutes.  Ready?  Go!"
Frame 1 is already the title: JAPAN'S ENTIRE / HISTORY (vermilion brush).  A year counter races from c. 14,000 BC to
2026 while the era names flash past behind it, faint and huge.  On "two minutes" a vermilion ensō stopwatch is
brushed round a big 2; on "Ready?" the counter rewinds to the start with a jolt; on "Go!" the camera punches in,
the stopwatch hand starts to sweep and a brushstroke races along the top: the timeline the whole reel travels on."""
import numpy as np

import kit
from art import enso
from engine import FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_HEAD, GREY, H, INK, VERM, W, Cam, StrokeSet, ease_in, ease_io, ease_out, lerp, noise, smooth, stroke, text_layer
from k6art import mist_hills
from engine import cached
from scenes.era import ERAS, RIB_X0, RIB_X1, RIB_Y, year_label
from scenes.kscene import SCREEN, KanjiScene
from timeline import ERA_KEYS, at

YEARS = [ERAS[k][3] for k in ERA_KEYS] + [2026]


class Scene(KanjiScene):
    paper_seed = 299
    paper_stains = 0.1

    def build(self):
        b = lambda s, n, seed: (lambda d: d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed)))(text_layer(s, FONT_BRUSH_EN, n)[0])
        self.l1, _ = text_layer("JAPAN'S ENTIRE", FONT_HEAD, 78)
        self.l2 = b('HISTORY', 200, 1)
        self.ghost = {k: text_layer(ERAS[k][0], FONT_BRUSH_JP, 330)[0] for k in ERA_KEYS}
        self.t_90 = at('two minutes')[0]
        self.t_ready = at('Ready')[0]
        self.t_go = at('Go')[0]
        self.n90 = b('2', 210, 3)
        self.sec, _ = text_layer('MINUTES', FONT_EN_BOLD, 34, tracking=10)
        ss = StrokeSet(W, H)
        enso(ss, 540, 1130, 215, 18, self.t_90 - 0.1, 0.55, seed=5, red=True)
        self.ring = ss
        hand = StrokeSet(40, 400)                            # pivot at the centre of the patch, the hand pointing up
        hand.add(stroke(40, 400, [(20, 200), (20, 30)], 9, ink=0.95, dry=0.3, profile=((0, 1), (0.85, 0.9), (1, 0.2)), seed=6), 0, 1)
        self.hand = hand.render(9)
        rb = StrokeSet(W, 260)
        rb.add(stroke(W, 260, [(RIB_X0 - 30, 130), (540, 126), (RIB_X1 + 30, 130)], 5, ink=0.6, dry=0.5,
                      profile=((0, 0.3), (0.1, 1), (0.9, 1), (1, 0.3)), seed=7), self.t_go, 0.45)
        self.rib = rb
        self.hills = cached('h7_hookhills_v1', lambda: mist_hills(1330, seed=17))['ink']
        self._years = {}
        self.t_hit = self.t_go

    def count(self, t):
        """the year on the counter: racing forward, rewinding on Ready?, held at the start on Go!"""
        if t < self.t_ready:
            u = ease_in(np.clip((t - 0.15) / 2.6, 0, 1))
            k = u * (len(YEARS) - 1)
            i = int(min(k, len(YEARS) - 2))
            return lerp(YEARS[i], YEARS[i + 1], k - i), i
        u = ease_out(np.clip((t - self.t_ready) / 0.5, 0, 1))
        return lerp(2026, YEARS[0], u), int((1 - u) * (len(YEARS) - 2))

    def year_patch(self, y):
        y = int(round(y))
        s = year_label(round(y / 1000) * 1000 if y < -2000 else round(y / 100) * 100 if y < 300 else y)
        if s not in self._years:
            self._years[s] = text_layer(s, FONT_HEAD, 96)[0]
        return self._years[s]

    def cam(self, t):
        punch = 0.06 * np.exp(-max(t - self.t_go, 0) * 5) * (t > self.t_go)
        q = t - self.t_ready
        jolt = 10 * np.exp(-q * 7) * np.sin(q * 50) * (q > 0)
        return Cam(540 + jolt, 960, 1.0 + 0.04 * smooth(t / 5) + punch)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        self.layer(fr, cam, self.hills, opacity=0.7)
        y, i = self.count(t)
        flash = 0.13 if t < self.t_ready + 0.5 else 0.13 * (1 - smooth((t - self.t_ready - 0.5) / 0.3))
        kit.put(fr, cam, self.ghost[ERA_KEYS[min(i, len(ERA_KEYS) - 1)]], 540, 790, INK, flash)
        kit.put(fr, cam, self.l1, 540, 335, INK, 1.0, 1.06 - 0.06 * ease_out(t / 0.5))
        kit.put(fr, cam, self.l2, 540, 480, VERM, 1.0, 1.1 - 0.1 * ease_out(t / 0.6), rot=-0.03)
        kit.put(fr, cam, self.year_patch(y), 540, 770, INK, 1.0, 1 + 0.1 * np.exp(-max(t - self.t_ready, 0) * 6) * (t > self.t_ready))
        # the stopwatch
        f9 = (t - self.t_90) / 0.3
        if f9 > 0:
            self.layer(fr, cam, self.ring.render(t, red=True), color=VERM, opacity=0.95)
            kit.put(fr, cam, self.n90, 540, 1110, INK, smooth(f9), 1 + 0.25 * np.exp(-f9 * 3))
            kit.put(fr, cam, self.sec, 540, 1215, GREY, smooth(f9 - 1))
            ang = 0.0 if t < self.t_go else (t - self.t_go) * 2.2
            kit.put(fr, cam, self.hand, 540, 1130, VERM, smooth(f9 - 0.5), rot=ang)
        if t > self.t_go - 0.05:
            kit.put(fr, SCREEN, self.rib.render(t), 540, RIB_Y, INK, 0.75)
        return fr.img
