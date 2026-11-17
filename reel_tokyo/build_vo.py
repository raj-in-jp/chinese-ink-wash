"""build_vo — the narration: Raj's English take with every Japanese word spoken by Raj in Japanese.

    audio/take_en_a.mp3 + words_en_a.json     the English take, romaji stand-ins in it (Scribe word timings)
    audio/words_ja_a.mp3                      the 31 Japanese words, one after another (split on their silences)
    audio/words_ja_b.mp3                      しょうぐん。 とくがわ。
    audio/matane_a.mp3                        またね！ (after "follow for more.")

Each stand-in (one word, or two for Murasaki Shikibu) is cut at the silent edge either side of it, so the pauses
round it stay, and replaced by its Japanese clip.  A word said twice (samurai, Tokyo) reuses its clip; the second
gets key `<key>2`.  Writes audio/narration.wav + .mp3 and audio/words.json: the English words shifted into place
(each replaced word shown in romaji, flagged ja) plus the Japanese segments {key: text, romaji, start, end}.
"""
import json
import os
import re
import subprocess

import numpy as np
from scipy.io import wavfile

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
SR = 48000
# the Japanese words (audio/words_ja_1.mp3), in order: (clip, kana, romaji shown in the captions)
JA_WORDS = [('tokyo', 'とうきょう', 'Tōkyō'), ('nara', 'なら', 'Nara'), ('kyoto', 'きょうと', 'Kyōto'), ('edo', 'えど', 'Edo')]
JA_WORDS2 = []
# stand-ins in the order they are spoken: (words in the take, normalised; clip)
STAND_IN = [(w, w) for w in ('tokyo', 'tokyo', 'nara', 'kyoto', 'edo', 'edo', 'edo', 'tokyo', 'kyoto', 'edo', 'tokyo')]
ERAS = []
MATANE = ('matane', 'またね！', 'matane!')
# silence after these words: the sentence lands, the three scripts are named, each "aha" gets a beat
HOLD = {'Tokyo!': 0.3, 'years.': 0.3, 'world.': 0.3, 'east.': 0.3, 'name:': 0.25, 'west.': 0.35, 'twist.': 0.3, 'capital!': 0.4}
PAD = 0.04
CUT = [("And here's the twist.", 'capital!')]          # the 'no law names the capital' line, taken out
ERA_BREATH = 0.0


def norm(s):
    return re.sub(r'[^a-z]', '', s.lower())


def load(name):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(A, name), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def env(x):
    h = SR // 100
    return 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')[::h]) + 1e-9)


def segments(x, thresh=-42, hold=12):
    on = env(x) > thresh
    segs, i = [], 0
    while i < len(on):
        if on[i]:
            j = i
            while j < len(on) and (on[j] or on[j:j + hold].any()):
                j += 1
            segs.append((max(0, i - 2) / 100, min(len(on), j + 3) / 100))
            i = j
        else:
            i += 1
    return segs


def faded(y, ms=10):
    y = y.copy()
    n = int(SR * ms / 1000)
    y[:n] *= np.linspace(0, 1, n)
    y[-n:] *= np.linspace(1, 0, n)
    return y


