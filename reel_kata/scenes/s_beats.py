"""Beats.  "Japanese words are built from small beats.  And almost every beat ends in a vowel.  か き く け こ.  The only
sound that can end without a vowel is 'n'."
JAPANESE IS BUILT FROM BEATS; five empty tile slots pulse like a drum; the formula K + A = カ (the vowel in vermilion);
then カ キ ク ケ コ drop into the slots one per spoken syllable while a vermilion ball bounces from tile to tile; finally
the row lifts and a gold ン tile slams down, glowing: THE ONLY ONE WITH NO VOWEL."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_PLAY, GREY, INK, VERM, Cam, ease_io, smooth, text_layer
from scenes.common12 import GOLD, INDIGO, PALETTE, Tile, chip, drop_y, label, pulse, rbox, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

KANA = 'カキクケコ'
ROM = ['ka', 'ki', 'ku', 'ke', 'ko']
SIZE = 150
ROW0 = 860


class Scene(KanjiScene):
    paper_seed = 1202

    def build(self):
        self.h1 = text_layer('JAPANESE IS BUILT', FONT_BOLD, 100, tracking=4)[0]
        self.h2 = text_layer('FROM BEATS', FONT_BOLD, 130, tracking=4)[0]
        self.vow = text_layer('EVERY BEAT ENDS IN A VOWEL', FONT_BOLD, 70, tracking=3)[0]
        self.tiles = [Tile(k, SIZE, PALETTE[j % 4], romaji=r, hot=(1,)) for j, (k, r) in enumerate(zip(KANA, ROM))]
        self.xs = tile_row(KANA, 540, SIZE, 18)
        slot = rbox(SIZE, SIZE, 24)
        inner = np.zeros_like(slot)
        inner[5:-5, 5:-5] = rbox(SIZE - 10, SIZE - 10, 20)
        self.slot = np.clip(slot - inner, 0, 1)
        self.K = text_layer('K', FONT_PLAY, 150)[0]
        self.A = text_layer('A', FONT_PLAY, 150)[0]
        self.plus, self.eq = label('+', 110, FONT_PLAY, 0), label('=', 110, FONT_PLAY, 0)
        self.ka = Tile('カ', 150, VERM)
        self.n = Tile('ン', 230, GOLD)
        self.nrom = text_layer('n', FONT_PLAY, 90)[0]
        self.only = label('THE ONLY ONE WITHOUT A VOWEL', 36, FONT_EN_BOLD, 6)
        ball = np.zeros((44, 44), np.float32)
        import cv2
        cv2.circle(ball, (22, 22), 18, 1.0, -1, cv2.LINE_AA)
        self.ball = ball
        self.t_beats = at('small beats')[0]
        self.t_every = at('almost every')[0]
        self.t_k = [JA[k]['start'] for k in ROM]
        self.t_only = at('The only')[0]
        self.t_n = at('n', after=self.t_only)[0]
        self.t_hit = self.t_k[0]

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 12))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        f1 = smooth((t - self.t0 - 0.2) / 0.3) * (1 - smooth((t - self.t_every + 0.1) / 0.3))
        kit.put(fr, cam, self.h1, 540, 270, INK, f1)
        kit.put(fr, cam, self.h2, 540, 385, VERM, f1, pulse(t, self.t_beats, 0.15))
        kit.put(fr, cam, self.vow, 540, 300, INK, smooth((t - self.t_every) / 0.3), pulse(t, self.t_every, 0.15))
        lift = ease_io((t - self.t_only) / 0.6)
        row = ROW0 - 300 * lift
        sc = 1 - 0.2 * lift
        # the slots, pulsing like a drum
        fs = smooth((t - self.t_beats + 0.2) / 0.3)
        for k, x in enumerate(self.xs):
            beat = pulse(t, self.t_beats + 0.25 * k, 0.12) if t < self.t_every else 1.0
            xx = 540 + (x - 540) * sc
            kit.put(fr, cam, self.slot, xx, row, GREY, 0.6 * fs * (t < self.t_k[k] + 0.3), beat * sc)
        # the formula K + A = カ
        ff = smooth((t - self.t_every - 0.2) / 0.3) * (1 - smooth((t - self.t_k[0] + 0.3) / 0.3))
        if ff > 0:
            y = 560
            kit.put(fr, cam, self.K, 250, y, INK, ff)
            kit.put(fr, cam, self.plus, 370, y, GREY, ff)
            kit.put(fr, cam, self.A, 480, y, VERM, ff, pulse(t, self.t_every + 0.6, 0.3))
            kit.put(fr, cam, self.eq, 600, y, GREY, ff)
            self.ka.draw(fr, cam, 760, y, ff, pulse(t, self.t_every + 0.9, 0.25))
        # か き く け こ, one per spoken syllable, a ball bouncing across
        for k, (tile, x) in enumerate(zip(self.tiles, self.xs)):
            t0 = self.t_k[k] - 0.08
            if t < t0:
                continue
            xx = 540 + (x - 540) * sc
            y = row + drop_y(t, t0, 240, 0.4) * (1 - lift)
            tile.draw(fr, cam, xx, y, smooth((t - t0) / 0.1), sc * pulse(t, t0 + 0.35, 0.12))
            tile.draw_rom(fr, cam, xx, row + 115 * sc, smooth((t - t0 - 0.25) / 0.2))
        if self.t_k[0] - 0.1 < t < self.t_only:
            k = max(j for j in range(5) if t >= self.t_k[j] - 0.1)
            q = np.clip((t - self.t_k[k] + 0.1) / 0.3, 0, 1)
            x0 = self.xs[k - 1] if k > 0 else self.xs[0] - 160
            x = x0 + (self.xs[k] - x0) * q
            y = row - SIZE / 2 - 30 - 120 * np.sin(np.pi * q) * (k > 0 or q < 1)
            kit.put(fr, cam, self.ball, x, y, VERM, 0.95, 1 + 0.25 * (q > 0.9))
        # ン, the odd one out
        fn = (t - self.t_only - 0.35) / 0.4
        if fn > 0:
            y = 1040 + drop_y(t, self.t_only + 0.35, 380, 0.5)
            glow = 0.6 + 0.4 * np.sin(t * 5)
            self.n.draw(fr, cam, 540, y, smooth(fn * 3), pulse(t, self.t_n, 0.25), glow=glow)
            kit.put(fr, cam, self.only, 540, 1225, INK, smooth((t - self.t_only - 0.8) / 0.3))
            kit.put(fr, cam, self.nrom, 540, 1310, VERM, smooth((t - self.t_n + 0.1) / 0.2), pulse(t, self.t_n, 0.4))
        return fr.img
