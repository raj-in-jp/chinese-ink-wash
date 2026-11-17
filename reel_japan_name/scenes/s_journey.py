"""The journey of the name, on the world chart, the camera flying along with it.
  "In China, the same kanji were read something like 'Jih-pen-kwo'.  'Sun-origin country'."
      the route draws itself from Japan to the Chinese capital; the paper name tag riding it changes 日本 NIHON into
      日本国 JIH-PEN-KUO
  "Around thirteen hundred, a traveller from Venice, Marco Polo, wrote about a faraway island full of gold.  He called
   it 'Chipangu'.  He never went there.  He only heard about it in China."
      ~1300; a camel caravan carries the tag west along the Silk Road to Venice (MARCO POLO); Marco Polo's golden
      palace pops up in a bubble; the tag becomes CIPANGU; the camera pulls back: a grey line from Venice to Japan is
      crossed out (NEVER WENT!) and China pulses (HEARD IT IN CHINA)
  "Two hundred years later, Christopher Columbus sailed west, looking for Chipangu.  He never found it.  He found
   America instead!"
      1492; a caravel sails west from Spain with a thought bubble CIPANGU?, crossed out halfway, and lands: AMERICA!
  "Meanwhile, sailors in Southeast Asia called it 'Japang'.  Portuguese traders wrote 'Japão'.  And in English, it
   became... 'Japan'."
      the camera whips across the world to Malacca, a junk bobbing there: JAPANG; a Portuguese caravel carries it round
      Africa to Lisbon: JAPÃO; then up to London, and JAPAN is stamped across the screen."""
import numpy as np

import kit
from draw9 import camel, caravel, junk, palace
from engine import FONT_BOLD, FONT_EN_BOLD, GREY, INK, VERM, W, Cam, StrokeSet, cached, ease_io, ease_out, noise, smooth, stroke, text_layer
from scenes.common9 import (GOLD, PAPER, PLACES, R_CHINA, R_COLUMBUS, R_ENGLAND, R_PORTUGAL, R_SILK, MapCam, Tag, chart, draw_map,
                            draw_route, label, path_px, pin, place_label, route_at)
from scenes.kscene import KanjiScene
from timeline import WORDS, at
from worldmap import chart_xy

SCREEN = Cam(540, 960, 1.0)
WASH = np.array([0.93, 0.90, 0.82], np.float32)
SAIL_BLUE = np.array([0.84, 0.86, 0.88], np.float32)


def word_start(text, after):
    return next(w['start'] for w in WORDS if w['start'] > after and w['text'].strip('".,!?…') == text)


