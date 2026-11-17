"""The title hook.  "Why is Japan called 'the Land of the Rising Sun'?  Because of China!"
From the first frame the sea is moving and a big red sun is coming up out of it; WHY IS JAPAN CALLED, then THE LAND OF
THE and RISING SUN letter by letter in Cinzel as the sun clears the horizon, its reflection shimmering on the water.
On "Because of China!" the camera jolts: BECAUSE OF on a slip, CHINA?! slammed in, and a vermilion seal 中國 stamped
beside it.  (Only the disc of the sun is drawn, no rays.)"""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_JP_ANTIQUE, FONT_TITLE, FONT_TITLE_LIGHT, GREY, INK, VERM, Cam, blur, ease_out, \
    smooth, text_layer
from scenes.common11 import PAPER, card, chip, label, vertical
from scenes.kscene import KanjiScene
from timeline import at

HORIZON = 1290
SEA = np.array([0.36, 0.47, 0.52], np.float32)


def _glow(r=260, pad=260):
    s = 2 * (r + pad)
    yy, xx = np.mgrid[0:s, 0:s] - s / 2
    d = np.hypot(xx, yy)
    return np.clip(1 - (d - r * 0.6) / (r + pad * 0.8), 0, 1).astype(np.float32) ** 2.2


def dash(h, w):
    """a soft brush dash, tapered at both ends"""
    x = np.linspace(-1, 1, max(w, 2))
    y = np.linspace(-1, 1, max(h, 2))
    return (np.clip(1 - x[None] ** 4, 0, 1) * np.clip(1 - y[:, None] ** 2, 0, 1)).astype(np.float32)


def disc(r, soft=1.5):
    s = int(r * 2 + 8)
    yy, xx = np.mgrid[0:s, 0:s] - s / 2
    return np.clip((r - np.hypot(xx, yy)) / soft + 0.5, 0, 1).astype(np.float32)


class Scene(KanjiScene):
    paper_seed = 1100

    def build(self):
        self.q = label('WHY IS JAPAN CALLED', 40, FONT_EN_BOLD, 10)
        self.l1 = text_layer('THE LAND OF THE', FONT_TITLE_LIGHT, 74, tracking=4)[0]
        self.letters = [text_layer(c, FONT_TITLE, 104)[0] if c != ' ' else None for c in 'RISING SUN']
        ws = [g.shape[1] if g is not None else 40 for g in self.letters]
        self.xs = np.cumsum([0] + [w + 6 for w in ws[:-1]]) + np.array(ws) / 2
        self.xs = self.xs - (self.xs[-1] + ws[-1] / 2) / 2 + 540
        self.sun = disc(220)
        self.glow = _glow()
        self.bc = text_layer('BECAUSE OF', FONT_BOLD, 120, tracking=6)[0]
        self.cn = text_layer('CHINA?!', FONT_BOLD, 250, tracking=6)[0]
        self.seal = vertical('中國', 70, FONT_JP_ANTIQUE)
        self.t_why = at('Why is Japan')[0]
        self.t_land = at('Land of')[0] - 0.2
        self.t_rs = at('Rising Sun')[0]
        self.t_bc = at('Because of')[0]
        self.t_cn = at('China', after=self.t_bc)[0]
        self.t_hit = self.t_cn

    def cam(self, t):
        q = t - self.t_cn
        shake = 14 * np.exp(-max(q, 0) * 7) * np.sin(q * 55) * (q > 0)
        z = 1.0 + 0.04 * smooth(t / 5) + 0.05 * ease_out(np.clip((t - self.t_bc) / 0.4, 0, 1))
        return Cam(540 + shake, 960 + 0.6 * shake, z)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # the sun coming up out of the sea (from the very first frame)
        u = ease_out(np.clip((t + 0.6) / (self.t_rs + 1.4), 0, 1))
        sy = HORIZON + 180 - 420 * u
        kit.put(fr, cam, self.glow, 540, sy, np.array([0.98, 0.70, 0.45], np.float32), 0.55 * smooth(u * 3))
        kit.put(fr, cam, self.sun, 540, sy, VERM, 0.95)
        # the sea: opaque below the horizon, so the sun comes out of it, with drifting wave strokes
        sea = np.zeros(fr.img.shape[:2], np.float32)
        sea[HORIZON:] = 1
        fr.over(PAPER, sea)
        fr.ink(sea * np.linspace(0.18, 0.45, fr.img.shape[0])[:, None], SEA, 1.0)
        kit.put(fr, cam, kit.box(5, 1200, 1.5), 540, HORIZON, INK, 0.75)
        rows = np.arange(HORIZON + 30, 1920, 46)
        for k, y in enumerate(rows):
            depth = (y - HORIZON) / (1920 - HORIZON)
            L, gap = 60 + 200 * depth, 140 + 260 * depth
            x0 = (t * (25 + 50 * depth) * (1 if k % 2 else -1) + k * 97) % gap
            for x in np.arange(-gap + x0, 1080 + gap, gap):
                kit.put(fr, cam, dash(int(4 + 6 * depth), int(L)), x, y + 4 * np.sin(t * 2 + x * 0.01), INK, 0.22 + 0.25 * depth)
        # the sun's reflection: shimmering vermilion dashes under it
        if sy < HORIZON + 60:
            for k, y in enumerate(np.arange(HORIZON + 22, HORIZON + 330, 26)):
                w = (200 - (y - HORIZON) * 0.35) * (0.7 + 0.3 * np.sin(t * 6 + k * 1.7))
                kit.put(fr, cam, dash(9, max(int(w), 12)), 540 + 10 * np.sin(t * 3 + k), y, VERM, 0.55 * smooth((HORIZON + 60 - sy) / 120))
        # the title
        fq = (t - self.t_why + 0.5) / 0.3
        kit.put(fr, cam, self.q, 540, 300, GREY, smooth(fq), 1 + 0.15 * np.exp(-max(fq, 0) * 3))
        fl = (t - self.t_land) / 0.35
        kit.put(fr, cam, self.l1, 540, 410 + 20 * (1 - smooth(fl)), INK, smooth(fl))
        for j, (g, x) in enumerate(zip(self.letters, self.xs)):
            if g is None:
                continue
            f = (t - self.t_rs + 0.1 - 0.06 * j) / 0.25
            if f > 0:
                kit.put(fr, cam, g, x, 545 + 30 * (1 - ease_out(min(f, 1))), VERM, smooth(f), 1 + 0.35 * np.exp(-f * 3))
        # BECAUSE OF CHINA?!
        fb = (t - self.t_bc + 0.05) / 0.2
        if fb > 0:
            chip(fr, cam, self.bc, 540, 745, smooth(fb), INK, 1 + 0.3 * np.exp(-fb * 3))
        fc = (t - self.t_cn + 0.05) / 0.15
        if fc > 0:
            s = 1 + 0.6 * np.exp(-fc * 2.5)
            card(fr, cam, 470, 930, self.cn.shape[1] + 70, self.cn.shape[0] + 40, smooth(fc), s, rim=False)
            kit.put(fr, cam, self.cn, 470, 930, INK, smooth(fc), s, rot=-0.03)
            fs = (t - self.t_cn - 0.25) / 0.15
            if fs > 0:
                ss = 1 + 0.8 * np.exp(-fs * 3)
                kit.put(fr, cam, kit.box(self.seal.shape[0] + 40, self.seal.shape[1] + 40, 3), 900, 930, VERM, smooth(fs), ss, rot=0.08,
                        over=True)
                kit.put(fr, cam, self.seal, 900, 930, PAPER, smooth(fs), ss, rot=0.08, over=True)
        return fr.img
