#!/usr/bin/env python3
"""
Offline composer for THE UNCOUNTED's regional music and ambience loops (supersedes the short drone loops that
build_assets_audio.make_music_and_ambience() used to write).

Everything is synthesised with numpy: Karplus-Strong plucks (lute), breathy sine flutes, detuned soft pads,
FM bells, filtered noise beds and a convolution reverb. Each file is rendered with a reverb tail that is wrapped
back onto the start, so the loop point is seamless (no click, no audible restart).

Run:  python tools/build_music_ambience.py
"""

import math
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 32000


# =============================================================================
# Utilities
# =============================================================================
def note_hz(name):
    """'D4', 'F#3', 'Bb2' -> frequency."""
    names = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    n = names[name[0]]
    rest = name[1:]
    if rest.startswith("#"):
        n += 1
        rest = rest[1:]
    elif rest.startswith("b"):
        n -= 1
        rest = rest[1:]
    octave = int(rest)
    midi = 12 * (octave + 1) + n
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def env_adsr(n, a, d, s, r):
    a, d, r = int(a * SR), int(d * SR), int(r * SR)
    e = np.full(n, s, dtype=np.float64)
    a = min(a, n)
    e[:a] = np.linspace(0, 1, a, endpoint=False) if a else e[:a]
    d = min(d, n - a)
    if d > 0:
        e[a:a + d] = np.linspace(1, s, d, endpoint=False)
    r = min(r, n)
    if r > 0:
        e[n - r:] *= np.linspace(1, 0, r)
    return e


def one_pole_lowpass(x, cutoff):
    k = math.exp(-2.0 * math.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # small buffers only (notes); beds use FFT filtering
        acc = (1 - k) * x[i] + k * acc
        y[i] = acc
    return y


def fft_bandpass(x, lo, hi, soft=0.15):
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    gain = np.clip((f - lo * (1 - soft)) / max(lo * soft, 1e-6), 0, 1) * np.clip((hi * (1 + soft) - f) / max(hi * soft, 1e-6), 0, 1)
    return np.fft.irfft(spec * gain, len(x))


def reverb(x, seconds=2.4, mix=0.32, damp=4000.0, seed=7):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t * 6.9 / seconds)
    ir = fft_bandpass(ir, 120.0, damp)
    ir[: int(0.012 * SR)] = 0.0  # pre-delay
    ir /= np.sqrt((ir ** 2).sum()) + 1e-9
    size = 1 << int(math.ceil(math.log2(len(x) + n)))
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x) + n]
    out = np.zeros(len(x) + n)
    out[: len(x)] += x * (1 - mix)
    out += wet * mix * 3.0
    return out


def loopify(buf, length):
    """Wraps everything past `length` (reverb/note tails) back onto the start for a seamless loop."""
    out = buf[:length].copy()
    tail = buf[length:]
    while len(tail):
        k = min(len(tail), length)
        out[:k] += tail[:k]
        tail = tail[k:]
    return out


def loop_crossfade(buf, length, fade_s=1.0):
    """Seamless loop for continuous noise beds: the material just past the loop end fades into the start."""
    f = min(int(fade_s * SR), len(buf) - length)
    out = buf[:length].copy()
    w = np.linspace(0.0, 1.0, f)
    out[:f] = buf[:f] * w + buf[length:length + f] * (1.0 - w)
    return out


def write_wav(rel, x, peak=0.7):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    data = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data)
    print("Wrote %s (%.1fs)" % (rel, len(x) / SR))


def add(buf, start_s, sig, gain=1.0):
    i = int(start_s * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


# =============================================================================
# Instruments
# =============================================================================
def pluck(freq, dur, rng, bright=0.5):
    """Karplus-Strong string (lute / harp)."""
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, period)
    buf = one_pole_lowpass(buf, 2000 + bright * 5000)
    out = np.empty(n)
    decay = 0.996 - 0.0015 * (freq / 600.0)
    idx = 0
    for i in range(n):
        v = buf[idx]
        nxt = buf[(idx + 1) % period]
        buf[idx] = decay * 0.5 * (v + nxt)
        out[i] = v
        idx = (idx + 1) % period
    return out * env_adsr(n, 0.002, 0.0, 1.0, 0.08)


def flute(freq, dur, rng, breath=0.06):
    n = int(dur * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * math.pi * 5.2 * t) * np.clip(t / 0.35, 0, 1)
    phase = 2 * math.pi * np.cumsum(freq * vib) / SR
    tone = np.sin(phase) + 0.18 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    noise = fft_bandpass(rng.standard_normal(n), freq * 0.8, freq * 4.0) * breath
    return (tone + noise) * env_adsr(n, 0.09, 0.15, 0.8, 0.25)


