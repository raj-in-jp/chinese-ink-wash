"""thumbnail — the cover (1080x1920): the hook's own frame as a still: TOKYO 東京 crossed out, 1866, NO TOKYO?!
stamped over the marsh where the city stands today.
    python thumbnail.py   -> output/thumbnail.jpg
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from scenes.s_hook import Scene  # noqa: E402


def main():
    sc = Scene(0.0, 7.8)
    img = sc.render(sc.t_back - 0.3)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
