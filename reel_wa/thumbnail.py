"""thumbnail — the cover (1080x1920): the opening frame as a still: THE LAND OF THE RISING SUN over a red sun coming
out of the sea, and BECAUSE OF CHINA?! with the 中國 seal.
    python thumbnail.py   -> output/thumbnail.jpg
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scenes.s_rising import Scene  # noqa: E402


def main():
    sc = Scene(0.0, 5.87)
    img = sc.render(sc.t_cn + 0.9)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
