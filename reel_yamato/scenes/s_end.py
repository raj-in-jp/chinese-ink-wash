"""The ending.  "Follow for more."  またね！
大和 large in brush ink with its tiles や ま と floating in a wave under it, then the black brush banner FOLLOW
@raj_in_jp and またね！"""
import numpy as np

import kit
from engine import FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, H, INK, VERM, W, Cam, StrokeSet, noise, smooth, stroke, text_layer
from scenes.common12 import INDIGO, IVORY, TEAL, Tile, label, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at


class Scene(KanjiScene):
    paper_seed = 1307

    def build(self):
        self.k = text_layer('大和', FONT_BRUSH_JP, 260)[0]
        self.tiles = [Tile(k, 120, c, romaji=r) for k, c, r in zip('やまと', (VERM, INDIGO, TEAL), ('ya', 'ma', 'to'))]
        self.xs = tile_row('やまと', 540, 120, 16)
        m = text_layer('またね！', FONT_BRUSH_JP, 130)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, FONT_EN_BOLD, 10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_follow = at('Follow for more')[0]
        self.t_mt = JA['matane']['start']
        self.t_hit = self.t_mt
        bn = StrokeSet(W, H)
        bn.add(stroke(W, H, [(250, 1296), (540, 1284), (830, 1292)], 118, ink=0.96, dry=0.45,
                      profile=((0, 0.55), (0.06, 1.0), (0.85, 0.95), (1, 0.5)), seed=171), self.t_follow + 0.05, 0.4)
        self.banner = bn

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 5))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.k, 540, 420, INK, smooth((t - self.t0 - 0.1) / 0.4))
        for k, (tl, x) in enumerate(zip(self.tiles, self.xs)):
            f = smooth((t - self.t0 - 0.3 - 0.08 * k) / 0.3)
            y = 720 - 24 * np.sin(t * 4 - k * 0.8) * f
            tl.draw(fr, cam, x, y, f)
            tl.draw_rom(fr, cam, x, y + 100, f)
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 1010, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1284, IVORY, smooth((t - self.t_follow - 0.2) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1200, INK, smooth(fb))
        return fr.img
