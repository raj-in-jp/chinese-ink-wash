"""The hook.  "Sixteen thousand years of Japan, [the pictures land] in two minutes.  Ready?  Go!"
The title JAPAN'S ENTIRE / HISTORY stays at the top the whole time.  Under it lies the relief map of Japan, and real
pictures of each age drop onto the map one by one, each landing on its own region with a vermilion pin, while the
caption under the title names the era: 縄文 JŌMON · c. 14,000 BC ... 令和 REIWA · 2019.  Together they cover Japan.
On "two minutes" the map sinks back and a vermilion ensō stopwatch is brushed round a big 2; on "Ready?" the camera
jolts; on "Go!" it punches in, the hand starts to sweep and a brushstroke races along the top."""
import os

import cv2
import numpy as np

import kit
from art import enso
from engine import (FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_HEAD, GREY, HERE, H, INK, VERM, W, Cam, StrokeSet,
                    blur, cached, ease_out, noise, smooth, stroke, text_layer)
from k6art import mist_hills
from scenes.era import ERAS, RIB_X0, RIB_X1, RIB_Y, year_label
from scenes.kscene import SCREEN, KanjiScene
from timeline import at

# the relief map (the user's, land cut out): source pixels -> world, scaled about the land's top centre
MAP_S, MAP_SRC0, MAP_DST0 = 1.12, (378.5, 100.0), (540.0, 640.0)


def on_map(x, y):
    return MAP_DST0[0] + (x - MAP_SRC0[0]) * MAP_S, MAP_DST0[1] + (y - MAP_SRC0[1]) * MAP_S


# (era, picture, pin on the relief map in source pixels, where the print lies in world pixels)
DROPS = [('jomon', 'jomon_pot.jpg', (520, 345), (360, 800)),               # Jōmon villages: the north-east
         ('kofun', 'kofun_daisen.jpg', (378, 670), (210, 1150)),            # the Daisen tomb, Osaka
         ('nara', 'nara_daibutsu.jpg', (395, 672), (300, 1640)),           # the Great Buddha, Nara
         ('muromachi', 'muromachi_kinkakuji.jpg', (392, 648), (430, 975)),  # the Golden Pavilion, Kyōto
         ('edo', 'edo_great_wave.jpg', (478, 655), (900, 1395)),          # the Great Wave, off Kanagawa
         ('ships', 'ships_kurofune.jpg', (497, 652), (590, 1655)),        # the black ships at Uraga
         ('showa', 'showa_shinkansen0.jpg', (435, 655), (870, 1640)),     # the first shinkansen on the Tōkaidō
         ('reiwa', 'reiwa_tokyo.jpg', (490, 615), (895, 1135))]           # Tokyo today
DROP_DUR = 0.6
CAP_Y = 560


def _name(k):
    return ERAS[k][2].replace(' PERIOD', '').replace(' ERA', '').replace('THE ', '').split(' ·')[0]


