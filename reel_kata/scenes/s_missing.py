"""Missing sounds.  "Some English sounds don't exist in Japanese at all.  There's no separate L and R.  Just one sound in
between.  So rice and lice are both ライス.  There's no 'th', so thank you becomes サンキュー.  And 'v' often becomes
'b'.  Violin is バイオリン."
SOUNDS JAPANESE DOESN'T HAVE; three chips fly in (L/R, TH, V), each stamped with a red cross.  Then four beats:
 1. L and R slide together and merge into one glowing ラ tile (ra ri ru re ro);
 2. a painted bowl of RICE and a little cartoon LICE side by side — both get the same ライス tiles, with an "=" between;
 3. a big TH slashed with a red brush X, THANK YOU snapping into サ ン キュ ー;
 4. V morphs into B, a painted violin swings in, バ イ オ リ ン drop below it."""
import cv2
import numpy as np

import kit
from draw12 import louse, rice_bowl, violin
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_PLAY, FONT_ROUND, GREY, INK, VERM, Cam, cached, ease_io, ease_out, smooth, text_layer
from scenes.common12 import brush_x
from scenes.common12 import GOLD, INDIGO, PALETTE, TEAL, Tile, Word, chip, drop_y, label, paint, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at


def _rgba(fn):
    def go():
        rgb, a = fn()
        return {'rgb': rgb, 'a': a}
    return go


