"""The mystery.  "And what does やまと itself mean?  Nobody knows for sure.  Maybe 'mountain gate'.  Maybe 'the place of
the mountains'."
On やまと the three tiles bounce in at the top with a big wobbling vermilion ?; NOBODY KNOWS FOR SURE is stamped.  Then
two painted theory cards drop in, one after the other, each tagged MAYBE: 山門 MOUNTAIN GATE (two peaks with a pass and a
path through it) and 山処 PLACE OF THE MOUNTAINS (a village in a valley ringed by mountains)."""
import numpy as np

import kit
from draw13 import gate_view, valley_view
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_JP, FONT_PLAY, GREY, INK, VERM, Cam, cached, smooth, text_layer
from scenes.common12 import INDIGO, TEAL, Tile, card, chip, drop_y, label, mixed, paint, pulse, tile_row
from scenes.kscene import KanjiScene
from timeline import JA, at


def _rgba(fn):
    def go():
        rgb, a = fn()
        return {'rgb': rgb, 'a': a}
    return go


class Scene(KanjiScene):
    paper_seed = 1305

    def build(self):
        self.tiles = [Tile(k, 120, c, romaji=r) for k, c, r in zip('やまと', (VERM, INDIGO, TEAL), ('ya', 'ma', 'to'))]
        self.txs = tile_row('やまと', 420, 120, 14)
        self.q = text_layer('?', FONT_PLAY, 260)[0]
        self.nobody = text_layer('NOBODY KNOWS FOR SURE', FONT_BOLD, 84, tracking=3)[0]
        self.views = [cached('r13_gate_v1', _rgba(gate_view)), cached('r13_valley_v1', _rgba(valley_view))]
        self.names = [mixed([('山門', 60, FONT_JP, 0), ('MOUNTAIN GATE', 50, FONT_BOLD, 4)], 16),
                      mixed([('山処', 56, FONT_JP, 0), ('PLACE OF THE MOUNTAINS', 36, FONT_BOLD, 2)], 12)]
        self.maybe = text_layer('MAYBE?', FONT_BOLD, 64, tracking=4)[0]
        self.t_ya = JA['yamato3']['start']
        self.t_nobody = at('Nobody knows')[0]
        self.t_th = [at('mountain gate')[0], at('place of the mountains')[0]]
        self.t_hit = self.t_ya

    def cam(self, t):
        return Cam(540, 960, 1.0 + 0.03 * smooth((t - self.t0) / 9))

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        for k, (tl, x) in enumerate(zip(self.tiles, self.txs)):
            tk = self.t_ya + 0.15 * k
            if t > tk:
                tl.draw(fr, cam, x, 300 + drop_y(t, tk, 220, 0.4), smooth((t - tk) / 0.1), pulse(t, tk + 0.3, 0.2))
        fq = (t - self.t0 - 0.15) / 0.3      # the ? pops in as the scene opens: no empty paper before やまと
        if fq > 0:
            kit.put(fr, cam, self.q, 820, 300, VERM, smooth(fq), (1 + 0.5 * np.exp(-fq * 2.5)) * (1 + 0.05 * np.sin(t * 5)), rot=0.12 * np.sin(t * 2.5))
        fn = (t - self.t_nobody + 0.05) / 0.2
        if fn > 0:
            chip(fr, cam, self.nobody, 540, 500, smooth(fn), VERM, 1 + 0.4 * np.exp(-fn * 2.5))
        for j in range(2):
            t0 = self.t_th[j] - 0.25
            f = (t - t0) / 0.35
            if f <= 0:
                continue
            y = (830, 1180)[j] + drop_y(t, t0, 220, 0.45)
            o = smooth(f)
            x = 540
            card(fr, cam, x, y, 980, 330, o, rim=True)
            v = self.views[j]
            paint(fr, cam, v['rgb'], v['a'], x - 255, y, o, 0.72)
            kit.put(fr, cam, self.names[j], x + 215, y - 30, INK, o)
            fm = (t - t0 - 0.35) / 0.2
            if fm > 0:
                kit.put(fr, cam, self.maybe, x + 200, y + 70, VERM, smooth(fm), 1 + 0.4 * np.exp(-fm * 3), rot=-0.06)
        return fr.img