def pad(freqs, dur, rng, cutoff=1400.0):
    """Soft detuned saw pad, low-passed; slow attack so chords swell rather than drone."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            ph = (t * f * (1 + det) + rng.random()) % 1.0
            sig += (2 * ph - 1)
    sig = fft_bandpass(sig, 90.0, cutoff, soft=0.5)
    sig /= len(freqs) * 3
    return sig * env_adsr(n, min(1.5, dur * 0.35), 0.5, 0.85, min(1.8, dur * 0.4))


def bell(freq, dur, rng, index=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    mod = np.sin(2 * math.pi * freq * 1.41 * t) * index * np.exp(-t * 3.0)
    car = np.sin(2 * math.pi * freq * t + mod)
    return car * np.exp(-t * 1.6) * env_adsr(n, 0.003, 0.0, 1.0, 0.3)


def chord_tones(root, quality):
    r = note_hz(root)
    if quality == "m":
        return [r, r * 2 ** (3 / 12), r * 2 ** (7 / 12)]
    return [r, r * 2 ** (4 / 12), r * 2 ** (7 / 12)]


# =============================================================================
# Music
# =============================================================================
def compose_bellwether():
    """Rain-soaked village: melancholic D dorian folk, plucked lute arpeggios + flute in the second half."""
    rng = np.random.default_rng(11)
    bpm = 76
    beat = 60.0 / bpm
    prog = [("D3", "m"), ("C3", ""), ("Bb2", ""), ("C3", ""), ("D3", "m"), ("F3", ""), ("C3", ""), ("A2", "m")]
    bars_per_chord = 2
    cycles = 2
    length_s = len(prog) * bars_per_chord * 4 * beat * cycles
    buf = np.zeros(int((length_s + 4) * SR))
    scale = [note_hz(n) for n in ("D4", "E4", "F4", "G4", "A4", "B4", "C5", "D5", "E5", "F5")]
    pattern = [0, 2, 1, 2, 0, 2, 1, 2]
    t = 0.0
    for cyc in range(cycles):
        for ci, (root, q) in enumerate(prog):
            tones = chord_tones(root, q)
            dur = bars_per_chord * 4 * beat
            add(buf, t, pad([f * 2 for f in tones], dur + 1.2, rng, cutoff=1100), 0.22)
            for b in range(bars_per_chord * 8):
                if rng.random() < 0.08:
                    continue
                f = tones[pattern[b % 8]] * (2 if b % 8 in (2, 6) else 1)
                add(buf, t + b * beat / 2 + rng.uniform(0, 0.012), pluck(f, 2.2, rng, bright=0.35), 0.5 if b % 4 == 0 else 0.36)
            if cyc == 1:
                # Flute melody: chord-tone anchored random walk with breathing room
                deg = scale.index(min(scale, key=lambda s: abs(s - tones[0] * 4)))
                bt = 0.0
                while bt < bars_per_chord * 4:
                    step = rng.choice([-2, -1, -1, 1, 1, 2, 0])
                    deg = int(np.clip(deg + step, 0, len(scale) - 1))
                    ln = rng.choice([1.0, 1.5, 2.0, 0.5])
                    if rng.random() < 0.22:
                        bt += ln
                        continue
                    add(buf, t + bt * beat, flute(scale[deg], ln * beat * 1.1, rng), 0.26)
                    bt += ln
            t += dur
    out = loopify(reverb(buf, 2.8, 0.34), int(length_s * SR))
    write_wav("assets/audio/music/bellwether_theme.wav", out)


def compose_old_road():
    """Lonely road through a forgotten borough: sparse A minor pads, distant flute phrases, occasional harp."""
    rng = np.random.default_rng(23)
    bpm = 64
    beat = 60.0 / bpm
    prog = [("A2", "m"), ("G2", ""), ("F2", ""), ("E2", "m"), ("A2", "m"), ("C3", ""), ("G2", ""), ("E2", "m")]
    length_s = len(prog) * 8 * beat
    buf = np.zeros(int((length_s + 5) * SR))
    penta = [note_hz(n) for n in ("A4", "C5", "D5", "E5", "G5", "A5")]
    t = 0.0
    for ci, (root, q) in enumerate(prog):
        tones = chord_tones(root, q)
        dur = 8 * beat
        add(buf, t, pad([f * 2 for f in tones] + [tones[0]], dur + 2.0, rng, cutoff=900), 0.28)
        for k in range(3):
            if rng.random() < 0.7:
                f = tones[rng.integers(0, 3)] * 4
                add(buf, t + rng.uniform(0, dur - 1), pluck(f, 3.0, rng, bright=0.6), 0.22)
        if ci % 2 == 0:
            bt = rng.uniform(0.5, 2.0)
            deg = rng.integers(1, 4)
            for _ in range(rng.integers(3, 6)):
                ln = rng.choice([1.0, 1.5, 2.0])
                add(buf, t + bt * beat, flute(penta[deg], ln * beat * 1.15, rng, breath=0.09), 0.3)
                deg = int(np.clip(deg + rng.choice([-1, 1, -2, 1]), 0, len(penta) - 1))
                bt += ln + rng.choice([0, 0, 0.5])
        t += dur
    out = loopify(reverb(buf, 3.4, 0.4), int(length_s * SR))
    write_wav("assets/audio/music/old_road_theme.wav", out)


def compose_crypt():
    """The Annex beneath the road: no drone - sparse cold bells, breathing low pads and distant thuds in silence."""
    rng = np.random.default_rng(37)
    length_s = 96.0
    buf = np.zeros(int((length_s + 6) * SR))
    scale = [note_hz(n) for n in ("C#4", "D#4", "E4", "G#4", "A4", "C#5", "E5")]
    roots = [("C#3", "m"), ("A2", ""), ("F#2", "m"), ("G#2", "")]
    t = 0.0
    seg = length_s / len(roots)
    for root, q in roots:
        tones = chord_tones(root, q)
        add(buf, t + 0.5, pad([f * 2 for f in tones], seg * 0.8, rng, cutoff=700), 0.3)
        t += seg
    t = 1.0
    while t < length_s - 2:
        add(buf, t, bell(scale[rng.integers(0, len(scale))], 4.0, rng), 0.16 if rng.random() < 0.7 else 0.24)
        if rng.random() < 0.3:
            add(buf, t + 0.4, bell(scale[rng.integers(0, len(scale))] * 0.5, 4.0, rng, index=1.4), 0.12)
        t += rng.uniform(2.2, 5.5)
    for _ in range(6):  # distant stone settling
        n = int(1.2 * SR)
        thud = fft_bandpass(rng.standard_normal(n), 40, 180) * np.exp(-np.arange(n) / SR * 5)
        add(buf, rng.uniform(4, length_s - 4), thud, 0.5)
    out = loopify(reverb(buf, 4.5, 0.5, damp=2500), int(length_s * SR))
    write_wav("assets/audio/music/crypt_theme.wav", out, peak=0.6)


def music_box(freq, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * math.pi * freq * t) + 0.35 * np.sin(2 * math.pi * freq * 3.01 * t) * np.exp(-t * 6)         + 0.12 * np.sin(2 * math.pi * freq * 5.2 * t) * np.exp(-t * 12)
    return tone * np.exp(-t * 2.4) * env_adsr(n, 0.002, 0.0, 1.0, 0.2)


def compose_vault_lullaby():
    """Vault III: a slow A-minor waltz on a music box, the song the Warden sings the hidden children."""
    rng = np.random.default_rng(41)
    beat = 60.0 / 66
    bar = 3 * beat
    melody = [  # (note, beats) - four 4-bar phrases
        ("E5", 2), ("D5", 1), ("C5", 2), ("B4", 1), ("A4", 2), ("B4", 1), ("C5", 3),
        ("D5", 2), ("C5", 1), ("B4", 2), ("A4", 1), ("G#4", 2), ("A4", 1), ("B4", 3),
        ("E5", 2), ("D5", 1), ("C5", 2), ("B4", 1), ("A4", 2), ("C5", 1), ("E5", 3),
        ("F5", 2), ("E5", 1), ("D5", 2), ("B4", 1), ("A4", 3), (None, 3),
    ]
    chords = [("A2", "m"), ("A2", "m"), ("F2", ""), ("C3", ""), ("D2", "m"), ("E2", ""), ("E2", ""), ("E2", ""),
              ("A2", "m"), ("A2", "m"), ("F2", ""), ("C3", ""), ("D2", "m"), ("E2", ""), ("A2", "m"), ("A2", "m")]
    passes = 3
    length_s = len(chords) * bar * passes
    buf = np.zeros(int((length_s + 6) * SR))
    for p in range(passes):
        t0 = p * len(chords) * bar
        for i, (root, q) in enumerate(chords):
            tones = chord_tones(root, q)
            bt = t0 + i * bar
            add(buf, bt, pad([f * 2 for f in tones], bar + 1.0, rng, cutoff=800), 0.12)
            add(buf, bt, pluck(tones[0], 2.6, rng, bright=0.2), 0.3)
            for k, f in ((1, tones[1] * 2), (2, tones[2] * 2)):
                add(buf, bt + k * beat, pluck(f, 1.6, rng, bright=0.25), 0.13)
        t = t0
        for note, beats in melody:
            if note:
                f = note_hz(note) * (0.5 if p == 1 else 1.0)  # second verse an octave lower, like a hummed reprise
                add(buf, t + rng.uniform(0, 0.01), music_box(f, beats * beat + 1.5, rng), 0.42 if p != 1 else 0.36)
                if p == 2 and beats >= 2:
                    add(buf, t + beat, music_box(f * 2, 1.2, rng), 0.1)  # faint echo an octave up
            t += beats * beat
    out = loopify(reverb(buf, 3.6, 0.45, damp=3200), int(length_s * SR))
    write_wav("assets/audio/music/vault_lullaby.wav", out, peak=0.6)


# =============================================================================
# Ambience
# =============================================================================
def ambience_rain():
    rng = np.random.default_rng(5)
    length = 30.0
    n = int(length * SR)
    bed = fft_bandpass(rng.standard_normal(n + SR), 900, 7000) * 0.35
    bed += fft_bandpass(rng.standard_normal(n + SR), 200, 900) * 0.12
    gust = 0.8 + 0.2 * np.sin(np.arange(n + SR) / SR * 2 * math.pi / 15.0)
    buf = bed * gust
    for _ in range(int(length * 22)):  # nearby drops on stone and leaves
        m = int(0.03 * SR)
        f = rng.uniform(1800, 4200)
        drop = np.sin(2 * math.pi * f * np.arange(m) / SR) * np.exp(-np.arange(m) / SR * 160)
        add(buf, rng.uniform(0, length), drop, rng.uniform(0.05, 0.22))
    for _ in range(int(length / 2.5)):  # eaves dripping into puddles
        m = int(0.12 * SR)
        f0 = rng.uniform(500, 900)
        tt = np.arange(m) / SR
        plink = np.sin(2 * math.pi * f0 * (1 + 2.5 * tt) * tt) * np.exp(-tt * 30)
        add(buf, rng.uniform(0, length), plink, rng.uniform(0.15, 0.3))
    write_wav("assets/audio/ambience/village_rain.wav", loop_crossfade(buf, n), peak=0.5)


def ambience_forest():
    rng = np.random.default_rng(9)
    length = 30.0
    n = int(length * SR)
    tt = np.arange(n + SR) / SR
    gusts = 0.45 + 0.35 * np.sin(2 * math.pi * tt / 11.0) + 0.2 * np.sin(2 * math.pi * tt / 4.3 + 1.0)
    buf = fft_bandpass(rng.standard_normal(n + SR), 250, 2400, soft=0.6) * 0.3 * gusts
    leaves = fft_bandpass(rng.standard_normal(n + SR), 3000, 9000) * 0.05 * np.clip(gusts - 0.4, 0, 1)
    buf += leaves
    for _ in range(9):  # birds
        start = rng.uniform(0, length - 1)
        for k in range(rng.integers(2, 5)):
            m = int(0.09 * SR)
            t2 = np.arange(m) / SR
            f = rng.uniform(2600, 3800)
            chirp = np.sin(2 * math.pi * (f + 1800 * t2 / 0.09) * t2) * np.sin(math.pi * t2 / 0.09)
            add(buf, start + k * 0.13, chirp, 0.08)
    for _ in range(3):  # creaking trunk
        m = int(0.8 * SR)
        t2 = np.arange(m) / SR
        creak = np.sign(np.sin(2 * math.pi * (70 + 20 * t2) * t2)) * np.sin(math.pi * t2 / 0.8)
        add(buf, rng.uniform(0, length - 1), fft_bandpass(creak, 200, 1500), 0.04)
    write_wav("assets/audio/ambience/forest_wind.wav", loop_crossfade(buf, n), peak=0.45)


def ambience_crypt():
    rng = np.random.default_rng(13)
    length = 30.0
    n = int(length * SR)
    buf = fft_bandpass(rng.standard_normal(n + SR), 180, 600) * 0.04  # faint air in stone, not a hum
    for _ in range(int(length / 1.6)):
        m = int(0.25 * SR)
        t2 = np.arange(m) / SR
        f0 = rng.uniform(900, 1600)
        drip = np.sin(2 * math.pi * f0 * (1 - 0.6 * t2) * t2) * np.exp(-t2 * 24)
        add(buf, rng.uniform(0, length), drip, rng.uniform(0.1, 0.35))
    for _ in range(2):  # distant chain
        start = rng.uniform(2, length - 3)
        for k in range(6):
            m = int(0.05 * SR)
            ring = fft_bandpass(rng.standard_normal(m), 1500, 5000) * np.exp(-np.arange(m) / SR * 60)
            add(buf, start + k * rng.uniform(0.06, 0.14), ring, 0.06)
    out = loop_crossfade(reverb(buf, 3.0, 0.55, damp=3000), n)
    write_wav("assets/audio/ambience/crypt_drips.wav", out, peak=0.45)


if __name__ == "__main__":
    compose_bellwether()
    compose_old_road()
    compose_crypt()
    compose_vault_lullaby()
    ambience_rain()
    ambience_forest()
    ambience_crypt()
