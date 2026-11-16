"""Kanji arrive.  "About fifteen hundred years ago, Japan had no writing.  So it borrowed Chinese characters: kanji."
~1,500 YEARS AGO at the top; a framed sea chart of East Asia; on "no writing" Japan gets a tag NO WRITING (yet);
on "borrowed" a stream of characters (漢 字 山 川 日 月 人 木) sails from China, past Korea, to Japan along a dashed
vermilion route; on "kanji" 漢字 KANJI is brushed big over the chart, "Chinese characters"."""
import cv2
import numpy as np

import kit
import r5art
from engine import FONT_EN_ITALIC, FONT_HEAD, FONT_JP, GREY, H, INK, VERM, W, Cam, cached, ease_io, smooth, spline, text_layer
from scenes.common import BLUE, SCREEN, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import JA, at

PANEL = (540, 1020, 1000, 760)
VIEW = (126.8, 35.6, 0.42)
ROUTE = [(112.5, 34.3), (118.5, 37.2), (124.0, 37.8), (127.0, 36.2), (129.3, 35.0), (132.5, 34.2), (135.8, 34.7)]
STREAM = '漢字山川日月人木'


class Scene(KanjiScene):
    paper_seed = 802

    def build(self):
        self.chart = cached('h7_chart_v1', r5art.east_asia_chart)['rgb'].astype(np.float32)
        lo, la, s = VIEW
        self.c = r5art.chart_xy(lo, la)
        self.s = s
        self.route = np.array(spline([tuple(r5art.chart_xy(x, y)) for x, y in ROUTE], 24), np.float32)
        cx, cy, pw, ph = PANEL
        m = np.zeros((H, W), np.float32)
        m[int(cy - ph / 2):int(cy + ph / 2), int(cx - pw / 2):int(cx + pw / 2)] = 1
        self.mask = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
        self.rim = kit.rim(ph + 16, pw + 16, inset=4, t=3)
        self.year = text_layer('ABOUT 1,500 YEARS AGO', FONT_HEAD, 64)[0]
        self.nowr = label('NO WRITING (YET)', 30)
        self.kanji = text_layer('漢字', FONT_JP, 150)[0]
        self.kl = label('KANJI', 50, tracking=12)
        self.kg = label('Chinese characters', 40, FONT_EN_ITALIC, 1)
        self.t_nw = at('no writing')[0]
        self.t_b = at('borrowed')[0]
        self.t_k = JA['kanji2']['start']
        self.t_hit = self.t_k

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 7))

    def to_screen(self, p):
        return np.array([PANEL[0], PANEL[1]], np.float32) + (np.asarray(p, np.float32) - self.c) * self.s

    def route_at(self, u):
        P = np.array([self.to_screen(q) for q in self.route])
        seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
        L = seg[-1] * u
        return P, seg, np.array([np.interp(L, seg, P[:, 0]), np.interp(L, seg, P[:, 1])])

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        legend(fr, t, self.t0, active='K' if t > self.t_k else None)
        fy = smooth((t - self.t0 - 0.1) / 0.4)
        kit.put(fr, cam, self.year, 540, 330 + 15 * (1 - fy), INK, fy)
        # the sea chart
        fm = smooth((t - self.t0 - 0.2) / 0.5)
        if fm > 0:
            s = self.s
            cx, cy = PANEL[:2]
            A = np.array([[s, 0, cx - s * self.c[0]], [0, s, cy - s * self.c[1]]], np.float32)
            img = cv2.warpAffine(self.chart, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            k = self.mask * fm
            fr.img = fr.img * (1 - k) + img * k
            kit.put(fr, SCREEN, self.rim, cx, cy, INK, 0.8 * fm)
        # NO WRITING on Japan
        jp = self.to_screen(r5art.chart_xy(134.0, 39.4))
        fn = smooth((t - self.t_nw) / 0.3) * (1 - smooth((t - self.t_b - 1.2) / 0.4))
        if fn > 0:
            self.plate(fr, SCREEN, jp[0], jp[1], 330, 56, fn)
            kit.put(fr, SCREEN, self.nowr, jp[0], jp[1], VERM, fn)
        # the route and the characters sailing along it
        u = ease_io((t - self.t_b + 0.1) / 1.6)
        if u > 0:
            P, seg, tip = self.route_at(u)
            d = np.zeros((H, W), np.float32)
            n = np.searchsorted(seg, seg[-1] * u)
            pts = np.vstack([P[:n], tip])
            dash = 0.0
            for a_, b_ in zip(pts[:-1], pts[1:]):
                ln = np.hypot(*(b_ - a_))
                q = 0.0
                while q < ln:
                    on = (dash % 28) < 18
                    step = min(ln - q, (18 - dash % 28) if on else (28 - dash % 28))
                    if on:
                        p0, p1 = a_ + (b_ - a_) * q / ln, a_ + (b_ - a_) * (q + step) / ln
                        cv2.line(d, tuple(np.round(p0).astype(int)), tuple(np.round(p1).astype(int)), 1.0, 6, cv2.LINE_AA)
                    q += max(step, 1e-3)
                    dash += max(step, 1e-3)
            fr.ink(d, VERM, 0.9)
        for j, ch in enumerate(STREAM):
            v = (t - self.t_b - 0.15 * j) / 1.7
            if 0 < v < 1.25:
                _, _, p = self.route_at(ease_io(min(v, 1)))
                o = smooth(v * 5) * (1 - smooth((v - 1.0) / 0.25))
                kit.put(fr, SCREEN, glyph(ch, 54), p[0], p[1] - 34 + 6 * np.sin(t * 6 + j), BLUE, o)
        # 漢字 KANJI
        fk = (t - self.t_k + 0.15) / 0.35
        if fk > 0:
            o = smooth(fk)
            self.plate(fr, cam, 540, 585, 560, 270, o)
            kit.put(fr, cam, self.kanji, 540, 545, BLUE, o, 1 + 0.25 * np.exp(-fk * 2.5))
            kit.put(fr, cam, self.kl, 540, 660, BLUE, smooth(fk - 0.8))
            kit.put(fr, cam, self.kg, 540, 715, GREY, smooth(fk - 1.4))
        return fr.img
