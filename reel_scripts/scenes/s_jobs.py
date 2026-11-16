"""Each script has a job.  "And each one has a job.  Kanji carries the meaning.  Watashi, 'I'.  Nomu, 'drink'.
Hiragana handles the grammar.  Wa, o, and the polite ending, masu.  Katakana writes foreign words.  Kōhī comes from the
Dutch word for coffee."
The sentence stays small at the top with only the script being explained in colour.  Under it, a big two-line header
(KANJI / = MEANING, then HIRAGANA / = GRAMMAR, then KATAKANA / = FOREIGN WORDS) slides in for each part, and:
  kanji     two cards: 私 with a little brushed figure = "I", 飲 with the steaming cup = "drink"
  hiragana  the sentence large, は を ます hopping up in orange as Raj says them, each with its role under it
  katakana  koffie (Dutch, with its flag) → コーヒー, which pops in green on "kōhī"."""
import numpy as np

import kit
from draw8 import cup, dutch_flag, person, steam
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_EN_ITALIC, GREY, INK, VERM, Cam, cached, ease_io, ease_out, smooth, text_layer
from scenes.common import COL, GREEN, ORANGE, BLUE, SENT, Sentence, glyph, label, legend
from scenes.kscene import KanjiScene
from timeline import JA, at

CARD = np.array([0.965, 0.94, 0.88], np.float32)
COFFEE = np.array([0.36, 0.22, 0.12], np.float32)
WASH = np.array([0.55, 0.52, 0.48], np.float32)


