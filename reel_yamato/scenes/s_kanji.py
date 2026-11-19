"""Kanji arrive.  "Then kanji arrived from China.  Japan kept the old Japanese word, and just picked kanji for the meaning.
First, this one.  Then, in the seven hundreds, these two.  'Great harmony.'"
A scroll slides in from the left with a 中国 → 日本 tag and unrolls; in the middle a sound bubble やまと (the spoken
word) floats and pulses — SOUND: KEPT.  On "First, this one" 倭 is brushed on the scroll under the bubble.  On "seven
hundreds" a 700s chip pops; on "these two" 倭 ink-fades away and 大和 is brushed in its place; on "Great harmony" the
tags GREAT and HARMONY pop under the two kanji.  The bubble never changes: same sound, new kanji."""
import cv2
import numpy as np

import kit
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_JP, GREY, INK, VERM, Cam, ease_out, smooth, text_layer
from glyphs import typeset
from scenes.common12 import IVORY, SCROLL, card, chip, label, mixed, pulse, drop_y
from scenes.kscene import KanjiScene
from timeline import at

SY = 980


class Scene(KanjiScene):
    paper_seed = 1303

    def build(self):
        self.route = mixed([('中国', 60, FONT_JP, 0), ('→', 60, FONT_EN_BOLD, 0), ('日本', 60, FONT_JP, 0)], 18)
        self.head = text_layer('KANJI ARRIVE FROM CHINA', FONT_BOLD, 84, tracking=3)[0]
        self.bub = text_layer('やまと', FONT_JP, 92)[0]
        self.kept = label('SOUND: KEPT', 36, FONT_EN_BOLD, 10)
        self.wo = typeset('倭', 300, font=FONT_BRUSH_JP, seed=1330, medians=False, sweep=(0.7, 1))
        self.g = [typeset(c, 300, font=FONT_BRUSH_JP, seed=1331 + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate('大和')]
        self.first = label('FIRST', 38, FONT_EN_BOLD, 10)
        self.c700 = text_layer('700s', FONT_BOLD, 120, tracking=4)[0]
        self.great, self.harm = text_layer('GREAT', FONT_BOLD, 76, tracking=4)[0], text_layer('HARMONY', FONT_BOLD, 76, tracking=4)[0]
        b = np.zeros((170, 360), np.float32)
        cv2.ellipse(b, (180, 78), (170, 70), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
        cv2.fillPoly(b, [np.array([(150, 140), (200, 140), (175, 168)], np.int32)], 1.0, cv2.LINE_AA)
        self.bubble = cv2.GaussianBlur(b, (0, 0), 1.0)
        self.t_arr = at('arrived from China')[0]
        self.t_kept = at('kept the old')[0]
        self.t_first = at('First this one')[0]
        self.t_700 = at('seven hundreds')[0]
        self.t_two = at('these two')[0]
        self.t_great = at('Great harmony')[0]
        self.t_hit = self.t_two

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 12))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.head, 540, 270, INK, smooth((t - self.t_arr + 0.2) / 0.3))
        # the scroll slides in from the left (from China) and unrolls
        u = ease_out(np.clip((t - self.t_arr) / 1.0, 0, 1))
        if u > 0:
            x = -300 + 840 * u
            card(fr, cam, x, SY, int(140 + 520 * u), 700, 1.0, color=SCROLL, rim=False)
            for dx in (-1, 1):
                kit.put(fr, cam, kit.box(740, 30, 4), x + dx * (70 + 260 * u), SY, np.array([0.45, 0.30, 0.18], np.float32), 1.0, over=True)
            kit.put(fr, cam, self.route, x, SY + 300, GREY, smooth((u - 0.6) * 3))
        # the sound bubble: やまと, kept all the way through
        fb = (t - self.t_kept + 0.1) / 0.3
        if fb > 0:
            s = pulse(t, self.t_kept, 0.2) * (1 + 0.04 * np.sin(t * 4))
            kit.put(fr, cam, self.bubble, 540, 470, IVORY, smooth(fb), s, over=True)
            kit.put(fr, cam, self.bubble, 540, 470, VERM, 0.25 * smooth(fb), s)
            kit.put(fr, cam, self.bub, 540, 455, VERM, smooth(fb), s)
            kit.put(fr, cam, self.kept, 540, 590, GREY, smooth((t - self.t_kept - 0.4) / 0.3))
        # 倭 first, then 大和
        fw = (t - self.t_first) / 0.7
        out = smooth((t - self.t_two + 0.1) / 0.35)
        if fw > 0 and out < 1:
            kit.put(fr, cam, self.wo.at(fw, soft=0.05), 540, SY - 40, INK, 1 - out)
            kit.put(fr, cam, self.first, 540, SY + 160, GREY, smooth(fw) * (1 - out))
        for j, g in enumerate(self.g):
            f = (t - self.t_two - 0.15 - 0.3 * j) / 0.6
            if f > 0:
                kit.put(fr, cam, g.at(f, soft=0.05), 400 + 280 * j, SY - 40, INK, 1.0, 0.9)
        f7 = (t - self.t_700 + 0.05) / 0.2
        if f7 > 0:
            chip(fr, cam, self.c700, 830, 760, smooth(f7) * (1 - smooth((t - self.t_great - 0.6) / 0.3)), VERM, 1 + 0.4 * np.exp(-f7 * 3), )
        for j, (tag, t0) in enumerate(((self.great, self.t_great), (self.harm, self.t_great + 0.45))):
            f = (t - t0 + 0.05) / 0.2
            if f > 0:
                chip(fr, cam, tag, 400 + 280 * j, SY + 190, smooth(f), VERM, 1 + 0.3 * np.exp(-f * 3))
        return fr.img
