"""build_vo — the narration: Raj's English take with every Japanese word spoken by Raj in Japanese.

The English take is recorded WITH A PAUSE wherever a Japanese word goes ("Test becomes... [pause]").  Each Japanese
clip is dropped into that silence — nothing is ever cut out of the middle of speech, so there is no leftover English
syllable, no clipped word and no click.  Cuts happen only inside silence (< -50 dB), with short fades.

    audio/take_en_b.mp3 + words_en_b.json    the English take (Scribe word timings; "[pause]" tokens mark the slots)
    audio/words_ja_1.mp3                     マクドナルド か き く け こ テスト クリスマス ライス サンキュー バイオリン パリ パリス
    audio/words_ja_2.mp3                     エネルギー アレルギー パン コーヒー
    audio/matane_a.mp3                       またね！ (after "follow for more.")

Writes audio/narration.wav + .mp3 and audio/words.json: the English words shifted into place, each Japanese word
inserted as a word flagged ja (romaji for the captions), plus the Japanese segments {key: text, romaji, start, end}.
"""
import json
import os
import re
import subprocess

import numpy as np
from scipy.io import wavfile

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'audio')
SR = 48000
TAKE, WORDS_JSON = 'take_en_a.mp3', 'words_en_a.json'
# one slow, clear take of every Japanese word, written in hiragana so it is always read with Japanese sounds
JA_TAKES = [('words_ja_1.mp3', [('daiwa', 'だいわ', 'dai-wa'), ('yamato', 'やまと', 'Yamato'), ('nara', 'なら', 'Nara'),
                                ('kyo', 'きょう', 'kyō'), ('otona', 'おとな', 'otona'), ('damashii', 'やまとだましい', 'Yamato-damashii'),
                                ('nadeshiko', 'やまとなでしこ', 'Yamato nadeshiko')])]
# what goes in each [pause] of the English take, in order; a clip said again gets key <clip>2, <clip>3 …
SLOTS = [['daiwa'], ['yamato'], ['yamato'], ['nara'], ['kyo'], ['otona'], ['yamato'], ['damashii'], ['nadeshiko']]
PUNCT = ['?', '.', '', '.', '.', '.', '', '.', ',']
MATANE = ('matane', 'またね！', 'matane!')
LEAD, TAIL, GAP = 0.16, 0.22, 0.16        # silence kept before / after a clip, and between clips in one slot


def load(name):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(A, name), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def env(x):
    h = SR // 100
    return 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')[::h]) + 1e-9)


def runs(mask):
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


