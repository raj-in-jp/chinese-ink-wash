"""The puzzle.  "Now, a little puzzle for you.  Ice cream.  How do you think Japanese says it?  Tell me in the comments."
PUZZLE TIME! slams in; a painted ice-cream cone bobs and wobbles in the middle; ICE CREAM in chunky letters; seven
blank ? tiles pop in one by one (a hint: it takes seven beats in Japanese) and keep pulsing; TELL ME IN THE COMMENTS ↓."""
import numpy as np

import kit
from draw12 import ice_cream
from engine import FONT_BOLD, FONT_EN_BOLD, GREY, INK, VERM, Cam, cached, smooth, text_layer
from scenes.common12 import INDIGO, Tile, Word, chip, drop_y, label, paint, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import at


class Scene(KanjiScene):
    paper_seed = 1208

    def build(self):
        self.head = text_layer('PUZZLE TIME!', FONT_BOLD, 150, tracking=4)[0]
        self.ice = cached('r12_ice_v1', lambda: dict(zip(('rgb', 'a'), ice_cream())))
        self.word = Word('ICE CREAM', 130)
        self.q = [Tile('？', 104, INDIGO) for _ in range(7)]
        self.xs = tile_row('1234567', 540, 104, 14)
        self.hint = label('7 BEATS IN JAPANESE', 34, FONT_EN_BOLD, 8)
        self.cm = label('TELL ME IN THE COMMENTS ↓', 40, FONT_EN_BOLD, 6)
        self.t_pz = at('puzzle')[0]
        self.t_ice = at('Ice cream')[0]
        self.t_how = at('How do you')[0]
        self.t_cm = at('comments')[0]
        self.t_hit = self.t_pz

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 5))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fp = (t - self.t_pz + 0.1) / 0.15
        if fp > 0:
            chip(fr, cam, self.head, 540, 270, smooth(fp), VERM, 1 + 0.5 * np.exp(-fp * 2.5))
        fi = smooth((t - self.t0 - 0.2) / 0.4)
        paint(fr, cam, self.ice['rgb'], self.ice['a'], 540, 700 + 12 * np.sin(t * 2.4) + drop_y(t, self.t0 + 0.2, 300, 0.5), fi, 0.82,
              0.06 * np.sin(t * 1.8))
        n = len(self.word.letters)
        if t > self.t_ice - 0.2:
            offs = [(0, drop_y(t, self.t_ice - 0.2 + 0.04 * k, 180, 0.4)) for k in range(n)]
            ops = [smooth((t - self.t_ice + 0.2 - 0.04 * k) / 0.12) for k in range(n)]
            self.word.draw(fr, cam, 540, 1060, INK, 1.0, 1.0, offs, ops)
        for k, (tl, x) in enumerate(zip(self.q, self.xs)):
            t0 = self.t_how + 0.12 * k
            if t > t0:
                tl.draw(fr, cam, x, 1220 + drop_y(t, t0, 200, 0.4), smooth((t - t0) / 0.1), pulse(t, t0 + 0.3, 0.2) *
                        (1 + 0.05 * np.sin(t * 6 - k * 0.8) * (t > t0 + 0.6)))
        kit.put(fr, cam, self.hint, 540, 1310, GREY, smooth((t - self.t_how - 1.0) / 0.3))
        kit.put(fr, cam, self.cm, 540, 1390, INK, smooth((t - self.t_cm + 0.1) / 0.3), pulse(t, self.t_cm, 0.15))
        return fr.img
