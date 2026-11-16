"""The scenes of the reel: the hook sentence, kanji borrowed from China, the verb-ending problem, hiragana (安 → あ),
katakana (伊 → イ), the payoff (no spaces), and the ending.  Each scene is built lazily and renders a float RGB frame
for any absolute time inside its window."""
import importlib

from timeline import SCENES

_MODULES = {'hook': 's_hook', 'borrow': 's_borrow', 'endings': 's_endings', 'hira': 's_hira', 'kata': 's_kata',
            'payoff': 's_payoff', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
