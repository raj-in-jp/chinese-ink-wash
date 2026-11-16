"""The problem.  "But there was a problem.  Chinese words never change their endings.  Japanese words do.  Taberu, eat.
Tabeta, ate.  Tabenai, don't eat.  Kanji alone couldn't write those endings."
THE PROBLEM at the top.  A small card: CHINESE · 吃 = eat / ate / don't eat, the same word every time (a lock).
Then JAPANESE: three rows brushed in as Raj says them, 食べる eat / 食べた ate / 食べない don't eat, the ending of each
boxed.  On "Kanji alone couldn't write those endings" the endings drain away into dashed vermilion boxes with a ?
in each: there was no kanji for them."""
import numpy as np

import kit
from engine import FONT_EN_ITALIC, FONT_HEAD, GREY, INK, VERM, Cam, ease_out, smooth, text_layer
from scenes.common import BLUE, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import JA, at

ROWS = [('taberu', 'べる', 'eat'), ('tabeta', 'べた', 'ate'), ('tabenai', 'べない', "don't eat")]
RY = [900, 1060, 1220]


def dashed_box(h, w, dash=14, gap=9, t=4):
    m = np.zeros((h, w), np.float32)
    for x in range(0, w, dash + gap):
        m[:t, x:x + dash] = 1
        m[-t:, x:x + dash] = 1
    for y in range(0, h, dash + gap):
        m[y:y + dash, :t] = 1
        m[y:y + dash, -t:] = 1
    return m


class Scene(KanjiScene):
    paper_seed = 803

    def build(self):
        self.title = text_layer('THE PROBLEM', FONT_HEAD, 66)[0]
        self.cn = label('CHINESE', 34, tracking=10)
        self.chi = glyph('吃', 110)
        self.cn_g = label('eat · ate · don’t eat', 46, FONT_EN_ITALIC, 1)
        self.cn_s = label('SAME WORD, NO ENDINGS', 32)
        self.jp = label('JAPANESE', 34, tracking=10)
        self.jp_s = label('THE ENDING CHANGES', 32)
        self.no = label('NO KANJI FOR THESE ENDINGS', 32)
        self.rows = [(glyph('食', 104), [glyph(c, 104) for c in end], label(en, 50, FONT_EN_ITALIC, 1), JA[k]['start'])
                     for k, end, en in ROWS]
        self.q = text_layer('?', FONT_HEAD, 84)[0]
        self.t_p = at('problem')[0]
        self.t_cn = at('Chinese words')[0]
        self.t_jp = at('Japanese words do')[0]
        self.t_no = JA['kanji3']['start']
        self.t_hit = self.t_no

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.025 * smooth((t - self.t0) / 14))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        legend(fr, t, self.t0 - 1, active='K')
        ft = smooth((t - self.t0 - 0.1) / 0.35)
        kit.put(fr, cam, self.title, 540, 300, VERM, ft, 1 + 0.1 * (1 - ease_out(min((t - self.t0) / 0.5, 1))))
        # CHINESE: one word, never changing
        fc = smooth((t - self.t_cn) / 0.35)
        if fc > 0:
            self.plate(fr, cam, 540, 540, 820, 190, fc)
            kit.put(fr, cam, self.cn, 300, 490, GREY, fc)
            kit.put(fr, cam, self.chi, 300, 575, BLUE, fc, 1 + 0.2 * np.exp(-max(t - self.t_cn, 0) * 5))
            kit.put(fr, cam, self.cn_g, 650, 515, INK, smooth((t - self.t_cn - 0.4) / 0.3))
            kit.put(fr, cam, self.cn_s, 650, 580, VERM, smooth((t - self.t_cn - 0.8) / 0.3))
        # JAPANESE: the three rows
        fj = smooth((t - self.t_jp) / 0.35)
        if fj > 0:
            kit.put(fr, cam, self.jp, 300, 770, GREY, fj)
            kit.put(fr, cam, self.jp_s, 700, 772, VERM, fj)
        gone = smooth((t - self.t_no - 0.1) / 0.5)
        for j, (k, ends, en, tj) in enumerate(self.rows):
            f = (t - tj + 0.1) / 0.3
            if f <= 0:
                continue
            o, y = smooth(f), RY[j]
            kit.put(fr, cam, k, 250, y + 14 * (1 - o), BLUE, o)
            x0 = 250 + 100
            w = 100 * len(ends)
            for i, g in enumerate(ends):
                kit.put(fr, cam, g, x0 + 50 + 100 * i, y + 14 * (1 - o), INK, o * (1 - gone))
            # the ending, boxed: solid while it is shown, dashed with a ? once kanji can't write it
            kit.put(fr, cam, kit.rim(126, w + 24, inset=4, t=3), x0 + w / 2, y, VERM, 0.6 * o * (1 - gone))
            if gone > 0:
                kit.put(fr, cam, dashed_box(126, w + 24), x0 + w / 2, y, VERM, 0.9 * gone)
                kit.put(fr, cam, self.q, x0 + w / 2, y, VERM, gone, 1 + 0.4 * np.exp(-gone * 4))
            kit.put(fr, cam, en, 850, y, INK, smooth(f - 0.8))
        if gone > 0:
            self.plate(fr, cam, 540, 1370, 620, 60, gone)
            kit.put(fr, cam, self.no, 540, 1370, VERM, gone)
        return fr.img
