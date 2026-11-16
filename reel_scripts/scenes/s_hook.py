"""The hook.  "Japanese uses three alphabets... in one sentence!  Why?!  Look.  私はコーヒーを飲みます。  'I drink
coffee.'  Kanji.  Hiragana.  Katakana.  All in one line."
Nothing is ever still: big ghost characters 漢 あ ア drift and turn behind everything in their colours, an ink drawing of
a coffee cup steams at the bottom (the sentence is 'I drink coffee'), and an ink splash blooms behind the title.
Frame 1: 3 ALPHABETS slams in, IN 1 SENTENCE?! slides up, and the eleven characters of the sentence fly in from all
over the page, already in their script colours, landing one after another with a small pop.  WHY?! is stamped with a
jolt.  Then each script hops up in turn as Raj names it, with its name tagged under the line, and a vermilion stroke
sweeps under the whole sentence on "all in one line"."""
import numpy as np

import kit
from art import enso
from draw8 import cup, steam
from engine import (FONT_BOLD, FONT_EN_ITALIC, GREY, INK, VERM, Cam, StrokeSet, cached, ease_out, noise, smooth, stroke, text_layer)
from scenes.common import COL, NAME, SENT, Sentence, glyph, label
from scenes.kscene import KanjiScene
from timeline import JA, at

SY = 860
COFFEE = np.array([0.36, 0.22, 0.12], np.float32)
WASH = np.array([0.55, 0.52, 0.48], np.float32)
GHOSTS = [('漢', 'K', 200, 560, 0.0), ('あ', 'H', 880, 640, 1.7), ('ア', 'T', 260, 1430, 3.1), ('漢', 'K', 860, 1520, 4.4)]


