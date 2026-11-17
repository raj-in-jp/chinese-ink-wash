"""The hook.  "Tokyo is one of the biggest cities on Earth.  But a hundred and sixty years ago, there was no Tokyo!"
Frame 1 is already alive: Tokyo at night, painted in colour — a dusk-to-indigo sky, a haze of far towers, Tokyo Tower
in the middle (orange and white lattice, Main and Top Decks lit, glowing), near towers with twinkling windows and
blinking red aviation lights, car light-trails streaming along the road.  TOKYO / 東京 slam in over the sky.
On "a hundred and sixty years ago" the year spins back 2026 -> 1866 while the city drops away layer by layer and the
night fades to sepia paper; Edo rises in its place (Fuji, the castle wall and turret, a sea of tiled roofs).  On
"no Tokyo!" the title is slashed in vermilion and NO TOKYO?! is stamped."""
import cv2
import numpy as np

import kit
from engine import Frame, FONT_BOLD, FONT_EN_BOLD, FONT_JP, H, INK, VERM, W, Cam, StrokeSet, blur, cached, ease_io, ease_out, smooth, \
    stroke, text_layer
from paint10 import edo_town, tower, towers
from scenes.kscene import KanjiScene
from timeline import JA, at

IVORY = np.array([0.98, 0.95, 0.88], np.float32)
GROUND = 1760                                                # street level


def paint(fr, cam, rgb, a, x, y, op=1.0, sc=1.0):
    if op <= 0:
        return
    h, w = a.shape
    M = kit.affine(cam, x, y, w, h, sc, sc, 0.0)
    A = cv2.warpAffine(a, M, (W, H))
    if A.max() > 0:
        fr.over(cv2.warpAffine(rgb, M, (W, H)), A, op)


def add(fr, cam, m, x, y, color, op, sc=1.0):
    """additive light (windows, glow, trails)"""
    if op <= 0:
        return
    h, w = m.shape
    A = cv2.warpAffine(m, kit.affine(cam, x, y, w, h, sc, sc, 0.0), (W, H))
    fr.img += A[..., None] * np.asarray(color, np.float32) * op


def _tower():
    rgb, a, info = tower(1180)
    return {'rgb': rgb, 'a': a, 'info': np.asarray(info, np.float32), 'glow': blur(a, 30)}


def _towers(far, seed):
    def go():
        rgb, a, L, tops = towers(seed=seed, far=far)
        return {'rgb': rgb, 'a': a, 'L': L, 'tops': np.asarray(tops, np.float32)}
    return go