class Scene(KanjiScene):
    paper_seed = 299
    paper_stains = 0.1

    def build(self):
        b = lambda s, n, seed: (lambda d: d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed)))(text_layer(s, FONT_BRUSH_EN, n)[0])
        self.l1, _ = text_layer("JAPAN'S ENTIRE", FONT_HEAD, 74)
        self.l2 = b('HISTORY', 180, 1)
        self.t_90 = at('two minutes')[0]
        self.t_ready = at('Ready')[0]
        self.t_go = at('Go')[0]
        # the drops: from just before "Sixteen" until just before "two minutes"
        t_a, t_b = 0.25, self.t_90 - 0.2 - DROP_DUR
        self.t_drop = [t_a + j * (t_b - t_a) / (len(DROPS) - 1) for j in range(len(DROPS))]
        self.n90 = b('2', 210, 3)
        self.sec, _ = text_layer('MINUTES', FONT_EN_BOLD, 34, tracking=10)
        ss = StrokeSet(W, H)
        enso(ss, 540, 1130, 215, 18, self.t_90 + 0.1, 0.55, seed=5, red=True)
        self.ring = ss
        hand = StrokeSet(40, 400)                            # pivot at the centre of the patch, the hand pointing up
        hand.add(stroke(40, 400, [(20, 200), (20, 30)], 9, ink=0.95, dry=0.3, profile=((0, 1), (0.85, 0.9), (1, 0.2)), seed=6), 0, 1)
        self.hand = hand.render(9)
        rb = StrokeSet(W, 260)
        rb.add(stroke(W, 260, [(RIB_X0 - 30, 130), (540, 126), (RIB_X1 + 30, 130)], 5, ink=0.6, dry=0.5,
                      profile=((0, 0.3), (0.1, 1), (0.9, 1), (1, 0.3)), seed=7), self.t_go, 0.45)
        self.rib = rb
        self.hills = cached('h7_hookhills_v1', lambda: mist_hills(1330, seed=17))['ink']
        self.t_hit = self.t_go
        m = cached('h7_hookmap_v2', _map_layer)
        self.map_rgb, self.map_a = m['rgb'], m['a']
        self.cards = cached('h7_hookcards_v3', _drop_cards)['cards']
        self.cap = []
        for k, *_ in DROPS:
            kj = text_layer(ERAS[k][0], FONT_BRUSH_JP, 84)[0]
            tx = text_layer(f'{_name(k)}  ·  {year_label(ERAS[k][3])}', FONT_EN_BOLD, 40, tracking=3)[0]
            self.cap.append((kj, tx))

    def cam(self, t):
        punch = 0.06 * np.exp(-max(t - self.t_go, 0) * 5) * (t > self.t_go)
        q = t - self.t_ready
        jolt = 10 * np.exp(-q * 7) * np.sin(q * 50) * (q > 0)
        return Cam(540 + jolt, 960, 1.0 + 0.03 * smooth(t / 6) + punch)

    def recede(self, t):
        """0 while the pictures land, 1 once the stopwatch has the stage"""
        return smooth((t - self.t_90 + 0.1) / 0.5)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        r = self.recede(t)
        self.layer(fr, cam, self.hills, opacity=0.45 + 0.25 * r)
        # the map group: the relief map with its pins and prints, sinking back as the stopwatch arrives
        g = 1.0 - 0.1 * r
        G = np.array([[g, 0, (1 - g) * 540], [0, g, (1 - g) * 1130], [0, 0, 1]], np.float32)
        M = cam.matrix() @ G
        op_map = 1.0 - 0.8 * r
        a = cv2.warpAffine(self.map_a, M, (W, H))[..., None] * smooth(t / 0.35) * op_map
        fr.img = fr.img * (1 - a) + cv2.warpAffine(self.map_rgb, M, (W, H)) * a
        for j, (k, _, pin, at_) in enumerate(DROPS):
            u = (t - self.t_drop[j]) / DROP_DUR
            if u <= 0:
                continue
            px, py = on_map(*pin)
            # the leader line and the pin, drawn as the print settles
            lk = smooth((u - 0.75) / 0.5)
            if lk > 0:
                _leader(fr, M, (px, py), at_, lk, 0.55 * op_map)
                pp = _xf(M, px, py)
                land = max(u - 1.0, 0)
                rip = smooth(land / 0.5)
                if 0 < rip < 1:
                    _ring(fr, pp, 10 + 40 * rip, 0.7 * (1 - rip) * op_map)
                _dot(fr, pp, 8 * g * cam.zoom, op_map * lk)
            # the print falls onto the map: from above and larger, easing down, a small settle at the end
            e = ease_out(min(u, 1.0))
            settle = 0.025 * np.exp(-max(u - 1, 0) * 9) * np.sin(max(u - 1, 0) * 24) if u > 1 else 0.0
            sc = (1.0 + 0.45 * (1 - e) + settle) * g * cam.zoom
            x, y = _xf(M, at_[0], at_[1] - 300 * (1 - e) ** 1.6)
            rot = (0.035 if j % 2 else -0.035) + 0.16 * (1 - e) * (-1 if j % 2 else 1)
            lift = 1 - e
            _paste(fr, self.cards[j], x, y, smooth(u / 0.22) * (1 - 0.65 * r), sc, rot,
                   shadow=(10 + 50 * lift, 14 + 70 * lift), shadow_op=0.3 - 0.15 * lift, shadow_blur=10 + 18 * lift)
        # the title, always there
        kit.put(fr, cam, self.l1, 540, 250, INK, 1.0, 1.06 - 0.06 * ease_out(t / 0.5))
        kit.put(fr, cam, self.l2, 540, 395, VERM, 1.0, 1.1 - 0.1 * ease_out(t / 0.6), rot=-0.03)
        # the caption: the era of the print that has just landed
        landed = [j for j in range(len(DROPS)) if t >= self.t_drop[j] + 0.35 * DROP_DUR]
        if landed and r < 1:
            j = landed[-1]
            v = smooth((t - self.t_drop[j] - 0.35 * DROP_DUR) / 0.18)
            kj, tx = self.cap[j]
            wk, wt, gap = kj.shape[1], tx.shape[1], 26
            x0 = 540 - (wk + gap + wt) / 2
            op = v * (1 - r)
            kit.put(fr, cam, kj, x0 + wk / 2, CAP_Y + 12 * (1 - v), INK, op)
            kit.put(fr, cam, tx, x0 + wk + gap + wt / 2, CAP_Y + 4 + 12 * (1 - v), GREY, op)
        # the stopwatch
        f9 = (t - self.t_90 - 0.1) / 0.3
        if f9 > 0:
            self.layer(fr, cam, self.ring.render(t, red=True), color=VERM, opacity=0.95)
            kit.put(fr, cam, self.n90, 540, 1110, INK, smooth(f9), 1 + 0.25 * np.exp(-f9 * 3))
            kit.put(fr, cam, self.sec, 540, 1215, GREY, smooth(f9 - 1))
            ang = 0.0 if t < self.t_go else (t - self.t_go) * 2.2
            kit.put(fr, cam, self.hand, 540, 1130, VERM, smooth(f9 - 0.5), rot=ang)
        if t > self.t_go - 0.05:
            kit.put(fr, SCREEN, self.rib.render(t), 540, RIB_Y, INK, 0.75)
        return fr.img