class Scene(KanjiScene):
    paper_seed = 811
    paper_stains = 0.08

    def build(self):
        self.l1 = text_layer('JAPANESE USES', FONT_BOLD, 74, tracking=4)[0]
        self.l2 = text_layer('3 ALPHABETS', FONT_BOLD, 190, tracking=2)[0]
        self.l3 = text_layer('IN 1 SENTENCE?!', FONT_BOLD, 96, tracking=3)[0]
        self.why = text_layer('WHY?!', FONT_BOLD, 230, tracking=4)[0]
        self.s = Sentence(88, 90)
        self.rom = label('watashi wa kōhī o nomimasu', 48, FONT_EN_ITALIC, 1)
        self.en = label('“I DRINK COFFEE.”', 40, tracking=6)
        self.ghost = {c: glyph(c, 420) for c, *_ in GHOSTS}
        self.cup = cached('r8_cup_v1', cup)
        # landing order and start points of the flying characters
        r = np.random.default_rng(8)
        self.fly = [(r.uniform(-500, 500), r.uniform(-700, 700), r.uniform(-1.2, 1.2), 0.12 + 0.05 * i) for i in range(len(SENT))]
        ss = StrokeSet(1080, 1920)
        enso(ss, 540, 330, 330, 30, 0.0, 0.45, seed=21, red=False)
        self.splash = ss
        self.t_why = at('Why')[0]
        self.t_look = at('Look')[0]
        self.t_sent = JA['sentence']['start']
        self.t_en = at('I drink')[0]
        self.t_k, self.t_h, self.t_t = JA['kanji']['start'], JA['hiragana']['start'], JA['katakana']['start']
        self.t_line = at('All in one')[0]
        self.t_hit = self.t_why
        sw = StrokeSet(1080, 260)
        sw.add(stroke(1080, 260, [(60, 140), (540, 128), (1020, 138)], 12, ink=0.85, dry=0.4,
                      profile=((0, 0.3), (0.08, 1), (0.9, 0.9), (1, 0.2)), seed=31), self.t_line, 0.5)
        self.sweep = sw

    def cam(self, t):
        q = t - self.t_why
        shake = 9 * np.exp(-max(q, 0) * 6) * np.sin(q * 55) * (q > 0)
        slam = 0.05 * np.exp(-max(t - 0.1, 0) * 6)
        return Cam(540 + shake, 960 + 0.6 * shake, 1.0 + 0.03 * smooth(t / 15) + slam)

    def lit(self, t):
        if t < self.t_look:
            return {s: 1.0 for s in 'KHT'}
        drain = 1 - smooth((t - self.t_look) / 0.3)
        return {s: max(0.25 * drain + 0.0, drain, smooth((t - ts + 0.1) / 0.25)) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t))}

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        # ghost characters drifting behind everything
        for c, s, x, y, ph in GHOSTS:
            kit.put(fr, cam, self.ghost[c], x + 30 * np.sin(t * 0.5 + ph), y + 24 * np.cos(t * 0.4 + ph), COL[s], 0.07,
                    1.0 + 0.05 * np.sin(t * 0.3 + ph), rot=0.12 * np.sin(t * 0.25 + ph))
        # the ink splash behind the title
        self.layer(fr, cam, self.splash.render(t), color=INK, opacity=0.08)
        # the steaming cup
        fc = smooth((t - 0.3) / 0.5)
        if fc > 0:
            cy = 1335 + 40 * (1 - ease_out(min((t - 0.3) / 0.8, 1)))
            k = 0.8
            kit.put(fr, cam, self.cup['wash'], 540, cy, WASH, 0.8 * fc, k)
            kit.put(fr, cam, self.cup['coffee'], 540, cy, COFFEE, 0.9 * fc, k)
            kit.put(fr, cam, self.cup['ink'], 540, cy, INK, 0.9 * fc, k)
            kit.put(fr, cam, steam(t, h=240), 525, cy - 245, GREY, 0.4 * fc)
        # the title
        e1 = ease_out(min(t / 0.35, 1))
        kit.put(fr, cam, self.l1, 540, 230 - 30 * (1 - e1), INK, 0.6 + 0.4 * smooth(t / 0.25))
        sl = (t + 0.12) / 0.3
        if sl > 0:
            kit.put(fr, cam, self.l2, 540, 360, VERM, smooth(sl * 2), 1 + 0.6 * np.exp(-sl * 3.5) * np.cos(sl * 6) * (sl < 1.5), rot=-0.025)
        f3 = smooth((t - 0.2) / 0.3)
        kit.put(fr, cam, self.l3, 540, 495 + 40 * (1 - f3), INK, f3)
        # the sentence: characters fly in, then the scripts hop up as Raj names them
        up = smooth((t - self.t_look) / 0.5)
        lit = self.lit(t)
        xs = self.s.xs(540, 0)
        for i, (c, s) in enumerate(SENT):
            dx, dy, rot, t_land = self.fly[i]
            u = ease_out(np.clip((t - t_land + 0.45) / 0.45, 0, 1))
            if u <= 0:
                continue
            hop = 0.0
            for s2, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t)):
                if s == s2:
                    q = t - ts
                    hop = -38 * np.exp(-max(q, 0) * 5) * np.sin(min(max(q, 0) * 9, np.pi)) * (q > 0)
            col = COL[s] * lit[s] + INK * (1 - lit[s])
            land = t - t_land
            pop = 1 + 0.25 * np.exp(-max(land, 0) * 9) * (land > 0)
            x = xs[i] + dx * (1 - u)
            y = SY + dy * (1 - u) + hop
            kit.put(fr, cam, self.s.g[i], x, y, col, smooth(u * 3), pop * (1 + 0.6 * (1 - u)), rot=rot * (1 - u))
        am = {s: smooth((t - ts) / 0.3) for s, ts in (('K', self.t_k), ('H', self.t_h), ('T', self.t_t))}
        self.s.brackets(fr, cam, 540, SY, xs, am, texts={})
        for j, (s_, ch) in enumerate((('K', '漢'), ('H', 'あ'), ('T', 'ア'))):
            u = am[s_]
            if u > 0:
                lb = label(NAME[s_], 30)
                x, y = (180, 525, 880)[j], 1035
                w = 70 + 16 + lb.shape[1]
                kit.put(fr, cam, glyph(ch, 70), x - w / 2 + 35, y + 12 * (1 - u), COL[s_], u, 1 + 0.3 * np.exp(-u * 4))
                kit.put(fr, cam, lb, x - w / 2 + 86 + lb.shape[1] / 2, y + 12 * (1 - u), COL[s_], u)
        if t > self.t_line - 0.05:
            kit.put(fr, cam, self.sweep.render(t), 540, SY + 112, VERM, 0.8)
        # WHY?! stamped across the cup, with a jolt
        fw = (t - self.t_why + 0.05) / 0.15
        if fw > 0:
            o = smooth(fw) * (1 - smooth((t - self.t_look) / 0.3))
            kit.put(fr, cam, self.why, 540, 1035, VERM, o, 1 + 0.7 * np.exp(-fw * 2.5), rot=-0.07)
        # the reading and the meaning
        fr_ = smooth((t - self.t_sent) / 0.35) * (1 - smooth((t - self.t_k + 0.2) / 0.3))
        kit.put(fr, cam, self.rom, 540, SY + 95, GREY, fr_)
        kit.put(fr, cam, self.en, 540, SY + 150, INK, smooth((t - self.t_en) / 0.3) * (1 - smooth((t - self.t_k + 0.2) / 0.3)))
        return fr.img
