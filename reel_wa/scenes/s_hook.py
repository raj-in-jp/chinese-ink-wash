"""The hook.  "In 607, Japan sent China a letter so bold, the Chinese emperor was furious.  It began: 'From the Son of
Heaven where the sun rises... to the Son of Heaven where the sun sets.'"
607 slams in; a scroll unrolls with the real opening of the letter in two columns of classical Chinese,
日出處天子致書 / 日沒處天子無恙; on "furious" the page jolts and FURIOUS! is stamped.  Then the letter is read: 日出處
lights up in vermilion and, low on the page, a sun rises on the right over JAPAN 日出; 日沒處 lights up and a second
sun sinks on the left over CHINA 日沒, the English line under the scroll each time."""
import numpy as np

import kit
from draw9 import sun
from engine import FONT_BOLD, FONT_EN_ITALIC, FONT_TITLE, FONT_JP, GREY, INK, VERM, Cam, StrokeSet, ease_io, ease_out, smooth, stroke, text_layer
from scenes.common11 import PAPER, SCREEN, SCROLL, card, chip, label
from scenes.kscene import KanjiScene
from timeline import at

COL_R, COL_L = '日出處天子致書', '日沒處天子無恙'
HORIZON = 1400


class Scene(KanjiScene):
    paper_seed = 1101

    def build(self):
        self.y607 = text_layer('607', FONT_TITLE, 210, tracking=6)[0]
        self.sub = label('A LETTER FROM JAPAN TO CHINA', 36)
        self.fur = text_layer('FURIOUS!', FONT_BOLD, 180, tracking=4)[0]
        self.chars = [[label(c, 78, FONT_JP, 0) for c in col] for col in (COL_R, COL_L)]
        self.en1 = label('“From the Son of Heaven where the sun rises…”', 38, FONT_EN_ITALIC, 0)
        self.en2 = label('“…to the Son of Heaven where the sun sets.”', 38, FONT_EN_ITALIC, 0)
        self.sun = sun(58)
        self.jp = label('JAPAN  日出', 30)
        self.cn = label('CHINA  日沒', 30)
        self.jpk, self.cnk = label('JAPAN', 32), label('CHINA', 32)
        self.t607 = at('six-oh-seven')[0]
        self.t_let = at('letter')[0]
        self.t_fur = at('furious')[0]
        self.t_rise = at('sun rises')[0]
        self.t_set = at('sun sets')[0]
        self.t_hit = self.t_fur

    def cam(self, t):
        q = t - self.t_fur
        shake = 12 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.03 * smooth((t - self.t0) / 14))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        q = t - self.t_fur
        fr.img *= 1 - 0.12 * np.exp(-max(q, 0) * 4) * (q > 0) * (1 - np.array([0.95, 0.55, 0.45], np.float32))
        # 607 and the subtitle
        sl = (t - self.t607 + 0.1) / 0.3
        kit.put(fr, cam, self.y607, 540, 260, VERM, smooth(sl * 2), 1 + 0.5 * np.exp(-max(sl, 0) * 3), rot=-0.02)
        kit.put(fr, cam, self.sub, 540, 385, INK, smooth((t - self.t_let) / 0.3))
        # the scroll unrolling downward, the two columns read right to left
        u = ease_out(np.clip((t - self.t607 - 0.5) / 1.4, 0, 1))
        if u > 0:
            top, full = 450, 720
            h = int(60 + full * u)
            card(fr, cam, 540, top + h / 2, 520, h, 1.0, color=SCROLL, rim=False)
            kit.put(fr, cam, kit.box(34, 580, 4), 540, top, np.array([0.45, 0.30, 0.18], np.float32), 1.0, over=True)
            kit.put(fr, cam, kit.box(34, 580, 4), 540, top + h, np.array([0.45, 0.30, 0.18], np.float32), 1.0, over=True)
            for ci, (col, x) in enumerate(((self.chars[0], 650), (self.chars[1], 430))):
                for j, g in enumerate(col):
                    y = top + 62 + j * 96
                    if y > top + h - 50:
                        continue
                    ts = self.t_rise if ci == 0 else self.t_set
                    hot = smooth((t - ts + 0.1 - 0.15 * j) / 0.25) if j < 3 else 0.0
                    col_ = INK * (1 - hot) + VERM * hot
                    kit.put(fr, cam, g, x, y, col_, 1.0, 1 + 0.25 * hot * np.exp(-max(t - ts - 0.15 * j, 0) * 4))
        # FURIOUS!
        fq = (t - self.t_fur + 0.05) / 0.15
        if fq > 0:
            o = smooth(fq) * (1 - smooth((t - self.t_rise + 0.4) / 0.3))
            kit.put(fr, cam, self.fur, 540, 820, VERM, o, 1 + 0.6 * np.exp(-fq * 2.5), rot=-0.07)
        # the two suns: rising over Japan (east, right), setting over China (west, left)
        fh = smooth((t - self.t_rise + 0.3) / 0.4)
        if fh > 0:
            kit.put(fr, cam, kit.box(4, 1000, 1.5), 540, HORIZON, INK, 0.7 * fh)
            ur = ease_out(np.clip((t - self.t_rise) / 1.4, 0, 1))
            kit.put(fr, cam, self.sun, 820, HORIZON + 50 - 130 * ur, VERM, 0.9 * fh)
            fr.img[HORIZON + 3:] = fr.img[HORIZON + 3:] * 0 + self.frame(cam).img[HORIZON + 3:]
            kit.put(fr, cam, self.jpk, 820, HORIZON + 40, INK, fh)
            us = ease_io(np.clip((t - self.t_set) / 1.4, 0, 1))
            fs = smooth((t - self.t_set + 0.2) / 0.3)
            if fs > 0:
                kit.put(fr, cam, self.sun, 260, HORIZON - 80 + 130 * us, VERM, 0.9 * fs * (1 - 0.6 * us))
                fr.img[HORIZON + 3:] = fr.img[HORIZON + 3:] * 0 + self.frame(cam).img[HORIZON + 3:]
                kit.put(fr, cam, self.cnk, 260, HORIZON + 40, INK, fs)
                kit.put(fr, cam, self.jpk, 820, HORIZON + 40, INK, fh)
        # the English lines
        f1 = smooth((t - self.t_rise + 0.6) / 0.3) * (1 - smooth((t - self.t_set + 0.5) / 0.3))
        f2 = smooth((t - self.t_set + 0.3) / 0.3)
        kit.put(fr, cam, self.en1, 540, 1290, INK, f1)
        kit.put(fr, cam, self.en2, 540, 1290, INK, f2)
        return fr.img
