"""thumbnail — the cover (1080x1920): the hook as a still: 大和 with BIG and HARMONY, DAI and WA crossed out, the やまと tiles
and 0 SOUNDS MATCH!
    python thumbnail.py   -> output/thumbnail.jpg
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scenes.s_hook import Scene  # noqa: E402
from timeline import SCENES  # noqa: E402


def main():
    t0, t1 = [s[1:] for s in SCENES if s[0] == 'hook'][0]
    sc = Scene(t0, t1)
    img = sc.render(sc.t_zero + 0.7)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
