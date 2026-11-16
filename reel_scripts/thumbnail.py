"""thumbnail — the cover (1080x1920): the hook's own frame as a still.  JAPANESE USES / 3 ALPHABETS / IN 1 SENTENCE,
私はコーヒーを飲みます with every script in its colour and bracketed, the three names under it (漢 KANJI · あ HIRAGANA ·
ア KATAKANA) and WHY?! stamped below.  Everything sits inside the profile grid's 3:4 crop (y 240-1680).
    python thumbnail.py   -> output/thumbnail.jpg
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kit  # noqa: E402
from engine import Cam, Frame, VERM  # noqa: E402
from scenes.common import COL, NAME, glyph, label  # noqa: E402
from scenes.s_hook import SY, Scene  # noqa: E402

CAM = Cam(540, 960, 1.0)


def main():
    sc = Scene(0.0, 20.0)
    sc.cam = lambda t_: CAM
    t = sc.t_why - 0.3                                   # every script lit, just before WHY?! (stamped below)
    fr = Frame(sc.render(t))
    xs = sc.s.xs(540, 0)
    sc.s.brackets(fr, CAM, 540, SY, xs, {'K': 1, 'H': 1, 'T': 1}, texts={})
    for j, (s_, ch) in enumerate((('K', '漢'), ('H', 'あ'), ('T', 'ア'))):
        lb = label(NAME[s_], 30)
        x, y = (180, 525, 880)[j], 1060
        w = 70 + 16 + lb.shape[1]
        kit.put(fr, CAM, glyph(ch, 70), x - w / 2 + 35, y, COL[s_], 1.0)
        kit.put(fr, CAM, lb, x - w / 2 + 86 + lb.shape[1] / 2, y, COL[s_], 1.0)
    kit.put(fr, CAM, sc.why, 540, 1300, VERM, 1.0, 1.0, rot=-0.06)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
