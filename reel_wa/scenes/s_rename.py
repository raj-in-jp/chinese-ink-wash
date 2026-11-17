"""The new name.  "Japan wanted a better name.  So, around the year 700, Japanese envoys told China: we are not Wa anymore.
We are Nihon.  'The origin of the sun.'  Chinese records even say the Japanese disliked the old name, because it was
not elegant."
倭 is slashed with a brush X; AROUND 700; a Japanese envoy ship sails west across a strip of sea with a speech bubble
NOT 倭 ANYMORE!; 日本 is brushed in big with a red sun rising behind it, NIHON, and 日 = SUN · 本 = ORIGIN; then 日本
steps back and an old Chinese record unrolls with the real line 倭國自惡其名不雅 and its gloss, NOT ELEGANT! stamped."""
import numpy as np

import kit
from draw9 import junk, sun
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_EN_ITALIC, FONT_JP, GREY, INK, VERM, Cam, cached, ease_io, ease_out, smooth, text_layer
from glyphs import typeset
from scenes.common11 import SCROLL, brush_x, card, chip, label, mixed, vertical
from scenes.kscene import KanjiScene
from timeline import JA, at

SEA = np.array([0.42, 0.57, 0.59], np.float32)


class Scene(KanjiScene):
    paper_seed = 1103

    def build(self):
        self.wa = text_layer('倭', FONT_BRUSH_JP, 380)[0]
        self.t_better = at('better name')[0]
        self.t_700 = at('seven hundred')[0]
        self.t_env = at('envoys')[0]
        self.t_not = at('not')[0] if at('not')[0] > self.t0 else at('not', after=self.t0)[0]
        self.t_nihon = JA['nihon']['start']
        self.t_or = at('origin of')[0]
        self.t_rec = at('Chinese records')[0]
        self.t_dis = at('disliked')[0]
        self.t_el = at('elegant')[0]
        self.x = brush_x(540, 700, 230, self.t_better + 0.1, seed=31)
        self.y700 = text_layer('AROUND 700', FONT_BOLD, 110, tracking=4)[0]
        self.ship = cached('r9_junk_v1', junk)
        self.bubble = mixed([('NOT', 52, FONT_BOLD, 3), ('倭', 50, FONT_JP, 0), ('ANYMORE!', 52, FONT_BOLD, 3)], 12)
        self.g = [typeset(c, 300, font=FONT_BRUSH_JP, seed=1130 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('日本')]
        self.sun = sun(220)
        self.nih = label('NIHON', 64, FONT_BOLD, 14)
        self.sunl = mixed([('日', 56, FONT_JP, 0), ('= SUN', 60, FONT_BOLD, 3)])
        self.orl = mixed([('本', 56, FONT_JP, 0), ('= ORIGIN', 60, FONT_BOLD, 3)])
        self.quote = vertical('倭國自惡其名不雅', 66)
        self.gloss = label('“Wa disliked its own name: it was not elegant.”', 32, FONT_EN_ITALIC, 1)
        self.src = label('— OLD BOOK OF TANG, A CHINESE HISTORY', 24)
        self.ne = text_layer('NOT ELEGANT!', FONT_BOLD, 110, tracking=4)[0]
        self.t_hit = self.t_nihon

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 17))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        rec = ease_io((t - self.t_rec + 0.1) / 0.6)
        # 倭, slashed
        fw = 1 - smooth((t - self.t_nihon + 0.3) / 0.4)
        if fw > 0:
            kit.put(fr, cam, self.wa, 540, 700, INK, fw)
            if t > self.t_better:
                kit.put(fr, cam, self.x.render(t), 540, 960, VERM, 0.95 * fw)
        f7 = smooth((t - self.t_700) / 0.3) * (1 - smooth((t - self.t_nihon) / 0.3))
        if f7 > 0:
            chip(fr, cam, self.y700, 540, 320, f7, VERM, 1 + 0.2 * np.exp(-max(t - self.t_700, 0) * 5))
        # the envoy ship sailing west, with its message
        fs = smooth((t - self.t_env + 0.3) / 0.4) * (1 - smooth((t - self.t_nihon - 0.2) / 0.4))
        if fs > 0:
            band = np.zeros((1920, 1080), np.float32)
            band[1180:1330] = 1
            fr.ink(band * 0.25, SEA, fs)
            u = ease_io((t - self.t_env) / 3.0)
            x = 960 - 720 * u
            bob = 5 * np.sin(t * 5)
            for k, col in (('wash', np.array([0.80, 0.70, 0.60], np.float32)), ('ink', INK)):
                kit.put(fr, cam, self.ship[k], x, 1200 + bob, col, fs, -0.7, 0.7, rot=0.04 * np.sin(t * 2))
            fb = smooth((t - self.t_not + 0.1) / 0.3) * fs
            if fb > 0:
                bw = self.bubble.shape[1] + 60
                bx = min(max(x, bw / 2 + 30), 1050 - bw / 2)
                card(fr, cam, bx, 1090, bw, 96, fb, 1 + 0.15 * np.exp(-max(t - self.t_not, 0) * 6), rim=True)
                kit.put(fr, cam, self.bubble, bx, 1090, VERM, fb, 1 + 0.15 * np.exp(-max(t - self.t_not, 0) * 6))
        # 日本 with the rising sun
        fn = (t - self.t_nihon + 0.3) / 0.5
        if fn > 0:
            sc = 1 - 0.5 * rec
            y = 700 - 300 * rec
            ur = ease_out(min(fn, 1))
            kit.put(fr, cam, self.sun, 540, y + 80 - 80 * ur, VERM, 0.8 * smooth(fn), sc)
            for j, g in enumerate(self.g):
                kit.put(fr, cam, g.at(fn - 0.3 * j, soft=0.05), 540 + (j - 0.5) * 320 * sc, y, INK, 1.0, sc)
            kit.put(fr, cam, self.nih, 540, y + 225 * sc, GREY, smooth(fn - 0.8) * (1 - rec))
            fo = smooth((t - self.t_or) / 0.3) * (1 - rec)
            kit.put(fr, cam, self.sunl, 540, 1050, VERM, fo)
            kit.put(fr, cam, self.orl, 540, 1140, VERM, smooth((t - self.t_or - 0.4) / 0.3) * (1 - rec))
        # the old Chinese record
        if rec > 0:
            card(fr, cam, 540, 930, 360, 690, rec, color=SCROLL, rim=False)
            kit.put(fr, cam, self.quote, 540, 930, INK, rec)
            fd = smooth((t - self.t_dis) / 0.3)
            kit.put(fr, cam, self.gloss, 540, 1330, INK, fd)
            kit.put(fr, cam, self.src, 540, 1385, GREY, fd)
            fe = (t - self.t_el + 0.05) / 0.15
            if fe > 0:
                chip(fr, cam, self.ne, 540, 930, smooth(fe), VERM, 1 + 0.5 * np.exp(-fe * 2.5))
        return fr.img
