"""The hook.  "Why does Japanese turn McDonald's into マクドナルド?  It's not a mistake.  It's a rule."
From frame 1: WHY DOES JAPANESE SAY… and McDonald's dropping in letter by letter over a painted burger.  On the
Japanese word the letters burst apart and six katakana tiles drop into a row, マ ク ド ナ ル ド, each with its romaji
(the added vowels in vermilion); the burger hops.  NOT A MISTAKE. on a slip, then IT'S A RULE! stamped with a jolt."""
import numpy as np

import kit
from draw12 import burger
from engine import FONT_BOLD, FONT_EN_BOLD, GREY, INK, VERM, Cam, cached, ease_out, smooth, text_layer
from scenes.common12 import PALETTE, Tile, Word, chip, drop_y, label, paint, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

ROW = 640
KANA = 'マクドナルド'
ROM = [('ma', (1,)), ('ku', (1,)), ('do', ()), ('na', ()), ('ru', (1,)), ('do', (1,))]


class Scene(KanjiScene):
    paper_seed = 1201

    def build(self):
        self.q = label('WHY DOES JAPANESE SAY…', 40, FONT_EN_BOLD, 8)
        self.word = Word("McDonald's", 150)
        self.burger = cached('r12_burger_v1', lambda: dict(zip(('rgb', 'a'), burger())))
        self.tiles = [Tile(k, 140, PALETTE[j % 4], romaji=r, hot=h) for j, (k, (r, h)) in enumerate(zip(KANA, ROM))]
        self.xs = tile_row(KANA, 540, 140, 14)
        self.mis = text_layer('NOT A MISTAKE.', FONT_BOLD, 96, tracking=4)[0]
        self.rule = text_layer("IT'S A RULE!", FONT_BOLD, 170, tracking=4)[0]
        self.t_jp = JA['makudonarudo']['start']
        self.t_mis = at('not a mistake')[0]
        self.t_rule = at('rule')[0]
        r = np.random.default_rng(3)
        self.burst = [(r.uniform(-1, 1) * 500, r.uniform(-1.2, -0.2) * 500, r.uniform(-1.5, 1.5)) for _ in self.word.letters]
        self.t_hit = self.t_jp

    def cam(self, t):
        q = t - self.t_rule
        shake = 12 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.04 * smooth(t / 7))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # the burger, bobbing; it hops when the word turns Japanese
        hop = 40 * np.sin(np.pi * np.clip((t - self.t_jp) / 0.45, 0, 1))
        paint(fr, cam, self.burger['rgb'], self.burger['a'], 540, 1215 + 8 * np.sin(t * 2.2) - hop, 1.0, 0.85)
        kit.put(fr, cam, self.q, 540, 300, GREY, 1.0)
        # McDonald's, letter by letter, then bursting apart
        b = np.clip((t - self.t_jp + 0.1) / 0.45, 0, 1)
        if b < 1:
            offs, ops, rots = [], [], []
            for k, (dx, dy, rr) in enumerate(self.burst):
                d = drop_y(t, -0.15 + 0.045 * k, 220, 0.4)
                e = ease_out(b)
                offs.append((dx * e, d + dy * e + 900 * e * e))
                ops.append(smooth((t + 0.2 - 0.045 * k) / 0.12) * (1 - b))
                rots.append(rr * e)
            self.word.draw(fr, cam, 540, ROW, INK, 1.0, 1.0, offs, ops, None, rots)
        # the tiles drop in, one per beat of the Japanese word
        for k, (tile, x) in enumerate(zip(self.tiles, self.xs)):
            t0 = self.t_jp + 0.13 * k
            if t < t0:
                continue
            y = ROW + drop_y(t, t0, 300, 0.45)
            sq = 1 + 0.18 * np.exp(-max(t - t0 - 0.3, 0) * 9) * (t > t0 + 0.3)
            tile.draw(fr, cam, x, y, smooth((t - t0) / 0.12), 1.0 * (2 - sq) ** 0.5 * sq, 1.0 / sq)
            tile.draw_rom(fr, cam, x, ROW + 120, smooth((t - t0 - 0.3) / 0.25))
        # NOT A MISTAKE.  IT'S A RULE!
        fm = smooth((t - self.t_mis + 0.05) / 0.25) * (1 - smooth((t - self.t_rule + 0.1) / 0.2))
        if fm > 0:
            chip(fr, cam, self.mis, 540, 880, fm, INK, pulse(t, self.t_mis, 0.2))
        fr_ = (t - self.t_rule + 0.05) / 0.15
        if fr_ > 0:
            chip(fr, cam, self.rule, 540, 880, smooth(fr_), VERM, 1 + 0.6 * np.exp(-fr_ * 2.5))
        return fr.img
