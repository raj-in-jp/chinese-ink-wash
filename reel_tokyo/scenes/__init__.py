"""The scenes of reel 10, 'Tokyo is only 150 years old': the hook (the skyline vanishes), the capitals on the Japan
chart (Nara, Kyoto, Edo), the rename (Edo becomes Tokyo, the eastern capital), the twist (no law names the capital),
and the ending."""
import importlib

from timeline import SCENES

_MODULES = {'hook': 's_hook', 'capitals': 's_capitals', 'rename': 's_rename', 'twist': 's_twist', 'end': 's_end'}
_built = {}


def get(name):
    if name not in _built:
        t0, t1 = next((a, b) for n, a, b in SCENES if n == name)
        _built[name] = importlib.import_module('scenes.' + _MODULES[name]).Scene(t0, t1)
    return _built[name]
