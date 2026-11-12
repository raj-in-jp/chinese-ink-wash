"""The scenes of the reel: the hook, one scene per era (scenes/era.py, built from its key), and the ending.  Each
scene is built lazily (painting its assets once, cached on disk) and renders a float RGB frame for any absolute time
inside its window."""
import importlib

from timeline import ERA_KEYS, SCENES

_MODULES = {'hook': 's_hook', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        if name in ERA_KEYS:
            from scenes.era import Scene
            _built[name] = Scene(t0, t1, name)
        else:
            _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
