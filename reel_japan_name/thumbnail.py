"""thumbnail — the cover (1080x1920): the hook's own frame as a still.  The sea chart close on Japan, JAPAN crossed
out with a vermilion brush X, 日本 stamped on it with ISN'T JAPANESE, and WHO NAMED IT? across the top.
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
    sc = Scene(0.0, 9.6)
    img = sc.render(sc.t_who + 0.6)
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    out = os.path.join(HERE, 'output', 'thumbnail.jpg')
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out, quality=95)
    print('wrote', out)


if __name__ == '__main__':
    main()
