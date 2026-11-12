"""thumbnail — the cover (1080x1920), painted with the reel's own ink engine.  The profile grid shows the centre 3:4
(y 240-1680), so the title, the motif and the handle all sit inside it.
  JAPAN'S ENTIRE / HISTORY / IN 2 MINUTES over a vermilion ensō with 90 in it, the fifteen era names in three rows
  under it, misty hills, and the @raj_in_jp banner at the bottom.
    python thumbnail.py   -> output/thumbnail.jpg
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402
from art import enso  # noqa: E402
from cards import INDIGO  # noqa: E402
from engine import (GREY, FONT_BRUSH_EN, FONT_EN_BOLD, FONT_HEAD, FONT_JP, H, INK, VERM, W, Cam, Frame, StrokeSet,  # noqa: E402
                    cached, make_paper, noise, stroke, text_layer)
from k6art import mist_hills  # noqa: E402
from scenes.era import ERAS, FURI  # noqa: E402
from timeline import ERA_KEYS  # noqa: E402

CAM = Cam(540, 960, 1.0)
IVORY = np.array([0.98, 0.95, 0.88], np.float32)


def brush(s, size, seed):
    d, _ = text_layer(s, FONT_BRUSH_EN, size)
    return d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed))


def main():
    fr = Frame(make_paper(W, H, 299, stains=0.08))
    fr.ink(cached('h7_hookhills_v1', lambda: mist_hills(1330, seed=17))['ink'], INK, 0.7)
    kit.put(fr, CAM, text_layer("JAPAN'S ENTIRE", FONT_HEAD, 86)[0], 540, 330, INK, 1.0)
    kit.put(fr, CAM, brush('HISTORY', 230, 1), 540, 480, VERM, 1.0, rot=-0.03)
    ss = StrokeSet(W, H)
    enso(ss, 540, 790, 175, 18, 0, 0.01, seed=5, red=True)
    fr.ink(ss.render(5, red=True), VERM, 0.95)
    kit.put(fr, CAM, brush('2', 190, 3), 540, 760, INK, 1.0)
    kit.put(fr, CAM, text_layer('MINUTES', FONT_EN_BOLD, 34, tracking=10)[0], 540, 870, INK, 0.8)
    keys = [k for k in ERA_KEYS if k != 'ships']
    for j, k in enumerate(keys):
        x, y = 160 + (j % 5) * 190, 1050 + (j // 5) * 158
        kit.put(fr, CAM, text_layer(ERAS[k][0], FONT_JP, 74)[0], x, y, INK if j < 14 else VERM, 1.0)
        fu = FURI[k]
        for i, f in enumerate(fu):
            if f:
                fx = x if not all(fu) else x + (i - 0.5) * 74
                kit.put(fr, CAM, text_layer(f, FONT_JP, 22)[0], fx, y - 52, INDIGO, 0.9)
        kit.put(fr, CAM, text_layer(ERAS[k][2].split(' ')[0], FONT_EN_BOLD, 22, tracking=3)[0], x, y + 52, GREY, 1.0)
    bn = StrokeSet(W, H)
    bn.add(stroke(W, H, [(270, 1596), (540, 1586), (810, 1594)], 112, ink=0.96, dry=0.5,
                  profile=((0, 0.6), (0.06, 1.0), (0.85, 0.95), (1, 0.4)), seed=171), 0, 1)
    fr.ink(bn.render(5), INK, 0.96)
    kit.put(fr, CAM, text_layer('@raj_in_jp', FONT_BRUSH_EN, 86)[0], 540, 1584, IVORY, 1.0, over=True)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
