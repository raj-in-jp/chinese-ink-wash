"""The hook.  "Japanese uses three alphabets... in one sentence.  Why?!  Look at this.  私はコーヒーを飲みます。  'I drink
coffee.'  This part is kanji.  This is hiragana.  And this, is katakana.  Three scripts, in one sentence."
Frame 1 already shows the claim and the sentence: JAPANESE USES / 3 ALPHABETS / IN 1 SENTENCE over 私はコーヒーを飲みます,
whose three scripts flash blue, orange and green one after another; WHY?! is stamped under it.  Then the colour drains,
the reading and the meaning come in, and each script lights up again as Raj names it, with its name bracketed under it."""
import numpy as np

import kit
from engine import FONT_BRUSH_EN, FONT_EN_ITALIC, FONT_HEAD, GREY, INK, VERM, Cam, ease_out, noise, smooth, text_layer
from scenes.common import COL, NAME, Sentence, glyph, label
from scenes.kscene import KanjiScene
from timeline import JA, at

SY = 860


class Scene(KanjiScene):
    paper_seed = 801
    paper_stains = 0.08

    def build(self):
        b = lambda s, n, seed: (lambda d: d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed)))(text_layer(s, FONT_BRUSH_EN, n)[0])
        self.l1 = text_layer('JAPANESE USES', FONT_HEAD, 58)[0]
        self.l2 = b('3 ALPHABETS', 124, 1)
        self.l3 = text_layer('IN 1 SENTENCE', FONT_HEAD, 58)[0]
        self.why = b('WHY?!', 170, 2)
        self.s = Sentence(88, 90)
        self.rom = label('watashi wa kōhī o nomimasu', 48, FONT_EN_ITALIC, 1)
        self.en = label('“I DRINK COFFEE.”', 40, tracking=6)
        self.three = label('3 SCRIPTS · 1 SENTENCE', 40, tracking=8)
        self.t_why = at('Why')[0]
        self.t_look = at('Look at')[0]
        self.t_sent = JA['sentence']['start']
        self.t_en = at('I drink')[0]
        self.t_k, self.t_h, self.t_t = JA['kanji']['start'], JA['hiragana']['start'], JA['katakana']['start']
        self.t_three = at('Three scripts')[0]
        self.t_hit = self.t_why

    def cam(self, t):
        q = t - self.t_why
        kick = 0.035 * np.exp(-max(q, 0) * 5) * (q > 0)
        return Cam(540, 960, 1.0 + 0.025 * smooth(t / 18) + kick)

    def lit(self, t):
        """colour per script: a quick flash round all three in the first seconds, drained on 'Look at this', then lit
        one by one as Raj names them"""
        if t < self.t_look:
            out = {}
            for j, s in enumerate('KHT'):
                out[s] = smooth((t - 0.2 - 0.45 * j) / 0.2)
            return out
        drain = 1 - smooth((t - self.t_look) / 0.3)
        return {s: max(drain, smooth((t - ts + 0.1) / 0.25)) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t))}

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # the claim at the top: big at first, then it steps back to make room
        up = smooth((t - self.t_look) / 0.5)
        y0, sc = 300 - 60 * up, 1.0 - 0.25 * up
        kit.put(fr, cam, self.l1, 540, y0, INK, 1.0, sc * (1.04 - 0.04 * ease_out(t / 0.4)))
        kit.put(fr, cam, self.l2, 540, y0 + 125 * sc, VERM, 1.0, sc * (1.1 - 0.1 * ease_out(t / 0.5)), rot=-0.03)
        kit.put(fr, cam, self.l3, 540, y0 + 250 * sc, INK, 1.0, sc)
        lit = self.lit(t)
        last = max(((s, ts) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t)) if t > ts), key=lambda x: x[1], default=None)
        if t < self.t_look:
            j = int(np.clip((t - 0.2) / 0.45, 0, 2))
            last = ('KHT'[j], 0.2 + 0.45 * j)
        xs = self.s.draw(fr, cam, 540, SY, t, lit=lit, pulse=last, scale=1.0 + 0.04 * smooth((t - self.t_sent) / 0.4) * (1 - smooth((t - self.t_k) / 0.4)))
        # the brackets and names, once Raj names each script
        am = {s: smooth((t - ts) / 0.3) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t))}
        self.s.brackets(fr, cam, 540, SY, xs, am, texts={})
        # the three names, one tag each, as Raj says them
        for j, (s_, ch) in enumerate((('K', '漢'), ('H', 'あ'), ('T', 'ア'))):
            u = am[s_]
            if u > 0:
                x, y = 200 + 340 * j, 1060
                lb = label(NAME[s_], 34)
                w = 70 + 16 + lb.shape[1]
                kit.put(fr, cam, glyph(ch, 70), x - w / 2 + 35, y + 12 * (1 - u), COL[s_], u, 1 + 0.3 * np.exp(-u * 4))
                kit.put(fr, cam, lb, x - w / 2 + 86 + lb.shape[1] / 2, y + 12 * (1 - u), COL[s_], u)
        # WHY?! stamped under the sentence, gone when we start reading it
        fw = (t - self.t_why + 0.05) / 0.15
        if fw > 0:
            o = smooth(fw) * (1 - smooth((t - self.t_look) / 0.3))
            kit.put(fr, cam, self.why, 540, 1150, VERM, o, 1 + 0.5 * np.exp(-fw * 2.5), rot=-0.06)
        # the reading and the meaning
        fr_ = smooth((t - self.t_sent) / 0.35) * (1 - smooth((t - self.t_k + 0.2) / 0.3))
        kit.put(fr, cam, self.rom, 540, SY + 95, GREY, fr_)
        kit.put(fr, cam, self.en, 540, SY + 150, INK, smooth((t - self.t_en) / 0.3) * (1 - smooth((t - self.t_k + 0.2) / 0.3)))
        # 3 SCRIPTS · 1 SENTENCE
        f3 = smooth((t - self.t_three) / 0.35)
        if f3 > 0:
            self.plate(fr, cam, 540, 1200, 640, 80, f3)
            kit.put(fr, cam, self.three, 540, 1200, VERM, f3, 1 + 0.15 * np.exp(-max(t - self.t_three, 0) * 5))
        return fr.img
