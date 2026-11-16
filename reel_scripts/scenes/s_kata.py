"""Katakana.  "Then Buddhist monks took just one piece of a kanji, like the left side of i, and made katakana.  Today, it
writes foreign words, like kōhī, coffee."
BUDDHIST MONKS' SHORTCUT at the top.  伊 stands big; on "left side" the right part fades back while the left part 亻
lights up green; on "i" it slides over and becomes イ: 伊 i → イ i.  On "katakana" KATAKANA カタカナ comes in green; on
"foreign words" a card: コーヒー, and on "kōhī" its reading and meaning: kōhī = coffee."""
import numpy as np

import kit
from engine import FONT_EN_BOLD, FONT_EN_ITALIC, FONT_HEAD, GREY, INK, VERM, Cam, ease_io, smooth, text_layer
from scenes.common import BLUE, GREEN, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import JA, at

Y = 700


class Scene(KanjiScene):
    paper_seed = 805

    def build(self):
        self.title = text_layer("BUDDHIST MONKS' SHORTCUT", FONT_HEAD, 54)[0]
        g = glyph('伊', 330)
        col = g.sum(0)
        w = g.shape[1]
        a, b = int(w * 0.25), int(w * 0.5)
        cut = a + int(np.argmin(col[a:b]))
        m = np.zeros_like(g)
        m[:, :cut] = 1
        self.left, self.right = g * m, g * (1 - m)
        self.cut_dx = cut / 2 - w / 2                     # centre of the left part, relative to the glyph centre
        self.ki = glyph('イ', 330)
        self.lab_i = [label('i', 48, FONT_EN_ITALIC, 1), label('i', 48, FONT_EN_ITALIC, 1)]
        self.piece = label('JUST ONE PIECE', 30)
        self.arrow = text_layer('→', FONT_EN_BOLD, 80)[0]
        self.kl = label('KATAKANA', 60, tracking=12)
        self.kk = glyph('カタカナ', 64)
        self.fw = label('FOREIGN WORDS', 34)
        self.coffee = glyph('コーヒー', 120)
        self.cg = label('kōhī = coffee', 50, FONT_EN_ITALIC, 1)
        self.t_m = at('Buddhist monks')[0]
        self.t_piece = at('one piece')[0]
        self.t_left = at('left side')[0]
        self.t_i = JA['i']['start']
        self.t_kata = JA['katakana2']['start']
        self.t_fw = at('foreign words', after=self.t0)[0]
        self.t_kohi = JA['kohi']['start']
        self.t_hit = self.t_kata

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 10))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        legend(fr, t, self.t0 - 1, active='T' if t > self.t_kata else 'K')
        kit.put(fr, cam, self.title, 540, 300, VERM, smooth((t - self.t_m + 0.1) / 0.35))
        fg = smooth((t - self.t_piece + 0.2) / 0.4)
        sl = smooth((t - self.t_left) / 0.4)                 # the left piece lights up
        mv = ease_io((t - self.t_i + 0.1) / 0.6)             # ...and becomes イ beside its kanji
        if fg > 0:
            x0 = 540 - 240 * mv                              # the kanji steps left
            kit.put(fr, cam, self.right, x0, Y, INK, fg * (1 - 0.8 * sl * (1 - mv)), 1 - 0.3 * mv)
            kit.put(fr, cam, self.left, x0, Y, BLUE if mv > 0 else GREEN if sl > 0.5 else INK, fg, 1 - 0.3 * mv)
            if 0 < sl and mv < 1:
                kit.put(fr, cam, self.piece, 540 + self.cut_dx, Y + 200, GREEN, sl * (1 - mv))
            # the piece flies over and turns into イ
            if mv > 0:
                px = (x0 + self.cut_dx * (1 - 0.3 * mv)) + (780 - (x0 + self.cut_dx)) * mv
                kit.put(fr, cam, self.left, px, Y, GREEN, 1 - smooth((mv - 0.4) / 0.4), 1 - 0.3 * mv)
                kit.put(fr, cam, self.ki, 780, Y, GREEN, smooth((mv - 0.4) / 0.5), 0.7 * (1 + 0.2 * np.exp(-max(mv - 0.8, 0) * 8)))
                kit.put(fr, cam, self.arrow, 540, Y, VERM, smooth((mv - 0.5) / 0.4))
                kit.put(fr, cam, self.lab_i[0], 300, Y + 150, BLUE, smooth((mv - 0.6) / 0.4))
                kit.put(fr, cam, self.lab_i[1], 780, Y + 150, GREEN, smooth((mv - 0.8) / 0.2))
        # KATAKANA カタカナ
        fk = (t - self.t_kata + 0.1) / 0.35
        if fk > 0:
            o = smooth(fk)
            kit.put(fr, cam, self.kl, 540, 955, GREEN, o, 1 + 0.2 * np.exp(-fk * 3))
            kit.put(fr, cam, self.kk, 540, 1040, GREEN, smooth(fk - 0.6))
        # foreign words: コーヒー
        fc = (t - self.t_fw + 0.1) / 0.35
        if fc > 0:
            o = smooth(fc)
            self.plate(fr, cam, 540, 1260, 700, 250, o)
            kit.put(fr, cam, self.fw, 540, 1165, GREY, o)
            kit.put(fr, cam, self.coffee, 540, 1255, GREEN, o, 1 + 0.15 * np.exp(-max(t - self.t_kohi, 0) * 5) * (t > self.t_kohi))
            kit.put(fr, cam, self.cg, 540, 1345, INK, smooth((t - self.t_kohi) / 0.3))
        return fr.img
