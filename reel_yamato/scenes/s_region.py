"""The region.  "That's because やまと is older than writing in Japan.  It was the name of one small region.  Today, that's
なら.  The first rulers of Japan lived there, so the name grew to mean the whole country."
The ink-wash sea chart of Japan, seen whole; OLDER THAN WRITING tag.  The camera flies in to the Nara basin; a vermilion
brush ring draws itself round it and a 大和 YAMATO label pops; on なら the pin 奈良 NARA drops in.  On "first rulers" a
small gold crown seal stamps on the basin.  On "the whole country" the camera pulls back while a gold glow spreads over
the land outward from Nara until all of Japan is lit, and 大和 = JAPAN appears."""
import cv2
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_JP, GREY, H, INK, VERM, W, Cam, ease_io, smooth, text_layer
from japanmap import chart_xy, japan_chart
from engine import cached
from scenes.common10 import MapCam, draw_map
from scenes.common12 import GOLD, IVORY, chip, label, mixed, pulse, drop_y
from scenes.kscene import KanjiScene
from timeline import JA, at

NARA = (135.80, 34.55)


def _ring(r=1.0):
    m = np.zeros((300, 300), np.float32)
    cv2.ellipse(m, (150, 150), (120, 95), -15, 0, 360, 1.0, 9, cv2.LINE_AA)
    return cv2.GaussianBlur(m, (0, 0), 1.2)


class Scene(KanjiScene):
    paper_seed = 1302

    def build(self):
        d = cached('r10_japan_v1', japan_chart)
        self.img = d['rgb'].astype(np.float32)
        land = d['land'].astype(np.uint8)
        # distance over the land from Nara, so the glow spreads along the islands
        nx, ny = chart_xy(*NARA)
        seed = np.ones_like(land)
        cv2.circle(seed, (int(nx), int(ny)), 6, 0, -1)
        self.dist = cv2.distanceTransform(seed, cv2.DIST_L2, 5).astype(np.float32)
        self.land = cv2.GaussianBlur(land.astype(np.float32), (0, 0), 1.0)
        self.tag = label('OLDER THAN WRITING', 40, FONT_EN_BOLD, 10)
        self.ring = _ring()
        self.yam = mixed([('大和', 64, FONT_JP, 0), ('YAMATO', 66, FONT_BOLD, 6)], 16)
        self.nara = mixed([('奈良', 58, FONT_JP, 0), ('NARA', 60, FONT_BOLD, 6)], 16)
        self.rulers = label('THE FIRST RULERS', 36, FONT_EN_BOLD, 8)
        self.japan = mixed([('大和', 100, FONT_JP, 0), ('= JAPAN', 110, FONT_BOLD, 6)], 20)
        pin = np.zeros((70, 46), np.float32)
        cv2.circle(pin, (23, 22), 18, 1.0, -1, cv2.LINE_AA)
        cv2.fillPoly(pin, [np.array([(8, 30), (38, 30), (23, 68)], np.int32)], 1.0, cv2.LINE_AA)
        self.pin = cv2.GaussianBlur(pin, (0, 0), 0.8)
        crown = np.zeros((90, 120), np.float32)
        cv2.fillPoly(crown, [np.array([(10, 80), (110, 80), (110, 30), (85, 55), (60, 15), (35, 55), (10, 30)], np.int32)], 1.0, cv2.LINE_AA)
        self.crown = cv2.GaussianBlur(crown, (0, 0), 0.8)
        self.t_older = at('older than')[0]
        self.t_region = at('one small region')[0]
        self.t_nara = JA['nara']['start']
        self.t_rulers = at('first rulers')[0]
        self.t_whole = at('whole country')[0]
        t0 = self.t0
        self.mc = MapCam([(t0, 137.5, 36.8, 0.86), (self.t_region - 0.3, 137.2, 36.4, 0.95), (self.t_region + 1.2, 135.9, 34.6, 1.55),
                          (self.t_rulers + 0.6, 135.85, 34.58, 1.65), (self.t_whole - 0.2, 136.6, 35.6, 1.0), (self.t_whole + 1.4, 137.5, 36.8, 0.86)])
        self.t_hit = self.t_nara

    def cam(self, t):
        return Cam(540, 960, 1.0)

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        M, z = self.mc.matrix(t)
        draw_map(fr, self.img, M)
        # the gold glow spreading over the land from Nara
        g = np.clip((t - self.t_rulers - 0.8) / 3.2, 0, 1)
        if g > 0:
            reach = 60 + 2400 * ease_io(g)
            glow = self.land * np.clip((reach - self.dist) / 120, 0, 1)
            G = cv2.warpAffine(glow, M, (W, H))
            fr.img = fr.img * (1 - 0.45 * G[..., None]) + GOLD * 0.45 * G[..., None]
        nx, ny = chart_xy(*NARA)
        sx, sy = M[0, 0] * nx + M[0, 2], M[1, 1] * ny + M[1, 2]
        kit.put(fr, cam, self.tag, 540, 300, INK, smooth((t - self.t_older + 0.2) / 0.3) * (1 - smooth((t - self.t_region) / 0.3)))
        fr_ = smooth((t - self.t_region - 0.9) / 0.4) * (1 - smooth((t - self.t_whole) / 0.4))
        if fr_ > 0:
            m = self.ring.copy()
            u = np.clip((t - self.t_region - 0.9) / 0.6, 0, 1)
            yy, xx = np.mgrid[0:300, 0:300]
            ang = (np.arctan2(yy - 150, xx - 150) + np.pi) / (2 * np.pi)
            m *= ang <= u
            kit.put(fr, cam, m, sx, sy, VERM, 0.9 * fr_, z / 1.55)
            chip(fr, cam, self.yam, sx, sy - 210 * z / 1.55, fr_ * smooth((t - self.t_region - 1.3) / 0.3), VERM)
        fn = (t - self.t_nara + 0.1) / 0.3
        if fn > 0 and t < self.t_whole + 0.4:
            o = smooth(fn) * (1 - smooth((t - self.t_whole) / 0.4))
            kit.put(fr, cam, self.pin, sx, sy - 30 + drop_y(t, self.t_nara - 0.1, 120, 0.35), VERM, o, over=True)
            chip(fr, cam, self.nara, sx, sy + 190 * z / 1.55, o, INK, pulse(t, self.t_nara, 0.2))
        fc = (t - self.t_rulers - 0.2) / 0.2
        if fc > 0 and t < self.t_whole + 0.4:
            o = smooth(fc) * (1 - smooth((t - self.t_whole) / 0.4))
            cx_ = max(sx - 230, 190)
            kit.put(fr, cam, self.crown, cx_, sy - 20, GOLD, o, 1 + 0.5 * np.exp(-fc * 2.5), over=True)
            kit.put(fr, cam, self.rulers, cx_, sy + 60, INK, o)
        fj = smooth((t - self.t_whole - 0.9) / 0.4)
        if fj > 0:
            chip(fr, cam, self.japan, 540, 300, fj, VERM, pulse(t, self.t_whole + 0.9, 0.25))
        return fr.img
