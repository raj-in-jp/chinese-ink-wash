"""intro — a 5.4 s cold open for reel 12 cut from the user's copy of Namewee's "Tokyo Bon 2020" music video.

The clip (41.0–46.4 s of the video: "Makudonarudo… Guguru Toiletto… Kitto Katto") plays in one continuous piece, so
the song is never cut mid-beat.  It sits in a rounded frame on the reel's ink paper, gently zooming, with the burnt-in
subtitle band cropped off; above it THIS SONG SINGS ENGLISH… LIKE THIS, below it each sung word arrives as the English
word plus its katakana tiles and romaji, swapped in time with the singer; a small credit line at the bottom.
The last 0.3 s dissolve into the reel's own first frames (done in assemble_intro).

    python3 intro.py SRC.mp4      -> output/intro.mp4 (video) + audio/intro.wav (the song, levelled, no peaks)
"""
import os
import subprocess
import sys

import cv2
import numpy as np

import kit
from engine import FONT_BOLD, FONT_EN_BOLD, FONT_ROUND, GREY, H, INK, VERM, W, Cam, ease_out, smooth, text_layer
from scenes.common12 import PALETTE, Tile, label, rbox, tile_row, drop_y, pulse
from scenes.kscene import KanjiScene

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
CLIP0, DUR = 41.0, 5.4
HOLD = 0.4                                     # 41.0-41.4 is a blurry whip-pan: show the sign from frame 1
VX, VY, VW = 540, 800, 1000                    # the video frame on the page
WORDS = [  # (time in the clip, English, katakana, romaji per tile)
    (0.0, "McDonald's", 'マクドナルド', ['ma', 'ku', 'do', 'na', 'ru', 'do']),
    (1.8, 'Google, Toilet', 'グーグル トイレット', ['gu', 'u', 'gu', 'ru', '', 'to', 'i', 're', 't', 'to']),
    (3.6, 'Kit Kat', 'キット カット', ['ki', 't', 'to', '', 'ka', 't', 'to']),
]


