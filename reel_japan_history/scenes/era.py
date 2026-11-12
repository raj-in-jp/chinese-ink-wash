"""era — one scene per period of Japanese history, all built from the same page.

Top: the timeline ribbon, sixteen stops along one brushstroke, the marker sliding on to this era's stop.  Under it the
era's name is brushed in large (縄文, 弥生 ...), its reading set in indigo and its romaji under that, then the year
rolls forward from the last era's year to this one's in vermilion.  Below, the era's painting washes in from one
side, and each era has its own small action, timed to Raj's words: the Mongol junks are swept back, the black ships
steam in, the train crosses, the ground cracks, the bubble bursts, plum petals fall.  The page turns to the next era
with an ink sweep from the right, like unrolling a handscroll."""
import numpy as np

import hart
import kit
from cards import INDIGO
from engine import (spline, FONT_BRUSH_JP, FONT_EN_BOLD, FONT_EN_ITALIC, FONT_HEAD, FONT_JP, GREY, H, INK, VERM, W, Cam, blur, cached,
                    ease_io, ease_out, lerp, noise, reveal_time, smooth, text_layer, wash_map, wipe_mix)
from art import soft_disc
from glyphs import typeset
from scenes.kscene import KanjiScene
from timeline import ERA_KEYS, JA, at

GOLD = np.array([0.80, 0.62, 0.22], np.float32)
BLUE = np.array([0.16, 0.24, 0.46], np.float32)
PALE = np.array([0.55, 0.53, 0.5], np.float32)
BLOSS = np.array([0.93, 0.55, 0.62], np.float32)
IVORY = np.array([0.98, 0.95, 0.88], np.float32)
COLOURS = {'grey': PALE, 'blue': BLUE, 'red': VERM, 'gold': GOLD, 'ink': INK, 'bloss': BLOSS}
ERAS = {'jomon': ('縄文', 'じょうもん', 'JŌMON PERIOD', -14000), 'yayoi': ('弥生', 'やよい', 'YAYOI PERIOD', -300),
        'kofun': ('古墳', 'こふん', 'KOFUN PERIOD', 300), 'asuka': ('飛鳥', 'あすか', 'ASUKA PERIOD', 538),
        'nara': ('奈良', 'なら', 'NARA PERIOD', 710), 'heian': ('平安', 'へいあん', 'HEIAN PERIOD', 794),
        'kamakura': ('鎌倉', 'かまくら', 'KAMAKURA PERIOD', 1185), 'muromachi': ('室町', 'むろまち', 'MUROMACHI PERIOD', 1336),
        'sengoku': ('戦国', 'せんごく', 'SENGOKU · WARRING STATES', 1467), 'edo': ('江戸', 'えど', 'EDO PERIOD', 1603),
        'ships': ('黒船', 'くろふね', 'THE BLACK SHIPS', 1853), 'meiji': ('明治', 'めいじ', 'MEIJI ERA', 1868),
        'taisho': ('大正', 'たいしょう', 'TAISHŌ ERA', 1912), 'showa': ('昭和', 'しょうわ', 'SHŌWA ERA', 1926),
        'heisei': ('平成', 'へいせい', 'HEISEI ERA', 1989), 'reiwa': ('令和', 'れいわ', 'REIWA ERA', 2019)}
RIB_Y, RIB_X0, RIB_X1 = 205, 110, 970
FURI_Y, KANJI_Y, ROM_Y, YEAR_Y = 318, 470, 640, 712
# furigana over each character ('' = the reading spans both: 飛鳥 is read あすか as a whole)
FURI = {'jomon': ('じょう', 'もん'), 'yayoi': ('や', 'よい'), 'kofun': ('こ', 'ふん'), 'asuka': ('あすか', ''), 'nara': ('な', 'ら'),
        'heian': ('へい', 'あん'), 'kamakura': ('かま', 'くら'), 'muromachi': ('むろ', 'まち'), 'sengoku': ('せん', 'ごく'),
        'edo': ('え', 'ど'), 'ships': ('くろ', 'ふね'), 'meiji': ('めい', 'じ'), 'taisho': ('たい', 'しょう'), 'showa': ('しょう', 'わ'),
        'heisei': ('へい', 'せい'), 'reiwa': ('れい', 'わ')}
