"""The old capitals, on the Japan chart.
  "Japan's first great capital was Nara, in 710.  Then in 794, the emperor moved to a new city, Kyoto.  Its name simply
   means 'capital city'.  And it stayed the capital for over a thousand years."
      the camera close on the Kansai: a pin and 奈良 NARA, 710; the road draws itself to Kyoto: 京都 KYOTO, 794;
      a card 京 = CAPITAL · 都 = CITY; a bar 794 → 1868 fills: OVER 1,000 YEARS
  "Meanwhile, far to the east, there was a small castle town called Edo.  Its name means 'the door of the bay'.  In 1603,
   the samurai rulers made Edo their base.  By the 1700s, it had a million people.  Maybe the biggest city in the world."
      the camera glides east; Edo Castle rises on the bay: 江戸 EDO; a card 江 = BAY · 戸 = DOOR; 1603 THE SHOGUN'S CITY;
      little houses spread out round the castle as a counter runs to 1,000,000 PEOPLE; BIGGEST CITY IN THE WORLD?"""
import numpy as np

import kit
from draw10 import castle, house
from engine import FONT_BOLD, FONT_JP, GREY, INK, VERM, Cam, cached, ease_io, ease_out, smooth, text_layer
from japanmap import chart_xy
from scenes.common10 import PAPER, PLACES, R_NARA_KYOTO, MapCam, chart, draw_map, draw_route, label, path_px, pin, place_label
from scenes.kscene import KanjiScene
from timeline import JA, at

SCREEN = Cam(540, 960, 1.0)
WASH = np.array([0.80, 0.78, 0.74], np.float32)


def meaning_card(fr, pairs, y, o, pop):
    """[(kanji glyph, label)] side by side on a paper card"""
    if o <= 0:
        return
    n = len(pairs)
    w = 300 * n + 40
    kit.put(fr, SCREEN, kit.box(260, w, 10), 540 + 8, y + 12, INK, 0.2 * o, pop)
    kit.put(fr, SCREEN, kit.box(250, w, 4), 540, y, PAPER, o, pop, over=True)
    kit.put(fr, SCREEN, kit.rim(250, w, inset=8, t=3), 540, y, VERM, 0.8 * o, pop)
    for j, (g, lb) in enumerate(pairs):
        x = 540 + (j - (n - 1) / 2) * 300 * pop
        kit.put(fr, SCREEN, g, x, y - 30 * pop, INK, o, pop)
        kit.put(fr, SCREEN, lb, x, y + 85 * pop, VERM, o, pop)


