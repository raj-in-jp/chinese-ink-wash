"""thumbnail — the cover (1080x1920): the hook's own frame as a still.  JAPANESE USES / 3 ALPHABETS / IN 1 SENTENCE?!,
私はコーヒーを飲みます with every script in its colour, WHY?! stamped under it and the steaming cup.  Everything sits inside the profile grid's 3:4 crop (y 240-1680).
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
    t = sc.t_why + 0.45                                  # title, the sentence in its three colours, WHY?!, the steaming cup
    fr = Frame(sc.render(t))
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(fr.img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
