"""thumbnail — the cover (1080x1920), the hook's own last beat as a still: JAPAN'S ENTIRE / HISTORY at the top, the
relief map of Japan under it with every real picture pinned to its region as a polaroid, and IN (2) MINUTES — the
vermilion ensō round the 2 — between the title and the map.  The profile grid shows the centre 3:4 (y 240-1680), so
the title, the ensō and the map all sit inside it.
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
from engine import Frame, FONT_BRUSH_EN, FONT_HEAD, H, INK, VERM, W, Cam, StrokeSet, noise, text_layer  # noqa: E402
from scenes.s_hook import Scene  # noqa: E402

CAM = Cam(540, 960, 1.0)


def brush(s, size, seed):
    d, _ = text_layer(s, FONT_BRUSH_EN, size)
    return d * (0.86 + 0.14 * noise(*d.shape, 6, 2, seed))


def main():
    sc = Scene(0.0, 10.0)
    z = np.zeros((2, 2), np.float32)
    sc.cap = [(z, z)] * len(sc.cap)                      # no era caption: the ensō takes that place
    t = sc.t_90 - 0.15                                   # every picture has landed, the map not yet sunk back
    sc.cam = lambda t_: CAM
    img = sc.render(t)

    fr = Frame(img)
    # "IN (2) MINUTES": a small vermilion ensō round a brushed 2
    ss = StrokeSet(W, H)
    enso(ss, 470, 585, 62, 9, 0, 0.01, seed=5, red=True)
    m = ss.render(5, red=True)
    a = m[..., None] * 0.95
    fr.img = fr.img * (1 - a) + VERM * a
    kit.put(fr, CAM, text_layer('IN', FONT_HEAD, 52)[0], 350, 588, INK, 1.0)
    kit.put(fr, CAM, brush('2', 96, 3), 470, 582, INK, 1.0)
    kit.put(fr, CAM, text_layer('MINUTES', FONT_HEAD, 52)[0], 685, 588, INK, 1.0)
    # shrink the whole page a little onto fresh paper, so the profile grid's 3:4 crop (y 240-1680) holds all of it
    import cv2
    k, cy = 0.87, 975
    M = np.array([[k, 0, 540 * (1 - k)], [0, k, cy * (1 - k)]], np.float32)
    small = cv2.warpAffine(fr.img, M, (W, H), flags=cv2.INTER_AREA)
    m = np.zeros((H, W), np.float32)
    m[150:-150, 130:-130] = 1
    m = cv2.GaussianBlur(cv2.warpAffine(m, M, (W, H)), (0, 0), 55)[..., None]
    paper = sc.frame(CAM).img
    fr.img = small * m + paper * (1 - m)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
