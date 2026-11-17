"""The scenes of reel 9, 'Who named Japan?': the hook, 日本 = sun + origin, the journey of the name across the world
map (China, Marco Polo, Columbus, the Portuguese, English), the whole chain of names, and the ending."""
import importlib

from timeline import SCENES

_MODULES = {'hook': 's_hook', 'nihon': 's_nihon', 'journey': 's_journey', 'outro': 's_outro', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
