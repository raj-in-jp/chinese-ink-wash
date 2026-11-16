"""The scenes of the reel: the hook sentence, each script's job (kanji = meaning, hiragana = grammar, katakana =
foreign words), the payoff (no spaces: a wall of hiragana vs the three mixed), and the ending.  Each scene is built lazily and renders a float RGB frame
for any absolute time inside its window."""
import importlib

from timeline import SCENES

_MODULES = {'hook': 's_hook', 'jobs': 's_jobs', 'payoff': 's_payoff', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
