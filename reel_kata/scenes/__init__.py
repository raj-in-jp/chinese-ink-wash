"""The scenes of reel 12, 'Why does Japanese say Ma-ku-do-na-ru-do?': the hook, beats, added vowels, missing
sounds, Paris, and the ending."""
import importlib

from timeline import SCENES

_MODULES = {'hook': 's_hook', 'beats': 's_beats', 'vowels': 's_vowels', 'missing': 's_missing', 'paris': 's_paris', 'origins': 's_origins', 'puzzle': 's_puzzle', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