class Scene(KanjiScene):
    paper_seed = 1002

    def build(self):
        self.img = chart()
        T = self.T = {}
        T['nara'] = JA['nara']['start']
        T['794'] = at('seven ninety-four')[0]
        T['kyoto'] = JA['kyoto']['start']
        T['cap'] = at('capital city')[0]
        T['1000'] = at('thousand years')[0]
        T['mean'] = at('Meanwhile')[0]
        T['castle'] = at('small castle')[0]
        T['edo'] = JA['edo']['start']
        T['door'] = at('door of')[0]
        T['1603'] = at('sixteen-oh-three')[0]
        T['1700'] = at('seventeen-hundreds')[0]
        T['million'] = at('million')[0]
        T['big'] = at('biggest city')[0]
        self.cam_ = MapCam([(self.t0, 135.8, 34.85, 1.6), (T['794'], 135.8, 34.85, 1.6), (T['cap'] - 0.2, 135.78, 34.95, 1.75),
                            (T['mean'] + 0.2, 135.8, 34.95, 1.6), (T['castle'] - 0.1, 139.5, 35.55, 1.5), (T['1700'], 139.65, 35.62, 1.7),
                            (self.t1, 139.72, 35.66, 2.0)], cy=1050)
        self.path = path_px(R_NARA_KYOTO)
        g = lambda c: text_layer(c, FONT_JP, 130)[0]
        self.card_kyoto = [(g('京'), label('CAPITAL', 56, FONT_BOLD, 4)), (g('都'), label('CITY', 56, FONT_BOLD, 4))]
        self.card_edo = [(g('江'), label('BAY', 56, FONT_BOLD, 4)), (g('戸'), label('DOOR', 56, FONT_BOLD, 4))]
        bold = lambda s, n: text_layer(s, FONT_BOLD, n, tracking=4)[0]
        self.years = {k: bold(k, 120) for k in ('710', '794', '1603')}
        self.k1000 = bold('OVER 1,000 YEARS', 64)
        self.shogun = label("THE SHOGUN'S CITY", 36)
        self.biggest = bold('BIGGEST CITY IN THE WORLD?', 74)
        self.castle = cached('r10_castle_v1', castle)
        self.house = cached('r10_house_v1', lambda: {'d': house()})['d']
        r = np.random.default_rng(4)
        self.houses = [(r.normal(0, 1), r.normal(0, 1), r.uniform(0.7, 1.1)) for _ in range(140)]
        self.pop = {}
        self.t_hit = T['kyoto']

    def popcount(self, n):
        s = f'{n:,} PEOPLE'
        if s not in self.pop:
            self.pop[s] = text_layer(s, FONT_BOLD, 90, tracking=4)[0]
        return self.pop[s]

    def render(self, t):
        T = self.T
        fr = self.frame(SCREEN)
        M, z = self.cam_.matrix(t)
        draw_map(fr, self.img, M, 1.0)
        to_s = lambda key: np.array(chart_xy(*PLACES[key])) * M[0, 0] + M[:, 2]
        # Nara, then the road to Kyoto
        for key, nm, ts, dy in (('nara', '奈良  NARA', T['nara'], 70), ('kyoto', '京都  KYOTO', T['kyoto'], -75)):
            f = smooth((t - ts + 0.1) / 0.3)
            if f > 0:
                p = to_s(key)
                pin(fr, SCREEN, p[0], p[1], f, 1.2 + 0.6 * np.exp(-max(t - ts, 0) * 5))
                place_label(fr, SCREEN, nm, p[0], p[1] + dy, f, 40)
        draw_route(fr, M, self.path, ease_io((t - T['794'] - 0.3) / 1.6), width=10, dash=(18, 10))
        # the year chips
        for key, ts, te in (('710', T['nara'] + 0.4, T['794']), ('794', T['794'], T['cap']), ('1603', T['1603'], T['1700'])):
            f = smooth((t - ts) / 0.3) * (1 - smooth((t - te + 0.1) / 0.3))
            if f > 0:
                y = self.years[key]
                kit.put(fr, SCREEN, kit.box(y.shape[0] + 30, y.shape[1] + 60, 6), 540, 330, PAPER, 0.9 * f, over=True)
                kit.put(fr, SCREEN, y, 540, 330, VERM, f, 1 + 0.25 * np.exp(-max(t - ts, 0) * 5))
        # 京 = CAPITAL · 都 = CITY
        fc = (t - T['cap'] + 0.1) / 0.3
        meaning_card(fr, self.card_kyoto, 420, smooth(fc) * (1 - smooth((t - T['1000'] - 0.6) / 0.3)), 1 + 0.2 * np.exp(-max(fc, 0) * 3))
        # over a thousand years
        fb = smooth((t - T['1000'] + 0.1) / 0.3) * (1 - smooth((t - T['mean'] - 0.3) / 0.3))
        if fb > 0:
            u = ease_io((t - T['1000']) / 1.2)
            kit.put(fr, SCREEN, kit.box(150, 900, 6), 540, 330, PAPER, 0.92 * fb, over=True)
            kit.put(fr, SCREEN, self.k1000, 540, 300, VERM, fb)
            kit.put(fr, SCREEN, kit.box(16, 760, 2), 540, 372, GREY, 0.3 * fb)
            kit.put(fr, SCREEN, kit.box(16, 760, 2), 160 + 380 * u, 372, VERM, 0.9 * fb, u)
            kit.put(fr, SCREEN, label('794', 30), 160, 405, INK, fb)
            kit.put(fr, SCREEN, label('1868', 30), 920, 405, INK, fb * smooth((u - 0.8) / 0.2))
        # Edo: the castle on the bay
        fe = (t - T['castle']) / 0.5
        if fe > 0:
            p = to_s('edo')
            o = smooth(fe)
            sc = 0.75 * (1 + 0.15 * np.exp(-fe * 3))
            # the city growing round it
            grow = ease_out(np.clip((t - T['1700']) / (T['big'] - T['1700']), 0, 1))
            n = int(len(self.houses) * grow)
            for k in range(n):
                hx, hy, hs = self.houses[k]
                rad = 70 + 230 * np.sqrt((k + 1) / len(self.houses))
                ang = np.arctan2(hy, hx)
                q = np.clip((grow * len(self.houses) - k) / 3, 0, 1)
                kit.put(fr, SCREEN, self.house, p[0] + np.cos(ang) * rad * 1.2, p[1] + 20 + np.sin(ang) * rad * 0.7, INK, 0.85 * q, hs * 0.8)
            kit.put(fr, SCREEN, self.castle['wash'], p[0], p[1] - 110, WASH, o, sc)
            kit.put(fr, SCREEN, self.castle['ink'], p[0], p[1] - 110, INK, o, sc)
            pin(fr, SCREEN, p[0], p[1], o, 1.2)
            place_label(fr, SCREEN, '江戸  EDO', p[0], p[1] + 75, smooth((t - T['edo'] + 0.1) / 0.3), 40)
        fd = (t - T['door'] + 0.1) / 0.3
        meaning_card(fr, self.card_edo, 420, smooth(fd) * (1 - smooth((t - T['1603'] + 0.1) / 0.3)), 1 + 0.2 * np.exp(-max(fd, 0) * 3))
        fs = smooth((t - at('samurai rulers')[0]) / 0.3) * (1 - smooth((t - T['1700'] + 0.1) / 0.3))
        if fs > 0:
            kit.put(fr, SCREEN, kit.box(80, 470, 5), 540, 450, PAPER, 0.9 * fs, over=True)
            kit.put(fr, SCREEN, self.shogun, 540, 450, INK, fs)
        # a million people, the biggest city in the world
        fm = smooth((t - T['1700'] + 0.1) / 0.3)
        if fm > 0:
            u = ease_out(np.clip((t - T['1700']) / (T['million'] + 0.4 - T['1700']), 0, 1))
            n = int(round(1_000_000 * u / 10000.0)) * 10000
            g = self.popcount(n)
            kit.put(fr, SCREEN, kit.box(g.shape[0] + 30, g.shape[1] + 60, 6), 540, 330, PAPER, 0.9 * fm, over=True)
            kit.put(fr, SCREEN, g, 540, 330, VERM, fm, 1 + 0.06 * np.sin(t * 25) * (u < 1))
        fg = (t - T['big'] + 0.1) / 0.25
        if fg > 0:
            kit.put(fr, SCREEN, kit.box(130, 1000, 8), 540, 470, PAPER, 0.9 * smooth(fg), over=True)
            kit.put(fr, SCREEN, self.biggest, 540, 470, INK, smooth(fg), 1 + 0.3 * np.exp(-fg * 3))
        return fr.img
