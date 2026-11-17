"""Edo becomes Tokyo.  "Then, in 1868, the samurai era ended.  The young emperor moved east.  And Edo got a new name:
Tokyo.  'The eastern capital'.  Because Kyoto, the old capital, was in the west."
The chart wide, Kyoto on the left and Edo on the right.  1868; on "the samurai era ended" Edo Castle fades back;
on "the young emperor" the imperial chrysanthemum appears at Kyoto, and on "moved east" it travels the Tōkaidō road
to Edo, the route drawing behind it.  On "a new name" the label at Edo flips 江戸 EDO → 東京 TOKYO with a stamp; a card
東 = EAST · 京 = CAPITAL; then 西 WEST tags Kyoto and 東 EAST tags Tokyo, with an arrow between them."""
import numpy as np

import kit
from draw10 import castle, crest
from engine import FONT_BOLD, FONT_JP, INK, VERM, Cam, cached, ease_io, smooth, text_layer
from japanmap import chart_xy
from scenes.common10 import PAPER, PLACES, R_TOKAIDO, MapCam, chart, draw_map, draw_route, label, path_px, pin, place_label, route_at
from scenes.kscene import KanjiScene
from scenes.s_capitals import meaning_card
from timeline import JA, at

SCREEN = Cam(540, 960, 1.0)
WASH = np.array([0.80, 0.78, 0.74], np.float32)
GOLD = np.array([0.80, 0.60, 0.16], np.float32)


class Scene(KanjiScene):
    paper_seed = 1003

    def build(self):
        self.img = chart()
        T = self.T = {}
        T['1868'] = at('eighteen sixty-eight')[0]
        T['end'] = at('samurai era')[0]
        T['emp'] = at('young emperor')[0]
        T['east'] = at('moved east')[0]
        T['name'] = at('new name')[0]
        T['tokyo'] = JA['tokyo3']['start']
        T['cap'] = at('eastern capital')[0]
        T['west'] = JA['kyoto2']['start']
        self.cam_ = MapCam([(self.t0, 137.7, 35.3, 1.0), (self.t1, 137.8, 35.3, 1.08)], cy=1050)
        self.road = path_px(R_TOKAIDO)
        self.castle = cached('r10_castle_v1', castle)
        self.crest = cached('r10_crest_v1', lambda: {'d': crest()})['d']
        self.y1868 = text_layer('1868', FONT_BOLD, 130, tracking=4)[0]
        self.end = label('THE SAMURAI ERA ENDS', 40, FONT_BOLD, 4)
        self.emp = label('THE EMPEROR MOVES EAST', 40, FONT_BOLD, 4)
        g = lambda c: text_layer(c, FONT_JP, 130)[0]
        self.card = [(g('東'), label('EAST', 56, FONT_BOLD, 4)), (g('京'), label('CAPITAL', 56, FONT_BOLD, 4))]
        self.arrow = text_layer('→', FONT_JP, 120)[0] if False else None
        self.t_hit = T['tokyo']

    def render(self, t):
        T = self.T
        fr = self.frame(SCREEN)
        q = t - T['tokyo']
        shake = 8 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        M, z = self.cam_.matrix(t)
        M = M.copy()
        M[0, 2] += shake
        draw_map(fr, self.img, M, 1.0)
        to_s = lambda key: np.array(chart_xy(*PLACES[key])) * M[0, 0] + M[:, 2]
        k, e = to_s('kyoto'), to_s('edo')
        # Edo Castle, fading back as the samurai era ends
        fc = 1 - 0.75 * smooth((t - T['end']) / 0.6)
        kit.put(fr, SCREEN, self.castle['wash'], e[0], e[1] - 95, WASH, fc, 0.6)
        kit.put(fr, SCREEN, self.castle['ink'], e[0], e[1] - 95, INK, fc, 0.6)
        pin(fr, SCREEN, k[0], k[1], 1.0, 1.2)
        pin(fr, SCREEN, e[0], e[1], 1.0, 1.2)
        place_label(fr, SCREEN, '京都  KYOTO', k[0], k[1] + 70, 1.0, 40)
        # the emperor's road east
        u = ease_io((t - T['east']) / 1.8)
        draw_route(fr, M, self.road, u, width=10, dash=(18, 10), color=VERM)
        fe = smooth((t - T['emp']) / 0.3)
        if fe > 0:
            p = route_at(self.road * M[0, 0] + M[:, 2], u)[0] if u > 0 else k
            kit.put(fr, SCREEN, self.crest, p[0], p[1] - 90, GOLD, fe, 0.8 * (1 + 0.3 * np.exp(-max(t - T['emp'], 0) * 5)))
        # Edo's label flips to Tokyo
        flip = smooth((t - T['tokyo'] + 0.05) / 0.2)
        if flip < 1:
            place_label(fr, SCREEN, '江戸  EDO', e[0], e[1] + 70, 1 - flip, 40)
        if flip > 0:
            pop = 1 + 0.6 * np.exp(-max(q, 0) * 4) * (q > 0)
            place_label(fr, SCREEN, '東京  TOKYO', e[0], e[1] + 70, flip, int(40 * pop), VERM)
        # the headline chips
        for g, ts, te in ((self.y1868, T['1868'], T['end']), (self.end, T['end'], T['emp']), (self.emp, T['emp'], T['name'])):
            f = smooth((t - ts) / 0.25) * (1 - smooth((t - te + 0.1) / 0.25))
            if f > 0:
                kit.put(fr, SCREEN, kit.box(g.shape[0] + 30, g.shape[1] + 60, 6), 540, 360, PAPER, 0.9 * f, over=True)
                kit.put(fr, SCREEN, g, 540, 360, VERM if g is self.y1868 else INK, f, 1 + 0.2 * np.exp(-max(t - ts, 0) * 5))
        # 東 = EAST · 京 = CAPITAL
        fc2 = (t - T['cap'] + 0.1) / 0.3
        meaning_card(fr, self.card, 420, smooth(fc2) * (1 - smooth((t - T['west'] + 0.2) / 0.3)), 1 + 0.2 * np.exp(-max(fc2, 0) * 3))
        # west and east
        fw = smooth((t - T['west']) / 0.3)
        if fw > 0:
            place_label(fr, SCREEN, '西  WEST · OLD CAPITAL', k[0], k[1] - 150, fw, 34, INK)
            fe2 = smooth((t - T['west'] - 0.6) / 0.3)
            place_label(fr, SCREEN, '東  EAST · NEW CAPITAL', e[0], e[1] - 210, fe2, 34, VERM)
        return fr.img
