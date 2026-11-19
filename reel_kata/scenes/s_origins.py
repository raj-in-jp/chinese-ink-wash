"""Not English at all.  "And Paris isn't alone.  A lot of 'weird English' in Japanese isn't English at all.  Energy?
エネルギー.  That's from German, Energie.  Allergy?  アレルギー.  German too.  Bread?  パン.  From Portuguese, pão.
Coffee?  コーヒー.  From Dutch, koffie.  So when Japanese English sounds odd… it might not be English at all!"
"WEIRD ENGLISH"? on a slip.  Then four cards, one after another: the English word in chunky letters; its katakana
tiles drop in as Raj says them; on the source language the English word is struck through with a red brush line and the
real source word pops in with its flag (Germany, Germany, Portugal, the Netherlands).  At the end everything clears and
≠ ENGLISH is stamped with a jolt over the four little flags."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, GREY, INK, VERM, Cam, ease_out, smooth, text_layer
from scenes.common12 import INDIGO, IVORY, PALETTE, TEAL, Tile, Word, chip, drop_y, label, pulse, rbox, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at

BLACK = np.array([0.08, 0.08, 0.08], np.float32)
DE = (BLACK, np.array([0.86, 0.10, 0.12], np.float32), np.array([0.98, 0.80, 0.0], np.float32))
NL = (np.array([0.68, 0.11, 0.16], np.float32), np.array([0.98, 0.97, 0.95], np.float32), np.array([0.13, 0.27, 0.55], np.float32))
PT_G, PT_R, PT_Y = np.array([0.0, 0.40, 0.0], np.float32), np.array([0.86, 0.10, 0.10], np.float32), np.array([0.98, 0.84, 0.0], np.float32)
FW, FH = 150, 100


def flag(fr, cam, kind, x, y, op, s=1.0):
    """a small flag: DE / NL horizontal tricolours, PT green-red with a yellow disc"""
    if op <= 0:
        return
    kit.put(fr, cam, np.ones((FH + 8, FW + 8), np.float32), x + 5, y + 7, INK, 0.25 * op, s)
    if kind in ('DE', 'NL'):
        cols = DE if kind == 'DE' else NL
        for k, c in enumerate(cols):
            kit.put(fr, cam, np.ones((FH // 3 + 1, FW), np.float32), x, y + (k - 1) * FH / 3 * s, c, op, s, over=True)
    else:
        kit.put(fr, cam, np.ones((FH, int(FW * 0.4)), np.float32), x - FW * 0.3 * s, y, PT_G, op, s, over=True)
        kit.put(fr, cam, np.ones((FH, int(FW * 0.6) + 1), np.float32), x + FW * 0.2 * s, y, PT_R, op, s, over=True)
        d = np.zeros((44, 44), np.float32)
        import cv2
        cv2.circle(d, (22, 22), 19, 1.0, -1, cv2.LINE_AA)
        kit.put(fr, cam, d, x - FW * 0.1 * s, y, PT_Y, op, s, over=True)


class Scene(KanjiScene):
    paper_seed = 1207

    def build(self):
        self.head = text_layer('“WEIRD ENGLISH”?', FONT_BOLD, 110, tracking=4)[0]
        self.cards = []
        spec = [('ENERGY', 'enerugi', 'エネルギー', ('e', 'ne', 'ru', 'gi', 'i'), 'Energie', 'DE', 'GERMAN', 'German Energie'),
                ('ALLERGY', 'arerugi', 'アレルギー', ('a', 're', 'ru', 'gi', 'i'), 'Allergie', 'DE', 'GERMAN', 'German too'),
                ('BREAD', 'pan', 'パン', ('pa', 'n'), 'pão', 'PT', 'PORTUGUESE', 'Portuguese'),
                ('COFFEE', 'kohi', 'コーヒー', ('ko', 'o', 'hi', 'i'), 'koffie', 'NL', 'DUTCH', 'Dutch')]
        for j, (en, key, kana, rom, src, fl, lang, cue) in enumerate(spec):
            tiles = [Tile(k, 120, PALETTE[(j + n) % 4], romaji=r) for n, (k, r) in enumerate(zip(kana, rom))]
            self.cards.append(dict(word=Word(en, 150), tiles=tiles, xs=tile_row(kana, 540, 120, 12),
                                   src=text_layer(src, FONT_BOLD, 130, tracking=3)[0], flag=fl, lang=label(lang, 36, FONT_EN_BOLD, 8),
                                   t_ja=JA[key]['start'], t_src=at(cue)[0]))
        for j, c in enumerate(self.cards):
            c['t_in'] = c['t_ja'] - 1.0
            c['t_out'] = self.cards[j + 1]['t_ja'] - 1.2 if j + 1 < len(self.cards) else at('sounds odd')[0] - 0.1
        line = np.zeros((16, 600), np.float32)
        line[4:12] = 1
        self.strike = line
        self.neq = text_layer('≠ ENGLISH', FONT_BOLD, 230, tracking=4)[0]
        self.t_weird = at('weird English')[0]
        self.t_odd = at('sounds odd')[0]
        self.t_neq = at('might not be')[0]
        self.t_hit = self.cards[0]['t_ja']

    def cam(self, t):
        q = t - self.t_neq
        shake = 12 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        return Cam(540 + shake, 960, 1.0 + 0.03 * smooth((t - self.t0) / 22))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fh = smooth((t - self.t_weird + 0.1) / 0.3) * (1 - smooth((t - self.t_odd) / 0.3))
        if fh > 0:
            up = smooth((t - self.cards[0]['t_in'] + 0.35) / 0.4)
            chip(fr, cam, self.head, 540, 760 - 480 * up, fh, INK, (1.45 - 0.45 * up) * pulse(t, self.t_weird, 0.15))
        for c in self.cards:
            w = smooth((t - c['t_in']) / 0.3) * (1 - smooth((t - c['t_out']) / 0.3))
            if w <= 0:
                continue
            # the English word, struck through once the real source is named
            n = len(c['word'].letters)
            offs = [(0, drop_y(t, c['t_in'] + 0.04 * k, 180, 0.4)) for k in range(n)]
            ops = [smooth((t - c['t_in'] - 0.04 * k) / 0.12) for k in range(n)]
            struck = smooth((t - c['t_src']) / 0.3)
            col = INK * (1 - 0.45 * struck) + np.array([0.6, 0.58, 0.55], np.float32) * 0.45 * struck
            c['word'].draw(fr, cam, 540, 540, col, w, 1.0, offs, ops)
            ln = ease_out(np.clip((t - c['t_src']) / 0.3, 0, 1))
            if ln > 0:
                L = self.strike.copy()
                L[:, int(L.shape[1] * ln):] = 0
                kit.put(fr, cam, L, 540, 530, VERM, 0.95 * w, min(1.0, (c['word'].width + 60) / 600), 1.0)
            # the katakana tiles
            for k, (tl, x) in enumerate(zip(c['tiles'], c['xs'])):
                t0 = c['t_ja'] + 0.12 * k
                if t > t0:
                    tl.draw(fr, cam, x, 790 + drop_y(t, t0, 240, 0.4), w * smooth((t - t0) / 0.1), pulse(t, t0 + 0.3, 0.15))
                    tl.draw_rom(fr, cam, x, 900, w * smooth((t - t0 - 0.25) / 0.2))
            # the real source, with its flag
            fs = (t - c['t_src'] + 0.05) / 0.25
            if fs > 0:
                s = 1 + 0.35 * np.exp(-fs * 3)
                flag(fr, cam, c['flag'], 540, 1060 + drop_y(t, c['t_src'] - 0.05, 160, 0.4), w * smooth(fs * 2), s)
                kit.put(fr, cam, c['lang'], 540, 1150, GREY, w * smooth(fs))
                kit.put(fr, cam, c['src'], 540, 1250, INK, w * smooth(fs), s)
        # ≠ ENGLISH, over the four flags
        fe = smooth((t - self.t_odd + 0.1) / 0.3)
        if fe > 0:
            for k, fl in enumerate(('DE', 'DE', 'PT', 'NL')):
                t0 = self.t_odd + 0.15 * k
                flag(fr, cam, fl, 255 + 190 * k, 1080 + drop_y(t, t0, 200, 0.4), smooth((t - t0) / 0.15), 0.9)
            fn = (t - self.t_neq + 0.05) / 0.15
            if fn > 0:
                chip(fr, cam, self.neq, 540, 760, smooth(fn), VERM, 1 + 0.6 * np.exp(-fn * 2.5))
        return fr.img