class Intro(KanjiScene):
    paper_seed = 1201

    def build(self):
        self.l1 = text_layer('THIS SONG SINGS ENGLISH…', FONT_BOLD, 92, tracking=3)[0]
        self.l2 = text_layer('LIKE THIS!', FONT_BOLD, 120, tracking=4)[0]
        self.credit = label('MUSIC VIDEO: NAMEWEE – TOKYO BON 2020', 26, FONT_EN_BOLD, 4)
        self.rows = []
        for j, (t, en, kana, rom) in enumerate(WORDS):
            n = sum(1 for k in kana if k != ' ')
            size = 132 if n <= 6 else 98
            gap, wgap = (14, 0) if n <= 6 else (8, 26)
            tiles, xs, x = [], [], 0.0
            for i, (k, r) in enumerate(zip(kana, rom)):
                if k == ' ':
                    x += wgap
                    continue
                tiles.append(Tile(k, size, PALETTE[(len(tiles) + j) % 4], romaji=r))
                xs.append(x)
                x += size + gap
            w = xs[-1]
            xs = [540 - w / 2 + v for v in xs]
            self.rows.append((t, label(en, 64, FONT_ROUND, 2), tiles, xs, size))

    def render(self, t, vid):
        cam = Cam(540, 960, 1.0)
        fr = self.frame(cam)
        # titles: on screen from frame 1
        kit.put(fr, cam, self.l1, 540, 205, INK, 1.0)
        f2 = (t - 0.15) / 0.2
        if f2 > 0:
            kit.put(fr, cam, self.l2, 540, 330, VERM, smooth(f2), 1 + 0.35 * np.exp(-f2 * 2.5), rot=-0.03)
        # the clip: rounded, ivory rim, soft shadow, slow push-in
        h = int(round(VW * vid.shape[0] / vid.shape[1]))
        img = cv2.resize(vid, (VW, h), interpolation=cv2.INTER_CUBIC)
        img = np.clip(img * 1.0 + (img - cv2.GaussianBlur(img, (0, 0), 1.6)) * 0.6, 0, 1)   # gentle sharpen of the 360p source
        m = rbox(h, VW, 34)
        sh = cv2.GaussianBlur(rbox(h + 40, VW + 40, 50), (0, 0), 14)
        kit.put(fr, cam, sh, VX + 10, VY + 18, INK, 0.35)
        kit.put(fr, cam, rbox(h + 22, VW + 22, 42), VX, VY, np.array([0.98, 0.96, 0.9], np.float32), 1.0, over=True)
        y0, x0 = VY - h // 2, VX - VW // 2
        a = m[..., None]
        fr.img[y0:y0 + h, x0:x0 + VW] = fr.img[y0:y0 + h, x0:x0 + VW] * (1 - a) + img * a
        # the sung words: English on a slip, katakana tiles dropping in, romaji under
        for j, (t0, en, tiles, xs, size) in enumerate(self.rows):
            t1 = self.rows[j + 1][0] if j + 1 < len(self.rows) else 99
            if t < t0 or t > t1 + 0.12:
                continue
            out = 1 - smooth((t - t1) / 0.12)
            fe = (t - t0) / 0.15
            kit.put(fr, cam, en, 540, 1180, INK, smooth(fe) * out, 1 + 0.2 * np.exp(-fe * 3))
            for k, (tl, x) in enumerate(zip(tiles, xs)):
                tk = t0 + 0.06 * k
                if t > tk:
                    y = 1360 + drop_y(t, tk, 160, 0.3)
                    tl.draw(fr, cam, x, y, smooth((t - tk) / 0.08) * out, pulse(t, tk + 0.2, 0.18))
                    tl.draw_rom(fr, cam, x, y + size * 0.72, smooth((t - tk - 0.15) / 0.15) * out)
        kit.put(fr, cam, self.credit, 540, 1640, GREY, 0.9)
        return fr.img


def main(src):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(CLIP0), '-t', str(DUR), '-i', src,
                          '-vf', f'fps={FPS},crop=640:268:0:0,format=rgb24', '-f', 'rawvideo', '-'],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 268, 640, 3)
    n = int(round(DUR * FPS))
    sc = Intro(0, DUR)
    out = os.path.join(HERE, 'output', 'intro.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                          '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        v = fr[min(max(k, int(HOLD * FPS)), len(fr) - 1)].astype(np.float32) / 255   # hold the sign shot through the whip-pan
        z = 1 + 0.05 * t / DUR                                   # slow push-in, centred a little high (on the faces)
        hh, ww = v.shape[:2]
        M = np.array([[z, 0, (1 - z) * ww / 2], [0, z, (1 - z) * hh * 0.4]], np.float32)
        v = cv2.warpAffine(v, M, (ww, hh), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        p.stdin.write((np.clip(sc.render(t, v), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()
    # the song: same stretch, fades of 25 ms in / 300 ms out, levelled to sit just under Raj's voice with a limiter
    import re
    r = subprocess.run(['ffmpeg', '-ss', str(CLIP0), '-t', str(DUR), '-i', src, '-af', 'ebur128', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    lufs = float(re.search(r'I:\s+(-?[\d.]+) LUFS', r[r.rfind('Summary:'):]).group(1))
    gain = -17.0 - lufs
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(CLIP0), '-t', str(DUR), '-i', src, '-ac', '2', '-ar', '48000',
                    '-af', f'volume={gain:.2f}dB,acompressor=threshold=0.18:ratio=2.5:attack=8:release=120,'
                           f'alimiter=limit=0.6:attack=3:release=60:level=0,afade=t=in:d=0.025,afade=t=out:st={DUR - 0.3}:d=0.3',
                    os.path.join(HERE, 'audio', 'intro.wav')], check=True)
    print('wrote', out, n, 'frames')


if __name__ == '__main__':
    main(sys.argv[1])