class Scene(KanjiScene):
    paper_seed = 1001

    def build(self):
        self.tw = cached('r10_tower_v2', _tower)
        self.far = cached('r10_far_v2', _towers(True, 7))
        self.near = cached('r10_near_v2', _towers(False, 2))
        self.edo = cached('r10_edo_v2', lambda: {'d': edo_town()})['d']
        y = np.linspace(0, 1, H)[:, None, None]
        top, mid, low = np.array([0.04, 0.05, 0.14]), np.array([0.16, 0.13, 0.30]), np.array([0.86, 0.45, 0.34])
        sky = np.where(y < 0.55, top + (mid - top) * (y / 0.55), mid + (low - mid) * ((y - 0.55) / 0.45))
        sky = (sky * np.ones((H, W, 3))).astype(np.float32)
        r = np.random.default_rng(4)
        for k in range(120):                                  # a few stars high up
            sx, sy = int(r.uniform(0, W)), int(r.uniform(0, 800))
            sky[sy:sy + 2, sx:sx + 2] += r.uniform(0.15, 0.5)
        self.sky = sky
        self.tokyo = text_layer('TOKYO', FONT_BOLD, 250, tracking=10)[0]
        self.kanji = text_layer('東京', FONT_JP, 140)[0]
        self.big = text_layer('ONE OF THE BIGGEST CITIES ON EARTH', FONT_EN_BOLD, 34, tracking=6)[0]
        self.no = text_layer('NO TOKYO?!', FONT_BOLD, 180, tracking=4)[0]
        self.years = {}
        self.t_big = at('biggest')[0]
        self.t_back = at('hundred and sixty')[0]
        self.t_no = JA['tokyo2']['start']
        x = StrokeSet(W, 1920)
        prof = ((0, 0.4), (0.1, 1), (0.85, 0.9), (1, 0.2))
        x.add(stroke(W, 1920, [(230, 180), (540, 330), (850, 470)], 26, ink=0.95, dry=0.35, profile=prof, seed=11), self.t_no - 0.1, 0.2)
        x.add(stroke(W, 1920, [(850, 180), (540, 330), (240, 470)], 26, ink=0.95, dry=0.35, profile=prof, seed=12), self.t_no + 0.06, 0.2)
        self.slash = x
        trail = np.zeros((8, 220), np.float32)
        trail[2:6] = np.linspace(0, 1, 220) ** 2
        self.trail = blur(trail, 1.2)
        dot = np.zeros((14, 14), np.float32)
        cv2.circle(dot, (7, 7), 4, 1.0, -1, cv2.LINE_AA)
        self.dot = blur(dot, 1.0)
        self.t_hit = self.t_no

    def year(self, y):
        if y not in self.years:
            self.years[y] = text_layer(str(y), FONT_BOLD, 170, tracking=8)[0]
        return self.years[y]

    def cam(self, t):
        q = t - self.t_no
        shake = 12 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960 - 30 * smooth(t / 4), 1.0 + 0.05 * smooth(t / 4.5))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)                                  # the paper (Edo, after the rewind)
        back = ease_io((t - self.t_back) / 1.8)
        night = 1 - smooth((back - 0.25) / 0.6)
        # ---- 1866: Edo rises out of the paper
        fe = smooth((back - 0.35) / 0.5)
        if fe > 0:
            kit.put(fr, cam, self.edo, 540, 1340 + 120 * (1 - ease_out(fe)), INK, 0.9 * fe, 1.3)
        # ---- 2026: Tokyo at night, dropping away layer by layer
        if night > 0:
            N = Frame(cv2.warpAffine(self.sky, cam.matrix(), (W, H), borderMode=cv2.BORDER_REFLECT))
            drop = lambda d: 1400 * ease_io(np.clip((back - d) / 0.55, 0, 1))
            f = self.far
            paint(N, cam, f['rgb'], f['a'], 540, GROUND - 120 - 550 + drop(0.2))
            add(N, cam, f['L'], 540, GROUND - 120 - 550 + drop(0.2), (0.55, 0.50, 0.38), 0.55)
            tw = self.tw
            tx, ty = 540, GROUND - 590 + drop(0.0)
            add(N, cam, tw['glow'], tx, ty, (0.95, 0.45, 0.15), 0.35)
            paint(N, cam, tw['rgb'], tw['a'], tx, ty)
            hh = tw['a'].shape[0]
            mx, my = tw['info'][0] - tw['a'].shape[1] / 2 + tx, tw['info'][1] - hh / 2 + ty
            add(N, cam, self.dot, mx, my, (1.0, 0.15, 0.1), 0.9 * (np.sin(t * 5) > 0))       # the mast's warning light
            nr = self.near
            ny = GROUND - 550 + drop(0.1)
            paint(N, cam, nr['rgb'], nr['a'], 540, ny)
            tw_ = 0.85 + 0.15 * np.sin(t * 9)
            add(N, cam, nr['L'], 540, ny, (1.0, 0.80, 0.45), 0.9 * tw_)
            for k, (x, y) in enumerate(nr['tops'][::2]):                                   # aviation lights on the roofs
                if np.sin(t * 4 + k * 1.3) > 0.2:
                    add(N, cam, self.dot, x, y - 550 + ny, (1.0, 0.12, 0.08), 0.8)
            # the street: car light-trails
            road = np.zeros((H, W), np.float32)
            road[GROUND + 0:] = 1
            N.over(np.array([0.05, 0.05, 0.08], np.float32), road * (1 - smooth(back / 0.3)), 1.0)
            for k in range(10):
                lane = GROUND + 40 + (k % 4) * 30
                sp = 700 + 130 * (k % 3)
                if k % 2:
                    x = (t * sp + k * 290) % 1500 - 200
                    add(N, cam, self.trail[:, ::-1], x, lane, (1.0, 0.25, 0.15), 0.9)
                else:
                    x = 1300 - (t * sp + k * 290) % 1500
                    add(N, cam, self.trail, x, lane, (1.0, 0.95, 0.85), 0.9)
            fr.img = fr.img * (1 - night) + N.img * night
            # a sepia flash as the years run back
            fr.img = fr.img * (1 - 0.35 * np.sin(np.pi * np.clip(back, 0, 1))) + np.array([0.80, 0.68, 0.50], np.float32) * \
                0.35 * np.sin(np.pi * np.clip(back, 0, 1))
        # ---- the title: ivory on the night, vermilion / ink on the paper
        c_t = IVORY * night + VERM * (1 - night)
        c_k = IVORY * night + INK * (1 - night)
        sl = (t + 0.1) / 0.3
        kit.put(fr, cam, self.tokyo, 540, 250, c_t, smooth(sl * 2), 1 + 0.5 * np.exp(-max(sl, 0) * 3), rot=-0.02, over=True)
        kit.put(fr, cam, self.kanji, 540, 440, c_k, smooth((t - 0.25) / 0.3), over=True)
        fb = smooth((t - self.t_big) / 0.3) * (1 - smooth((t - self.t_back) / 0.3))
        kit.put(fr, cam, self.big, 540, 560, IVORY, fb, over=True)
        if t > self.t_back - 0.1:
            y = int(round(2026 - 160 * back))
            fy = smooth((t - self.t_back + 0.1) / 0.2)
            kit.put(fr, cam, self.year(y), 540, 600, c_k, fy, 1 + 0.06 * np.sin(t * 30) * (back < 1), over=True)
        if t > self.t_no - 0.15:
            kit.put(fr, cam, self.slash.render(t), 540, 960, VERM, 0.95)
            fn = (t - self.t_no - 0.35) / 0.18
            if fn > 0:
                s = 1 + 0.5 * np.exp(-fn * 2.5)
                kit.put(fr, cam, kit.box(self.no.shape[0] + 40, self.no.shape[1] + 70, 4), 540, 780, IVORY, smooth(fn), s, rot=-0.05,
                        over=True)
                kit.put(fr, cam, self.no, 540, 780, VERM, smooth(fn), s, rot=-0.05, over=True)
        return fr.img
