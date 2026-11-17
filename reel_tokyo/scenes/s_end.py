"""The ending.  "Would you rather live in old Edo, or modern Tokyo?  Tell me in the comments, and follow for more."  またね！
WOULD YOU RATHER LIVE IN… at the top; two cards: 江戸 EDO with the castle, 東京 TOKYO with the skyline, a vermilion
VS between them, each bouncing as Raj names it; a ring swings between them; TELL ME IN THE COMMENTS ↓, the black
banner FOLLOW @raj_in_jp, and またね！ brushed in."""
import cv2
import numpy as np

import kit
from draw10 import castle
from engine import FONT_BOLD, FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_JP, H, INK, VERM, W, Cam, StrokeSet, cached, ease_io, noise, smooth, stroke, text_layer
from scenes.common10 import label
from scenes.kscene import KanjiScene
from timeline import JA, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)
CARD = np.array([0.96, 0.93, 0.86], np.float32)
WASH = np.array([0.80, 0.78, 0.74], np.float32)
LIGHT = np.array([0.90, 0.68, 0.22], np.float32)
XS, CY, CW, CH = (285, 795), 800, 400, 500


def _night_card(w=340, h=250):
    """the hook's painted night Tokyo, shrunk into a card picture: sky, far towers, Tokyo Tower, lit near towers"""
    from paint10 import tower, towers
    Hh, Ww = 1500, 1080
    y = np.linspace(0, 1, Hh)[:, None, None]
    img = ((np.array([0.05, 0.06, 0.16]) * (1 - y) + np.array([0.80, 0.44, 0.36]) * y) * np.ones((Hh, Ww, 3))).astype(np.float32)
    def comp(rgb, a, x0, y0, L=None, lc=None):
        hh, ww = a.shape
        img[y0:y0 + hh, x0:x0 + ww] = img[y0:y0 + hh, x0:x0 + ww] * (1 - a[..., None]) + rgb * a[..., None]
        if L is not None:
            img[y0:y0 + hh, x0:x0 + ww] += L[..., None] * np.asarray(lc, np.float32)
    fr_, fa, fL, _ = towers(seed=7, far=True)
    comp(fr_, fa, 0, Hh - 1100 - 120, fL, (0.3, 0.27, 0.2))
    trgb, ta, _ = tower(1180)
    comp(trgb, ta, 540 - ta.shape[1] // 2, Hh - 1180 - 60)
    nr, na, nL, _ = towers(seed=2)
    comp(nr, na, 0, Hh - 1100, nL, (0.9, 0.72, 0.4))
    crop = img[Hh - 1300:Hh - 80, 140:940]
    rgb = cv2.resize(np.clip(crop, 0, 1), (w, h * 1220 // 800 if False else h), interpolation=cv2.INTER_AREA)
    a = np.zeros((h, w), np.float32)
    cv2.rectangle(a, (2, 2), (w - 3, h - 3), 1.0, -1)
    return {'rgb': rgb.astype(np.float32), 'a': cv2.GaussianBlur(a, (0, 0), 0.8)}


class Scene(KanjiScene):
    paper_seed = 1005

    def build(self):
        self.q = text_layer('WOULD YOU RATHER', FONT_BOLD, 100, tracking=3)[0]
        self.q2 = text_layer('LIVE IN…', FONT_BOLD, 130, tracking=3)[0]
        self.box, self.rim = kit.box(CH, CW, 2.5), kit.rim(CH, CW, inset=6, t=3)
        self.sel = kit.rim(CH + 24, CW + 24, inset=4, t=8)
        self.kj = [text_layer('江戸', FONT_JP, 110)[0], text_layer('東京', FONT_JP, 110)[0]]
        self.lab = [label('OLD EDO', 40, FONT_BOLD, 6), label('MODERN TOKYO', 40, FONT_BOLD, 6)]
        self.castle = cached('r10_castle_v1', castle)
        self.night = cached('r10_card_night_v1', _night_card)
        self.vs = text_layer('VS', FONT_BOLD, 110, tracking=2)[0]
        self.cm = label('TELL ME IN THE COMMENTS ↓', 40, FONT_EN_BOLD, 4)
        m = text_layer('またね！', FONT_BRUSH_JP, 110)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, FONT_EN_BOLD, 10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_q = at('Would you rather')[0]
        self.t_n = (JA['edo4']['start'], JA['tokyo4']['start'])
        self.t_cm = at('comments')[0]
        self.t_follow = at('follow for')[0]
        self.t_mt = JA['matane']['start']
        self.t_hit = self.t_mt
        bn = StrokeSet(W, H)
        bn.add(stroke(W, H, [(250, 1336), (540, 1324), (830, 1332)], 118, ink=0.96, dry=0.45,
                      profile=((0, 0.55), (0.06, 1.0), (0.85, 0.95), (1, 0.5)), seed=171), self.t_follow - 0.05, 0.4)
        self.banner = bn

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 6))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fq = smooth((t - self.t_q + 0.2) / 0.35)
        kit.put(fr, cam, self.q, 540, 290 + 15 * (1 - fq), INK, fq)
        kit.put(fr, cam, self.q2, 540, 420, VERM, smooth((t - self.t_q - 0.3) / 0.35))
        for j in range(2):
            f = (t - self.t0 - 0.3 - 0.15 * j) / 0.35
            if f <= 0:
                continue
            o = smooth(f)
            dy = -30 * (1 - ease_io(min(f, 1)))
            q = t - self.t_n[j]
            bounce = 1 + 0.12 * np.exp(-max(q, 0) * 5) * np.cos(q * 18) * (q > 0)
            x = XS[j]
            kit.card(fr, cam, self.box, self.rim, x, CY + dy, o, color=CARD)
            if j == 0:
                kit.put(fr, cam, self.castle['wash'], x, CY - 40 + dy, WASH, o, 0.9 * bounce)
                kit.put(fr, cam, self.castle['ink'], x, CY - 40 + dy, INK, o, 0.9 * bounce)
            else:
                sc = bounce
                M = kit.affine(cam, x, CY - 40 + dy, self.night['a'].shape[1], self.night['a'].shape[0], sc, sc, 0.0)
                A = cv2.warpAffine(self.night['a'], M, (W, H))
                fr.over(cv2.warpAffine(self.night['rgb'], M, (W, H)), A, o)
            kit.put(fr, cam, self.kj[j], x, CY + 150 + dy, VERM, o, bounce)
            kit.put(fr, cam, self.lab[j], x, CY + 220 + dy, INK, o)
        kit.put(fr, cam, self.vs, 540, CY, VERM, smooth((t - self.t0 - 0.6) / 0.3), 1 + 0.3 * np.exp(-max(t - self.t0 - 0.6, 0) * 4), rot=-0.08)
        u = (t - self.t_q - 0.6) / max(self.t_cm - self.t_q - 0.6, 0.5)
        if 0 < u < 1.1:
            j = int(8 * (1 - (1 - min(u, 1)) ** 2)) % 2
            kit.put(fr, cam, self.sel, XS[j], CY, VERM, 0.95 * (1 - smooth((u - 0.9) / 0.2)))
        kit.put(fr, cam, self.cm, 540, 1095, INK, smooth((t - self.t_cm + 0.1) / 0.3))
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 1170, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow + 0.05) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1324, IVORY, smooth((t - self.t_follow - 0.15) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1252, INK, smooth(fb))
        return fr.img
