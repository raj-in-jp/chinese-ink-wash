"""The payoff.  "And here's the payoff.  Japanese has no spaces.  But kanji carries the meaning, hiragana the grammar,
and katakana the foreign words.  So every time the script changes, your eye sees where a word starts, and ends."
THE PAYOFF at the top; the sentence from the hook again, all in ink.  On "no spaces" NO SPACES is stamped and an
English line run together shows what that means: Idrinkcoffee.  Then each script lights up with its job bracketed
under it (MEANING / GRAMMAR / FOREIGN WORD); on "every time the script changes" vermilion dividers drop between the
words and the line opens out, and the English opens to "I drink coffee" with it: the colours do the job of spaces."""
import numpy as np

import kit
from engine import FONT_EN_ITALIC, FONT_HEAD, GREY, INK, VERM, Cam, ease_io, smooth, text_layer
from scenes.common import COL, Sentence, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import JA, at

SY = 780
JOBS = {'K': 'MEANING', 'H': 'GRAMMAR', 'T': 'FOREIGN WORD'}


class Scene(KanjiScene):
    paper_seed = 806

    def build(self):
        self.title = text_layer('THE PAYOFF', FONT_HEAD, 66)[0]
        self.s = Sentence(88, 90)
        self.nosp = label('NO SPACES', 44, tracking=10)
        self.run = label('Idrinkcoffee', 60, FONT_EN_ITALIC, 1)
        self.sp = label('I drink coffee', 60, FONT_EN_ITALIC, 1)
        self.rule = label('NEW SCRIPT  =  NEW WORD', 40, tracking=6)
        self.t_p = at('payoff')[0]
        self.t_ns = at('no spaces')[0]
        self.t_k, self.t_h, self.t_t = JA['kanji6']['start'], JA['hiragana3']['start'], JA['katakana3']['start']
        self.t_ch = at('script changes')[0]
        self.t_eye = at('your eye')[0]
        self.t_hit = self.t_ch

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 15))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        lit = {s: smooth((t - ts + 0.1) / 0.3) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t))}
        legend(fr, t, self.t0 - 1, active=None)
        kit.put(fr, cam, self.title, 540, 300, VERM, smooth((t - self.t_p + 0.1) / 0.35), 1 + 0.15 * np.exp(-max(t - self.t_p, 0) * 4))
        gap = 34 * ease_io((t - self.t_ch) / 0.8)
        div = smooth((t - self.t_ch) / 0.9)
        pulse = max(((s, ts) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t)) if t > ts), key=lambda x: x[1], default=None)
        xs = self.s.draw(fr, cam, 540, SY, t, lit=lit, gap=gap, div=div, op=smooth((t - self.t0 - 0.1) / 0.4), pulse=pulse,
                         scale=1 - 0.15 * smooth((t - self.t_ch) / 0.8))
        self.s.brackets(fr, cam, 540, SY, xs, lit, texts={}, scale=1 - 0.15 * smooth((t - self.t_ch) / 0.8))
        # what each script does, one tag each
        for j, (s_, ch) in enumerate((('K', '漢'), ('H', 'あ'), ('T', 'ア'))):
            u = lit[s_]
            if u > 0:
                lb = label(JOBS[s_], 30)
                x, y = 185 + 325 * j, 930
                w = 60 + 14 + lb.shape[1]
                kit.put(fr, cam, glyph(ch, 60), x - w / 2 + 30, y + 10 * (1 - u), COL[s_], u, 1 + 0.3 * np.exp(-u * 4))
                kit.put(fr, cam, lb, x - w / 2 + 74 + lb.shape[1] / 2, y + 10 * (1 - u), COL[s_], u)
        # NO SPACES, and what that would look like in English
        fn = (t - self.t_ns + 0.05) / 0.2
        if fn > 0:
            o = smooth(fn)
            self.plate(fr, cam, 540, 1130, 600, 220, o)
            kit.put(fr, cam, self.nosp, 540, 1075, VERM, o * (1 - smooth((t - self.t_ch) / 0.4)), 1 + 0.4 * np.exp(-fn * 2.5), rot=-0.03)
            kit.put(fr, cam, self.rule, 540, 1075, VERM, smooth((t - self.t_ch - 0.4) / 0.4))
            sw = smooth((t - self.t_ch - 0.2) / 0.5)
            kit.put(fr, cam, self.run, 540, 1170, GREY, smooth(fn - 1) * (1 - sw))
            kit.put(fr, cam, self.sp, 540, 1170, INK, sw)
        return fr.img