class Scene(KanjiScene):
    paper_seed = 812

    def build(self):
        self.small = Sentence(60, 64)
        self.big = Sentence(88, 90)
        self.head = {s: (text_layer(n, FONT_BOLD, 140, tracking=4)[0], text_layer(j, FONT_BOLD, 84, tracking=3)[0])
                     for s, n, j in (('K', 'KANJI', '= MEANING'), ('H', 'HIRAGANA', '= GRAMMAR'), ('T', 'KATAKANA', '= FOREIGN WORDS'))}
        self.job = text_layer('EACH ONE HAS A JOB', FONT_BOLD, 110, tracking=3)[0]
        self.box, self.rim = kit.box(470, 400, 2.5), kit.rim(470, 400, inset=6, t=3)
        self.k1, self.k2 = glyph('私', 170), glyph('飲', 170)
        self.fig = person(130)
        self.cup = cached('r8_cup_v1', cup)
        self.w1, self.w2 = label('“I”', 64, FONT_EN_ITALIC, 1), label('“drink”', 64, FONT_EN_ITALIC, 1)
        self.r1, self.r2 = label('watashi', 34, FONT_EN_ITALIC, 1), label('nomu', 34, FONT_EN_ITALIC, 1)
        self.roles = {1: label('TOPIC', 34), 6: label('OBJECT', 34), 9: label('POLITE', 34)}
        self.koffie = label('koffie', 80, FONT_EN_ITALIC, 1)
        self.dutch = label('DUTCH', 30, tracking=8)
        self.arrow = text_layer('→', FONT_EN_BOLD, 110)[0]
        self.kohi = glyph('コーヒー', 150)
        self.kohi_r = label('kōhī = coffee', 50, FONT_EN_ITALIC, 1)
        self.flag = dutch_flag(120, 80)
        self.t_job = at('each one has')[0]
        self.t_k, self.t_h, self.t_t = JA['kanji2']['start'], JA['hiragana2']['start'], JA['katakana2']['start']
        self.t_wat, self.t_nomu = JA['watashi']['start'], JA['nomu']['start']
        self.t_wa, self.t_o, self.t_masu = JA['wa']['start'], JA['o']['start'], JA['masu']['start']
        self.t_kohi, self.t_dutch = JA['kohi']['start'], at('Dutch')[0]
        self.t_hit = self.t_k

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.02 * smooth((t - self.t0) / 18))

    def part(self, t):
        """which script is being explained, and how far in (0..1 fade in, 1..0 fade out)"""
        bounds = [('K', self.t_k, self.t_h), ('H', self.t_h, self.t_t), ('T', self.t_t, self.t1 + 5)]
        return [(s, smooth((t - a + 0.02) / 0.3) * (1 - smooth((t - b + 0.3) / 0.25))) for s, a, b in bounds]

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        parts = self.part(t)
        act = max(parts, key=lambda p: p[1])
        legend(fr, t, self.t0 - 1, active=act[0] if act[1] > 0.5 else None)
        # the sentence, small, at the top: the script being explained in colour
        lit = {s: v for s, v in parts}
        bigmode = smooth((t - self.t_h) / 0.4) * (1 - smooth((t - self.t_t + 0.1) / 0.3))
        self.small.draw(fr, cam, 540, 300, t, lit=lit, op=1 - bigmode)
        # EACH ONE HAS A JOB
        fj = smooth((t - self.t_job + 0.1) / 0.3) * (1 - smooth((t - self.t_k + 0.2) / 0.3))
        if fj > 0:
            kit.put(fr, cam, self.job, 540, 800, VERM, fj, 1 + 0.25 * np.exp(-max(t - self.t_job, 0) * 5))
        # the header of each part
        for s, v in parts:
            if v <= 0:
                continue
            n, j = self.head[s]
            kit.put(fr, cam, n, 540 - 60 * (1 - v), 480, COL[s], v)
            kit.put(fr, cam, j, 540 + 60 * (1 - v), 590, INK, v)
        vk, vh, vt = (v for _, v in parts)
        # KANJI: 私 = I, 飲 = drink
        if vk > 0:
            for j, (x, g, ts, wd, rd) in enumerate(((290, self.k1, self.t_wat, self.w1, self.r1), (790, self.k2, self.t_nomu, self.w2, self.r2))):
                f = (t - ts + 0.15) / 0.35
                if f <= 0:
                    continue
                o = smooth(f) * vk
                y = 1010 + 50 * (1 - ease_out(min(f, 1)))
                kit.card(fr, cam, self.box, self.rim, x, y, o, color=CARD)
                kit.put(fr, cam, g, x, y - 125, BLUE, o, 1 + 0.25 * np.exp(-f * 3))
                if j == 0:
                    kit.put(fr, cam, self.fig, x, y + 80, INK, 0.85 * o)
                else:
                    kit.put(fr, cam, self.cup['wash'], x, y + 90, WASH, 0.8 * o, 0.3)
                    kit.put(fr, cam, self.cup['coffee'], x, y + 90, COFFEE, 0.9 * o, 0.3)
                    kit.put(fr, cam, self.cup['ink'], x, y + 90, INK, 0.9 * o, 0.3)
                    kit.put(fr, cam, steam(t, w=140, h=80), x - 6, y + 20, GREY, 0.3 * o)
                kit.put(fr, cam, wd, x, y + 195, INK, o)
                kit.put(fr, cam, rd, x, y - 15, GREY, o * smooth(f - 1))
        # HIRAGANA: the sentence large, は を ます hop up, each with its role
        if vh > 0:
            hops = {1: self.t_wa, 6: self.t_o, 8: self.t_masu, 9: self.t_masu + 0.08, 10: self.t_masu + 0.16}
            xs = self.big.xs(540, 0)
            for i, (c, s) in enumerate(SENT):
                q = t - hops.get(i, 1e9)
                hop = -45 * np.exp(-max(q, 0) * 4) * np.sin(min(max(q, 0) * 8, np.pi)) * (q > 0)
                on = s == 'H'
                col = ORANGE if on else GREY
                kit.put(fr, cam, self.big.g[i], xs[i], 980 + hop, col, vh * (1.0 if on else 0.55), 1 + (0.15 if on and q > 0 else 0))
            for i, lb in self.roles.items():
                ts = {1: self.t_wa, 6: self.t_o, 9: self.t_masu}[i]
                f = smooth((t - ts) / 0.3) * vh
                if f > 0:
                    kit.put(fr, cam, kit.box(40, 4, 1.0), xs[i], 1070, ORANGE, f)
                    kit.put(fr, cam, lb, xs[i], 1120, ORANGE, f)
        # KATAKANA: koffie (Dutch) -> コーヒー
        if vt > 0:
            fd = smooth((t - self.t_dutch + 0.1) / 0.35) * vt
            fk = (t - self.t_kohi + 0.1) / 0.35
            if fk > 0:
                o = smooth(fk) * vt
                self.plate(fr, cam, 540, 1050, 900, 360, o)
                kit.put(fr, cam, self.kohi, 540 + 200 * fd, 1000, GREEN, o, (1 + 0.3 * np.exp(-fk * 3)) * (1 - 0.25 * fd))
                kit.put(fr, cam, self.kohi_r, 540 + 200 * fd, 1110, INK, smooth(fk - 0.8) * vt)
            fcp = smooth((t - self.t_t) / 0.5) * vt
            if fcp > 0:
                kit.put(fr, cam, self.cup['wash'], 540, 1360, WASH, 0.8 * fcp, 0.6)
                kit.put(fr, cam, self.cup['coffee'], 540, 1360, COFFEE, 0.9 * fcp, 0.6)
                kit.put(fr, cam, self.cup['ink'], 540, 1360, INK, 0.9 * fcp, 0.6)
                kit.put(fr, cam, steam(t, h=170), 528, 1180, GREY, 0.3 * fcp)
            if fd > 0:
                rgb, a = self.flag
                kit.put(fr, cam, self.koffie, 230, 1000, INK, fd)
                kit.put(fr, cam, self.arrow, 470, 1000, VERM, fd)
                kit.put(fr, cam, self.dutch, 230, 1080, GREY, fd)
                # the flag, pasted as colour
                x0, y0 = 230 - 60, 870
                win = fr.img[y0:y0 + 80, x0:x0 + 120]
                win[:] = win * (1 - fd) + rgb * fd
        return fr.img
