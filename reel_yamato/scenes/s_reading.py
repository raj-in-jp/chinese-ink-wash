"""Read the meaning.  "So you read the meaning, not the sound.  Japanese does this a lot.  Today is… きょう.  Adult is…
おとな."
READ THE MEANING, / NOT THE SOUND! (the second line stamped).  Two cards drop in side by side:
  今日: the kanji with their meanings 今 NOW + 日 DAY over a little red sun; on きょう the tiles き ょ う drop below;
  大人: 大 BIG + 人 PERSON over a small ink figure that grows tall; on おとな the tiles お と な drop below."""
import numpy as np

import kit
from draw13 import person, sun_icon
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_JP, GREY, INK, VERM, Cam, cached, ease_out, smooth, text_layer
from scenes.common12 import INDIGO, TEAL, GOLD, Tile, card, chip, drop_y, label, paint, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

XS = (290, 790)
CY = 900


class Scene(KanjiScene):
    paper_seed = 1304

    def build(self):
        self.h1 = text_layer('READ THE MEANING,', FONT_BOLD, 96, tracking=3)[0]
        self.h2 = text_layer('NOT THE SOUND!', FONT_BOLD, 120, tracking=3)[0]
        self.k = [[text_layer(c, FONT_JP, 130)[0] for c in w] for w in ('今日', '大人')]
        self.m = [[label(s, 30, FONT_EN_BOLD, 6) for s in w] for w in (('NOW', 'DAY'), ('BIG', 'PERSON'))]
        self.sun = cached('r13_sun_v1', lambda: dict(zip(('rgb', 'a'), sun_icon(60))))
        self.kid, self.adult = person(110), person(200)
        self.tiles = [[Tile(k, 104, c, romaji=r) for k, c, r in zip(kana, cols, roms)] for kana, cols, roms in
                      ((['き', 'ょ', 'う'], (VERM, VERM, VERM), ('ki', 'yo', 'u')), (['お', 'と', 'な'], (INDIGO, TEAL, GOLD), ('o', 'to', 'na')))]
        self.tiles[0] = [Tile('きょ', 104, VERM, romaji='kyo'), Tile('う', 104, VERM, romaji='u')]
        self.t_read = at('read the meaning')[0]
        self.t_not = at('not the sound')[0]
        self.t_card = [at('Today is')[0], at('Adult is')[0]]
        self.t_ja = [JA['kyo']['start'], JA['otona']['start']]
        self.t_hit = self.t_ja[0]

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 9))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.h1, 540, 260, INK, smooth((t - self.t_read + 0.1) / 0.3))
        fn = (t - self.t_not + 0.05) / 0.15
        if fn > 0:
            chip(fr, cam, self.h2, 540, 380, smooth(fn), VERM, 1 + 0.5 * np.exp(-fn * 2.5))
        for j, x in enumerate(XS):
            t0 = self.t_card[j] - 0.2
            f = (t - t0) / 0.35
            if f <= 0:
                continue
            y = CY + drop_y(t, t0, 200, 0.45)
            o = smooth(f)
            card(fr, cam, x, y, 440, 640, o, rim=True)
            for k in range(2):
                kit.put(fr, cam, self.k[j][k], x - 95 + 190 * k, y - 210, INK, o)
                kit.put(fr, cam, self.m[j][k], x - 95 + 190 * k, y - 110, VERM, o * smooth((t - t0 - 0.4) / 0.3))
            kit.put(fr, cam, label('+', 50, FONT_EN_BOLD, 0), x, y - 210, GREY, o)
            if j == 0:
                paint(fr, cam, self.sun['rgb'], self.sun['a'], x, y + 40 - 30 * ease_out(min(f, 1)), o, 1.0)
            else:
                g = smooth((t - self.t_ja[1]) / 0.6)
                kit.put(fr, cam, self.kid, x - 60, y + 60, INK, o * (1 - g))
                kit.put(fr, cam, self.adult, x - 60, y + 10, INK, o * g)
                kit.put(fr, cam, self.kid, x + 70, y + 60, INK, o * 0.5)
            row = self.tiles[j]
            xs = tile_row(['x'] * len(row), x, 104, 12)
            for k, (tl, tx) in enumerate(zip(row, xs)):
                tk = self.t_ja[j] + 0.15 * k
                if t > tk:
                    tl.draw(fr, cam, tx, y + 215 + drop_y(t, tk, 200, 0.4), smooth((t - tk) / 0.1), pulse(t, tk + 0.3, 0.2))
                    tl.draw_rom(fr, cam, tx, y + 305, smooth((t - tk - 0.25) / 0.2))
        return fr.img
