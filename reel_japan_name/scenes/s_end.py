"""The ending.  "Which name do you like better?  Nihon, or Japan?  Tell me in the comments, and follow for more."  またね！
WHICH NAME DO YOU LIKE BETTER? at the top; two cards, 日本 NIHON (a red sun behind the kanji) and JAPAN, with a
vermilion VS between them, each card bouncing as Raj says its name; a ring swings between them while he asks; on
"comments" TELL ME IN THE COMMENTS ↓, on "follow" the black banner FOLLOW @raj_in_jp, and またね！ brushed in."""
import numpy as np

import kit
from draw9 import sun
from engine import FONT_BOLD, FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_JP, H, INK, VERM, W, Cam, StrokeSet, ease_io, noise, smooth, stroke, text_layer
from scenes.common9 import label
from scenes.kscene import KanjiScene
from timeline import JA, WORDS, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)
CARD = np.array([0.96, 0.93, 0.86], np.float32)
XS, CY, CW, CH = (285, 795), 800, 400, 440


class Scene(KanjiScene):
    paper_seed = 905

    def build(self):
        self.q = text_layer('WHICH NAME DO YOU', FONT_BOLD, 96, tracking=3)[0]
        self.q2 = text_layer('LIKE BETTER?', FONT_BOLD, 130, tracking=3)[0]
        self.box, self.rim = kit.box(CH, CW, 2.5), kit.rim(CH, CW, inset=6, t=3)
        self.sel = kit.rim(CH + 24, CW + 24, inset=4, t=8)
        self.nihon = text_layer('日本', FONT_JP, 150)[0]
        self.sun = sun(115)
        self.japan = text_layer('JAPAN', FONT_BOLD, 150, tracking=4)[0]
        self.lab = [label('NIHON', 40, FONT_EN_BOLD, 10), label('ENGLISH', 40, FONT_EN_BOLD, 10)]
        self.vs = text_layer('VS', FONT_BOLD, 110, tracking=2)[0]
        self.cm = label('TELL ME IN THE COMMENTS ↓', 40, FONT_EN_BOLD, 4)
        m = text_layer('またね！', FONT_BRUSH_JP, 110)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, FONT_EN_BOLD, 10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_q = at('Which name')[0]
        self.t_n = JA['nihon3']['start']
        self.t_j = next(w['start'] for w in WORDS if w['start'] > self.t_n and w['text'].startswith('Japan'))
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

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fq = smooth((t - self.t_q + 0.2) / 0.35)
        kit.put(fr, cam, self.q, 540, 290 + 15 * (1 - fq), INK, fq)
        kit.put(fr, cam, self.q2, 540, 420, VERM, smooth((t - self.t_q) / 0.35), 1 + 0.2 * np.exp(-max(t - self.t_q, 0) * 5))
        for j, ts in enumerate((self.t_n, self.t_j)):
            f = (t - self.t0 - 0.3 - 0.15 * j) / 0.35
            if f <= 0:
                continue
            o = smooth(f)
            dy = -30 * (1 - ease_io(min(f, 1)))
            q = t - ts
            bounce = 1 + 0.12 * np.exp(-max(q, 0) * 5) * np.cos(q * 18) * (q > 0)
            x = XS[j]
            kit.card(fr, cam, self.box, self.rim, x, CY + dy, o, color=CARD)
            if j == 0:
                kit.put(fr, cam, self.sun, x, CY - 40 + dy, VERM, 0.85 * o, bounce)
                kit.put(fr, cam, self.nihon, x, CY - 40 + dy, IVORY, o, bounce, over=True)
            else:
                kit.put(fr, cam, self.japan, x, CY - 40 + dy, INK, o, bounce)
            kit.put(fr, cam, self.lab[j], x, CY + 150 + dy, VERM, o)
        kit.put(fr, cam, self.vs, 540, CY, VERM, smooth((t - self.t0 - 0.6) / 0.3), 1 + 0.3 * np.exp(-max(t - self.t0 - 0.6, 0) * 4), rot=-0.08)
        u = (t - self.t_q - 0.6) / max(self.t_cm - self.t_q - 0.6, 0.5)
        if 0 < u < 1.1:
            j = int(8 * (1 - (1 - min(u, 1)) ** 2)) % 2
            kit.put(fr, cam, self.sel, XS[j], CY, VERM, 0.95 * (1 - smooth((u - 0.9) / 0.2)))
        kit.put(fr, cam, self.cm, 540, 1080, INK, smooth((t - self.t_cm + 0.1) / 0.3))
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 1185, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow + 0.05) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1324, IVORY, smooth((t - self.t_follow - 0.15) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1252, INK, smooth(fb))
        return fr.img
