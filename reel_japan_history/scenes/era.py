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
from engine import (FONT_BRUSH_JP, FONT_EN_BOLD, FONT_EN_ITALIC, FONT_HEAD, FONT_JP, GREY, H, INK, VERM, W, Cam, blur, cached,
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
KANJI_Y, KANA_Y, ROM_Y, YEAR_Y = 425, 600, 655, 728


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
        self.kana, _ = text_layer(kana, FONT_JP, 58)
        self.rom, _ = text_layer(rom, FONT_EN_BOLD, 40, tracking=8)
        self.art = cached(f'h7_{k}_v1', getattr(hart, k))
        self.T_art = wash_map(H, W, (0 if self.idx % 2 else W, 1100), noise_amp=0.3, noise_scale=180, seed=self.paper_seed)
        self.T_turn = wash_map(H, W, None, direction=(-1, -0.15), noise_amp=0.22, noise_scale=260, seed=self.paper_seed + 1)
        self._years = {}
        self.dot = soft_disc(40, 40, 20, 20, 14, edge=2).astype(np.float32)
        self.rim = (soft_disc(44, 44, 22, 22, 15, edge=1.5) - soft_disc(44, 44, 22, 22, 11, edge=1.5)).clip(0, 1).astype(np.float32)
        self.extra_build()

    # ---------------------------------------------------------------- per-era extras
    def extra_build(self):
        k = self.key
        if k == 'kamakura':
            self.junks = [hart.junk() for _ in range(3)]
            self.t_back = at('driven back')[0]
        elif k == 'heian':
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

    # ---------------------------------------------------------------- camera and transition
    def cam(self, t):
        u = smooth((t - self.t0) / max(self.t1 - self.t0, 1))
        shake = 0
        if self.key == 'taisho':
            q = t - self.t_quake
            shake = 14 * np.exp(-q * 2.5) * np.sin(q * 47) * (q > 0)
        return Cam(540 + 18 * (u - 0.5) * (1 if self.idx % 2 else -1) + shake, 960 + 0.5 * shake, 1.0 + 0.035 * u)

    def enter(self, prev_img, cur_img, f, prev_scene):
        """the next era is unrolled over the last one from the right, a wet ink edge riding the front"""
        return wipe_mix(prev_img, cur_img, self.T_turn, ease_io(f) * 1.12 - 0.04, soft=0.05, edge=0.35)

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
        fa = (t - self.t0 - 0.1) / 1.0
        for c in ('grey', 'blue', 'red', 'gold', 'ink', 'bloss'):
            if c in self.art and fa > 0:
                self.layer(fr, cam, reveal_time(self.art[c], self.T_art, fa), *self.art_offset(t, c), color=COLOURS[c],
                           opacity=0.95 if c != 'red' else 0.85)
        self.extras(fr, cam, t)
        # the era's name, reading, romaji and year
        for j, g in enumerate(self.glyphs):
            fk = (t - self.t_in + 0.25 - 0.18 * j) / 0.45
            if fk > 0:
                x = 540 + (j - (len(self.glyphs) - 1) / 2) * 280
                kit.put(fr, cam, g.at(fk, soft=0.05), x, KANJI_Y, INK, 1.0, 1 + 0.12 * np.exp(-fk * 3))
        fr_ = smooth((t - self.t_in - 0.3) / 0.3)
        kit.put(fr, cam, self.kana, 540, KANA_Y + 10 * (1 - fr_), INDIGO, fr_)
        kit.put(fr, cam, self.rom, 540, ROM_Y + 10 * (1 - fr_), GREY, smooth((t - self.t_in - 0.45) / 0.3))
        kit.put(fr, cam, self.year_patch(t), 540, YEAR_Y, VERM, smooth((t - self.t0 - 0.1) / 0.25))
        self.ribbon(fr, t)
        return fr.img

    def art_offset(self, t, c):
        if self.key == 'edo' and c == 'blue':
            return 0, 6 * np.sin(t * 2.2)
        if self.key == 'ships':
            return 160 * (1 - ease_out((t - self.t0) / 2.4)), 3 * np.sin(t * 2.5)
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
        elif k == 'heian':
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
                ox = 160 * (1 - ease_out((t - self.t0) / 2.4))
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
