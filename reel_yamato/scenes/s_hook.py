"""The hook.  "Read this.  Big… harmony?  だいわ?  Nope.  It's read… やまと.  And not one sound matches the kanji!"
From frame 1 a brush writes 大和 huge across the page.  BIG and HARMONY tags pop under each kanji; on だいわ the sound
tags DAI and WA appear, and on "Nope" each is crossed with a red brush X; on やまと three tiles や ま と slam in under
both kanji with a bracket that spans them; 0 SOUNDS MATCH! is stamped with a jolt."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_PLAY, GREY, INK, VERM, Cam, smooth, text_layer
from glyphs import typeset
from scenes.common12 import GOLD, INDIGO, TEAL, Tile, brush_x, chip, drop_y, label, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

KX = (330, 750)
KY = 600


class Scene(KanjiScene):
    paper_seed = 1301

    def build(self):
        self.g = [typeset(c, 400, font=FONT_BRUSH_JP, seed=1310 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('大和')]
        self.read = label('READ THIS.', 44, FONT_EN_BOLD, 12)
        self.big, self.harm = text_layer('BIG', FONT_BOLD, 80, tracking=4)[0], text_layer('HARMONY', FONT_BOLD, 80, tracking=4)[0]
        self.dai, self.wa = text_layer('DAI', FONT_PLAY, 90)[0], text_layer('WA', FONT_PLAY, 90)[0]
        self.tiles = [Tile(k, 150, c, romaji=r) for k, c, r in zip('やまと', (VERM, INDIGO, TEAL), ('ya', 'ma', 'to'))]
        self.txs = tile_row('やまと', 540, 150, 20)
        self.zero = text_layer('0 SOUNDS MATCH!', FONT_BOLD, 120, tracking=4)[0]
        br = np.zeros((14, 780), np.float32)
        br[:, :8] = br[:, -8:] = 1
        br[:5] = 1
        self.bracket = br
        self.t_read = at('Read this')[0]
        self.t_big = at('Big')[0]
        self.t_harm = at('harmony')[0]
        self.t_dai = JA['daiwa']['start']
        self.t_nope = at('Nope')[0]
        self.t_ya = JA['yamato']['start']
        self.t_zero = at('not one sound')[0]
        self.xs = [brush_x(x, 1080, 80, self.t_nope + 0.05 + 0.2 * j, seed=21 + j, width=18) for j, x in enumerate(KX)]
        self.t_hit = self.t_ya

    def cam(self, t):
        q = t - self.t_zero
        shake = 12 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.04 * smooth(t / 9))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # 大和 brushed from the first frame
        for j, (g, x) in enumerate(zip(self.g, KX)):
            f = (t + 0.45 - 0.4 * j) / 0.9
            if f > 0:
                kit.put(fr, cam, g.at(f, soft=0.05), x, KY, INK, 1.0, pulse(t, self.t_ya, 0.08))
        fr_ = 1 - smooth((t - self.t_zero + 0.2) / 0.3)
        kit.put(fr, cam, self.read, 540, 300, GREY, fr_)
        # meaning tags
        for tag, x, t0 in ((self.big, KX[0], self.t_big), (self.harm, KX[1], self.t_harm)):
            f = (t - t0 + 0.05) / 0.2
            if f > 0:
                chip(fr, cam, tag, x, 880, smooth(f), VERM, 1 + 0.3 * np.exp(-f * 3))
        # the sound tags DAI / WA, crossed out
        for j, (tag, x) in enumerate(((self.dai, KX[0]), (self.wa, KX[1]))):
            t0 = self.t_dai + 0.3 * j
            if t > t0:
                kit.put(fr, cam, tag, x, 1080 + drop_y(t, t0, 160, 0.35), GREY * 0.7, smooth((t - t0) / 0.1))
            if t > self.t_nope:
                kit.put(fr, cam, self.xs[j].render(t), 540, 960, VERM, 0.95)
        # や ま と, spanning both kanji
        for k, (tl, x) in enumerate(zip(self.tiles, self.txs)):
            t0 = self.t_ya + 0.18 * k
            if t > t0:
                tl.draw(fr, cam, x, 1290 + drop_y(t, t0, 260, 0.4), smooth((t - t0) / 0.1), pulse(t, t0 + 0.3, 0.2))
                tl.draw_rom(fr, cam, x, 1410, smooth((t - t0 - 0.25) / 0.2))
        fb = smooth((t - self.t_ya - 0.5) / 0.3)
        kit.put(fr, cam, self.bracket, 540, 1180, VERM, 0.8 * fb, 0.4 + 0.6 * fb, 1.0)
        fz = (t - self.t_zero + 0.05) / 0.15
        if fz > 0:
            chip(fr, cam, self.zero, 540, 300, smooth(fz), VERM, 1 + 0.6 * np.exp(-fz * 2.5))
        return fr.img