def _xf(M, x, y):
    return float(M[0, 0] * x + M[0, 1] * y + M[0, 2]), float(M[1, 0] * x + M[1, 1] * y + M[1, 2])


def _dot(fr, p, r, op):
    m = np.zeros((H, W), np.float32)
    cv2.circle(m, (int(p[0] * 4), int(p[1] * 4)), int(r * 4), 1.0, -1, cv2.LINE_AA, shift=2)
    cv2.circle(m, (int(p[0] * 4), int(p[1] * 4)), int(r * 4 * 0.42), 0.0, -1, cv2.LINE_AA, shift=2)
    a = m[..., None] * op
    fr.img = fr.img * (1 - a) + np.array(VERM, np.float32) * a


def _ring(fr, p, r, op):
    m = np.zeros((H, W), np.float32)
    cv2.circle(m, (int(p[0] * 4), int(p[1] * 4)), int(r * 4), 1.0, 3, cv2.LINE_AA, shift=2)
    a = m[..., None] * op
    fr.img = fr.img * (1 - a) + np.array(VERM, np.float32) * a


def _leader(fr, M, pin, card, k, op):
    """a thin ink line from the pin towards the print, drawn out over k = 0..1"""
    p0 = np.array(_xf(M, *pin))
    p1 = np.array(_xf(M, *card))
    p1 = p0 + (p1 - p0) * k
    m = np.zeros((H, W), np.float32)
    cv2.line(m, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), 1.0, 2, cv2.LINE_AA, shift=2)
    a = m[..., None] * op
    fr.img = fr.img * (1 - a) + np.array(INK, np.float32) * a


