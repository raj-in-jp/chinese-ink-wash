"""word_bounds(e, s0, s1, minlen): the true start/end (seconds) of a word in the take, from the loudness envelope e
(10 ms frames, dB), given Scribe's rough s0..s1 (which can be 0.2-0.5 s off).
Start candidates in [s0-0.35, s0+0.15]: the end of the last real silence (< -50 dB for >= 50 ms) plus any deep dip
(< -45 dB) after it; if there is no silence, every dip below -30 dB (word boundaries run together there).  They are
tried from the latest back; a start is accepted only if the word it gives (up to the next silence, or the next dip once
`minlen` has passed) is at least `minlen` long — so a closure INSIDE the word (the k of Tokyo) is never taken for its
start, and a word before it ("And | Edo", "because | Kyoto") is never swallowed."""
import numpy as np


def _runs(mask):
    out, k = [], 0
    while k < len(mask):
        if mask[k]:
            j = k
            while j < len(mask) and mask[j]:
                j += 1
            out.append((k, j))
            k = j
        else:
            k += 1
    return out


def _dips(e, lo, hi, thr):
    return [k for k in range(max(lo, 1), min(hi, len(e) - 1)) if e[k] < thr and e[k] <= e[k - 1] and e[k] <= e[k + 1]]


def _end(e, a, s1, minlen):
    hi = int((s1 + 0.45) * 100)
    sil = [r for r in _runs(e[a + 5:hi] < -50) if r[1] - r[0] >= 5]
    if sil:
        return a + 5 + sil[0][0]
    d = _dips(e, a + int(minlen * 100), hi, -30)
    return d[0] if d else a + int(minlen * 100) + int(np.argmin(e[a + int(minlen * 100):hi]))


def _word_bounds(e, s0, s1, minlen):
    lo, hi = max(0, int((s0 - 0.35) * 100)), int((s0 + 0.15) * 100)
    sil = [r for r in _runs(e[lo:hi] < -50) if r[1] - r[0] >= 5]
    if sil:
        a0 = lo + sil[-1][1]
        cands = [a0] + [k + 1 for k in _dips(e, a0 + 8, hi, -45)]
    else:
        cands = _dips(e, lo, hi, -30) or [lo + int(np.argmin(e[lo:hi]))]
    for a in sorted(cands, reverse=True):
        b = _end(e, a, s1, minlen)
        if (b - a) / 100 >= minlen:
            return a / 100, b / 100
    a = min(cands)
    return a / 100, _end(e, a, s1, minlen) / 100


def word_bounds(e, s0, s1, minlen):
    """as _word_bounds, but if the span found holds no speech at all (Scribe placed the word in the silence after it),
    look again further back, up to 0.8 s earlier"""
    for back in (0.0, 0.25, 0.5, 0.8):
        a, b = _word_bounds(e, s0 - back, s1 - back, minlen)
        if b > a and e[int(a * 100):int(b * 100)].max() > -35:
            return a, b
    return _word_bounds(e, s0, s1, minlen)
