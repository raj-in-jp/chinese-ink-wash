"""The payoff.  "But why mix all three?  Because Japanese has no spaces.  Write it all in hiragana, and it's a wall of
letters.  Mix the three, and every time the script changes, your eye sees a new word."
BUT WHY MIX ALL 3? at the top.  On "no spaces" NO SPACES! is stamped, with the English run together under it
(Idrinkcoffee).  On "write it all in hiragana" a wall of hiragana builds up row by row, the sentence itself in the
middle row (わたしはこーひーをのみます), the rest a blur of more kana: hard to read.  On "mix the three" the wall falls away
and the middle row turns back into 私はコーヒーを飲みます in its three colours; on "script changes" vermilion dividers drop
between the words, the line opens out, the English opens to "I drink coffee", and SCRIPT CHANGE = NEW WORD lands."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_ITALIC, GREY, INK, VERM, Cam, ease_io, ease_out, smooth, text_layer
from scenes.common import ORANGE, Sentence, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import at

SY = 960
ALL_HIRA = 'わたしはこーひーをのみます'
WALL = ['あさはぱんとたまごをたべます', 'ひるはともだちとがっこうでべ', 'んきょうしますよるはほんをよ',
        'わたしはこーひーをのみます', 'みますそしてはやくねますまい', 'にちにほんごをれんしゅうしま', 'すきょうもあしたもがんばりま']


class Scene(KanjiScene):
    paper_seed = 813

    def build(self):
        self.title = text_layer('BUT WHY MIX ALL 3?', FONT_BOLD, 120, tracking=3)[0]
        self.nosp = text_layer('NO SPACES!', FONT_BOLD, 150, tracking=4)[0]
        self.s = Sentence(88, 90)
        self.wall = [[glyph(c, 60) for c in row] for row in WALL]
        self.mid = [glyph(c, 70) for c in ALL_HIRA]
        self.allh = label('ALL HIRAGANA = A WALL OF LETTERS', 34, tracking=4)
        self.rule = text_layer('SCRIPT CHANGE = NEW WORD', FONT_BOLD, 84, tracking=3)[0]
        self.run = label('Idrinkcoffee', 64, FONT_EN_ITALIC, 1)
        self.sp = label('I drink coffee', 64, FONT_EN_ITALIC, 1)
        self.q = text_layer('?!', FONT_BOLD, 160)[0]
        self.t_q = at('But why mix')[0]
        self.t_ns = at('no spaces')[0]
        self.t_wall = at('Write it all')[0]
        self.t_mix = at('Mix the three')[0]
        self.t_ch = at('script changes')[0]
        self.t_new = at('new word')[0]
        self.t_hit = self.t_ch

    def cam(self, t):
        q = t - self.t_ns
        shake = 7 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.03 * smooth((t - self.t0) / 14))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        legend(fr, t, self.t0 - 1, active=None)
        ft = (t - self.t_q + 0.1) / 0.3
        kit.put(fr, cam, self.title, 540, 300, INK, smooth(ft), 1 + 0.2 * np.exp(-max(ft, 0) * 3))
        # NO SPACES!  and the English run together
        fn = (t - self.t_ns + 0.05) / 0.15
        out = smooth((t - self.t_mix + 0.3) / 0.4)
        if fn > 0:
            kit.put(fr, cam, self.nosp, 540, 470, VERM, smooth(fn) * (1 - out), 1 + 0.6 * np.exp(-fn * 2.5), rot=-0.04)
        # the wall of hiragana, row by row
        wall_in = (t - self.t_wall + 0.1)
        mix = ease_io((t - self.t_mix) / 0.7)
        if wall_in > 0 and mix < 1:
            for r, row in enumerate(self.wall):
                if r == 3:
                    continue
                f = smooth((wall_in - 0.12 * abs(r - 3)) / 0.3)
                y = SY + (r - 3) * 92
                drop = 500 * mix * (1 if r > 3 else -1) * (0.6 + 0.15 * abs(r - 3))
                for i, g in enumerate(row):
                    x = 540 + (i - (len(row) - 1) / 2) * 66 + 3 * np.sin(t * 7 + i + r)
                    kit.put(fr, cam, g, x, y + drop, ORANGE, 0.55 * f * (1 - mix))
            # the middle row: the sentence, all in hiragana
            for i, g in enumerate(self.mid):
                x = 540 + (i - (len(self.mid) - 1) / 2) * 74
                kit.put(fr, cam, g, x, SY, ORANGE, smooth(wall_in / 0.3) * (1 - mix))
            fq = smooth((t - self.t_wall - 1.0) / 0.3) * (1 - mix)
            kit.put(fr, cam, self.q, 945, 470, VERM, fq, 1 + 0.3 * np.exp(-max(t - self.t_wall - 1.0, 0) * 4), rot=0.15)
            self.plate(fr, cam, 540, SY + 380, 700, 50, smooth((t - self.t_wall - 0.6) / 0.3) * (1 - mix))
            kit.put(fr, cam, self.allh, 540, SY + 380, VERM, smooth((t - self.t_wall - 0.6) / 0.3) * (1 - mix))
        # mixed again: the three scripts, dividers, the line opening out
        if mix > 0:
            gap = 34 * ease_io((t - self.t_ch) / 0.8)
            div = smooth((t - self.t_ch) / 0.9)
            sc = 1 - 0.15 * smooth((t - self.t_ch) / 0.8)
            self.s.draw(fr, cam, 540, SY, t, lit={'K': mix, 'H': mix, 'T': mix}, gap=gap, div=div, op=mix,
                        scale=sc * (1 + 0.15 * (1 - mix)), pulse=('K', self.t_mix + 0.3))
            fr_ = smooth((t - self.t_new + 0.1) / 0.4)
            if fr_ > 0:
                kit.put(fr, cam, self.rule, 540, SY + 200, VERM, fr_, 1 + 0.3 * np.exp(-fr_ * 3))
        # the English, run together then opened up
        if fn > 0:
            sw = smooth((t - self.t_ch - 0.2) / 0.5)
            yy = 600 if mix < 0.5 else 1300
            o = smooth(fn - 1)
            if mix < 0.5:
                kit.put(fr, cam, self.run, 540, 600, GREY, o * (1 - smooth((t - self.t_wall) / 0.3)))
            kit.put(fr, cam, self.run, 540, 1330, GREY, mix * (1 - sw))
            kit.put(fr, cam, self.sp, 540, 1330, INK, mix * sw, 1 + 0.15 * np.exp(-max(t - self.t_ch - 0.2, 0) * 5) * (sw > 0))
        return fr.img