KX = 140                                   # half the gap between the two characters
# the map moments: a framed sea chart in the painting's place, routes brushed on in vermilion as Raj says them
#   view = (lon, lat) at the panel centre and chart px -> screen px; routes = [(lon, lat), ...]; phase = (from, until)
MAPS = {
    'yayoi': dict(view=(128.5, 34.5, 0.52), phase=('rice farming', None), boat=False,
                  routes=[[(126.9, 35.6), (128.2, 34.6), (129.6, 33.9), (130.4, 33.6)], [(121.6, 31.0), (125.5, 31.6), (129.2, 32.6), (130.0, 33.0)]],
                  labels=[('RICE  ·  METAL', 124.8, 33.4), ('KYŪSHŪ', 131.4, 32.4)]),
    'asuka': dict(view=(131.0, 35.0, 0.52), phase=('Buddhism arrives', 'and Japan builds'), boat=False,
                  routes=[[(126.9, 36.2), (127.4, 34.7), (129.4, 34.0), (131.3, 33.95), (133.3, 34.25), (135.4, 34.62)]],
                  labels=[('BUDDHISM', 127.6, 37.6), ('NARA 奈良', 136.6, 33.6)]),
    'kamakura': dict(view=(131.6, 34.7, 0.55), phase=('samurai warriors', None), boat=True, back='storms drive', route_t='Mongol fleets',
                     takeover=dict(markers=[('鎌倉', 'KAMAKURA', 139.55, 35.32, 'samurai warriors')],
                                   spread='take control', origin=(139.55, 35.32),
                                   riders=[(135.77, 35.01), (135.5, 34.7), (132.4, 34.4), (130.6, 32.8), (133.5, 33.8), (140.9, 38.3),
                                           (139.0, 37.9)]),
                     routes=[[(128.6, 35.2), (129.4, 34.4), (130.3, 33.7)], [(121.8, 29.9), (125.6, 31.0), (128.9, 32.6), (130.2, 33.55)]],
                     labels=[('1274', 128.0, 34.1), ('1281', 123.4, 30.3)]),
    'ships': dict(view=(139.5, 33.4, 0.55), phase=(None, 'black ships'), boat=True,
                  routes=[[(147.7, 30.4), (145.0, 31.6), (141.8, 33.6), (139.75, 35.2)]],
                  labels=[('FROM THE U.S.', 144.6, 29.8), ('EDO 江戸', 140.6, 36.3)]),
}
PANEL = (540, 1080, 1000, 560)
# real pictures, shown as prints laid on the page: (file, crop x0, y0, x1, y1 in source px, caption, from phrase, until phrase)
PHOTOS = {
    'jomon': ('jomon_pot.jpg', (0, 0, 736, 867), 'JŌMON POT', 'oldest pottery', None),
    'kofun': ('kofun_daisen.jpg', (0, 0, 735, 500), 'DAISEN KOFUN · OSAKA', 'giant keyhole-shaped', None),
    'nara': ('nara_daibutsu.jpg', (0, 40, 736, 840), 'THE GREAT BUDDHA · TŌDAI-JI', 'giant bronze', None),
    'muromachi': ('muromachi_kinkakuji.jpg', (0, 110, 736, 900), 'KINKAKU-JI · THE GOLDEN PAVILION', 'ja:zen', None),
    'sengoku': ('sengoku_unifier.jpg', (0, 0, 736, 780), 'JAPAN UNITED', 'united again', None),
    'ships': ('ships_kurofune.jpg', (0, 0, 736, 414), 'A BLACK SHIP, DRAWN BY A JAPANESE ARTIST · 1850s', 'black ships', None),
    'meiji': ('meiji_samurai.jpg', (0, 0, 551, 720), 'A SAMURAI · 19TH CENTURY', 'samurai era', 'Railways'),
    'reiwa': ('reiwa_tokyo.jpg', (0, 80, 736, 760), 'TOKYO TODAY', 'ja:reiwa', 'first era'),
}
PHOTO_BOX = (880, 520)                                     # largest picture inside the print
ART_DEPTH = 1.25                            # the paintings sit nearer than the page: they travel more with the camera
BIRDS = ('jomon', 'yayoi', 'asuka', 'nara', 'heian', 'muromachi', 'edo', 'reiwa')              # map panel centre and size on screen


def year_label(y):
    y = int(round(y))
    if y < 0:
        return f'c. {-y:,} BC'
    if y <= 300:
        return f'c. {y} AD'
    return str(y)


def rib_x(k):
    return RIB_X0 + (RIB_X1 - RIB_X0) * k / (len(ERA_KEYS) - 1)