def _map_layer():
    """the relief map's land, placed in world pixels (RGB and alpha, full frame)"""
    im = cv2.imread(os.path.join(HERE, 'data', 'photos', 'hook_japan_relief.png'), cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
    rgb, a = im[..., 2::-1], im[..., 3]
    # warm it slightly towards the paper so it sits in the ink-wash page
    rgb = rgb * 0.88 + np.array([0.96, 0.92, 0.84], np.float32) * 0.12
    M = np.array([[MAP_S, 0, MAP_DST0[0] - MAP_SRC0[0] * MAP_S], [0, MAP_S, MAP_DST0[1] - MAP_SRC0[1] * MAP_S]], np.float32)
    rgb = cv2.warpAffine(np.ascontiguousarray(rgb), M, (W, H), flags=cv2.INTER_AREA if MAP_S < 1 else cv2.INTER_CUBIC)
    a = cv2.warpAffine(np.ascontiguousarray(a), M, (W, H), flags=cv2.INTER_LINEAR)
    return {'rgb': np.clip(rgb, 0, 1).astype(np.float32), 'a': np.clip(a, 0, 1).astype(np.float32)}


def _drop_cards(h=168):
    """the prints: each real picture cropped to a 4:3 window, on a cream mat"""
    out = []
    for _, f, _, _ in DROPS:
        im = cv2.imread(os.path.join(HERE, 'data', 'photos', f))[..., ::-1].astype(np.float32) / 255
        ih, iw = im.shape[:2]
        w = int(h * 4 / 3)
        s = max(w / iw, h / ih)
        im = cv2.resize(im, (int(iw * s + 1), int(ih * s + 1)), interpolation=cv2.INTER_AREA)
        y0, x0 = (im.shape[0] - h) // 2, (im.shape[1] - w) // 2
        if f == 'nara_daibutsu.jpg':                      # keep the Buddha's face in the window
            y0 = max(0, int(im.shape[0] * 0.08))
        im = im[y0:y0 + h, x0:x0 + w] * 0.92 + np.array([0.95, 0.92, 0.85], np.float32) * 0.08
        m = 10
        card = np.ones((h + 2 * m, w + 2 * m, 3), np.float32) * np.array([0.97, 0.95, 0.9], np.float32)
        card[m:m + h, m:m + w] = im
        out.append(card.astype(np.float32))
    return {'cards': np.stack(out)}


def _paste(fr, card, cx, cy, op, sc, rot, shadow=(8, 12), shadow_op=0.25, shadow_blur=10):
    if op <= 0:
        return
    Hc, Wc = card.shape[:2]
    Mc = cv2.getRotationMatrix2D((Wc / 2, Hc / 2), np.degrees(rot), sc)
    Mc[:, 2] += (cx - Wc / 2, cy - Hc / 2)
    # work in a window around the print only
    r = int(max(Hc, Wc) * sc * 0.75 + shadow_blur * 3 + max(shadow) + 4)
    x0, y0 = max(int(cx) - r, 0), max(int(cy) - r, 0)
    x1, y1 = min(int(cx) + r, W), min(int(cy) + r, H)
    if x1 <= x0 or y1 <= y0:
        return
    Mw = Mc.copy()
    Mw[:, 2] -= (x0, y0)
    size = (x1 - x0, y1 - y0)
    ones = np.ones((Hc, Wc), np.float32)
    a = cv2.warpAffine(ones, Mw, size)
    Ms = Mw.copy()
    Ms[:, 2] += shadow
    sh = blur(cv2.warpAffine(ones, Ms, size), shadow_blur)
    win = fr.img[y0:y1, x0:x1]
    win *= (1 - sh[..., None] * shadow_op * op)
    a = a[..., None] * op
    fr.img[y0:y1, x0:x1] = win * (1 - a) + cv2.warpAffine(card, Mw, size) * a
