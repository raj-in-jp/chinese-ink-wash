"""Paris.  "So why is Paris パリ?  Because Japan borrowed it from French, where the S is silent.  From English, it would
have been パリス."
The Eiffel Tower drawing itself up in ink on the right; PARIS in chunky letters; パ リ tiles drop under it; a tricolour
FROM FRENCH tag; on "the S" the S greys out and shrinks, SILENT under it; then FROM ENGLISH… with ghost tiles パ リ ス,
the ス pulsing."""
import numpy as np

import kit
from draw12 import eiffel
from engine import FONT_BOLD, FONT_EN_BOLD, GREY, INK, VERM, Cam, cached, ease_out, smooth, text_layer
from scenes.common12 import INDIGO, IVORY, PALETTE, Tile, Word, chip, drop_y, label, pulse
from scenes.kscene import KanjiScene
from timeline import JA, at

BLUE = np.array([0.0, 0.33, 0.64], np.float32)
RED = np.array([0.88, 0.16, 0.20], np.float32)
WX = 380


class Scene(KanjiScene):
    paper_seed = 1205

    def build(self):
        self.tower = cached('r12_eiffel_v1', lambda: {'d': eiffel()})['d']
        self.word = Word('PARIS', 170)
        self.pari = [Tile(k, 170, PALETTE[j], romaji=r) for j, (k, r) in enumerate(zip('パリ', ('pa', 'ri')))]
        self.french = label('FROM FRENCH', 40, FONT_EN_BOLD, 8)
        self.silent = label('SILENT', 40, FONT_EN_BOLD, 10)
        self.english = label('FROM ENGLISH IT WOULD BE…', 34, FONT_EN_BOLD, 6)
        self.parisu = [Tile(k, 120, INDIGO, romaji=r, hot=h) for k, r, h in zip('パリス', ('pa', 'ri', 'su'), ((), (), (0, 1)))]
        self.bar = np.ones((14, 90), np.float32)
        self.t_paris = at('Paris')[0]
        self.t_pari = JA['pari']['start']
        self.t_fr = at('French')[0]
        self.t_s = at('S', after=self.t_fr)[0]
        self.t_sil = at('silent')[0]
        self.t_en = at('From English')[0]
        self.t_parisu = JA['parisu']['start']
        self.t_hit = self.t_pari

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 9))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # the tower draws itself up from the ground
        g = ease_out(np.clip((t - self.t0 - 0.2) / 1.6, 0, 1))
        if g > 0:
            tw = self.tower.copy()
            h = tw.shape[0]
            tw[:int(h * (1 - g))] = 0
            kit.put(fr, cam, tw, 830, 1020, INK, 0.85, 0.85)
        # PARIS, the S going silent
        sil = smooth((t - self.t_s) / 0.4)
        fw = [smooth((t - self.t_paris + 0.15 - 0.05 * k) / 0.12) for k in range(5)]
        offs = [(0, drop_y(t, self.t_paris - 0.15 + 0.05 * k, 200, 0.4) + (40 * sil if k == 4 else 0)) for k in range(5)]
        cols = [INK] * 4 + [INK * (1 - sil) + np.array([0.72, 0.70, 0.66], np.float32) * sil]
        ops = fw[:4] + [fw[4] * (1 - 0.55 * sil)]
        self.word.draw(fr, cam, WX, 420, INK, 1.0, 1.0, offs, ops, cols)
        if t > self.t_sil - 0.2:
            sx = WX + self.word.xs[4] + 10
            kit.put(fr, cam, self.silent, sx, 560, GREY, smooth((t - self.t_sil + 0.2) / 0.25), pulse(t, self.t_sil, 0.25))
        # パ リ
        for k, tl in enumerate(self.pari):
            t0 = self.t_pari + 0.18 * k
            if t > t0:
                x = WX - 95 + 190 * k
                tl.draw(fr, cam, x, 760 + drop_y(t, t0, 260, 0.45), smooth((t - t0) / 0.1), pulse(t, t0 + 0.35, 0.15))
                tl.draw_rom(fr, cam, x, 885, smooth((t - t0 - 0.25) / 0.2))
        # FROM FRENCH (tricolour)
        ff = smooth((t - self.t_fr + 0.1) / 0.3)
        if ff > 0:
            for k, c in enumerate((BLUE, IVORY, RED)):
                kit.put(fr, cam, self.bar, WX - 90 + 90 * k, 975, c, ff, over=True)
            kit.put(fr, cam, self.french, WX, 1020, INK, ff, pulse(t, self.t_fr, 0.2))
        # from English it would be パリス
        fe = smooth((t - self.t_en + 0.1) / 0.3)
        if fe > 0:
            kit.put(fr, cam, self.english, WX, 1150, GREY, fe)
            for k, tl in enumerate(self.parisu):
                t0 = self.t_parisu + 0.15 * k
                if t > t0:
                    x = WX - 135 + 135 * k
                    s = pulse(t, t0 + 0.3, 0.15) * (1 + 0.08 * np.sin(t * 8) * (k == 2) * (t > t0 + 0.5))
                    tl.draw(fr, cam, x, 1270 + drop_y(t, t0, 200, 0.4), 0.85 * smooth((t - t0) / 0.1), s)
                    tl.draw_rom(fr, cam, x, 1360, smooth((t - t0 - 0.2) / 0.2))
        return fr.img