class Scene(KanjiScene):
    paper_seed = 1204

    def build(self):
        self.h1 = text_layer('SOUNDS JAPANESE', FONT_BOLD, 100, tracking=4)[0]
        self.h2 = text_layer("DOESN'T HAVE", FONT_BOLD, 120, tracking=4)[0]
        self.chips = [text_layer(s, FONT_PLAY, 90)[0] for s in ('L / R', 'TH', 'V')]
        xm = np.zeros((120, 120), np.float32)
        cv2.line(xm, (12, 12), (108, 108), 1.0, 14, cv2.LINE_AA)
        cv2.line(xm, (108, 12), (12, 108), 1.0, 14, cv2.LINE_AA)
        self.xm = cv2.GaussianBlur(xm, (0, 0), 1.2)
        self.L = text_layer('L', FONT_PLAY, 300)[0]
        self.R = text_layer('R', FONT_PLAY, 300)[0]
        self.ra = Tile('ラ', 230, INDIGO)
        self.rarow = label('ra · ri · ru · re · ro', 46, FONT_ROUND, 2)
        self.rice = cached('r12_rice_v1', _rgba(rice_bowl))
        self.louse = cached('r12_louse_v1', _rgba(louse))
        self.lab_rice, self.lab_lice = text_layer('RICE', FONT_PLAY, 90)[0], text_layer('LICE', FONT_PLAY, 90)[0]
        self.raisu = [[Tile(k, 92, VERM) for k in 'ライス'], [Tile(k, 92, VERM) for k in 'ライス']]
        self.eq = text_layer('=', FONT_PLAY, 130)[0]
        self.TH = text_layer('TH', FONT_PLAY, 320)[0]
        self.thx = brush_x(540, 700, 230, 0, seed=41, width=30)
        self.thanks = Word('THANK YOU', 110)
        self.san = [Tile(k, 140, PALETTE[j], romaji=r) for j, (k, r) in enumerate(zip(['サ', 'ン', 'キュ', 'ー'], ['sa', 'n', 'kyu', 'u']))]
        self.sxs = tile_row('1234', 540, 140, 16)
        self.V = text_layer('V', FONT_PLAY, 300)[0]
        self.B = text_layer('B', FONT_PLAY, 300)[0]
        self.arrow = text_layer('→', FONT_EN_BOLD, 150)[0]
        self.vio = cached('r12_violin_v1', _rgba(violin))
        self.bai = [Tile(k, 124, PALETTE[(j + 2) % 4], romaji=r) for j, (k, r) in enumerate(zip('バイオリン', ('ba', 'i', 'o', 'ri', 'n')))]
        self.bxs = tile_row('バイオリン', 540, 124, 14)
        self.t_some = at('Some English')[0]
        self.t_sep = at('separate')[0]
        self.t_L, self.t_R = at('L', after=self.t_sep)[0], at('R', after=self.t_sep)[0]
        self.t_one = at('Just one')[0]
        self.t_rice, self.t_lice = at('rice')[0], at('lice')[0]
        self.t_rai = JA['raisu']['start']
        self.t_thanks = at('thank you')[0]
        self.t_th = at('th', after=self.t_rai)[0]
        self.t_san = JA['sankyu']['start']
        self.t_v = at('v', after=self.t_san)[0]
        self.t_b = at('b', after=self.t_v)[0]
        self.t_vio = at('Violin')[0]
        self.t_bai = JA['baiorin']['start']
        self.thx = brush_x(540, 780, 230, self.t_th + 0.15, seed=41, width=30)
        self.t_hit = self.t_rai

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 18))

    def window(self, t, a, b):
        return smooth((t - a) / 0.3) * (1 - smooth((t - b) / 0.3))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fh = smooth((t - self.t_some + 0.1) / 0.3)
        kit.put(fr, cam, self.h1, 540, 250, INK, fh)
        kit.put(fr, cam, self.h2, 540, 365, VERM, fh, pulse(t, self.t_some + 0.3, 0.12))
        # the three missing sounds, crossed out
        fc = 1 - smooth((t - self.t_sep + 0.3) / 0.3)
        for k, g in enumerate(self.chips):
            t0 = self.t_some + 0.5 + 0.45 * k
            if t > t0 and fc > 0:
                x, y = (230, 540, 850)[k], 860 + drop_y(t, t0, 300, 0.45)
                chip(fr, cam, g, x, y, smooth((t - t0) / 0.1) * fc, INK, pulse(t, t0 + 0.35, 0.15))
                fx = (t - t0 - 0.45) / 0.15
                if fx > 0:
                    kit.put(fr, cam, self.xm, x, y, VERM, 0.9 * smooth(fx) * fc, 1.4 + 0.5 * np.exp(-fx * 3))
        # 1. L and R merge into one sound
        w1 = self.window(t, self.t_sep - 0.1, self.t_rice - 0.4)
        if w1 > 0:
            m = ease_io((t - self.t_one) / 0.6)
            kit.put(fr, cam, self.L, 300 + 240 * m, 820 + drop_y(t, self.t_L - 0.1, 300, 0.45), INK,
                    w1 * smooth((t - self.t_L + 0.1) / 0.1) * (1 - m), 1 - 0.5 * m)
            kit.put(fr, cam, self.R, 780 - 240 * m, 820 + drop_y(t, self.t_R - 0.1, 300, 0.45), INK,
                    w1 * smooth((t - self.t_R + 0.1) / 0.1) * (1 - m), 1 - 0.5 * m)
            if m > 0.5:
                self.ra.draw(fr, cam, 540, 820, w1 * smooth((m - 0.5) * 4), pulse(t, self.t_one + 0.4, 0.35, 8, 14),
                             glow=0.7 + 0.3 * np.sin(t * 5))
                kit.put(fr, cam, self.rarow, 540, 1010, INDIGO, w1 * smooth((t - self.t_one - 0.6) / 0.3))
        # 2. rice and lice: both ライス
        w2 = self.window(t, self.t_rice - 0.4, self.t_th - 0.5)
        if w2 > 0:
            fr_ = smooth((t - self.t_rice + 0.2) / 0.3)
            paint(fr, cam, self.rice['rgb'], self.rice['a'], 280, 800 + drop_y(t, self.t_rice - 0.2, 200, 0.45), w2 * fr_, 0.95)
            kit.put(fr, cam, self.lab_rice, 280, 1040, INK, w2 * fr_)
            fl = smooth((t - self.t_lice + 0.2) / 0.3)
            wig = 0.08 * np.sin(t * 9)
            paint(fr, cam, self.louse['rgb'], self.louse['a'], 800, 790 + drop_y(t, self.t_lice - 0.2, 200, 0.45), w2 * fl, 1.15, wig)
            kit.put(fr, cam, self.lab_lice, 800, 1040, INK, w2 * fl)
            for side, x0 in ((0, 280), (1, 800)):
                for k, tl in enumerate(self.raisu[side]):
                    t0 = self.t_rai + 0.12 * k + 0.05 * side
                    if t > t0:
                        tl.draw(fr, cam, x0 + (k - 1) * 104, 1200 + drop_y(t, t0, 200, 0.4), w2 * smooth((t - t0) / 0.1),
                                pulse(t, t0 + 0.3, 0.15))
            fe = smooth((t - self.t_rai - 0.4) / 0.2)
            kit.put(fr, cam, self.eq, 540, 1200, VERM, w2 * fe, pulse(t, self.t_rai + 0.4, 0.5))
        # 3. no TH: thank you -> サンキュー
        w3 = self.window(t, self.t_th - 0.5, self.t_v - 0.4)
        if w3 > 0:
            kit.put(fr, cam, self.TH, 540, 780 + drop_y(t, self.t_th - 0.35, 260, 0.45), INK,
                    w3 * smooth((t - self.t_th + 0.35) / 0.1) * (1 - smooth((t - self.t_thanks + 0.1) / 0.3)))
            if t > self.t_th + 0.1:
                kit.put(fr, cam, self.thx.render(t), 540, 960, VERM, 0.95 * w3 * (1 - smooth((t - self.t_thanks + 0.1) / 0.3)))
            b = np.clip((t - self.t_san + 0.1) / 0.35, 0, 1)
            ft = smooth((t - self.t_thanks + 0.1) / 0.25) * (1 - b)
            if ft > 0:
                offs = [(0, drop_y(t, self.t_thanks - 0.1 + 0.03 * k, 150, 0.35) - 600 * b * b) for k in range(len(self.thanks.letters))]
                self.thanks.draw(fr, cam, 540, 780, INK, w3 * ft, 1.0, offs)
            for k, (tl, x) in enumerate(zip(self.san, self.sxs)):
                t0 = self.t_san + 0.14 * k
                if t > t0:
                    tl.draw(fr, cam, x, 900 + drop_y(t, t0, 260, 0.4), w3 * smooth((t - t0) / 0.1), pulse(t, t0 + 0.3, 0.15))
                    tl.draw_rom(fr, cam, x, 1020, w3 * smooth((t - t0 - 0.25) / 0.2))
        # 4. V becomes B; violin; バイオリン
        w4 = smooth((t - self.t_v + 0.4) / 0.3)
        if w4 > 0:
            fv = smooth((t - self.t_v + 0.15) / 0.12)
            kit.put(fr, cam, self.V, 290, 600 + drop_y(t, self.t_v - 0.15, 260, 0.45), INK, w4 * fv)
            kit.put(fr, cam, self.arrow, 540, 600, GREY, w4 * smooth((t - self.t_v - 0.5) / 0.3))
            fb = (t - self.t_b + 0.1) / 0.2
            if fb > 0:
                kit.put(fr, cam, self.B, 790, 600, VERM, w4 * smooth(fb), 1 + 0.4 * np.exp(-fb * 2.5))
            fvi = (t - self.t_vio + 0.2) / 0.5
            if fvi > 0:
                sw = 0.5 + 0.25 * (1 - ease_out(min(fvi, 1))) + 0.03 * np.sin(t * 2)
                paint(fr, cam, self.vio['rgb'], self.vio['a'], 540, 1010 - 140 * (1 - ease_out(min(fvi, 1))), w4 * smooth(fvi * 2), 0.66, sw)
            for k, (tl, x) in enumerate(zip(self.bai, self.bxs)):
                t0 = self.t_bai + 0.14 * k
                if t > t0:
                    tl.draw(fr, cam, x, 1330 + drop_y(t, t0, 260, 0.4), w4 * smooth((t - t0) / 0.1), pulse(t, t0 + 0.3, 0.15))
        return fr.img
