"""The fix: hiragana.  "The fix?  Scribes wrote kanji faster and faster, in flowing cursive, until the shapes softened.
An, became a.  That's hiragana.  And it writes the grammar, and the word endings."
THE FIX at the top.  安 stands big in the centre; as Raj says "faster and faster" the brush speeds up (speed lines);
on "cursive" it melts into its flowing cursive form, on "softened" into あ.  On "an" the three stages line up:
安 an → cursive → あ a, with arrows; on "hiragana" HIRAGANA ひらがな comes in orange; on "grammar … word endings"
the three verbs from the last scene come back with their endings now written in orange hiragana: 食べる 食べた 食べない."""
import numpy as np

import kit
from engine import FONT_BRUSH_JP, FONT_EN_BOLD, FONT_EN_ITALIC, FONT_HEAD, FONT_JP, GREY, INK, VERM, Cam, ease_io, smooth, text_layer
from scenes.common import BLUE, ORANGE, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import JA, at

SX = (220, 540, 860)


class Scene(KanjiScene):
    paper_seed = 804

    def build(self):
        self.title = text_layer('THE FIX', FONT_HEAD, 66)[0]
        self.a_m = glyph('安', 330)                         # the kanji, as printed
        self.a_c = glyph('安', 330, FONT_BRUSH_JP)          # written fast, in flowing brush
        self.a_h = glyph('あ', 330, FONT_BRUSH_JP)          # softened into hiragana
        self.a_hm = glyph('あ', 300)
        self.lab = [label('an', 44, FONT_EN_ITALIC, 1), label('written fast', 40, FONT_EN_ITALIC, 1), label('a', 44, FONT_EN_ITALIC, 1)]
        self.arrow = text_layer('→', FONT_EN_BOLD, 70)[0]
        self.hl = label('HIRAGANA', 60, tracking=12)
        self.hk = glyph('ひらがな', 64)
        self.gl = label('GRAMMAR & WORD ENDINGS', 34)
        self.verbs = [(glyph('食', 84), [glyph(c, 84) for c in e]) for e in ('べる', 'べた', 'べない')]
        self.t_fast = at('faster and')[0]
        self.t_cur = at('cursive')[0]
        self.t_soft = at('softened')[0]
        self.t_an, self.t_a = JA['an']['start'], JA['a']['start']
        self.t_hira = JA['hiragana2']['start']
        self.t_gram = at('grammar', after=self.t0)[0]
        self.t_hit = self.t_hira

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 12))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        legend(fr, t, self.t0 - 1, active='H' if t > self.t_hira else 'K')
        kit.put(fr, cam, self.title, 540, 300, VERM, smooth((t - self.t0 - 0.1) / 0.35))
        # the morph in the centre: 安 -> cursive 安 -> あ
        lineup = ease_io((t - self.t_an + 0.1) / 0.6)
        mc = smooth((t - self.t_cur) / 0.6)
        ms = smooth((t - self.t_soft) / 0.6)
        if lineup < 1:
            y = 690
            o = smooth((t - self.t0 - 0.2) / 0.4) * (1 - lineup)
            wob = 4 * np.sin(t * 30) * smooth((t - self.t_fast) / 0.3) * (1 - ms)
            kit.put(fr, cam, self.a_m, 540 + wob, y, INK, o * (1 - mc))
            kit.put(fr, cam, self.a_c, 540 + wob, y, INK, o * mc * (1 - ms), 1 + 0.04 * np.sin(t * 9) * (1 - ms))
            kit.put(fr, cam, self.a_h, 540, y, ORANGE, o * ms, 1 + 0.15 * np.exp(-max(t - self.t_soft - 0.4, 0) * 4) * (ms > 0.5))
            # speed lines while the brush hurries
            sp = smooth((t - self.t_fast) / 0.3) * (1 - smooth((t - self.t_soft) / 0.4))
            if sp > 0:
                for j in range(5):
                    u = ((t * 2.2 + j / 5) % 1)
                    kit.put(fr, cam, kit.box(5, 160, 1.5), 230 + 620 * u, 520 + 80 * j, GREY, 0.35 * sp * np.sin(np.pi * u))
        # the line-up: 安 an → cursive → あ a
        if lineup > 0:
            y = 690
            for j, (g, col) in enumerate(((self.a_m, BLUE), (self.a_c, INK), (self.a_h, ORANGE))):
                x = 540 + (SX[j] - 540) * lineup
                kit.put(fr, cam, g, x, y, col, lineup if j != 2 else 1.0, 0.62 + 0.38 * (1 - lineup))
                lt = (self.t_an, self.t_an + 0.4, self.t_a)[j]
                kit.put(fr, cam, self.lab[j], SX[j], y + 150, GREY if j == 1 else col, smooth((t - lt) / 0.3))
            for j in range(2):
                kit.put(fr, cam, self.arrow, (SX[j] + SX[j + 1]) / 2, y, VERM, smooth((t - self.t_an - 0.2 - 0.3 * j) / 0.3))
        # HIRAGANA ひらがな
        fh = (t - self.t_hira + 0.1) / 0.35
        if fh > 0:
            o = smooth(fh)
            kit.put(fr, cam, self.hl, 540, 955, ORANGE, o, 1 + 0.2 * np.exp(-fh * 3))
            kit.put(fr, cam, self.hk, 540, 1040, ORANGE, smooth(fh - 0.6))
        # the verbs come back, their endings in hiragana
        fg = (t - self.t_gram + 0.1) / 0.35
        if fg > 0:
            self.plate(fr, cam, 540, 1230, 940, 230, smooth(fg))
            x = 120
            for j, (k, ends) in enumerate(self.verbs):
                o = smooth(fg - 0.4 * j)
                w = 84 * (1 + len(ends))
                kit.put(fr, cam, k, x + 42, 1200, BLUE, o)
                for i, g in enumerate(ends):
                    kit.put(fr, cam, g, x + 42 + 84 * (i + 1), 1200, ORANGE, o, 1 + 0.2 * np.exp(-max(fg - 0.4 * j, 0) * 4))
                x += w + 40
            kit.put(fr, cam, self.gl, 540, 1310, ORANGE, smooth(fg - 1.6))
        return fr.img