def joined(y, first=False, ms=18):
    """a slice of the take that is about to be spliced: a short fade at each cut edge, so no join clicks or stops dead"""
    y = y.copy()
    k = int(SR * 0.02)
    lvl = lambda s: 20 * np.log10(np.sqrt(np.mean(s ** 2)) + 1e-9) if len(s) else -120
    for side in ('in', 'out'):
        if side == 'in' and first:
            continue
        edge = y[:k] if side == 'in' else y[-k:]
        L = 60 if lvl(edge) > -38 else ms                # cut on live speech: a longer, natural-sounding decay
        n = min(int(SR * L / 1000), len(y) // 2)
        if n <= 0:
            continue
        if side == 'in':
            y[:n] *= np.sin(np.linspace(0, np.pi / 2, n)) ** 2
        else:
            y[-n:] *= np.cos(np.linspace(0, np.pi / 2, n)) ** 2
    return y


def quietest(e, t0, t1):
    a, b = int(t0 * 100), max(int(t0 * 100) + 1, int(t1 * 100))
    return (a + int(np.argmin(e[a:b]))) / 100


def silent_edge(e, t0, t1, side, thresh=-55):
    a, b = int(t0 * 100), max(int(t0 * 100) + 1, int(t1 * 100))
    q = np.where(e[a:b] < thresh)[0]
    if len(q) == 0:
        return quietest(e, t0, t1)
    return (a + (q[-1] if side == 'before' else q[0])) / 100


def main():
    en = load('take_en_a.mp3')
    e = env(en)
    words = [w for w in json.load(open(os.path.join(A, 'words_en_a.json')))['words'] if w.get('type', 'word') == 'word']
    rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2))
    level = rms(en)
    # lines taken out of the take: (first words, last word); the audio is cut at the quiet gaps either side
    cut_ranges = []
    for first, last in CUT:
        fw = [norm(x) for x in first.split()]
        ci = next(i for i in range(len(words)) if [norm(w['text']) for w in words[i:i + len(fw)]] == fw)
        cj = next(k for k in range(ci, len(words)) if words[k]['text'] == last)
        cut_ranges.append((ci, cj))
    in_cut = lambda k: any(a_ <= k <= b_ for a_, b_ in cut_ranges)
    jw = load('words_ja_1.mp3')
    segs = []
    for a, b in segments(jw):                               # the small っ splits にっぽん: join it back
        if segs and (b - a < 0.15 or a - segs[-1][1] < 0.12):
            segs[-1] = (segs[-1][0], b)
        else:
            segs.append((a, b))
    assert len(segs) == len(JA_WORDS), f'{len(segs)} segments in the Japanese words take'
    bounds = [0.0] + [(segs[k][1] + segs[k + 1][0]) / 2 for k in range(len(segs) - 1)] + [len(jw) / SR]
    # keep each word's natural decay: 30 ms before and 80 ms after its loud part (never past halfway to the next word)
    clips = {k: faded(jw[int(max(a - 0.03, bounds[n]) * SR):int(min(b + 0.08, bounds[n + 1]) * SR)], 22)
             for n, ((k, _, _), (a, b)) in enumerate(zip(JA_WORDS, segs))}
    for k in clips:
        clips[k] *= 0.95 * level / rms(clips[k])
    edits, i0, seen = [], 0, {}
    for phrase, clip in STAND_IN:
        target = phrase.split()
        i = next(i for i in range(i0, len(words)) if not in_cut(i) and [norm(w['text']) for w in words[i:i + len(target)]] == target)
        j = i + len(target) - 1
        i0 = j + 1
        seen[clip] = seen.get(clip, 0) + 1
        key = clip if seen[clip] == 1 else f'{clip}{seen[clip]}'
        prev_end = words[i - 1]['end'] if i > 0 else 0.0
        nxt = words[j + 1]['start'] if j + 1 < len(words) else words[j]['end'] + 0.3
        a = 0.0 if i == 0 else silent_edge(e, prev_end - 0.04, words[i]['start'] + 0.06, 'before')
        b = silent_edge(e, words[j]['end'] - 0.06, nxt + 0.04, 'after')
        pad = np.zeros(int(PAD * SR), np.float32)
        pre = np.zeros(int(ERA_BREATH * SR), np.float32) if clip in ERAS and key == clip else pad
        edits.append([a, b, np.concatenate([pre, clips[clip], pad]), key, (i, j, clip)])
    for ci, cj in cut_ranges:
        a_ = quietest(e, words[ci - 1]['end'], words[ci]['start'] + 0.02)
        b_ = quietest(e, words[cj]['end'], words[cj + 1]['start'] + 0.02)
        edits.append([a_, b_, np.zeros(int(0.2 * SR), np.float32), None, (ci, cj, None)])
    for i, w in enumerate(words[:-1]):
        if in_cut(i) or in_cut(i + 1):
            continue
        if w['text'] in HOLD:
            # only where the voice has really died away; never cut a pause into the tail of a word
            a0, b0 = int((w['end'] + 0.02) * 100), int((words[i + 1]['start'] - 0.02) * 100)
            q = [k for k in range(a0, max(a0, b0)) if e[k] < -45]
            if not q:
                print(f'  hold after {w["text"]!r} skipped: no silence in the gap')
                continue
            c = q[len(q) // 2] / 100
            edits.append([c, c, np.zeros(int(HOLD[w['text']] * SR), np.float32), None, (i, i, None)])
    end = min(len(en) / SR, words[-1]['end'] + 0.15)
    mt = load('matane_a.mp3')
    ms = segments(mt, hold=40)
    mt = faded(mt[int(ms[0][0] * SR):int(ms[-1][1] * SR)])
    mt *= 0.95 * level / rms(mt)
    out, segs_out, cursor, t, shifts = [], {}, 0.0, 0.0, []
    for a, b, audio, k, _ in sorted(edits, key=lambda x: (x[0], x[1])):
        out.append(joined(en[int(cursor * SR):int(a * SR)], first=cursor == 0))
        t += a - cursor
        if k is not None:
            lead = ERA_BREATH if k in ERAS else PAD          # (k == clip only for the first time a word is said)
            segs_out[k] = dict(start=round(t + lead, 3), end=round(t + len(audio) / SR - PAD, 3))
        out.append(audio)
        t += len(audio) / SR
        shifts.append((a, b, t))
        cursor = b
    out.append(joined(en[int(cursor * SR):int(end * SR)]))
    t += end - cursor
    t_mt = t + 0.4
    out += [np.zeros(int(0.4 * SR), np.float32), mt, np.zeros(int(0.2 * SR), np.float32)]
    nar = np.concatenate(out)

    def sh(x):
        base_en, base_out = 0.0, 0.0
        for a, b, t_after in shifts:
            if x < a:
                break
            base_en, base_out = b, t_after
        return base_out + (x - base_en)

    lex = {k: (kana, rom) for k, kana, rom in JA_WORDS}
    span = {x[4][0]: (x[4][1], x[3], x[4][2]) for x in edits if x[3] is not None}
    ws, i = [], 0
    while i < len(words):
        w = words[i]
        if in_cut(i):
            i += 1
            continue
        if i in span:
            j, key, clip = span[i]
            last = words[j]['text']
            punct = last[-1] if last[-1] in '.,:!?' else ''
            ws.append(dict(text=lex[clip][1] + punct, type='word', ja=key, start=segs_out[key]['start'], end=segs_out[key]['end']))
            i = j + 1
            continue
        ws.append(dict(text=w['text'], type='word', start=round(sh(w['start']), 3), end=round(sh(w['end']), 3)))
        i += 1
    t_end = round(t_mt + len(mt) / SR, 3)
    ws.append(dict(text=MATANE[2], type='word', ja=MATANE[0], start=round(t_mt, 3), end=t_end))
    ja = {}
    for x in edits:
        if x[3] is not None:
            clip = x[4][2]
            ja[x[3]] = dict(text=lex[clip][0], romaji=lex[clip][1], **segs_out[x[3]])
    ja[MATANE[0]] = dict(text=MATANE[1], romaji=MATANE[2], start=round(t_mt, 3), end=t_end)
    wavfile.write(os.path.join(A, 'narration.wav'), SR, (np.clip(nar, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(A, 'narration.wav'), '-b:a', '192k',
                    os.path.join(A, 'narration.mp3')], check=True)
    json.dump({'words': ws, 'ja': ja}, open(os.path.join(A, 'words.json'), 'w'), ensure_ascii=False, indent=0)
    print(f'narration {len(nar) / SR:.2f}s')
    for k, v in sorted(ja.items(), key=lambda kv: kv[1]['start']):
        print(f'  {k:11s} {v["start"]:6.2f}-{v["end"]:6.2f}  {v["text"]}')


if __name__ == '__main__':
    main()