class Scene(KanjiScene):
    key = None

    def __init__(self, t0, t1, key):
        self.key = key
        self.paper_seed = 300 + ERA_KEYS.index(key)
        super().__init__(t0, t1)

    def build(self):
        k = self.key
        self.idx = ERA_KEYS.index(k)
        kanji, kana, rom, year = ERAS[k]
        self.year0 = ERAS[ERA_KEYS[self.idx - 1]][3] if self.idx else -16000
        self.year = year
        self.t_in = JA[k]['start'] if k in JA else at('Then in')[0] + 0.4
        self.glyphs = [typeset(c, 250, font=FONT_BRUSH_JP, seed=400 + 10 * self.idx + j, medians=False, sweep=(0.7, 1)) for j, c in enumerate(kanji)]
        self.furi = [text_layer(f, FONT_JP, 42)[0] if f else None for f in FURI[k]]
        self.rom, _ = text_layer(rom, FONT_EN_BOLD, 40, tracking=8)
        if k == 'heian':
            self.art = cached('h7_heian_nofan_v1', lambda: hart.heian(fan=False))
        elif k == 'taisho':
            self.art = cached('h7_taisho_notram_v1', lambda: hart.taisho(tram=False))
        else:
            self.art = cached(f'h7_{k}_v1', getattr(hart, k))
        self.T_art = wash_map(H, W, (0 if self.idx % 2 else W, 1100), noise_amp=0.3, noise_scale=180, seed=self.paper_seed)
        self.T_turn = wash_map(H, W, None, direction=(-1, -0.15), noise_amp=0.07, noise_scale=220, seed=self.paper_seed + 1)
        self._years = {}
        self.dot = soft_disc(40, 40, 20, 20, 14, edge=2).astype(np.float32)
        self.rim = (soft_disc(44, 44, 22, 22, 15, edge=1.5) - soft_disc(44, 44, 22, 22, 11, edge=1.5)).clip(0, 1).astype(np.float32)
        self.art_t0 = self.t0
        self.mp = None
        if k in MAPS:
            self.map_build(MAPS[k])
        self.photo = self.photo_build(PHOTOS[k]) if k in PHOTOS else None
        self.bloom = cached('h7_bloom_v2', lambda: {'d': _bloom()})['d']
        if k in BIRDS:
            r = np.random.default_rng(self.idx)
            self.birds = [(r.uniform(-0.3, 0.3), r.uniform(-40, 40), r.uniform(0.7, 1.1), r.uniform(0, 6)) for _ in range(4)]
            self.bird_sp = [_bird(f) for f in (0.0, 1.0)]
        if k == 'jomon':
            self.smoke = [hart.smoke_puff(seed=30 + j) for j in range(3)]
        self.extra_build()

    # ---------------------------------------------------------------- the real pictures
    def photo_build(self, P):
        import os
        import cv2
        from engine import HERE
        f, (x0, y0, x1, y1), cap, a, b = P
        im = cv2.imread(os.path.join(HERE, 'data', 'photos', f))[y0:y1, x0:x1, ::-1].astype(np.float32) / 255
        sc = min(PHOTO_BOX[0] / im.shape[1], PHOTO_BOX[1] / im.shape[0])
        im = cv2.resize(im, (int(im.shape[1] * sc * 1.08), int(im.shape[0] * sc * 1.08)), interpolation=cv2.INTER_AREA)
        paper = np.array([0.95, 0.92, 0.85], np.float32)
        im = im * 0.9 + paper * 0.1                              # a touch of the page's warmth, so it sits on the washi
        when = lambda p: (JA[p[3:]]['start'] if p.startswith('ja:') else at(p, after=self.t0 - 0.5)[0])
        return dict(img=im, w=int(im.shape[1] / 1.08), h=int(im.shape[0] / 1.08), cap=text_layer(cap, FONT_EN_BOLD, 22, tracking=4)[0],
                    t_in=when(a) - 0.25, t_out=None if b is None else when(b) - 0.15)

    def photo_amount(self, t):
        P = self.photo
        if P is None:
            return 0.0
        a = smooth((t - P['t_in']) / 0.45)
        return a if P['t_out'] is None else a * (1 - smooth((t - P['t_out']) / 0.35))

    def draw_photo(self, fr, t, o):
        """the print: a cream mat with a soft shadow, the picture slowly zooming inside it, a small caption on the mat"""
        import cv2
        P = self.photo
        w, h = P['w'], P['h']
        u = max(t - P['t_in'], 0)
        z = 1.0 + 0.07 * min(u / 5.0, 1)                         # Ken Burns: a slow push in
        H0, W0 = P['img'].shape[:2]
        cw, ch = int(W0 / 1.08 / z * 1.0), int(H0 / 1.08 / z * 1.0)
        cx0, cy0 = (W0 - cw) // 2, (H0 - ch) // 2
        pic = cv2.resize(P['img'][cy0:cy0 + ch, cx0:cx0 + cw], (w, h), interpolation=cv2.INTER_LINEAR)
        m, capb = 16, 46
        card = np.ones((h + 2 * m + capb, w + 2 * m, 3), np.float32) * np.array([0.97, 0.95, 0.9], np.float32)
        card[m:m + h, m:m + w] = pic
        ca = np.ones(card.shape[:2], np.float32)
        cg = P['cap']
        gy, gx = m + h + capb // 2 - cg.shape[0] // 2, (card.shape[1] - cg.shape[1]) // 2
        card[gy:gy + cg.shape[0], gx:gx + cg.shape[1]] *= (1 - cg[..., None] * (1 - np.array([0.3, 0.28, 0.26], np.float32)))
        e = ease_out(min(u / 0.6, 1))
        cx, cy = 540, 1070 + 40 * (1 - e)
        rot = np.radians(-1.6 * (1 - e) + 0.6 * np.sin(t * 0.6))
        sc = 0.94 + 0.06 * e
        Hc, Wc = card.shape[:2]
        M = cv2.getRotationMatrix2D((Wc / 2, Hc / 2), np.degrees(rot), sc)
        M[:, 2] += (cx - Wc / 2, cy - Hc / 2)
        shadow = cv2.warpAffine(ca, M + np.array([[0, 0, 10], [0, 0, 16]], np.float32), (W, H))
        fr.img *= (1 - blur(shadow, 12)[..., None] * 0.28 * o)
        a = cv2.warpAffine(ca, M, (W, H))[..., None] * o
        rgb = cv2.warpAffine(card, M, (W, H))
        fr.img = fr.img * (1 - a) + rgb * a

    def art_pulse(self, t, c):
        p = self.photo_amount(t)
        return (1 - 0.92 * p) * self.art_pulse_(t, c)

    def art_pulse_(self, t, c):
        if self.key == 'sengoku':                        # the castle steps back when the warlords come forward
            return 1 - 0.75 * smooth((t - self.lords[0]['t'] + 0.3) / 0.5)
        if self.key == 'nara' and c == 'red':
            return 0.85 + 0.15 * np.sin(t * 2.2)        # the halo breathes
        return 1.0

    def life(self, fr, cam, t):
        """small living things: birds crossing the sky, smoke from the hut"""
        a = smooth((t - self.art_t0 - 0.6) / 0.6)
        if self.key in BIRDS:
            dur = self.t1 - self.t0
            for j, (dy, dx, sc, ph) in enumerate(self.birds):
                u = (t - self.t0 + 0.4 * j) / (dur + 1.5)
                x = lerp(-80, 1160, u) + dx
                y = 880 + 160 * dy + 14 * np.sin(t * 1.6 + ph) - 60 * u
                flap = self.bird_sp[int((t * 7 + ph) % 2)]
                kit.put(fr, cam, flap, x, y, INK, 0.75 * a, sc * 0.9)
        if self.key == 'jomon':
            for j in range(3):
                v = ((t - self.t0) * 0.35 + j / 3) % 1
                kit.put(fr, cam, self.smoke[j], 222 + 40 * v + 10 * np.sin(t + j), 1205 - 230 * v, PALE, 0.35 * np.sin(np.pi * v) * a,
                        0.5 + 1.2 * v)

    # ---------------------------------------------------------------- the map moments
    def map_build(self, M):
        import r5art
        self.chart = cached('h7_chart_v1', r5art.east_asia_chart)['rgb'].astype(np.float32)
        a, b = M['phase']
        self.m_in = self.t0 if a is None else at(a, after=self.t0 - 0.5)[0] - 0.1
        self.m_out = None if b is None else at(b, after=self.t0 - 0.5)[0] - 0.2
        if a is None:
            self.art_t0 = self.m_out
        self.mp = M
        lo, la, sc = M['view']
        self.m_c = r5art.chart_xy(lo, la)
        self.routes = [np.array(spline([tuple(r5art.chart_xy(x, y)) for x, y in R], 24), np.float32) for R in M['routes']]
        self.m_labels = []
        for txt, x, y in M['labels']:                    # 'EDO 江戸': the English in Cormorant, the kanji under it
            en, _, jp = txt.partition(' ') if any(ord(c) > 0x2000 for c in txt) else (txt, '', '')
            self.m_labels.append((text_layer(en, FONT_EN_BOLD, 30, tracking=4)[0], r5art.chart_xy(x, y)))
            if jp:
                self.m_labels.append((text_layer(jp, FONT_JP, 30)[0], r5art.chart_xy(x, y) + np.array([0, 40 / M['view'][2]], np.float32)))
        cx, cy, pw, ph = PANEL
        m = np.zeros((H, W), np.float32)
        m[int(cy - ph / 2):int(cy + ph / 2), int(cx - pw / 2):int(cx + pw / 2)] = 1
        self.m_mask = blur(m, 6)[..., None]
        self.m_rim = kit.rim(ph + 16, pw + 16, inset=4, t=3)
        self.m_boat = hart.junk() if M['boat'] else None
        self.t_mback = at(M['back'], after=self.t0)[0] if 'back' in M else None
        self.m_route_t = at(M['route_t'], after=self.t0)[0] if 'route_t' in M else self.m_in
        self.tk = None
        if 'takeover' in M:
            self.takeover_build(M['takeover'], r5art)

    def takeover_build(self, T, r5art):
        """the samurai take over: Japan's land washed vermilion outward from Kamakura, riders galloping out"""
        def when(p):
            return JA[p[3:]]['start'] if p.startswith('ja:') else at(p, after=self.t0)[0]
        C = cached('h7_chart_v1', r5art.east_asia_chart)
        land = C['land'].astype(np.float32)
        h, w = land.shape
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        lon = r5art.CHART_LON0 + xx / r5art.CHART_K
        y_134, y_416 = r5art.chart_xy(0, 34.3)[1], r5art.chart_xy(0, 41.6)[1]
        japan = (lon > 129.6) | ((yy > y_134) & (lon > 128.5))
        japan &= yy > y_416
        o = r5art.chart_xy(*T['origin'])
        self.tk = dict(mask=(land * japan).astype(np.float32), dist=np.hypot(xx - o[0], yy - o[1]).astype(np.float32),
                       t_spread=when(T['spread']), origin=o,
                       markers=[(text_layer(jp, FONT_JP, 40)[0], text_layer(en, FONT_EN_BOLD, 24, tracking=4)[0], r5art.chart_xy(lo, la),
                                 when(tw)) for jp, en, lo, la, tw in T['markers']],
                       riders=[r5art.chart_xy(lo, la) for lo, la in T['riders']], icon=hart.samurai_icon())

    def draw_takeover(self, fr, t, m, A):
        import cv2
        T = self.tk
        scr = Cam(540, 960, 1.0)
        f = (t - T['t_spread']) / 2.6
        if f > 0:
            R = 920 * ease_out(min(f, 1))
            red = T['mask'] * np.clip((R - T['dist']) / 60, 0, 1)
            fr.ink(cv2.warpAffine(red, A, (W, H), flags=cv2.INTER_LINEAR) * self.m_mask[..., 0], VERM, 0.45 * m)
            ink, rd = T['icon']
            for j, dst in enumerate(T['riders']):
                u = ease_io(np.clip((t - T['t_spread'] - 0.15 * j) / 2.0, 0, 1))
                if u <= 0:
                    continue
                p = self.to_screen(T['origin'] + (dst - T['origin']) * u, t)
                fl = -1 if dst[0] < T['origin'][0] else 1
                bob = 3 * np.sin(t * 18 + j) * (u < 1)
                o = m * smooth(u * 5) * (1 - smooth((t - self.m_route_t + 0.2) / 0.5) * 0.7)
                kit.put(fr, scr, rd, p[0], p[1] - 30 + bob, VERM, 0.9 * o, 0.9 * fl, 0.9)
                kit.put(fr, scr, ink, p[0], p[1] - 30 + bob, INK, o, 0.9 * fl, 0.9)
        for jp, en, xy, tw in T['markers']:
            fm = (t - tw + 0.1) / 0.35
            if fm <= 0:
                continue
            p = self.to_screen(xy, t)
            kit.put(fr, scr, self.dot, p[0], p[1], VERM, m * smooth(fm), 0.7 * (1 + 0.6 * np.exp(-fm * 3)))
            self.plate(fr, scr, p[0], p[1] - 62, 150, 70, m * smooth(fm))
            kit.put(fr, scr, jp, p[0], p[1] - 76, INK, m * smooth(fm), 1 + 0.2 * np.exp(-fm * 3))
            kit.put(fr, scr, en, p[0], p[1] - 42, VERM, m * smooth(fm - 0.5))

    def map_amount(self, t):
        if self.mp is None:
            return 0.0
        a = smooth((t - self.m_in) / 0.45)
        return a if self.m_out is None else a * (1 - smooth((t - self.m_out) / 0.45))

    def map_scale(self, t):
        return self.mp['view'][2] * (1 + 0.06 * smooth((t - self.m_in) / 4))

    def to_screen(self, p, t):
        s = self.map_scale(t)
        return np.array([PANEL[0], PANEL[1]], np.float32) + (np.asarray(p, np.float32) - self.m_c) * s

    def draw_map(self, fr, t, m):
        import cv2
        s = self.map_scale(t)
        cx, cy = PANEL[:2]
        A = np.array([[s, 0, cx - s * self.m_c[0]], [0, s, cy - s * self.m_c[1]]], np.float32)
        img = cv2.warpAffine(self.chart, A, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        k = self.m_mask * m
        fr.img = fr.img * (1 - k) + img * k
        kit.put(fr, Cam(540, 960, 1.0), self.m_rim, cx, cy, INK, 0.8 * m)
        if self.tk is not None:
            self.draw_takeover(fr, t, m, A)
        # the routes, brushed on as dashes with an arrowhead (or a boat) at the tip
        d = np.zeros((H, W), np.float32)
        back = 0.0 if self.t_mback is None else ease_io((t - self.t_mback - 0.1) / 1.3)
        tips = []
        for j, R in enumerate(self.routes):
            u = ease_io((t - self.m_route_t - 0.35 - 0.45 * j) / 1.3)
            u = u * (1 - 0.55 * back)
            if u <= 0:
                continue
            P = np.array([self.to_screen(q, t) for q in R])
            seg = np.r_[0, np.cumsum(np.hypot(*np.diff(P, axis=0).T))]
            L = seg[-1] * u
            n = np.searchsorted(seg, L)
            tip = np.array([np.interp(L, seg, P[:, 0]), np.interp(L, seg, P[:, 1])])
            pts = np.vstack([P[:n], tip])
            dash = 0.0
            for a_, b_ in zip(pts[:-1], pts[1:]):
                ln = np.hypot(*(b_ - a_))
                q = 0.0
                while q < ln:
                    on = (dash % 28) < 18
                    step = min(ln - q, (18 - dash % 28) if on else (28 - dash % 28))
                    if on:
                        p0, p1 = a_ + (b_ - a_) * q / ln, a_ + (b_ - a_) * (q + step) / ln
                        cv2.line(d, tuple(np.round(p0).astype(int)), tuple(np.round(p1).astype(int)), 1.0, 7, cv2.LINE_AA)
                    q += max(step, 1e-3)
                    dash += max(step, 1e-3)
            dirv = pts[-1] - pts[-2] if len(pts) > 1 else np.array([1.0, 0])
            dirv = dirv / (np.hypot(*dirv) + 1e-6)
            tips.append((tip, dirv))
            if self.m_boat is None:
                nrm = np.array([-dirv[1], dirv[0]])
                tri = np.array([tip + dirv * 22, tip - dirv * 10 + nrm * 16, tip - dirv * 10 - nrm * 16]).astype(np.int32)
                cv2.fillPoly(d, [tri], 1.0, cv2.LINE_AA)
        fr.ink(d, VERM, 0.95 * m)
        for tip, dirv in tips:
            if self.m_boat is not None:
                ink, red = self.m_boat
                o = m * (1 - smooth((back - 0.7) / 0.3)) if back else m
                fl = -1 if back > 0 else 1
                kit.put(fr, Cam(540, 960, 1.0), red, tip[0], tip[1] - 30, VERM, 0.8 * o, 0.42 * fl, 0.42, rot=0.1 * np.sin(t * 3))
                kit.put(fr, Cam(540, 960, 1.0), ink, tip[0], tip[1] - 30, INK, o, 0.42 * fl, 0.42, rot=0.1 * np.sin(t * 3))
        if back > 0:                                     # the storms that drove them back
            sw = np.zeros((H, W), np.float32)
            c = self.to_screen(self.routes[0][-1], t)
            for j in range(3):
                r = 40 + 26 * j
                a0 = np.degrees(t * (3 - j)) % 360
                cv2.ellipse(sw, tuple(np.round(c).astype(int)), (r, int(r * 0.6)), 0, a0, a0 + 250, 1.0, 5, cv2.LINE_AA)
            fr.ink(sw, INK, 0.75 * m * smooth(back * 3))
        for j, (g, xy) in enumerate(self.m_labels):
            p = self.to_screen(xy, t)
            kit.put(fr, Cam(540, 960, 1.0), g, p[0], p[1], INK, m * smooth((t - self.m_route_t - 0.5 - 0.3 * j) / 0.3))

    # ---------------------------------------------------------------- per-era extras
    def extra_build(self):
        k = self.key
        if k == 'kamakura':
            self.junks = []
            self.t_back = self.t1 + 10
        elif k == 'heian':
            self.fans = cached('h7_fan_v1', lambda: {f'{c}{i}': a for i in range(9) for c, a in zip('ir', hart.fan_open(i / 8))})
            self.an = text_layer('安', FONT_JP, 170)[0]
            self.a = typeset('あ', 190, font=FONT_BRUSH_JP, seed=461, medians=False, sweep=(0.7, 1))
            self.arrow = text_layer('→', FONT_EN_BOLD, 80)[0]
            self.kana_lab = text_layer('KANA IS BORN', FONT_EN_BOLD, 30, tracking=6)[0]
            self.t_kana = JA['kana']['start']
        elif k == 'ships':
            self.puffs = [hart.smoke_puff(seed=j) for j in range(4)]
        elif k == 'meiji':
            self.train = cached('h7_train_v1', lambda: dict(zip(('ink', 'red'), hart.steam_train())))
            self.puffs = [hart.smoke_puff(seed=10 + j) for j in range(4)]
        elif k == 'taisho':
            self.tram = cached('h7_tram_v1', lambda: dict(zip(('ink', 'red'), hart.tram_sprite())))
            self.crack = cached('h7_crack_v1', lambda: {'d': hart.crack()})['d']
            self.T_crack = wash_map(H, W, None, direction=(1, 0), noise_amp=0.1, noise_scale=80, seed=9)
            self.t_quake = at('earthquake')[0]
        elif k == 'showa':
            self.bt = cached('h7_bullet_v1', lambda: dict(zip(('ink', 'blue'), hart.bullet_train())))
            self.t_train = at('bullet train')[0]
        elif k == 'heisei':
            self.bub = hart.bubble()
            self.globe = hart.globe()
            self.wave = cached('h7_wave_v1', lambda: {'d': hart.wave_line()})['d']
            self.t_burst = at('bubble bursts')[0] + 0.45
            self.t_tsu = JA['tsunami']['start']
            self.t_glob = JA['anime']['start']
        elif k == 'reiwa':
            self.man, _ = text_layer('万葉集', FONT_JP, 64)
            self.man_r, _ = text_layer("MAN'YŌSHŪ · 8th-century poems", FONT_EN_ITALIC, 30)
            self.t_poem = at('Japanese poetry')[0]
            r = np.random.default_rng(5)
            self.petals = [(r.uniform(80, 1000), r.uniform(0, 7), r.uniform(0.6, 1.2), r.uniform(0, 6)) for _ in range(22)]
            p = np.zeros((16, 22), np.float32)
            yy, xx = np.mgrid[0:16, 0:22]
            self.petal = np.clip(1 - np.hypot((xx - 11) / 10, (yy - 8) / 6), 0, 1).astype(np.float32) ** 0.6
        elif k == 'edo':
            self.t_kab = JA['kabuki']['start']
        elif k == 'sengoku':
            self.lords = []
            for j, (key, kanji, crest) in enumerate((('nobunaga', '織田信長', 'crescent'), ('hideyoshi', '豊臣秀吉', 'rays'),
                                                     ('ieyasu', '徳川家康', 'fern'))):
                d = cached(f'h7_lord_{key}_v1', lambda c=crest, j=j: dict(zip(('ink', 'red', 'gold'), hart.warrior(c, seed=90 + 20 * j))))
                ink, red, gold = d['ink'], d['red'], d['gold']
                self.lords.append(dict(ink=ink, red=red, gold=gold, t=at('warlords fight')[0] - 0.1 + 0.35 * j, x=195 + 345 * j))
            self.card_b, self.card_r = kit.box(430, 300, 2.5), kit.rim(430, 300, inset=8, t=3)
            self.t_unite = at('united again')[0]
            self.t_fight = at('fight for')[0]
            self.unite = _seal2('統一')
            self.unite_lab = text_layer('UNITED', FONT_EN_BOLD, 34, tracking=8)[0]

    # ---------------------------------------------------------------- camera and transition
    def cam(self, t):
        u = smooth((t - self.t0) / max(self.t1 - self.t0, 1))
        shake = 0
        if self.key == 'taisho':
            q = t - self.t_quake
            shake = 14 * np.exp(-q * 2.5) * np.sin(q * 47) * (q > 0)
        side = 1 if self.idx % 2 else -1
        return Cam(540 + 34 * (u - 0.5) * side + shake, 960 - 14 * u + 0.5 * shake, 1.0 + 0.06 * u)

    def enter(self, prev_img, cur_img, f, prev_scene):
        """the next era is unrolled over the last one from the right, a wet ink edge riding the front"""
        return wipe_mix(prev_img, cur_img, self.T_turn, ease_io(f) * 1.12 - 0.04, soft=0.05, edge=0.18)

    # ---------------------------------------------------------------- the page
    def ribbon(self, fr, t):
        from scenes.kscene import SCREEN
        a = smooth((t - self.t0) / 0.3)
        if not hasattr(self, '_line'):
            from engine import StrokeSet, stroke
            ss = StrokeSet(W, 260)
            ss.add(stroke(W, 260, [(RIB_X0 - 30, 130), (540, 126), (RIB_X1 + 30, 130)], 5, ink=0.6, dry=0.5,
                          profile=((0, 0.3), (0.1, 1), (0.9, 1), (1, 0.3)), seed=7), 0, 1)
            self._line = ss.render(9)
        kit.put(fr, SCREEN, self._line, 540, RIB_Y, INK, 0.75)
        slide = ease_io((t - self.t0 - 0.05) / 0.6)
        for j in range(len(ERA_KEYS)):
            x = rib_x(j)
            if j < self.idx:
                kit.put(fr, SCREEN, self.dot, x, RIB_Y, INK, 0.8 * a, 0.55)
            elif j > self.idx:
                kit.put(fr, SCREEN, self.rim, x, RIB_Y, GREY, 0.5 * a, 0.7)
        if self.idx:
            kit.put(fr, SCREEN, self.dot, rib_x(self.idx - 1), RIB_Y, INK, 0.8 * (1 - slide), 0.55)
        mx = lerp(rib_x(max(self.idx - 1, 0)), rib_x(self.idx), slide)
        pulse = 1 + 0.35 * np.exp(-max(t - self.t_in, 0) * 4) * (t > self.t_in)
        kit.put(fr, SCREEN, self.dot, mx, RIB_Y, VERM, 1.0, 1.15 * pulse)

    def year_patch(self, t):
        f = ease_out((t - self.t0 - 0.15) / 0.8)
        y = lerp(self.year0, self.year, f)
        step = 1000 if abs(y) >= 2000 else 100 if y < 0 or y <= 300 else 1
        y = round(y / step) * step if f < 1 else self.year
        s = year_label(y)
        if s not in self._years:
            self._years[s] = text_layer(s, FONT_HEAD, 66)[0]
        return self._years[s]

    def render(self, t):
        cam = self.cam(t)
        fr = self.frame(cam)
        fa = (t - self.art_t0 - 0.1) / 1.0
        m = self.map_amount(t)
        if self.key == 'kofun' and fa > 0:                # the drone shot: slowly pushing in over the tomb
            z = 0.84 + 0.16 * smooth((t - self.art_t0) / (self.t1 - self.art_t0))
            for c in ('blue', 'ink'):
                d = reveal_time(self.art[c], self.T_art, fa)
                kit.put(fr, cam, d, 540, 1150 + (960 - 1150) * z, COLOURS[c], 0.95 * (1 - 0.92 * self.photo_amount(t)), z)
            fa = -1
        for c in ('grey', 'blue', 'red', 'gold', 'ink', 'bloss'):
            if c in self.art and fa > 0 and m < 1:
                self.layer(fr, cam, reveal_time(self.art[c], self.T_art, fa), *self.art_offset(t, c), depth=ART_DEPTH, ref=(540, 960),
                           color=COLOURS[c], opacity=(0.95 if c != 'red' else 0.85) * (1 - m) * self.art_pulse(t, c))
        if m < 1:
            self.life(fr, cam, t)
            self.extras(fr, cam, t)
        po = self.photo_amount(t)
        if po > 0:
            self.draw_photo(fr, t, po)
        if m > 0:
            self.draw_map(fr, t, m)
        # the era's name, reading, romaji and year; a pale ink bloom opens behind the name as it is written
        fb = (t - self.t_in + 0.3) / 0.9
        if fb > 0:
            kit.put(fr, cam, self.bloom, 540, KANJI_Y, INK, 0.11 * (1 - 0.5 * smooth(fb - 1)), 0.6 + 0.5 * ease_out(min(fb, 1)))
        for j, g in enumerate(self.glyphs):
            fk = (t - self.t_in + 0.25 - 0.18 * j) / 0.45
            if fk > 0:
                x = 540 + (j - (len(self.glyphs) - 1) / 2) * 2 * KX
                kit.put(fr, cam, g.at(fk, soft=0.05), x, KANJI_Y, INK, 1.0, 1 + 0.12 * np.exp(-fk * 3))
        for j, g in enumerate(self.furi):
            if g is None:
                continue
            ff = smooth((t - self.t_in - 0.15 - 0.12 * j) / 0.3)
            x = 540 if any(f is None for f in self.furi) else 540 + (j - 0.5) * 2 * KX
            kit.put(fr, cam, g, x, FURI_Y + 10 * (1 - ff), INDIGO, ff)
        fr_ = smooth((t - self.t_in - 0.3) / 0.3)
        kit.put(fr, cam, self.rom, 540, ROM_Y + 10 * (1 - fr_), GREY, smooth((t - self.t_in - 0.45) / 0.3))
        kit.put(fr, cam, self.year_patch(t), 540, YEAR_Y, VERM, smooth((t - self.t0 - 0.1) / 0.25))
        self.ribbon(fr, t)
        return fr.img

    def art_offset(self, t, c):
        dx, dy = self.art_offset_(t, c)
        u = max(t - self.art_t0 - 0.1, 0)
        if self.key == 'kamakura':                       # dropped from above, lands with a bounce
            return dx, dy - 160 * np.exp(-u * 5) * np.cos(u * 11)
        return dx, dy + 45 * (1 - ease_out(min(u / 1.0, 1)))

    def art_offset_(self, t, c):
        if self.key == 'sengoku' and c == 'red':
            return 4 * np.sin(t * 5.5), 2 * np.sin(t * 3.1)
        if self.key == 'edo' and c == 'blue':
            return 0, 6 * np.sin(t * 2.2)
        if self.key == 'ships':
            return 160 * (1 - ease_out((t - self.art_t0) / 1.6)), 3 * np.sin(t * 2.5)
        return 0, 0

    def extras(self, fr, cam, t):
        k = self.key
        if k == 'kamakura':
            back = ease_io((t - self.t_back) / 1.4)
            for j, (ink, red) in enumerate(self.junks):
                x = 330 + 230 * j - 700 * back * (1 + 0.2 * j)
                y = 1235 + 18 * j + 6 * np.sin(t * 3 + j)
                o = smooth((t - self.t0 - 0.6) / 0.4) * (1 - smooth((back - 0.6) / 0.4))
                kit.put(fr, cam, red, x, y, VERM, 0.8 * o, 0.8, rot=0.1 * np.sin(t * 2 + j) - 0.2 * back)
                kit.put(fr, cam, ink, x, y, INK, o, 0.8, rot=0.1 * np.sin(t * 2 + j) - 0.2 * back)
        elif k == 'sengoku':
            cam = Cam(540, 960, 1.0)                     # the cards hold still on the screen
            clash = smooth((t - self.t_fight) / 0.3) * (1 - smooth((t - self.t_unite + 0.4) / 0.4))
            unite = ease_io((t - self.t_unite + 0.2) / 0.6)
            for j, L in enumerate(self.lords):
                f = (t - L['t'] + 0.25) / 0.45
                if f <= 0:
                    continue
                o = smooth(f)
                side = j - 1                             # left, middle, right: they lunge at each other while they fight
                lunge = clash * (18 * np.sin(t * 9 + j * 2.1) - 10 * side)
                x = L['x'] + lunge + side * (-60) * unite
                y = 1080 + 60 * (1 - ease_out(min(f, 1))) + clash * 6 * np.sin(t * 13 + j)
                rot = clash * 0.06 * np.sin(t * 7 + j * 1.7) - 0.05 * side * (1 - unite) * clash
                o *= 1 - self.photo_amount(t)
                if o <= 0.01:
                    continue
                kit.card(fr, cam, self.card_b, self.card_r, x, y, o, color=np.array([0.96, 0.93, 0.86], np.float32))
                for c, col in (('red', VERM), ('gold', GOLD), ('ink', INK)):
                    kit.put(fr, cam, L[c], x, y - 10, col, o * (0.9 if c != 'ink' else 1.0), 0.95, rot=rot)
            fu = (t - self.t_unite) / 0.18
            if fu > 0 and self.photo_amount(t) < 0.99:
                kit.put(fr, cam, self.unite, 540, 830, VERM, 0.95 * smooth(fu), 0.78 * (1.0 + 0.6 * np.exp(-fu * 2.4)), rot=-0.05)
                kit.put(fr, cam, self.unite_lab, 790, 830, INK, smooth(fu - 1.5) * (1 - self.photo_amount(t)))
        elif k == 'heian':
            fo = ease_out(np.clip((t - self.art_t0 - 0.3) / 0.9, 0, 1))      # the fan snaps open
            i = int(round(fo * 8))
            kit.put(fr, cam, self.fans[f'r{i}'], 300, 1140, VERM, 0.85 * smooth((t - self.art_t0) / 0.3), rot=0.06 * np.sin(t * 1.3))
            kit.put(fr, cam, self.fans[f'i{i}'], 300, 1140, INK, smooth((t - self.art_t0) / 0.3), rot=0.06 * np.sin(t * 1.3))
            f = (t - self.t_kana + 0.1) / 0.5
            if f > 0:
                self.plate(fr, cam, 780, 1090, 420, 300, smooth(f))
                m = smooth((t - self.t_kana - 0.5) / 0.5)
                kit.put(fr, cam, self.an, 680, 1075, INK, smooth(f), 1 + 0.15 * np.exp(-f * 3))
                kit.put(fr, cam, self.arrow, 785, 1075, VERM, m)
                kit.put(fr, cam, self.a.at((t - self.t_kana - 0.55) / 0.5, soft=0.05), 890, 1075, INK, 1.0)
                kit.put(fr, cam, self.kana_lab, 780, 1205, VERM, smooth((t - self.t_kana - 0.9) / 0.3))
        elif k == 'ships':
            for j, (sx, sy, s) in enumerate(((550, 1100, 1.0), (222, 1088, 0.55), (873, 1082, 0.45))):
                ox = 160 * (1 - ease_out((t - self.art_t0) / 1.6))
                for p in range(3):
                    u = ((t - self.t0) * 0.5 + p / 3 + j * 0.13) % 1
                    kit.put(fr, cam, self.puffs[(p + j) % 4], sx + ox - 90 * u * s + 10, sy - 40 * s - 160 * u * s, PALE,
                            0.5 * np.sin(np.pi * u) * smooth((t - self.t0 - 0.4) / 0.5), s * (0.6 + 1.4 * u))
        elif k == 'meiji':
            u = (t - self.t0 - 0.3) / (self.t1 - self.t0 - 0.3)
            x = lerp(-420, 1500, ease_io(np.clip(u, 0, 1)) * 0.75 + np.clip(u, 0, 1) * 0.25)
            y = 1185 + 2 * np.sin(t * 20)
            for p in range(5):
                v = ((t - self.t0) * 1.2 + p / 5) % 1
                kit.put(fr, cam, self.puffs[p % 4], x + 210 - 260 * v, y - 140 - 120 * v, PALE, 0.55 * (1 - v), 0.5 + 1.2 * v)
            kit.put(fr, cam, self.train['red'], x, y, VERM, 0.85)
            kit.put(fr, cam, self.train['ink'], x, y, INK, 1.0)
        elif k == 'taisho':
            u = ease_out(np.clip((t - self.art_t0) / (self.t_quake - self.art_t0), 0, 1))
            q = t - self.t_quake
            jolt = 10 * np.exp(-q * 3) * np.sin(q * 40) * (q > 0)
            x = lerp(-260, 330, u) + jolt
            y = 1170 + 2 * np.sin(t * 14) * (u < 1) + 0.5 * jolt
            kit.put(fr, cam, self.tram['red'], x, y, VERM, 0.85, rot=0.03 * np.sin(q * 30) * np.exp(-max(q, 0) * 3) * (q > 0))
            kit.put(fr, cam, self.tram['ink'], x, y, INK, 1.0, rot=0.03 * np.sin(q * 30) * np.exp(-max(q, 0) * 3) * (q > 0))
            fc = (t - self.t_quake - 0.15) / 0.5
            if fc > 0:
                self.layer(fr, cam, reveal_time(self.crack, self.T_crack, fc), color=INK, opacity=1.0)
        elif k == 'showa':
            u = (t - self.t_train + 0.3) / 1.6
            if 0 < u < 1.3:
                x = lerp(-700, 1800, ease_io(min(u, 1)))
                for j in range(4):
                    kit.put(fr, cam, kit.box(4, 160, 1.0), x - 640 - 90 * j, 1105 + 26 * j, GREY, 0.4 * (1 - j / 4))
                kit.put(fr, cam, self.bt['blue'], x, 1165, BLUE, 1.0)
                kit.put(fr, cam, self.bt['ink'], x, 1165, INK, 1.0)
        elif k == 'heisei':
            fb = (t - self.t0 - 0.3) / 0.4
            pop = (t - self.t_burst) / 0.35
            if fb > 0 and pop < 1:
                s = (0.6 + 0.4 * ease_out(min(fb, 1))) * (1 + 0.25 * max(pop, 0))
                kit.put(fr, cam, self.bub, 540, 955 + 6 * np.sin(t * 2), BLUE, 0.9 * (1 - smooth(pop)), s)
            if 0 < pop < 2:
                r = np.random.default_rng(3)
                for j in range(14):
                    a = j / 14 * 2 * np.pi + r.uniform(-0.2, 0.2)
                    d = 160 + 220 * ease_out(min(pop / 1.4, 1))
                    kit.put(fr, cam, self.dot, 540 + d * np.cos(a), 955 + d * np.sin(a) + 120 * pop ** 2, BLUE, 0.7 * (1 - pop / 2), 0.5)
            fw = smooth((t - self.t_tsu + 0.2) / 0.6) * (1 - smooth((t - self.t_glob + 0.3) / 0.4))
            if fw > 0:
                kit.put(fr, cam, self.wave, 540 - 120 * (1 - fw), 1200, BLUE, 0.8 * fw)
            fg = (t - self.t_glob + 0.1) / 0.4
            if fg > 0:
                kit.put(fr, cam, self.globe, 540, 960, INK, smooth(fg), 1 + 0.2 * np.exp(-fg * 3), rot=0.05 * np.sin(t))
                for j in range(5):
                    a = t * 0.8 + j * 2 * np.pi / 5
                    kit.put(fr, cam, self.dot, 540 + 220 * np.cos(a), 960 + 90 * np.sin(a), VERM, 0.8 * smooth(fg - 0.5), 0.45)
        elif k == 'reiwa':
            for x, d, sp, ph in self.petals:
                u = ((t - self.t0) * 0.12 * sp + d / 7) % 1
                kit.put(fr, cam, self.petal, x + 60 * np.sin(t * sp + ph) - 140 * u, 760 + 700 * u, BLOSS, 0.8 * smooth((t - self.t0 - 0.5) / 0.6),
                        rot=t * sp + ph)
            fm = smooth((t - self.t_poem + 0.1) / 0.4)
            if fm > 0:
                self.plate(fr, cam, 300, 880, 360, 150, fm)
                kit.put(fr, cam, self.man, 300, 855, INK, fm, 1 + 0.15 * np.exp(-max(t - self.t_poem, 0) * 4))
                kit.put(fr, cam, self.man_r, 300, 920, GREY, smooth((t - self.t_poem - 0.3) / 0.3))


def _bloom(s=700):
    """a pale, soft-edged ink blot with a broken rim (the wash behind a freshly brushed name)"""
    yy, xx = np.mgrid[0:s, 0:int(s * 1.5)].astype(np.float32)
    cx, cy = s * 0.75, s / 2
    r = np.hypot((xx - cx) / 1.5, yy - cy) / (s / 2)
    n = noise(s, int(s * 1.5), 60, 4, 21)
    d = np.clip((1 - r + 0.25 * (n - 0.5)) * 3, 0, 1) * (0.7 + 0.3 * noise(s, int(s * 1.5), 14, 3, 22))
    rim = np.exp(-((r - 0.88 - 0.1 * (n - 0.5)) / 0.05) ** 2) * 0.3
    return np.clip(blur(d, 6) + rim, 0, 1).astype(np.float32)


def _bird(f, w=70, h=40):
    """one ink bird in flight, wings up (f=0) or down (f=1)"""
    from engine import StrokeSet, stroke
    ss = StrokeSet(w, h)
    y = 14 if f else 26
    for s_ in (-1, 1):
        ss.add(stroke(w, h, spline([(35, 22), (35 + s_ * 14, y - 6 if not f else y + 4), (35 + s_ * 30, y - 2)], 6), 3, ink=0.9,
                      dry=0.3, profile=((0, 1), (0.6, 0.8), (1, 0.15)), seed=3 + s_ + int(f) * 7), 0, 1)
    return ss.render(9)


def _seal2(text, w=280, h=150):
    """a vermilion seal with the characters cut out in white, side by side (density: 1 = vermilion)"""
    d = np.zeros((h, w), np.float32)
    d[8:-8, 8:-8] = 1
    d = blur(d, 1.2) * (0.82 + 0.18 * noise(h, w, 10, 3, 141))
    for k, c in enumerate(text):
        g, _ = text_layer(c, FONT_JP, 100)
        gh, gw = g.shape
        cx, cy = w / 2 + (k - (len(text) - 1) / 2) * 120, h / 2
        y0, x0 = int(cy - gh / 2), int(cx - gw / 2)
        d[y0:y0 + gh, x0:x0 + gw] *= 1 - 0.95 * g
    return d