class Scene(KanjiScene):
    paper_seed = 903

    def build(self):
        self.img = chart()
        T = self.T = {}
        T['china'] = at('In China')[0]
        T['jih'] = at('Jih-pen-kwo')[0]
        T['polo'] = at('Around thirteen')[0]
        T['marco'] = at('Marco Polo')[0]
        T['gold'] = at('full of gold')[0]
        T['cip'] = at('called it')[1] + 0.1
        T['never'] = at('never went')[0]
        T['heard'] = at('only heard')[0]
        T['two'] = at('Two hundred')[0]
        T['west'] = at('sailed west')[0]
        T['look'] = at('looking for')[0]
        T['nofind'] = at('never found')[0]
        T['america'] = at('America')[0]
        T['mean'] = at('Meanwhile')[0]
        T['sea'] = at('Southeast Asia')[0]
        T['japang'] = word_start('Japang', 46)
        T['port'] = at('Portuguese')[0]
        T['japao'] = word_start('Japão', 48)
        T['eng'] = at('English')[0]
        T['japan'] = word_start('Japan', 52)
        self.t_hit = T['japan']
        self.cam_ = MapCam([
            (self.t0, 129.0, 36.5, 1.45), (T['china'] + 2.2, 122.0, 38.5, 1.25), (T['polo'] + 0.2, 116.0, 39.0, 1.15),
            (T['polo'] + 1.6, 98.0, 38.5, 0.85), (T['polo'] + 3.1, 72.0, 39.5, 0.85), (T['polo'] + 4.6, 44.0, 39.5, 0.85),
            (T['gold'] - 0.2, 16.0, 43.0, 1.0), (T['never'] - 0.1, 16.0, 43.0, 1.0), (T['never'] + 0.9, 76.0, 32.0, 0.215),
            (T['two'] + 0.2, 76.0, 32.0, 0.215), (T['west'] - 0.1, -12.0, 33.0, 0.6), (T['west'] + 1.5, -32.0, 28.0, 0.58),
            (T['america'] - 0.1, -66.0, 24.0, 0.62), (T['mean'] + 0.2, -68.0, 23.5, 0.62), (T['mean'] + 0.8, 15.0, 15.0, 0.2),
            (T['sea'] + 0.2, 100.0, 4.0, 0.8), (T['port'] + 0.1, 100.0, 4.0, 0.8), (T['port'] + 1.0, 45.0, -5.0, 0.24),
            (T['eng'] - 0.1, -6.0, 40.0, 0.6), (T['japan'] - 0.3, -2.0, 50.0, 1.05), (self.t1, -1.0, 50.8, 1.15)], cy=1000)
        self.paths = {k: path_px(r) for k, r in (('china', R_CHINA), ('silk', R_SILK), ('col', R_COLUMBUS), ('port', R_PORTUGAL),
                                                  ('eng', R_ENGLAND))}
        # (route, t start, t end)
        self.legs = [('china', T['china'] + 0.2, T['china'] + 2.3), ('silk', T['polo'] + 0.3, T['gold'] - 0.3),
                     ('col', T['west'], T['america'] - 0.2), ('port', T['port'] + 0.1, T['eng'] - 0.2),
                     ('eng', T['eng'] - 0.1, T['japan'] - 0.4)]
        self.tag = Tag([(self.t0, 'NIHON', '日本'), (T['jih'], 'JIH-PEN-KUO', '日本国'), (T['cip'], 'CIPANGU', None),
                        (T['japang'], 'JAPANG', None), (T['japao'], 'JAPÃO', None), (T['japan'], 'JAPAN', None)])
        self.sp = {'camel': cached('r9_camel_v1', lambda: {'d': camel()})['d'], 'car': cached('r9_caravel_v1', caravel),
                   'junk': cached('r9_junk_v1', junk), 'palace': cached('r9_palace_v1', palace)}
        bold = lambda s, n: text_layer(s, FONT_BOLD, n, tracking=4)[0]
        self.years = {'polo': bold('AROUND 1300', 96), 'col': bold('1492', 120), 'port': bold('1500s', 120)}
        self.marco = label('MARCO POLO', 64, FONT_BOLD, 6)
        self.never = bold('HE NEVER WENT!', 84)
        self.heard = label('HEARD OF IT IN CHINA', 34)
        self.thought = label('CIPANGU?', 40, FONT_EN_BOLD, 4)
        self.america = bold('AMERICA!', 110)
        self.japan = bold('JAPAN', 300)
        self.gloss = label('“sun-origin country”', 38, FONT_EN_BOLD, 1)
        x = StrokeSet(W, 1920)
        for j, ((x0, y0), (x1, y1)) in enumerate((((-60, -60), (60, 60)), ((60, -60), (-60, 60)))):
            x.add(stroke(W, 1920, [(540 + x0, 960 + y0), (540 + x1, 960 + y1)], 14, ink=0.95, dry=0.3, seed=60 + j), 0.11 * j, 0.12)
        self.cross = x.render(9)
        self.t_cross = 0.0

    def carrier(self, t):
        """(leg name, fraction along it) of whatever is carrying the name now, or a fixed place"""
        for name, a, b in self.legs:
            if a <= t <= b:
                return name, ease_io((t - a) / (b - a))
        T = self.T
        if t < self.legs[0][1]:
            return 'china', 0.0
        if t < self.legs[1][1]:
            return 'china', 1.0
        if t < T['west']:
            return 'silk', 1.0
        if t < T['mean'] + 0.3:
            return 'col', 1.0
        if t < T['port']:
            return 'port', 0.0
        if t < self.legs[4][1]:
            return 'port', 1.0
        return 'eng', 1.0

    def render(self, t):
        T = self.T
        fr = self.frame(SCREEN)
        q = t - T['japan']
        shake = 10 * np.exp(-max(q, 0) * 6) * np.sin(q * 50) * (q > 0)
        # the camera follows whatever carries the name while it travels
        leg, u = self.carrier(t)
        w = 0.0
        for name, a, b in self.legs:
            if name in ('silk', 'col', 'port'):
                w = max(w, smooth((t - a + 0.2) / 0.5) * (1 - smooth((t - b - 0.1) / 0.5)))
        c_key, _ = self.cam_.at(t)
        c_car = route_at(self.paths[leg], u)[0]
        M, z = self.cam_.matrix(t, center=c_key + (c_car - c_key) * w)
        M = M.copy()
        M[0, 2] += shake
        draw_map(fr, self.img, M, 1.0)
        to_s = lambda lon, lat: np.array(chart_xy(lon, lat)) * M[0, 0] + M[:, 2]
        # the routes travelled so far (Columbus's is grey: he was only looking)
        for name, a, b in self.legs:
            ur = ease_io((t - a) / (b - a))
            if ur > 0:
                draw_route(fr, M, self.paths[name], ur, width=8, dash=(16, 10), color=GREY if name == 'col' else VERM)
        # pins and place names
        for key, lbl, ts, dy in (('beijing', 'CHINA', T['china'] + 1.6, -70), ('venice', 'VENICE', T['marco'] - 0.3, 70),
                                 ('palos', 'SPAIN', T['two'] + 0.6, 70), ('malacca', 'SOUTHEAST ASIA', T['sea'], 80),
                                 ('lisbon', 'PORTUGAL', T['japao'] - 0.3, 70), ('london', 'ENGLAND', T['eng'] + 0.2, -80)):
            f = smooth((t - ts) / 0.3)
            if f > 0:
                p = to_s(*PLACES[key])
                pin(fr, SCREEN, p[0], p[1], f, 1 + 0.5 * np.exp(-max(t - ts, 0) * 5))
                place_label(fr, SCREEN, lbl, p[0], p[1] + dy, f)
        # the carrier: camel on the Silk Road, caravels at sea, a junk at Malacca
        P = self.paths[leg] * M[0, 0] + M[:, 2]
        tip, _, d = route_at(P, u)
        flip = -1 if d[0] < 0 else 1
        bob = 4 * np.sin(t * 5)
        on_silk = leg == 'silk' and self.legs[1][1] <= t <= self.legs[1][2] + 0.6
        if on_silk:
            for k in range(3):                                   # a little caravan, single file
                back = route_at(P, max(u - 0.02 * k, 0))[0]
                kit.put(fr, SCREEN, self.sp['camel'], back[0], back[1] - 50 + 3 * np.sin(t * 9 + k), INK, 0.95, 0.75 * flip, 0.75)
        ship = (leg in ('col', 'port', 'eng')) and (t >= T['west'] - 0.6) and not (T['mean'] + 0.3 < t < T['port'])
        if ship:
            c = self.sp['car']
            for k, col in (('wash', SAIL_BLUE), ('ink', INK), ('red', VERM)):
                kit.put(fr, SCREEN, c[k], tip[0], tip[1] - 80 + bob, col, 0.95, 0.6 * flip, 0.6, rot=0.04 * np.sin(t * 2.5))
        if T['sea'] - 0.4 < t < T['port'] + 0.6:
            j = self.sp['junk']
            p = to_s(*PLACES['malacca'])
            o = smooth((t - T['sea'] + 0.4) / 0.3) * (1 - smooth((t - T['port'] - 0.3) / 0.3))
            for k, col in (('wash', np.array([0.80, 0.70, 0.60], np.float32)), ('ink', INK)):
                kit.put(fr, SCREEN, j[k], p[0] - 120, p[1] - 40 + bob, col, 0.95 * o, 0.5, rot=0.05 * np.sin(t * 2))
        # the name tag rides with the carrier (hidden while the camera whips to Malacca)
        hide = smooth((t - T['mean'] - 0.2) / 0.3) * (1 - smooth((t - T['japang'] + 0.3) / 0.3))
        col_leg = smooth((t - T['west'] + 0.3) / 0.3) * (1 - smooth((t - T['japang'] + 0.3) / 0.3))   # Columbus only carries the question
        tag_op = smooth((t - self.t0 - 0.1) / 0.3) * (1 - hide) * (1 - col_leg) * (1 - smooth((t - T['japan'] + 0.1) / 0.2))
        ty = tip[1] - (190 if (ship or on_silk) else 130)
        self.tag.draw(fr, SCREEN, t, float(np.clip(tip[0], 260, 820)), float(np.clip(ty, 260, 1500)), tag_op, 0.95)
        fg = smooth((t - T['jih'] - 0.9) / 0.3) * (1 - smooth((t - T['polo']) / 0.3))
        if fg > 0:
            kit.put(fr, SCREEN, self.gloss, float(np.clip(tip[0], 260, 820)), float(np.clip(ty, 260, 1500)) + 90, INK, fg)
        # years along the top
        for key, ts, te in (('polo', T['polo'], T['two']), ('col', T['two'], T['mean']), ('port', T['port'] - 0.2, T['eng'])):
            f = smooth((t - ts) / 0.3) * (1 - smooth((t - te + 0.2) / 0.3))
            if f > 0:
                y = self.years[key]
                kit.put(fr, SCREEN, kit.box(y.shape[0] + 30, y.shape[1] + 60, 6), 540, 330, PAPER, 0.9 * f, over=True)
                kit.put(fr, SCREEN, y, 540, 330, VERM, f, 1 + 0.25 * np.exp(-max(t - ts, 0) * 5))
        # Marco Polo and his island of gold
        f = smooth((t - T['marco']) / 0.3) * (1 - smooth((t - T['never']) / 0.3))
        if f > 0:
            kit.put(fr, SCREEN, kit.box(100, 420, 5), 540, 1370, PAPER, 0.9 * f, over=True)
            kit.put(fr, SCREEN, self.marco, 540, 1370, INK, f)
        fgd = (t - T['gold']) / 0.35
        if fgd > 0:
            o = smooth(fgd) * (1 - smooth((t - T['never']) / 0.3))
            kit.put(fr, SCREEN, kit.box(420, 520, 30), 540, 760, PAPER, 0.92 * o, 1 + 0.3 * np.exp(-fgd * 3), over=True)
            pl = self.sp['palace']
            kit.put(fr, SCREEN, pl['gold'], 540, 760, GOLD, o, 1 + 0.3 * np.exp(-fgd * 3))
            kit.put(fr, SCREEN, pl['ink'], 540, 760, INK, o, 1 + 0.3 * np.exp(-fgd * 3))
            r = np.random.default_rng(int(t * 6))
            for k in range(6):                                   # glints of gold
                kit.put(fr, SCREEN, kit.box(10, 10, 3), 540 + r.uniform(-230, 230), 760 + r.uniform(-180, 160), GOLD, 0.8 * o)
        # he never went: Venice - - - Japan, crossed out; heard of it in China
        fn = smooth((t - T['never'] - 0.6) / 0.4) * (1 - smooth((t - T['two']) / 0.3))
        if fn > 0:
            a, b = to_s(*PLACES['venice']), to_s(*PLACES['japan'])
            Pv = np.array([a + (b - a) * k / 30 - np.array([0, 160 * np.sin(np.pi * k / 30)]) for k in range(31)], np.float32)
            Pv = (Pv - M[:, 2]) / M[0, 0]
            draw_route(fr, M, Pv, fn, width=6, dash=(10, 10), color=GREY)
            mid = (a + b) / 2 - np.array([0, 160])
            kit.put(fr, SCREEN, self.cross, mid[0], mid[1], VERM, fn, 1.4)
            kit.put(fr, SCREEN, self.never, 540, 470, VERM, fn, 1 + 0.3 * np.exp(-max(t - T['never'] - 0.6, 0) * 5))
            fh = smooth((t - T['heard']) / 0.3) * fn
            if fh > 0:
                p = to_s(*PLACES['beijing'])
                kit.put(fr, SCREEN, kit.rim(90, 90, inset=6, t=4), p[0], p[1], VERM, fh, 1 + 0.6 * ((t * 1.5) % 1))
                place_label(fr, SCREEN, 'HEARD OF IT IN CHINA', p[0], p[1] + 80, fh, 30, VERM)
        # Columbus's thought bubble, crossed out; AMERICA!
        if ship and leg == 'col':
            fb = smooth((t - T['look']) / 0.3)
            if fb > 0:
                bx, by = tip[0], tip[1] - 260
                kit.put(fr, SCREEN, kit.box(80, 260, 18), bx, by, PAPER, 0.92 * fb, over=True)
                kit.put(fr, SCREEN, self.thought, bx, by, INK, fb)
                fx = smooth((t - T['nofind']) / 0.25)
                if fx > 0:
                    kit.put(fr, SCREEN, self.cross, bx, by, VERM, fx, 1.2)
        fa = (t - T['america']) / 0.25
        if fa > 0:
            o = smooth(fa) * (1 - smooth((t - T['mean'] - 0.2) / 0.3))
            p = to_s(*PLACES['caribbean'])
            kit.put(fr, SCREEN, self.america, 540, 470, VERM, o, 1 + 0.4 * np.exp(-fa * 2.5), rot=-0.04)
            pin(fr, SCREEN, p[0], p[1], o, 1.5)
        # JAPAN, stamped
        fj = (t - T['japan'] + 0.05) / 0.2
        if fj > 0:
            kit.put(fr, SCREEN, kit.box(330, 980, 12), 540 + shake, 620, PAPER, 0.85 * smooth(fj), over=True)
            kit.put(fr, SCREEN, self.japan, 540 + shake, 620, VERM, smooth(fj), 1 + 0.6 * np.exp(-fj * 2.5), rot=-0.03)
        return fr.img
