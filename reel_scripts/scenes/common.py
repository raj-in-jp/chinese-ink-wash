"""What every scene of reel 8 shares: the three script colours, the sentence 私はコーヒーを飲みます set character by
character (each script lighting up in its own colour, brackets and labels under each group, dividers between the
groups), and the legend along the top (漢 KANJI · あ HIRAGANA · ア KATAKANA) that lights the script being talked
about, so every scene links back to the same three."""
import numpy as np

import kit
from engine import FONT_EN_BOLD, FONT_JP, GREY, INK, VERM, Cam, smooth, text_layer

SCREEN = Cam(540, 960, 1.0)
BLUE = np.array([0.15, 0.33, 0.64], np.float32)        # kanji
ORANGE = np.array([0.86, 0.45, 0.10], np.float32)      # hiragana
GREEN = np.array([0.16, 0.52, 0.30], np.float32)       # katakana
COL = {'K': BLUE, 'H': ORANGE, 'T': GREEN}
NAME = {'K': 'KANJI', 'H': 'HIRAGANA', 'T': 'KATAKANA'}
SENT = [('私', 'K'), ('は', 'H'), ('コ', 'T'), ('ー', 'T'), ('ヒ', 'T'), ('ー', 'T'), ('を', 'H'), ('飲', 'K'), ('み', 'H'),
        ('ま', 'H'), ('す', 'H')]
# the words (where a reader's eye splits the line): 私 | は | コーヒー | を | 飲みます
WORDS = [(0, 1), (1, 2), (2, 6), (6, 7), (7, 11)]
# the script groups (where the colour changes): 私 | は | コーヒー | を | 飲 | みます
GROUPS = [(0, 1, 'K'), (1, 2, 'H'), (2, 6, 'T'), (6, 7, 'H'), (7, 8, 'K'), (8, 11, 'H')]

_cache = {}


def glyph(c, size, font=FONT_JP):
    k = (c, size, font)
    if k not in _cache:
        _cache[k] = text_layer(c, font, size)[0]
    return _cache[k]


def label(s, size=30, font=FONT_EN_BOLD, tracking=6):
    k = ('L', s, size, font, tracking)
    if k not in _cache:
        _cache[k] = text_layer(s, font, size, tracking=tracking)[0]
    return _cache[k]


def mix(a, b, u):
    return a * (1 - u) + b * u


class Sentence:
    """the sentence at (cx, cy): `lit` = {script: 0..1} colour amount, `gap` = extra px between words (0 = no spaces),
    `div` = 0..1 the vermilion dividers between the words dropping in"""

    def __init__(self, size=84, adv=88):
        self.size, self.adv = size, adv
        self.g = [glyph(c, size) for c, _ in SENT]

    def xs(self, cx, gap):
        w = self.adv * len(SENT) + gap * (len(WORDS) - 1)
        x, out = cx - w / 2 + self.adv / 2, []
        for wi, (a, b) in enumerate(WORDS):
            for i in range(a, b):
                out.append(x)
                x += self.adv
            x += gap
        return out

    def draw(self, fr, cam, cx, cy, t, lit=None, gap=0.0, div=0.0, op=1.0, pulse=None, scale=1.0):
        lit = lit or {}
        xs = self.xs(cx, gap)
        for i, (c, s) in enumerate(SENT):
            col = mix(INK, COL[s], float(np.clip(lit.get(s, 0.0), 0, 1)))
            sc = scale
            if pulse is not None and pulse[0] == s:              # a small bounce as a script lights up
                sc *= 1 + 0.12 * np.exp(-max(t - pulse[1], 0) * 6) * (t > pulse[1])
            kit.put(fr, cam, self.g[i], cx + (xs[i] - cx) * scale, cy, col, op, sc)
        if div > 0:
            for wi in range(len(WORDS) - 1):
                b = WORDS[wi][1]
                x = cx + ((xs[b - 1] + xs[b]) / 2 - cx) * scale
                u = smooth(div * 1.6 - wi * 0.15)
                if u > 0:
                    h = int(self.size * 1.3)
                    kit.put(fr, cam, kit.box(h, 8, 1.2), x, cy - 30 * (1 - u), VERM, 0.9 * u * op)
        return xs

    def brackets(self, fr, cam, cx, cy, xs, amounts, y_off=78, op=1.0, texts=None, scale=1.0):
        """a coloured underline under each group of a script, with its name under it"""
        texts = NAME if texts is None else texts
        seen = set()
        for a, b, s in GROUPS:
            u = float(amounts.get(s, 0.0))
            if u <= 0:
                continue
            x0 = cx + (xs[a] - self.adv * 0.45 - cx) * scale
            x1 = cx + (xs[b - 1] + self.adv * 0.45 - cx) * scale
            w = max(int((x1 - x0) * smooth(u * 1.5)), 2)
            kit.put(fr, cam, kit.box(10, w, 1.0), x0 + w / 2, cy + y_off, COL[s], 0.9 * op)
            if s not in seen and texts.get(s):
                seen.add(s)
                kit.put(fr, cam, label(texts[s], 26), (x0 + x1) / 2, cy + y_off + 36, COL[s], smooth(u * 2 - 0.6) * op)


_LEG = [('K', '漢', 'KANJI'), ('H', 'あ', 'HIRAGANA'), ('T', 'ア', 'KATAKANA')]
LEG_Y = 150


def legend(fr, t, t0, active=None, op=1.0):
    """漢 KANJI · あ HIRAGANA · ア KATAKANA along the top, the active one in its colour and a little larger"""
    f = smooth((t - t0) / 0.4) * op
    if f <= 0:
        return
    for j, (s, ch, nm) in enumerate(_LEG):
        x = 210 + 330 * j
        on = 1.0 if active is None or s in active else 0.0
        col = mix(GREY, COL[s], on)
        sc = 1.0 + 0.12 * on * (active is not None)
        lb = label(nm, 26)
        w = 52 + 14 + lb.shape[1]
        kit.put(fr, SCREEN, glyph(ch, 52), x - w / 2 + 26, LEG_Y, col, f * (0.45 + 0.55 * on), sc)
        kit.put(fr, SCREEN, lb, x - w / 2 + 66 + lb.shape[1] / 2, LEG_Y + 2, col, f * (0.45 + 0.55 * on), sc)
