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
# the Japanese words, (clip, kana, romaji shown in the captions): the first three from audio/words_ja_1.mp3,
# the rest from audio/words_ja_2a.mp3
JA_WORDS = [('kanji', 'かんじ', 'kanji'), ('hiragana', 'ひらがな', 'hiragana'), ('katakana', 'カタカナ', 'katakana')]
JA_WORDS2 = [('watashi', 'わたし', 'watashi'), ('nomu', 'のむ', 'nomu'), ('wa', 'は', 'wa'), ('o', 'を', 'o'), ('masu', 'ます', 'masu'),
             ('kohi', 'コーヒー', 'kōhī')]
SENTENCE = ('sentence', '私はコーヒーを飲みます', 'watashi wa kōhī o nomimasu')        # audio/sentence_1.mp3
# stand-ins in the order they are spoken: (words in the take, normalised; clip)
STAND_IN = [('watashi wa kohi o nomimasu', 'sentence'), ('kanji', 'kanji'), ('hiragana', 'hiragana'), ('katakana', 'katakana'),
            ('kanji', 'kanji'), ('watashi', 'watashi'), ('nomu', 'nomu'), ('hiragana', 'hiragana'), ('wa', 'wa'), ('o', 'o'),
            ('masu', 'masu'), ('katakana', 'katakana'), ('kohi', 'kohi'), ('hiragana', 'hiragana'),
            ('hiragana', 'hiragana'), ('katakana', 'katakana'), ('kanji', 'kanji')]
ERAS = []
MATANE = ('matane', 'またね！', 'matane!')
# silence after these words: the sentence lands, the three scripts are named, each "aha" gets a beat
HOLD = {'Why?!': 0.25, 'line.': 0.2, 'job.': 0.25, 'coffee.': 0.3, 'spaces.': 0.3, 'letters.': 0.5, 'word.': 0.5}
PAD = 0.04
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
    en = load('take_en_v2a.mp3')
    e = env(en)
    words = [w for w in json.load(open(os.path.join(A, 'words_en_v2a.json')))['words'] if w.get('type', 'word') == 'word']
    rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2))
    level = rms(en)
    jw = load('words_ja_1.mp3')
    segs = segments(jw)
    clips = {k: faded(jw[int(a * SR):int(b * SR)]) for (k, _, _), (a, b) in zip(JA_WORDS, segs)}
    j2 = load('words_ja_2a.mp3')
    s2 = []
    for a, b in segments(j2):                               # a breath split off a word joins the word before it
        if s2 and (b - a < 0.15 or a - s2[-1][1] < 0.12):
            s2[-1] = (s2[-1][0], b)
        else:
            s2.append((a, b))
    assert len(s2) == len(JA_WORDS2), f'{len(s2)} segments in the second Japanese words take'
    clips.update({k: faded(j2[int(a * SR):int(b * SR)]) for (k, _, _), (a, b) in zip(JA_WORDS2, s2)})
    sn = load('sentence_1.mp3')
    ss = segments(sn, hold=40)
    clips['sentence'] = faded(sn[int(ss[0][0] * SR):int(ss[-1][1] * SR)])
    for k in clips:
        clips[k] *= 0.95 * level / rms(clips[k])
    edits, i0, seen = [], 0, {}
    for phrase, clip in STAND_IN:
        target = phrase.split()
        i = next(i for i in range(i0, len(words)) if [norm(w['text']) for w in words[i:i + len(target)]] == target)
        j = i + len(target) - 1
        i0 = j + 1
        seen[clip] = seen.get(clip, 0) + 1
        key = clip if seen[clip] == 1 else f'{clip}{seen[clip]}'
        prev_end = words[i - 1]['end']
        nxt = words[j + 1]['start'] if j + 1 < len(words) else words[j]['end'] + 0.3
        a = silent_edge(e, prev_end - 0.04, words[i]['start'] + 0.06, 'before')
        b = silent_edge(e, words[j]['end'] - 0.06, nxt + 0.04, 'after')
        pad = np.zeros(int(PAD * SR), np.float32)
        pre = np.zeros(int(ERA_BREATH * SR), np.float32) if clip in ERAS and key == clip else pad
        edits.append([a, b, np.concatenate([pre, clips[clip], pad]), key, (i, j, clip)])
    for i, w in enumerate(words[:-1]):
        if w['text'] in HOLD:
            c = quietest(e, w['end'] + 0.02, words[i + 1]['start'] - 0.02)
            edits.append([c, c, np.zeros(int(HOLD[w['text']] * SR), np.float32), None, (i, i, None)])
    end = min(len(en) / SR, words[-1]['end'] + 0.15)
    mt = load('matane_a.mp3')
    ms = segments(mt, hold=40)
    mt = faded(mt[int(ms[0][0] * SR):int(ms[-1][1] * SR)])
    mt *= 0.95 * level / rms(mt)
    out, segs_out, cursor, t, shifts = [], {}, 0.0, 0.0, []
    for a, b, audio, k, _ in sorted(edits, key=lambda x: (x[0], x[1])):
        out.append(en[int(cursor * SR):int(a * SR)])
        t += a - cursor
        if k is not None:
            lead = ERA_BREATH if k in ERAS else PAD          # (k == clip only for the first time a word is said)
            segs_out[k] = dict(start=round(t + lead, 3), end=round(t + len(audio) / SR - PAD, 3))
        out.append(audio)
        t += len(audio) / SR
        shifts.append((a, b, t))
        cursor = b
    out.append(faded(en[int(cursor * SR):int(end * SR)]))
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

    lex = {k: (kana, rom) for k, kana, rom in JA_WORDS + JA_WORDS2 + [SENTENCE]}
    span = {x[4][0]: (x[4][1], x[3], x[4][2]) for x in edits if x[3] is not None}
    ws, i = [], 0
    while i < len(words):
        w = words[i]
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
