"""倭.  "Why so bold?  For centuries, China had called Japan 'Wa'.  Written with a character that meant something like
'submissive'.  And later, many read it as 'dwarf'."
WHY SO BOLD? at the top; CHINESE RECORDS on a slip; on "Wa" 倭 is brushed in huge, WA under it; on "submissive"
a vermilion tag SUBMISSIVE is stamped across it; on "dwarf" the character shrinks, squashed, down to a tiny 倭,
and DWARF?! pops up beside it."""
import numpy as np

import kit
from engine import FONT_BOLD, FONT_BRUSH_JP, GREY, INK, VERM, Cam, ease_io, smooth, text_layer
from glyphs import typeset
from scenes.common11 import chip, label
from scenes.kscene import KanjiScene
from timeline import JA, at


class Scene(KanjiScene):
    paper_seed = 1102
    paper_stains = 0.0

    def build(self):
        self.q = text_layer('WHY SO BOLD?', FONT_BOLD, 130, tracking=4)[0]
        self.rec = label('FOR CENTURIES, CHINA CALLED JAPAN…', 34)
        self.g = typeset('倭', 520, font=FONT_BRUSH_JP, seed=1110, medians=False, sweep=(0.7, 1))
        self.wa = label('WA', 80, FONT_BOLD, 14)
        self.still = text_layer('倭', FONT_BRUSH_JP, 520)[0]
        self.sub = text_layer('“SUBMISSIVE”', FONT_BOLD, 100, tracking=3)[0]
        self.dwarf = text_layer('“DWARF”?!', FONT_BOLD, 120, tracking=3)[0]
        self.t_cent = at('centuries')[0]
        self.t_wa = JA['wa']['start']
        self.t_sub = at('submissive')[0]
        self.t_dw = at('dwarf')[0]
        self.t_hit = self.t_wa

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 10))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        kit.put(fr, cam, self.q, 540, 290, INK, smooth((t - self.t0 - 0.1) / 0.3), 1 + 0.2 * np.exp(-max(t - self.t0, 0) * 5))
        chip(fr, cam, self.rec, 540, 430, smooth((t - self.t_cent) / 0.3) * (1 - smooth((t - self.t_sub) / 0.3)), INK)
        fk = (t - self.t_wa + 0.4) / 0.6
        if fk > 0:
            sq = ease_io((t - self.t_dw) / 0.6)
            s = 1 - 0.62 * sq
            y = 860 + 260 * sq
            kit.put(fr, cam, self.g.at(fk, soft=0.05) if sq <= 0 else self.still, 540, y, INK, 1.0, s * (1 + 0.1 * np.exp(-fk * 3)), s * (1 - 0.15 * sq) * (1 + 0.1 * np.exp(-fk * 3)))
            kit.put(fr, cam, self.wa, 540, 1190 + 120 * sq, GREY, smooth((t - self.t_wa) / 0.3), 1 - 0.3 * sq)
        fs = (t - self.t_sub + 0.05) / 0.15
        if fs > 0:
            o = smooth(fs) * (1 - smooth((t - self.t_dw + 0.1) / 0.3))
            kit.put(fr, cam, self.sub, 540, 870, VERM, o, 1 + 0.5 * np.exp(-fs * 2.5), rot=-0.12)
        fd = (t - self.t_dw - 0.3) / 0.2
        if fd > 0:
            kit.put(fr, cam, self.dwarf, 540, 720, VERM, smooth(fd), 1 + 0.5 * np.exp(-fd * 2.5), rot=-0.05)
        return fr.img
