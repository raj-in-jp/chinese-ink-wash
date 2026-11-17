"""Same sound, new kanji.  "But they kept the old sound, 'wa'.  They just swapped the kanji, for one that means 'harmony'."
SAME SOUND · わ WA with sound rings pulsing on "wa"; the card with 倭 flips over like a coin on "swapped the kanji" and
lands as 和, vermilion; on "harmony" 和 = HARMONY is stamped under it, with the old 倭 small and greyed beside it."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_BRUSH_JP, FONT_JP, GREY, INK, VERM, Cam, ease_io, smooth, text_layer
from scenes.common11 import card, chip, label, mixed
from scenes.kscene import KanjiScene
from timeline import JA, at


class Scene(KanjiScene):
    paper_seed = 1104

    def build(self):
        self.same = text_layer('SAME SOUND', FONT_BOLD, 110, tracking=4)[0]
        self.wa_k = mixed([('わ', 80, FONT_JP, 0), ('WA', 84, FONT_BOLD, 6)], 24)
        self.old = text_layer('倭', FONT_BRUSH_JP, 340)[0]
        self.new = text_layer('和', FONT_BRUSH_JP, 340)[0]
        self.harm = mixed([('和', 100, FONT_JP, 0), ('= HARMONY', 110, FONT_BOLD, 4)], 20)
        self.ring = np.zeros((300, 300), np.float32)
        import cv2
        cv2.circle(self.ring, (150, 150), 130, 1.0, 6, cv2.LINE_AA)
        self.t_snd = at('old sound')[0]
        self.t_wa = JA['wa3']['start']
        self.t_sw = at('swapped')[0]
        self.t_h = at('harmony')[0]
        self.t_hit = self.t_sw

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 7))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        chip(fr, cam, self.same, 540, 300, smooth((t - self.t_snd + 0.1) / 0.3), VERM)
        fw = smooth((t - self.t_snd) / 0.3)
        kit.put(fr, cam, self.wa_k, 540, 450, INK, fw, 1 + 0.3 * np.exp(-max(t - self.t_wa, 0) * 5) * (t > self.t_wa))
        for k in range(3):                                       # sound rings on "wa"
            q = (t - self.t_wa - 0.15 * k) / 0.8
            if 0 < q < 1:
                kit.put(fr, cam, self.ring, 540, 450, VERM, 0.5 * (1 - q), 0.4 + 0.8 * q)
        # the flip: 倭 -> 和
        u = ease_io((t - self.t_sw) / 0.6)
        sx = abs(np.cos(np.pi * u))
        g = self.old if u < 0.5 else self.new
        col = INK if u < 0.5 else VERM
        fc = smooth((t - self.t0 - 0.2) / 0.3)
        card(fr, cam, 540, 860, 460, 520, fc, rim=True)
        kit.put(fr, cam, g, 540, 860, col, fc, max(sx, 0.02), 1.0)
        if u >= 1:
            fo = smooth((t - self.t_sw - 0.6) / 0.3)
            kit.put(fr, cam, self.old, 200, 860, GREY, 0.5 * fo, 0.35)
            kit.put(fr, cam, label('→', 60), 290, 860, GREY, 0.6 * fo)
        fh = (t - self.t_h + 0.05) / 0.2
        if fh > 0:
            kit.put(fr, cam, self.harm, 540, 1230, VERM, smooth(fh), 1 + 0.4 * np.exp(-fh * 2.5))
        return fr.img
