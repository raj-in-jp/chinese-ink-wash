"""The scenes of reel 11, 'Japan's old name': the hook (the bold letter of 607), 倭 Wa, the rename to 日本, the same sound
with a new kanji 和, 和 everywhere today, and the ending."""
import importlib

from timeline import SCENES

_MODULES = {'rising': 's_rising', 'hook': 's_hook', 'wa': 's_wa', 'rename': 's_rename', 'harmony': 's_harmony', 'today': 's_today', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
