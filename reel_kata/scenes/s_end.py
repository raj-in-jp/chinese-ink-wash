"""The ending.  "Follow for more."  またね！
THANK YOU FOR WATCHING! over サ ン キュ ー tiles floating in a wave (sankyū, from this very reel), then the black
brush banner FOLLOW @raj_in_jp and またね！"""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_BRUSH_EN, FONT_BRUSH_JP, FONT_EN_BOLD, H, INK, VERM, W, Cam, StrokeSet, noise, smooth, stroke, text_layer
from scenes.common12 import IVORY, PALETTE, Tile, label, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

KANA = ['サ', 'ン', 'キュ', 'ー']
ROM = ['sa', 'n', 'kyu', 'u']


class Scene(KanjiScene):
    paper_seed = 1206

    def build(self):
        self.tiles = [Tile(k, 150, PALETTE[j % 4], romaji=r) for j, (k, r) in enumerate(zip(KANA, ROM))]
        self.xs = tile_row(KANA, 540, 150, 18)
        self.thanks = text_layer('THANK YOU FOR WATCHING!', FONT_BOLD, 84, tracking=3)[0]
        m = text_layer('またね！', FONT_BRUSH_JP, 130)[0]
        self.matane = m * (0.86 + 0.14 * noise(*m.shape, 6, 2, 4))
        self.follow = label('FOLLOW', 40, FONT_EN_BOLD, 10)
        self.handle = text_layer('@raj_in_jp', FONT_BRUSH_EN, 84)[0]
        self.t_follow = at('Follow for more')[0]
        self.t_mt = JA['matane']['start']
        self.t_hit = self.t_mt
        bn = StrokeSet(W, H)
        bn.add(stroke(W, H, [(250, 1196), (540, 1184), (830, 1192)], 118, ink=0.96, dry=0.45,
                      profile=((0, 0.55), (0.06, 1.0), (0.85, 0.95), (1, 0.5)), seed=171), self.t_follow + 0.05, 0.4)
        self.banner = bn

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 5))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.thanks, 540, 330, INK, smooth((t - self.t0 - 0.1) / 0.3))
        for k, (tl, x) in enumerate(zip(self.tiles, self.xs)):
            f = smooth((t - self.t0 - 0.2 - 0.08 * k) / 0.3)
            y = 560 - 26 * np.sin(t * 4 - k * 0.7) * f
            tl.draw(fr, cam, x, y, f)
            tl.draw_rom(fr, cam, x, y + 120, f)
        fm = (t - self.t_mt + 0.1) / 0.4
        if fm > 0:
            kit.put(fr, cam, self.matane, 540, 920, VERM, smooth(fm), 1 + 0.25 * np.exp(-fm * 2.5), rot=-0.04)
        fb = (t - self.t_follow) / 0.4
        if fb > 0:
            self.layer(fr, cam, self.banner.render(t), opacity=0.96)
            kit.put(fr, cam, self.handle, 540, 1184, IVORY, smooth((t - self.t_follow - 0.2) / 0.3), 1 + 0.1 * np.exp(-fb * 2.5), over=True)
            kit.put(fr, cam, self.follow, 540, 1100, INK, smooth(fb))
        return fr.img