def faded(y, ms=12):
    y = y.copy()
    n = min(int(SR * ms / 1000), len(y) // 2)
    if n > 0:
        y[:n] *= np.sin(np.linspace(0, np.pi / 2, n)) ** 2
        y[-n:] *= np.cos(np.linspace(0, np.pi / 2, n)) ** 2
    return y


def ja_clips(level):
    rms = lambda x: np.sqrt(np.mean(x[np.abs(x) > 0.01] ** 2))
    clips, lex = {}, {}
    for take, words in JA_TAKES:
        jw = load(take)
        segs = []
        for a, b in segments(jw):
            if segs and (b - a < 0.15 or a - segs[-1][1] < 0.12):
                segs[-1] = (segs[-1][0], b)
            else:
                segs.append((a, b))
        assert len(segs) == len(words), f'{take}: {len(segs)} segments for {len(words)} words'
        bounds = [0.0] + [(segs[k][1] + segs[k + 1][0]) / 2 for k in range(len(segs) - 1)] + [len(jw) / SR]
        for n, ((k, kana, rom), (a, b)) in enumerate(zip(words, segs)):
            y = jw[int(max(a - 0.03, bounds[n]) * SR):int(min(b + 0.08, bounds[n + 1]) * SR)]
            y = faded(y, 20)
            clips[k] = y * 0.95 * level / rms(y)
            lex[k] = (kana, rom)
    return clips, lex


def main():
    en = load(TAKE)
    e = env(en)
    level = np.sqrt(np.mean(en[np.abs(en) > 0.01] ** 2))
    raw = json.load(open(os.path.join(A, WORDS_JSON)))['words']
    raw = [w for w in raw if w.get('type', 'word') == 'word']
    # drop the style note at the top ("[warm, curious storytelling]") — every word of it, not just the bracketed ends
    keep, inside = [], False
    for w in raw:
        if w['text'].startswith('[') and not w['text'].strip('.,') == '[pause]':
            inside = True
        if not inside:
            keep.append(w)
        if inside and w['text'].endswith(']'):
            inside = False
    raw = keep
    clips, lex = ja_clips(level)
    # the slots: each "[pause]" token; find the real silence round it from the sound (Scribe times drift)
    pauses = [i for i, w in enumerate(raw) if w['text'].strip('.,') == '[pause]']
    assert len(pauses) == len(SLOTS), f'{len(pauses)} pauses in the take, {len(SLOTS)} slots'
    cuts = []                                   # (silence start, silence end) in the take, one per slot
    for i in pauses:
        prev = max(k for k in range(i) if not raw[k]['text'].startswith('['))
        lo = int((raw[prev]['end'] - 0.3) * 100)
        nxt = [k for k in range(i + 1, len(raw)) if not raw[k]['text'].startswith('[')]
        hi = int(((raw[nxt[0]]['start'] if nxt else len(en) / SR) + 0.5) * 100)
        floor = int(cuts[-1][1] * 100) if cuts else 0           # never reuse the pause of the slot before
        lo = max(lo, floor)
        sil = [r for r in runs(e[lo:hi] < -50) if r[1] - r[0] >= 15]
        assert sil, f'no pause found near "{raw[prev]["text"]}" — the pause may have been spoken over'
        # the pause right after the word before the slot (Scribe's end time), preferring real pauses (>= 0.2 s)
        end_prev = raw[prev]['end'] * 100 - lo
        r0, r1 = min(sil, key=lambda r: abs(r[0] - end_prev) + (50 if r[1] - r[0] < 20 else 0))
        cuts.append(((lo + r0) / 100, (lo + r1) / 100))
    # assemble: English up to just inside each silence, the clip(s), English again from just before the silence ends
    out, t, cursor, shifts, ja = [], 0.0, 0.0, [], {}
    seen, slot_keys = {}, []
    for keys in SLOTS:
        ks = []
        for k in keys:
            seen[k] = seen.get(k, 0) + 1
            ks.append(k if seen[k] == 1 else f'{k}{seen[k]}')
        slot_keys.append(ks)
    for (s0, s1), keys, ukeys in zip(cuts, SLOTS, slot_keys):
        a = min(s0 + LEAD, (s0 + s1) / 2)
        b = max(s1 - TAIL, (s0 + s1) / 2)
        seg = en[int(cursor * SR):int(a * SR)]
        out.append(faded(seg, 8) if cursor > 0 else seg)
        t += len(seg) / SR
        for n, (k, uk) in enumerate(zip(keys, ukeys)):
            if n:
                out.append(np.zeros(int(GAP * SR), np.float32))
                t += GAP
            ja[uk] = dict(text=lex[k][0], romaji=lex[k][1], start=round(t, 3), end=round(t + len(clips[k]) / SR, 3))
            out.append(clips[k])
            t += len(clips[k]) / SR
        shifts.append((a, b, t))
        cursor = b
    end = min(len(en) / SR, max(w['end'] for w in raw) + 0.2)
    out.append(faded(en[int(cursor * SR):int(end * SR)], 8))
    t += end - cursor
    mt = load('matane_a.mp3')
    ms = segments(mt, hold=40)
    mt = faded(mt[int(ms[0][0] * SR):int(ms[-1][1] * SR)])
    mt *= 0.95 * level / np.sqrt(np.mean(mt[np.abs(mt) > 0.01] ** 2))
    t_mt = t + 0.4
    out += [np.zeros(int(0.4 * SR), np.float32), mt, np.zeros(int(0.25 * SR), np.float32)]
    nar = np.concatenate(out)

    def sh(x):
        base_en, base_out = 0.0, 0.0
        for a, b, t_after in shifts:
            if x < a:
                break
            base_en, base_out = b, t_after
        return base_out + (x - base_en)

    ws, slot = [], 0
    for w in raw:
        if w['text'].strip('.,') == '[pause]':
            for k, uk in zip(SLOTS[slot], slot_keys[slot]):
                ws.append(dict(text=lex[k][1] + PUNCT[slot], type='word', ja=uk, start=ja[uk]['start'], end=ja[uk]['end']))
            slot += 1
            continue
        if w['text'].startswith('[') or w['text'].endswith(']'):
            continue
        ws.append(dict(text=w['text'], type='word', start=round(sh(w['start']), 3), end=round(sh(w['end']), 3)))
    t_end = round(t_mt + len(mt) / SR, 3)
    ws.append(dict(text=MATANE[2], type='word', ja=MATANE[0], start=round(t_mt, 3), end=t_end))
    ja[MATANE[0]] = dict(text=MATANE[1], romaji=MATANE[2], start=round(t_mt, 3), end=t_end)
    wavfile.write(os.path.join(A, 'narration.wav'), SR, (np.clip(nar, -1, 1) * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(A, 'narration.wav'), '-b:a', '192k',
                    os.path.join(A, 'narration.mp3')], check=True)
    json.dump({'words': ws, 'ja': ja}, open(os.path.join(A, 'words.json'), 'w'), ensure_ascii=False, indent=0)
    print(f'narration {len(nar) / SR:.2f}s')
    for (s0, s1), keys in zip(cuts, SLOTS):
        print(f'  slot {"/".join(keys):22s} pause in take {s0:6.2f}-{s1:6.2f} ({s1 - s0:.2f}s)')
    for k, v in sorted(ja.items(), key=lambda kv: kv[1]['start']):
        print(f'  {k:13s} {v["start"]:6.2f}-{v["end"]:6.2f}  {v["text"]}  {v["romaji"]}')


if __name__ == '__main__':
    main()
