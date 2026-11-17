"""The twist.  "And here's the twist.  No Japanese law actually says that Tokyo is the capital!"
THE TWIST slams in; an old law book falls open in the middle of the page, its pages searched by a vermilion
magnifying ring that slides from line to line and finds nothing; a huge ? is stamped on the open pages, and
NO LAW SAYS TOKYO IS THE CAPITAL! lands under it."""
import cv2
import numpy as np

import kit
from draw10 import book
from engine import FONT_BOLD, INK, VERM, Cam, cached, ease_out, smooth, text_layer
from scenes.common10 import PAPER, label
from scenes.kscene import KanjiScene
from timeline import at

SCREEN = Cam(540, 960, 1.0)
PAGE = np.array([0.96, 0.94, 0.88], np.float32)


class Scene(KanjiScene):
    paper_seed = 1004

    def build(self):
        self.b = cached('r10_book_v1', book)
        self.twist = text_layer('THE TWIST', FONT_BOLD, 180, tracking=6)[0]
        self.q = text_layer('?', FONT_BOLD, 420)[0]
        self.l1 = text_layer('NO LAW SAYS', FONT_BOLD, 100, tracking=4)[0]
        self.l2 = text_layer('TOKYO IS THE CAPITAL!', FONT_BOLD, 100, tracking=4)[0]
        self.ring = np.zeros((120, 120), np.float32)
        cv2.circle(self.ring, (60, 60), 48, 1.0, 8, cv2.LINE_AA)
        self.t_tw = at('the twist')[0]
        self.t_law = at('No Japanese')[0]
        self.t_cap = at('is the capital')[0]
        from timeline import JA
        self.t_tok = JA['tokyo4']['start']
        self.t_hit = self.t_cap

    def cam(self, t):
        q = t - self.t_law - 1.4
        shake = 9 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.03 * smooth((t - self.t0) / 6))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        ft = (t - self.t_tw + 0.1) / 0.25
        kit.put(fr, cam, self.twist, 540, 330, VERM, smooth(ft), 1 + 0.5 * np.exp(-max(ft, 0) * 3), rot=-0.03)
        fb = (t - self.t_tw - 0.4) / 0.4
        if fb > 0:
            o = smooth(fb)
            sy = 0.4 + 0.6 * ease_out(min(fb, 1))
            kit.put(fr, cam, kit.box(390, 530, 16), 548, 912, INK, 0.25 * o, 1.4, 1.4 * sy)
            kit.put(fr, cam, self.b['wash'], 540, 900, PAGE, o, 1.4, 1.4 * sy, over=True)
            kit.put(fr, cam, self.b['ink'], 540, 900, INK, o, 1.4, 1.4 * sy)
            # the search: a ring sliding along the lines
            u = (t - self.t_law) / 1.5
            if 0 < u < 1:
                k = int(u * 8)
                x = (220 if k % 2 == 0 else 860) + (u * 8 - k) * (-200 if k % 2 else 200)
                y = 720 + 50 * (k % 7)
                kit.put(fr, cam, self.ring, x, y, VERM, 0.85 * o)
        fq = (t - self.t_law - 1.4) / 0.2
        if fq > 0:
            kit.put(fr, cam, self.q, 540, 900, VERM, smooth(fq), 1 + 0.6 * np.exp(-fq * 2.5), rot=0.06)
            kit.put(fr, cam, kit.box(250, 1000, 8), 540, 1300, PAPER, 0.9 * smooth(fq), over=True)
            kit.put(fr, cam, self.l1, 540, 1245, INK, smooth(fq))
            kit.put(fr, cam, self.l2, 540, 1355, VERM, smooth((t - self.t_tok + 0.1) / 0.25), 1 + 0.3 * np.exp(-max(t - self.t_tok, 0) * 5))
        return fr.img
