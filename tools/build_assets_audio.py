#!/usr/bin/env python3
"""
Offline External Audio (.wav) Builder for THE UNCOUNTED.
Writes standalone, replaceable 16-bit PCM WAV files into assets/audio/.
The C++ runtime loads these files externally via data definitions.
"""

import math
import os
import random
import struct
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_RATE = 22050


def write_wav(rel_path, samples):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with wave.open(full_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        buf = bytearray()
        for s in samples:
            v = max(-32000, min(32000, int(s * 32000.0)))
            buf.extend(struct.pack("<h", v))
        wf.writeframes(bytes(buf))


def make_sfx():
    rng = random.Random(42)

    # 1. sword_swing.wav - Whoosh
    n = int(SAMPLE_RATE * 0.24)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / n)
        freq = 320.0 - 180.0 * (i / n)
        noise = rng.uniform(-1, 1) * 0.35
        tone = math.sin(2 * math.pi * freq * t) * 0.25
        s.append((noise + tone) * env * 0.7)
    write_wav("assets/audio/sfx/sword_swing.wav", s)

    # 2. sword_hit.wav - Meaty metallic crunch
    n = int(SAMPLE_RATE * 0.22)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 18.0)
        clang = math.sin(2 * math.pi * 145 * t) * 0.5 + math.sin(2 * math.pi * 510 * t) * 0.3
        noise = rng.uniform(-1, 1) * 0.4
        s.append((clang + noise) * env * 0.85)
    write_wav("assets/audio/sfx/sword_hit.wav", s)

    # 3. shield_block.wav - Heavy iron clang
    n = int(SAMPLE_RATE * 0.30)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 12.0)
        ring = (math.sin(2 * math.pi * 420 * t) + 0.6 * math.sin(2 * math.pi * 685 * t) +
                0.4 * math.sin(2 * math.pi * 1120 * t)) * 0.4
        s.append(ring * env)
    write_wav("assets/audio/sfx/shield_block.wav", s)

    # 4. bow_release.wav - Twang
    n = int(SAMPLE_RATE * 0.26)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 14.0)
        freq = 165.0 + 35.0 * math.sin(2 * math.pi * 28.0 * t)
        s.append(math.sin(2 * math.pi * freq * t) * env * 0.7)
    write_wav("assets/audio/sfx/bow_release.wav", s)

    # 5. spell_cast.wav - Arcane shimmer
    n = int(SAMPLE_RATE * 0.42)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / n)
        f1 = 380.0 + 260.0 * (i / n)
        f2 = 570.0 + 390.0 * (i / n)
        val = (math.sin(2 * math.pi * f1 * t) + 0.6 * math.sin(2 * math.pi * f2 * t)) * 0.35
        s.append(val * env)
    write_wav("assets/audio/sfx/spell_cast.wav", s)

    # 6. spell_heal.wav - Warm chime chord
    n = int(SAMPLE_RATE * 0.55)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 4.5)
        chord = (math.sin(2 * math.pi * 523.25 * t) +
                 math.sin(2 * math.pi * 659.25 * t) +
                 math.sin(2 * math.pi * 783.99 * t)) * 0.25
        s.append(chord * env)
    write_wav("assets/audio/sfx/spell_heal.wav", s)

    # 7. skeleton_alert.wav - Dry bone rattle
    n = int(SAMPLE_RATE * 0.35)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        pulse = 1.0 if (i // 750) % 2 == 0 else 0.15
        env = math.exp(-t * 5.0) * pulse
        val = math.sin(2 * math.pi * 310 * t) * 0.4 + rng.uniform(-1, 1) * 0.35
        s.append(val * env)
    write_wav("assets/audio/sfx/skeleton_alert.wav", s)

    # 8. rat_squeak.wav
    n = int(SAMPLE_RATE * 0.22)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / n)
        f = 950.0 + 350.0 * math.sin(math.pi * i / n)
        s.append(math.sin(2 * math.pi * f * t) * env * 0.5)
    write_wav("assets/audio/sfx/rat_squeak.wav", s)

    # 9. crawler_hiss.wav
    n = int(SAMPLE_RATE * 0.32)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / n)
        s.append((rng.uniform(-1, 1) * 0.45 + math.sin(2 * math.pi * 220 * t) * 0.2) * env)
    write_wav("assets/audio/sfx/crawler_hiss.wav", s)

    # 10. sentinel_clang.wav
    n = int(SAMPLE_RATE * 0.42)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 7.0)
        s.append((math.sin(2 * math.pi * 180 * t) + 0.5 * math.sin(2 * math.pi * 365 * t)) * 0.4 * env)
    write_wav("assets/audio/sfx/sentinel_clang.wav", s)

    # 11. boss_roar.wav
    n = int(SAMPLE_RATE * 0.65)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / n)
        s.append((math.sin(2 * math.pi * 95 * t) * 0.5 + math.sin(2 * math.pi * 142 * t) * 0.3 + rng.uniform(-0.2, 0.2)) * env)
    write_wav("assets/audio/sfx/boss_roar.wav", s)

    # 12. enemy_death.wav
    n = int(SAMPLE_RATE * 0.40)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 6.5)
        f = 240.0 - 150.0 * (i / n)
        s.append((math.sin(2 * math.pi * f * t) * 0.45 + rng.uniform(-0.25, 0.25)) * env)
    write_wav("assets/audio/sfx/enemy_death.wav", s)

    # 13. player_hurt.wav
    n = int(SAMPLE_RATE * 0.22)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 11.0)
        s.append((math.sin(2 * math.pi * 135 * t) * 0.55 + rng.uniform(-0.2, 0.2)) * env)
    write_wav("assets/audio/sfx/player_hurt.wav", s)

    # 14. door_open.wav - Heavy oak creak & latch
    n = int(SAMPLE_RATE * 0.45)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.sin(math.pi * i / n)
        f = 115.0 + 25.0 * math.sin(2 * math.pi * 6.0 * t)
        s.append(math.sin(2 * math.pi * f * t) * env * 0.5)
    write_wav("assets/audio/sfx/door_open.wav", s)

    # 15. door_locked.wav - Metallic rattle
    n = int(SAMPLE_RATE * 0.20)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 14.0)
        s.append(math.sin(2 * math.pi * 340 * t) * env * 0.5)
    write_wav("assets/audio/sfx/door_locked.wav", s)

    # 16. chest_open.wav
    n = int(SAMPLE_RATE * 0.35)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 7.0)
        f = 290.0 if i < n // 2 else 435.0
        s.append(math.sin(2 * math.pi * f * t) * env * 0.45)
    write_wav("assets/audio/sfx/chest_open.wav", s)

    # 17. lever_pull.wav
    n = int(SAMPLE_RATE * 0.30)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 9.0)
        s.append((math.sin(2 * math.pi * 195 * t) + 0.4 * rng.uniform(-1, 1)) * env * 0.45)
    write_wav("assets/audio/sfx/lever_pull.wav", s)

    # 18. item_pickup.wav
    n = int(SAMPLE_RATE * 0.18)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 14.0)
        f = 587.33 if i < n // 2 else 880.0
        s.append(math.sin(2 * math.pi * f * t) * env * 0.4)
    write_wav("assets/audio/sfx/item_pickup.wav", s)

    # 19. coin_jingle.wav
    n = int(SAMPLE_RATE * 0.28)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 10.0)
        f = 1318.5 if i < n // 3 else (1567.98 if i < (2 * n) // 3 else 2093.0)
        s.append(math.sin(2 * math.pi * f * t) * env * 0.35)
    write_wav("assets/audio/sfx/coin_jingle.wav", s)

    # 20. page_turn.wav
    n = int(SAMPLE_RATE * 0.18)
    s = []
    for i in range(n):
        env = math.sin(math.pi * i / n)
        s.append(rng.uniform(-1, 1) * env * 0.25)
    write_wav("assets/audio/sfx/page_turn.wav", s)

    # 21. level_up.wav
    n = int(SAMPLE_RATE * 0.65)
    notes = [293.66, 369.99, 440.0, 587.33]
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        idx = min(3, (i * 4) // n)
        f = notes[idx]
        env = math.exp(-((i % (n // 4)) / SAMPLE_RATE) * 6.0)
        s.append((math.sin(2 * math.pi * f * t) + 0.4 * math.sin(4 * math.pi * f * t)) * env * 0.35)
    write_wav("assets/audio/sfx/level_up.wav", s)

    # 22. footstep_stone.wav
    n = int(SAMPLE_RATE * 0.09)
    s = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = math.exp(-t * 32.0)
        s.append((math.sin(2 * math.pi * 110 * t) * 0.4 + rng.uniform(-0.3, 0.3)) * env * 0.45)
    write_wav("assets/audio/sfx/footstep_stone.wav", s)


def make_music_and_ambience():
    rng = random.Random(99)

    # Helper to render a looping melancholic medieval lute/harp & pad track
    def render_track(rel_path, notes_hz, drone_hz, duration_sec=8.0):
        total = int(SAMPLE_RATE * duration_sec)
        s = [0.0] * total
        step_samples = total // len(notes_hz)
        for i in range(total):
            t = i / SAMPLE_RATE
            # Smooth loop crossfade at edges
            note_idx = min(len(notes_hz) - 1, i // step_samples)
            local_t = (i % step_samples) / SAMPLE_RATE
            f_mel = notes_hz[note_idx]
            pluck_env = math.exp(-local_t * 3.2)
            mel = (math.sin(2 * math.pi * f_mel * t) + 0.35 * math.sin(4 * math.pi * f_mel * t)) * pluck_env * 0.14
            drone = (math.sin(2 * math.pi * drone_hz * t) + 0.5 * math.sin(2 * math.pi * (drone_hz * 1.5) * t)) * 0.09
            s[i] = mel + drone
        write_wav(rel_path, s)

    # 1. bellwether_theme.wav (D Dorian atmospheric village lute)
    render_track(
        "assets/audio/music/bellwether_theme.wav",
        [293.66, 329.63, 349.23, 440.00, 392.00, 349.23, 329.63, 293.66],
        146.83,
        8.0
    )

    # 2. old_road_theme.wav (A Aeolian woodland exploration)
    render_track(
        "assets/audio/music/old_road_theme.wav",
        [220.00, 261.63, 293.66, 329.63, 293.66, 261.63, 246.94, 220.00],
        110.00,
        8.0
    )

    # 3. crypt_theme.wav (C Phrygian dark dungeon resonance)
    render_track(
        "assets/audio/music/crypt_theme.wav",
        [130.81, 138.59, 164.81, 196.00, 164.81, 138.59, 130.81, 98.00],
        65.41,
        8.0
    )

    # Ambience loops (4 seconds seamless)
    amb_len = int(SAMPLE_RATE * 4.0)

    # village_rain.wav
    rain = []
    prev = 0.0
    for i in range(amb_len):
        raw = rng.uniform(-1, 1)
        prev = prev * 0.82 + raw * 0.18
        rain.append(prev * 0.12)
    write_wav("assets/audio/ambience/village_rain.wav", rain)

    # forest_wind.wav
    wind = []
    prev = 0.0
    for i in range(amb_len):
        t = i / SAMPLE_RATE
        swell = 0.55 + 0.45 * math.sin(2 * math.pi * 0.25 * t)
        raw = rng.uniform(-1, 1)
        prev = prev * 0.92 + raw * 0.08
        wind.append(prev * swell * 0.16)
    write_wav("assets/audio/ambience/forest_wind.wav", wind)

    # crypt_drips.wav
    crypt = []
    prev = 0.0
    for i in range(amb_len):
        t = i / SAMPLE_RATE
        raw = rng.uniform(-1, 1)
        prev = prev * 0.95 + raw * 0.05
        drip = 0.0
        if 1.0 <= t < 1.12:
            dt = t - 1.0
            drip = math.sin(2 * math.pi * (680 + dt * 1200) * dt) * math.exp(-dt * 28.0) * 0.25
        elif 2.7 <= t < 2.82:
            dt = t - 2.7
            drip = math.sin(2 * math.pi * (540 + dt * 1100) * dt) * math.exp(-dt * 28.0) * 0.22
        crypt.append(prev * 0.10 + drip)
    write_wav("assets/audio/ambience/crypt_drips.wav", crypt)


if __name__ == "__main__":
    make_sfx()
    # Music & ambience are composed by tools/build_music_ambience.py (long, drone-free, seamless loops);
    # make_music_and_ambience() is kept only for reference and no longer run.
    print("External WAV SFX generated. Run tools/build_music_ambience.py for music and ambience.")
