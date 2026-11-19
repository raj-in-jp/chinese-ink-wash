"""The scenes of reel 12, 'Why does Japanese say Ma-ku-do-na-ru-do?': the hook, beats, added vowels, missing
sounds, Paris, and the ending."""
import importlib

from timeline import SCENES

_MODULES = {'hook': 's_hook', 'region': 's_region', 'kanji': 's_kanji', 'reading': 's_reading', 'mystery': 's_mystery', 'today': 's_today', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
