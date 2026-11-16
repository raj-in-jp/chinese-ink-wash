"""The ending.  "So, which one did you learn first?  Hiragana, katakana, or kanji?  Tell me in the comments, and follow
for more."  またね！
WHICH ONE DID YOU / learn first? at the top; three washi cards: あ HIRAGANA, ア KATAKANA, 漢 KANJI, each in its colour,
each bouncing as Raj names it, with a vermilion ring running round them like a roulette while he asks; on "comments"
TELL ME IN THE COMMENTS ↓, on "follow" the black banner FOLLOW @raj_in_jp, and またね！ brushed as Raj says it."""
import numpy as np

import kit
from engine import FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_HEAD, H, INK, VERM, W, Cam, StrokeSet, ease_io, noise, smooth, stroke, text_layer
from scenes.common import COL, NAME, glyph, label
from scenes.kscene import KanjiScene
from timeline import JA, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)
CARD = np.array([0.96, 0.93, 0.86], np.float32)
CARDS = [('H', 'あ', 'hiragana4'), ('T', 'ア', 'katakana3'), ('K', '漢', 'kanji3')]
XS, CY, CW, CH = (215, 540, 865), 760, 270, 330


class Scene(KanjiScene):
    paper_seed = 807

    def build(self):
        self.q1 = text_layer('WHICH ONE DID YOU', FONT_HEAD, 64)[0]
        b = text_layer('learn first?', FONT_BRUSH_EN, 110)[0]
        self.q2 = b * (0.86 + 0.14 * noise(*b.shape, 6, 2, 2))
        self.box, self.rim = kit.box(CH, CW, 2.5), kit.rim(CH, CW, inset=6, t=3)
        self.sel = kit.rim(CH + 20, CW + 20, inset=4, t=7)
        self.big = [glyph(c, 170) for _, c, _ in CARDS]
        self.names = [label(NAME[s], 30) for s, _, _ in CARDS]
        self.cm = label('TELL ME IN THE COMMENTS ↓', 38, tracking=4)
        m = text_layer('またね！', FONT_BRUSH_JP, 110)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, tracking=10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_q = at('which one')[0]
        self.t_lf = at('learn first')[0]
        self.t_name = [JA[k]['start'] for _, _, k in CARDS]
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
        kit.put(fr, cam, self.q1, 540, 300 + 15 * (1 - fq), INK, fq)
        kit.put(fr, cam, self.q2, 540, 420, VERM, smooth((t - self.t_lf + 0.1) / 0.35), rot=-0.03)
        for j, (s, ch, _) in enumerate(CARDS):
            f = (t - self.t0 - 0.3 - 0.12 * j) / 0.35
            if f <= 0:
                continue
            o = smooth(f)
            dy = -30 * (1 - ease_io(min(f, 1)))
            q = t - self.t_name[j]
            bounce = 1 + 0.12 * np.exp(-max(q, 0) * 5) * np.cos(q * 18) * (q > 0)
            kit.card(fr, cam, self.box, self.rim, XS[j], CY + dy, o, color=CARD)
            kit.put(fr, cam, self.big[j], XS[j], CY - 30 + dy, COL[s], o, bounce)
            kit.put(fr, cam, self.names[j], XS[j], CY + 115 + dy, COL[s], o)
        # the roulette ring: round and round while Raj asks, slowing, gone by "comments"
        u = (t - self.t_lf) / max(self.t_cm - self.t_lf, 0.5)
        if 0 < u < 1.1:
            pos = 10 * (1 - (1 - min(u, 1)) ** 2)
            j = int(pos) % 3
            kit.put(fr, cam, self.sel, XS[j], CY, VERM, 0.95 * (1 - smooth((u - 0.9) / 0.2)))
        fc = smooth((t - self.t_cm + 0.1) / 0.3)
        kit.put(fr, cam, self.cm, 540, 1010, INK, fc)
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 1125, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow + 0.05) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1324, IVORY, smooth((t - self.t_follow - 0.15) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1252, INK, smooth(fb))
        return fr.img
