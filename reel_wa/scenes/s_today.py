"""和 everywhere.  "And that kanji is still everywhere today.  Washoku, Japanese food.  Washi, Japanese paper.  Even Reiwa,
the name of this era."
和 IS EVERYWHERE at the top; three cards drop in as Raj names them, each with a small ink drawing and its 和 in
vermilion: 和食 WASHOKU (a rice bowl with chopsticks), 和紙 WASHI (a sheet of fibrous paper), 令和 REIWA (2019 —)."""
import cv2
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_ITALIC, FONT_JP, GREY, INK, VERM, Cam, blur, ease_io, noise, smooth, text_layer
from scenes.common11 import card, label, mixed
from scenes.kscene import KanjiScene
from timeline import JA, at

XS = (200, 540, 880)
CY = 900


def bowl(w=200, h=150):
    S = 4
    m = np.zeros((h * S, w * S), np.uint8)
    cv2.ellipse(m, (w * S // 2, int(h * 0.45 * S)), (int(w * 0.42 * S), int(h * 0.42 * S)), 0, 0, 180, 255, 4 * S, cv2.LINE_AA)
    cv2.line(m, (int(w * 0.08 * S), int(h * 0.45 * S)), (int(w * 0.92 * S), int(h * 0.45 * S)), 255, 4 * S, cv2.LINE_AA)
    cv2.ellipse(m, (w * S // 2, int(h * 0.45 * S)), (int(w * 0.32 * S), int(h * 0.2 * S)), 0, 180, 360, 160, -1, cv2.LINE_AA)  # rice
    cv2.line(m, (int(w * 0.55 * S), int(h * 0.05 * S)), (int(w * 0.95 * S), int(h * 0.38 * S)), 255, 3 * S, cv2.LINE_AA)       # chopsticks
    cv2.line(m, (int(w * 0.62 * S), int(h * 0.0 * S)), (int(w * 0.99 * S), int(h * 0.32 * S)), 255, 3 * S, cv2.LINE_AA)
    cv2.rectangle(m, (int(w * 0.38 * S), int(h * 0.86 * S)), (int(w * 0.62 * S), int(h * 0.94 * S)), 255, -1)
    return blur(cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255, 0.8)


def sheet(w=170, h=150, seed=3):
    m = np.zeros((h, w), np.float32)
    m[8:-8, 8:-8] = 0.25
    r = np.random.default_rng(seed)
    for k in range(60):                                          # fibres
        x, y = r.uniform(10, w - 10), r.uniform(10, h - 10)
        a = r.uniform(0, np.pi)
        L = r.uniform(8, 30)
        cv2.line(m, (int(x), int(y)), (int(x + np.cos(a) * L), int(y + np.sin(a) * L)), 0.7, 1, cv2.LINE_AA)
    m[6:10, 6:-6] = m[-10:-6, 6:-6] = 0.9
    m[6:-6, 6:10] = m[6:-6, -10:-6] = 0.9
    return blur(m, 0.6)


class Scene(KanjiScene):
    paper_seed = 1105

    def build(self):
        self.head = mixed([('和', 100, FONT_JP, 0), ('IS EVERYWHERE', 110, FONT_BOLD, 4)], 20)
        J = lambda c: label(c, 120, FONT_JP, 0)
        self.items = [((J('和'), J('食')), (0,), label('WASHOKU', 40, FONT_BOLD, 6), label('Japanese food', 32, FONT_EN_ITALIC, 1), bowl(), JA['washoku']['start']),
                      ((J('和'), J('紙')), (0,), label('WASHI', 40, FONT_BOLD, 6), label('Japanese paper', 32, FONT_EN_ITALIC, 1), sheet(), JA['washi']['start']),
                      ((J('令'), J('和')), (1,), label('REIWA', 40, FONT_BOLD, 6), label('this era, 2019 —', 32, FONT_EN_ITALIC, 1), None, JA['reiwa']['start'])]
        self.t_ev = at('everywhere')[0]
        self.t_hit = JA['reiwa']['start']

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 10))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.head, 540, 320, VERM, smooth((t - self.t_ev + 0.2) / 0.3), 1 + 0.2 * np.exp(-max(t - self.t_ev, 0) * 5))
        for j, ((a, b), hot, name, gloss, pic, ts) in enumerate(self.items):
            f = (t - ts + 0.2) / 0.35
            if f <= 0:
                continue
            o = smooth(f)
            x = XS[j]
            y = CY - 60 * (1 - ease_io(min(f, 1)))
            pop = 1 + 0.12 * np.exp(-max(t - ts, 0) * 5)
            card(fr, cam, x, y, 310, 560, o, pop)
            for k, g in enumerate((a, b)):
                kit.put(fr, cam, g, x, y - 175 + 125 * k, VERM if k in hot else INK, o, pop)
            if pic is not None:
                kit.put(fr, cam, pic, x, y + 110, INK, o, pop)
            else:
                kit.put(fr, cam, label('2019', 56, FONT_BOLD, 4), x, y + 110, VERM, o, pop)
            kit.put(fr, cam, name, x, y + 205, INK, o)
            kit.put(fr, cam, gloss, x, y + 245, GREY, o)
        return fr.img
