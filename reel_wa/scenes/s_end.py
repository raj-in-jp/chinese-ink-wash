"""The ending.  "So, which kanji would you choose for your country's name?  Tell me in the comments, and follow for more."
またね！
WHICH KANJI WOULD YOU CHOOSE / FOR YOUR COUNTRY? at the top; an empty card with a dashed vermilion frame where a brush
draws a big ? (YOUR KANJI); TELL ME IN THE COMMENTS ↓, the black banner FOLLOW @raj_in_jp, and またね！"""
import cv2
import numpy as np

import kit
from engine import FONT_BOLD, FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, H, INK, VERM, W, Cam, StrokeSet, noise, smooth, stroke, text_layer
from scenes.common11 import card, label
from scenes.kscene import KanjiScene
from timeline import JA, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)


def dashed(h, w, dash=22, gap=12, t=5):
    m = np.zeros((h, w), np.float32)
    for x in range(0, w, dash + gap):
        m[:t, x:x + dash] = 1
        m[-t:, x:x + dash] = 1
    for y in range(0, h, dash + gap):
        m[y:y + dash, :t] = 1
        m[y:y + dash, -t:] = 1
    return m


class Scene(KanjiScene):
    paper_seed = 1106

    def build(self):
        self.q1 = text_layer('WHICH KANJI WOULD YOU', FONT_BOLD, 92, tracking=3)[0]
        self.q2 = text_layer('CHOOSE FOR YOUR COUNTRY?', FONT_BOLD, 92, tracking=3)[0]
        self.frame_ = dashed(440, 440)
        self.your = label('YOUR KANJI', 36, FONT_BOLD, 8)
        prof = ((0, 0.4), (0.1, 1), (0.9, 0.9), (1, 0.3))
        self.cm = label('TELL ME IN THE COMMENTS ↓', 40, FONT_EN_BOLD, 4)
        m = text_layer('またね！', FONT_BRUSH_JP, 110)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, FONT_EN_BOLD, 10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_q = at('which kanji')[0]
        self.t_cm = at('comments')[0]
        self.t_follow = at('follow for')[0]
        self.t_mt = JA['matane']['start']
        self.t_hit = self.t_mt
        self.q_t0 = self.t_q + 0.6
        self.qmark = StrokeSet(W, H)
        self.qmark.add(stroke(W, H, [(470, 720), (500, 660), (580, 650), (620, 700), (600, 770), (545, 810), (540, 880)], 26, ink=0.95,
                              dry=0.3, profile=prof, seed=91), self.q_t0, 0.6)
        self.qmark.add(stroke(W, H, [(540, 950), (541, 965)], 30, ink=0.95, dry=0.2, profile=prof, seed=92), self.q_t0 + 0.65, 0.1)
        bn = StrokeSet(W, H)
        bn.add(stroke(W, H, [(250, 1406), (540, 1394), (830, 1402)], 118, ink=0.96, dry=0.45,
                      profile=((0, 0.55), (0.06, 1.0), (0.85, 0.95), (1, 0.5)), seed=171), self.t_follow - 0.05, 0.4)
        self.banner = bn

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 6))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fq = smooth((t - self.t_q + 0.2) / 0.35)
        kit.put(fr, cam, self.q1, 540, 290 + 15 * (1 - fq), INK, fq)
        kit.put(fr, cam, self.q2, 540, 400, VERM, smooth((t - self.t_q - 0.2) / 0.35))
        fc = smooth((t - self.t0 - 0.3) / 0.35)
        card(fr, cam, 540, 810, 480, 480, fc, rim=False)
        kit.put(fr, cam, self.frame_, 540, 810, VERM, 0.8 * fc)
        self.layer(fr, cam, self.qmark.render(t), color=INK, opacity=1.0)
        kit.put(fr, cam, self.your, 540, 990, VERM, smooth((t - self.q_t0 - 0.8) / 0.3))
        kit.put(fr, cam, self.cm, 540, 1100, INK, smooth((t - self.t_cm + 0.1) / 0.3))
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 1210, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow + 0.05) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1394, IVORY, smooth((t - self.t_follow - 0.15) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1312, INK, smooth(fb))
        return fr.img
