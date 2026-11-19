"""full QA of a finished reel: freezes, dead air in the voice, clicks / abrupt cuts, loudness, true peak, voice vs music"""
import json, os, re, subprocess, sys
import numpy as np
R, mp4 = sys.argv[1], sys.argv[2]
out = {}
# 1. frozen video (>1.5 s without change), ignoring the last 3.5 s hold for the handle
r = subprocess.run(['ffmpeg', '-i', mp4, '-vf', 'freezedetect=n=0.0008:d=1.5', '-map', '0:v', '-f', 'null', '-'], capture_output=True, text=True).stderr
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout)
fz = [(float(a), float(b)) for a, b in zip(re.findall(r'freeze_start: ([\d.]+)', r), re.findall(r'freeze_end: ([\d.]+)', r) + [str(dur)])]
out['freezes'] = [(round(a, 1), round(b, 1)) for a, b in fz if a < dur - 3.6]
# 2. dead air: silences in the voice longer than 0.9 s (after the first word, before the last)
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '48000', '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
v = load(os.path.join(R, 'audio', 'narration.wav')); h = 480
e = 20 * np.log10(np.sqrt(np.convolve(v ** 2, np.ones(h) / h, 'same')[::h]) + 1e-9)
on = np.where(e > -40)[0]
gaps, k = [], on[0]
for a, b in zip(on[:-1], on[1:]):
    if (b - a) / 100 > 0.9:
        gaps.append((round(a / 100 + 0.4, 2), round((b - a) / 100, 2)))
out['voice_gaps_over_0.9s'] = gaps
out['voice_abrupt_cuts'] = [i / 100 for i in range(1, len(e)) if e[i - 1] > -30 and e[i] < -55 and not any(
    abs(i / 100 - g[0] + 0.4) < 0.05 for g in gaps)]
# 2b. sudden voice peaks: any 400 ms stretch more than 6 dB louder than Raj's normal speaking level
w4 = 20 * np.log10(np.sqrt(np.convolve(v ** 2, np.ones(19200) / 19200, 'same')[::h]) + 1e-9)
m0 = np.median(w4[w4 > -30]); sp = w4[w4 > m0 - 10]; mid = np.median(sp)
peaks = []
for i in np.where(w4 - mid > 6)[0]:
    if not peaks or i / 100 + 0.4 - peaks[-1] > 1:
        peaks.append(round(i / 100 + 0.4, 2))
out['voice_sudden_peaks'] = peaks
out['voice_loudest_over_normal_dB'] = round(float(sp.max() - mid), 1)
# 3. clicks in the final mix
x = load(mp4); env = np.sqrt(np.convolve(x ** 2, np.ones(h) / h, 'same')); d = np.abs(np.diff(x))
out['clicks'] = int((d > np.maximum(0.2, 8 * env[1:] + 0.02)).sum())
# 4. loudness and true peak
r = subprocess.run(['ffmpeg', '-i', mp4, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
summ = r[r.rfind('Summary:'):]; out['LUFS'] = float(re.search(r'I:\s+(-?[\d.]+) LUFS', summ).group(1)); out['true_peak_dBFS'] = float(re.search(r'Peak:\s+(-?[\d.]+) dBFS', summ).group(1))
# 5. voice vs music while Raj speaks
st = os.path.join(R, 'audio', 'stems')
if os.path.exists(os.path.join(st, 'music.wav')):
    m = load(os.path.join(st, 'music.wav')); vv = load(os.path.join(st, 'voice.wav')); n = min(len(m), len(vv))
    ev = np.sqrt(np.convolve(vv[:n] ** 2, np.ones(h) / h, 'same')[::h]); em = np.sqrt(np.convolve(m[:n] ** 2, np.ones(h) / h, 'same')[::h])
    speak = ev > ev.max() * 0.05
    out['voice_over_music_dB'] = round(float(20 * np.log10(np.median(ev[speak]) / (np.median(em[speak]) + 1e-9))), 1)
    gapm = (~speak) & (np.arange(len(em)) > 100)
    out['music_never_drops_out'] = bool(np.percentile(em[gapm][:-350], 2) > 1e-4) if gapm.sum() > 400 else True
out['duration'] = round(dur, 2)
print(json.dumps(out, ensure_ascii=False))
