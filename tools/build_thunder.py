#!/usr/bin/env python3
"""Writes assets/audio/sfx/thunder_far.wav and thunder_near.wav: rolling thunder for the title screen's lightning.
Low-passed noise with a crack at the start and a few rumbling swells. Run: python3 tools/build_thunder.py"""
import math
import os
import random
import struct
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 22050


def write(rel, samples):
    with wave.open(os.path.join(ROOT, rel), "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
        peak = max(abs(x) for x in samples) or 1.0
        wf.writeframes(b"".join(struct.pack("<h", int(x / peak * 0.9 * 32000)) for x in samples))


def thunder(seed, length, crack, swells):
    rng = random.Random(seed)
    n = int(SR * length)
    lp1 = lp2 = lp3 = 0.0
    hp_prev = 0.0
    out = []
    for i in range(n):
        t = i / SR
        w = rng.uniform(-1, 1)
        lp1 += (w - lp1) * 0.08    # rumble: heavily low-passed noise
        lp2 += (lp1 - lp2) * 0.08
        lp3 += (lp2 - lp3) * 0.15
        rumble = lp3 * 9.0
        env = 0.0
        for (c, width, amp) in swells:  # rolling swells
            env += amp * math.exp(-((t - c) / width) ** 2)
        env *= min(1.0, t / 0.05) * max(0.0, 1.0 - t / length) ** 0.6
        s = rumble * env
        if crack > 0:  # the sharp crack of a near strike
            bright = w - hp_prev
            hp_prev = w
            s += bright * crack * math.exp(-t * 9.0) * min(1.0, t / 0.004)
        out.append(s)
    return out


write("assets/audio/sfx/thunder_far.wav", thunder(7, 5.0, 0.0, [(0.5, 0.45, 0.8), (1.4, 0.6, 1.0), (2.6, 0.9, 0.6), (3.6, 0.7, 0.3)]))
write("assets/audio/sfx/thunder_near.wav", thunder(11, 5.5, 0.35, [(0.15, 0.25, 1.0), (0.9, 0.5, 0.9), (2.0, 0.8, 0.7), (3.4, 1.0, 0.35)]))
print("ok")
