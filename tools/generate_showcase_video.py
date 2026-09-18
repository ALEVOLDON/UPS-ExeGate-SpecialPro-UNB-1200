"""
Automated Showcase Video Generator for ExeGate SpecialPro UPS Monitor.
Produces a 1080p 30fps MP4 video presentation with:
- Professional English voiceover (Microsoft Neural TTS)
- Synchronized Russian subtitles (ASS / libass)
- Ken Burns pan & zoom camera effects
- Cyberpunk / Dark UI styling matching the dashboard
- Synthesized ambient electronic background soundtrack with voice ducking
- Fast-loading GIF teaser for GitHub README
"""

import os
import sys
import json
import time
import asyncio
import subprocess
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    import edge_tts
except ImportError:
    print("edge-tts not installed. Run: pip install edge-tts")
    sys.exit(1)

OUTPUT_DIR = "assets"
SCRATCH_DIR = "scratch_video"
AUDIO_DIR = "scratch_audio"
FPS = 30
WIDTH = 1920
HEIGHT = 1080

SCENES_DEF = [
    {
        "id": "s1",
        "audio": "s1.mp3",
        "speech": "Meet ExeGate SpecialPro UPS Monitor — a modern, open-source dashboard designed for real-time power telemetry and intelligent system protection.",
        "subtitle": "Встречайте ExeGate SpecialPro UPS Monitor — современный открытый дашборд\\Nдля телеметрии электросети и надежной защиты системы.",
        "badge_tag": "OVERVIEW // OPEN SOURCE",
        "badge_title": "ExeGate SpecialPro Power Dashboard",
        "badge_sub": "Modern Telemetry & Smart Protection",
        "type": "intro_dashboard",
    },
    {
        "id": "s2",
        "audio": "s2.mp3",
        "speech": "Experience instant monitoring over WebSockets. Segmented dial gauges display incoming AC voltage, automatic voltage regulation, load wattage, and battery health.",
        "subtitle": "Мгновенный мониторинг через WebSockets: неоновые круговые шкалы\\Nотображают напряжение сети, работу AVR, нагрузку и состояние АКБ.",
        "badge_tag": "FEATURE 01 // TELEMETRY",
        "badge_title": "Real-Time Neon Dial Gauges",
        "badge_sub": "20-Segment Radial Gauges & Live Data",
        "type": "gauges",
        "img": "assets/dashboard_preview_en.jpg",
    },
    {
        "id": "s3",
        "audio": "s3.mp3",
        "speech": "Our built-in Grace Period protection eliminates false sensor drops to zero during USB HID polling delays, keeping your metrics perfectly stable.",
        "subtitle": "Умный буфер Grace Period исключает ложные сбросы показаний в ноль\\Nпри микрозадержках опроса USB HID, сохраняя стабильность графиков.",
        "badge_tag": "FEATURE 02 // RELIABILITY",
        "badge_title": "4s Grace Period Telemetry Buffer",
        "badge_sub": "Zero-Drop Protection for USB HID",
        "type": "grace_period",
        "img": "assets/dashboard_preview_en.jpg",
    },
    {
        "id": "s4",
        "audio": "s4.mp3",
        "speech": "Manage your connected devices with an interactive four-socket map, and watch animated power flows showing live energy routing from grid to battery.",
        "subtitle": "Управляйте подключенными приборами через карту 4 розеток 220V\\Nи наблюдайте за анимированными потоками энергии в реальном времени.",
        "badge_tag": "FEATURE 03 // POWER ROUTING",
        "badge_title": "Interactive 4-Socket 220V Map",
        "badge_sub": "Schuko Outlets & Animated Energy Flows",
        "type": "sockets",
        "img": "assets/dashboard_sidebar.jpg",
    },
    {
        "id": "s5",
        "audio": "s5.mp3",
        "speech": "Track cumulative kilowatt-hours and calculate your electricity costs with customizable currency tariffs, daily rates, and monthly expense forecasts.",
        "subtitle": "Ведите учет израсходованных кВт⋅ч и рассчитывайте расходы\\Nна электроэнергию по вашему тарифу с прогнозом затрат на месяц.",
        "badge_tag": "FEATURE 04 // EFFICIENCY",
        "badge_title": "Energy & Cost Calculator (kWh)",
        "badge_sub": "Real-time Metering & Monthly Forecasts",
        "type": "calculator",
        "img": "assets/dashboard_preview_en.jpg",
    },
    {
        "id": "s6",
        "audio": "s6.mp3",
        "speech": "Access deep analytics: grid stability scoring, voltage histograms, AVR event statistics, and full incident logs with one-click CSV export.",
        "subtitle": "Глубокая аналитика: индекс стабильности сети, гистограммы напряжений,\\Nстатистика AVR и экспорт журнала событий в CSV в 1 клик.",
        "badge_tag": "FEATURE 05 // ANALYTICS",
        "badge_title": "Incident History & KPI Dashboard",
        "badge_sub": "Chart.js Visualizations & CSV Export",
        "type": "modal",
        "img": "assets/modal_preview_en.jpg",
    },
    {
        "id": "s7",
        "audio": "s7.mp3",
        "speech": "Protect your PC with automated graceful Windows shutdown, background system tray operation, and native Windows toast notifications.",
        "subtitle": "Защита ПК: безопасное автовыключение Windows при разряде АКБ,\\Nинтеграция с системным треем и нативные системные уведомления.",
        "badge_tag": "FEATURE 06 // SYSTEM SAFETY",
        "badge_title": "Graceful Windows Shutdown",
        "badge_sub": "Countdown Timer, Tray & Toast Alerts",
        "type": "shutdown",
        "img": "assets/dashboard_preview_en.jpg",
    },
    {
        "id": "s8",
        "audio": "s8.mp3",
        "speech": "Built with Python, FastAPI, and modern web technologies. Free and open source under the MIT license. Star the repository on GitHub!",
        "subtitle": "Создано на Python, FastAPI и современных веб-технологиях.\\N100% бесплатно по лицензии MIT. Поставьте звезду на GitHub!",
        "badge_tag": "OPEN SOURCE // MIT LICENSE",
        "badge_title": "Star & Fork on GitHub",
        "badge_sub": "ALEVOLDON / UPS-ExeGate-SpecialPro-UNB-1200",
        "type": "outro",
    }
]

# Fonts
try:
    FONT_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 52)
    FONT_SUB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 28)
    FONT_BADGE_TAG = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
    FONT_BADGE_TITLE = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24)
    FONT_BADGE_SUB = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    FONT_TAG = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
except Exception:
    FONT_TITLE = ImageFont.load_default()
    FONT_SUB = ImageFont.load_default()
    FONT_BADGE_TAG = ImageFont.load_default()
    FONT_BADGE_TITLE = ImageFont.load_default()
    FONT_BADGE_SUB = ImageFont.load_default()
    FONT_TAG = ImageFont.load_default()

def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:01d}:{m:02d}:{s:05.2f}"

async def ensure_audio():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    for sc in SCENES_DEF:
        path = os.path.join(AUDIO_DIR, sc["audio"])
        if not os.path.exists(path) or os.path.getsize(path) < 1000:
            print(f"Synthesizing voice: {sc['id']}...")
            comm = edge_tts.Communicate(sc["speech"], "en-US-ChristopherNeural", rate="+2%")
            await comm.save(path)

def get_audio_duration(filepath):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", filepath]
    out = subprocess.check_output(cmd).decode()
    return float(json.loads(out)["format"]["duration"])

def generate_background_music(total_seconds, output_path):
    print("Generating ambient electronic music...")
    sr = 44100
    total_len = int(sr * total_seconds)
    t = np.linspace(0, total_seconds, total_len, endpoint=False)

    bpm = 112
    beat = 60.0 / bpm
    chord_prog = [
        [146.83, 174.61, 220.00, 261.63], # Dm7
        [116.54, 146.83, 174.61, 220.00], # Bbmaj7
        [130.81, 164.81, 196.00, 246.94], # Cmaj7
        [110.00, 130.81, 164.81, 196.00]  # Am7
    ]
    bar_len = beat * 4

    pad = np.zeros_like(t)
    bass = np.zeros_like(t)
    plucks = np.zeros_like(t)

    num_bars = int(total_seconds // bar_len) + 2
    for i in range(num_bars):
        chord = chord_prog[i % len(chord_prog)]
        t_start = i * bar_len
        idx_start = int(t_start * sr)
        idx_end = min(len(t), int((t_start + bar_len) * sr))
        if idx_start >= len(t):
            break
        
        chunk_len = idx_end - idx_start
        env = np.sin(np.linspace(0, np.pi, chunk_len)) ** 0.6
        chunk_pad = np.zeros(chunk_len)
        for freq in chord:
            chunk_pad += np.sin(2 * np.pi * freq * (t[idx_start:idx_end] - t_start))
            chunk_pad += 0.45 * np.sin(2 * np.pi * (freq * 1.005) * (t[idx_start:idx_end] - t_start))
            chunk_pad += 0.45 * np.sin(2 * np.pi * (freq * 0.995) * (t[idx_start:idx_end] - t_start))
        pad[idx_start:idx_end] += chunk_pad * env

        root = chord[0]
        chunk_bass = np.sin(2 * np.pi * (root / 2.0) * (t[idx_start:idx_end] - t_start))
        chunk_bass += 0.3 * np.sin(4 * np.pi * (root / 2.0) * (t[idx_start:idx_end] - t_start))
        b_env = np.exp(-1.4 * ((t[idx_start:idx_end] - t_start) % beat) / beat)
        bass[idx_start:idx_end] += chunk_bass * b_env

    # 16th note arp
    step = beat / 4
    num_steps = int(total_seconds // step)
    for s in range(num_steps):
        t_s = s * step
        idx_s = int(t_s * sr)
        idx_e = min(len(t), int((t_s + step * 2) * sr))
        if idx_s >= len(t): break
        chord = chord_prog[int((t_s // bar_len) % len(chord_prog))]
        note = chord[s % 4] * 2.0
        dur = (idx_e - idx_s) / sr
        env = np.exp(-14.0 * np.linspace(0, dur, idx_e - idx_s))
        plucks[idx_s:idx_e] += np.sin(2 * np.pi * note * np.linspace(0, dur, idx_e - idx_s)) * env * 0.35

    mix_l = pad * 0.4 + bass * 0.45 + plucks * 0.3
    mix_r = pad * 0.4 + bass * 0.45 + np.roll(plucks, 350) * 0.3

    b, a = butter(4, 2800 / (sr / 2), btype="low")
    mix_l = lfilter(b, a, mix_l)
    mix_r = lfilter(b, a, mix_r)

    fade_samples = int(3.5 * sr)
    mix_l[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    mix_r[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    # Normalize to -20 dB
    max_val = max(np.max(np.abs(mix_l)), np.max(np.abs(mix_r)))
    if max_val > 0:
        mix_l = (mix_l / max_val) * 0.12
        mix_r = (mix_r / max_val) * 0.12

    stereo = np.column_stack((mix_l, mix_r))
    wavfile.write(output_path, sr, (stereo * 32767).astype(np.int16))

def build_card(mode="intro"):
    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 14, 23, 255))
    draw = ImageDraw.Draw(img)

    # Glow
    glow = Image.new("RGBA", (900, 900), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    color = (0, 242, 254) if mode == "intro" else (79, 172, 254)
    for r in range(450, 0, -6):
        alpha = int(32 * (1 - r / 450.0))
        gdraw.ellipse((450 - r, 450 - r, 450 + r, 450 + r), fill=(color[0], color[1], color[2], alpha))
    img.paste(glow, (WIDTH // 2 - 450, 140), glow)

    # App icon
    if os.path.exists("assets/app_icon.png"):
        icon = Image.open("assets/app_icon.png").convert("RGBA").resize((210, 210), Image.Resampling.LANCZOS)
        img.paste(icon, (WIDTH // 2 - 105, 210), icon)

    if mode == "intro":
        draw.text((WIDTH // 2, 470), "ExeGate SpecialPro UPS Monitor", font=FONT_TITLE, fill=(255, 255, 255), anchor="mm")
        draw.text((WIDTH // 2, 535), "Intelligent Power Telemetry & System Safety Dashboard", font=FONT_SUB, fill=(0, 242, 254), anchor="mm")
        tags = ["PYTHON 3.9+", "FASTAPI", "WEBSOCKETS", "WINDOWS TRAY", "CHART.JS", "MIT LICENSE"]
        total_tag_w = len(tags) * 175
        start_x = (WIDTH - total_tag_w) // 2
        for i, tag in enumerate(tags):
            tx = start_x + i * 175
            ty = 615
            draw.rounded_rectangle((tx, ty, tx + 160, ty + 42), radius=8, fill=(18, 28, 48, 230), outline=(0, 242, 254, 180), width=1)
            draw.text((tx + 80, ty + 21), tag, font=FONT_TAG, fill=(220, 240, 255), anchor="mm")
    else: # outro
        draw.text((WIDTH // 2, 465), "Open Source Power Monitoring", font=FONT_TITLE, fill=(255, 255, 255), anchor="mm")
        draw.text((WIDTH // 2, 530), "Star & Download on GitHub: ALEVOLDON / UPS-ExeGate-SpecialPro-UNB-1200", font=FONT_SUB, fill=(0, 242, 254), anchor="mm")
        
        box_w = 680
        bx = (WIDTH - box_w) // 2
        by = 590
        draw.rounded_rectangle((bx, by, bx + box_w, by + 120), radius=14, fill=(16, 25, 42, 240), outline=(0, 242, 254, 220), width=2)
        draw.text((WIDTH // 2, by + 35), "github.com/ALEVOLDON/UPS-ExeGate-SpecialPro-UNB-1200", font=FONT_TAG, fill=(0, 242, 254), anchor="mm")
        draw.text((WIDTH // 2, by + 80), "MIT Licensed  •  Free & Community Driven  •  Created by @ALEVOLDON", font=FONT_BADGE_SUB, fill=(220, 240, 255), anchor="mm")

    return img

def render_badge_overlay(tag, title, subtitle):
    badge = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(badge)

    bx, by, bw, bh = 50, 45, 620, 82
    # Ambient shadow
    draw.rounded_rectangle((bx + 3, by + 5, bx + bw + 3, by + bh + 5), radius=14, fill=(0, 0, 0, 150))
    # Card body
    draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=14, fill=(12, 19, 34, 235), outline=(0, 242, 254, 220), width=2)
    # Accent indicator dot
    draw.ellipse((bx + 20, by + 21, bx + 30, by + 31), fill=(0, 242, 254))
    # Tag
    draw.text((bx + 40, by + 17), tag, font=FONT_BADGE_TAG, fill=(0, 242, 254))
    # Title
    draw.text((bx + 20, by + 38), title, font=FONT_BADGE_TITLE, fill=(255, 255, 255))
    # Subtitle
    draw.text((bx + 22, by + 62), subtitle, font=FONT_BADGE_SUB, fill=(150, 185, 215))

    return badge

def generate_ass_subtitles(timeline, output_file):
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "WrapStyle: 0",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: Default,Segoe UI,38,&H00FFFFFF,&H000000FF,&H0018120A,&HA0000000,1,0,0,0,100,100,0,0,3,4,0,2,60,60,65,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]

    for item in timeline:
        start_str = format_ass_time(item["start_time"])
        end_str = format_ass_time(item["end_time"])
        text = item["subtitle"]
        lines.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{text}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Subtitles saved to {output_file}")

def get_crop_box(im_w, im_h, target_aspect, factor, center_x_ratio, center_y_ratio):
    win_w = im_w / factor
    win_h = win_w / target_aspect
    if win_h > im_h / factor:
        win_h = im_h / factor
        win_w = win_h * target_aspect

    cx = im_w * center_x_ratio
    cy = im_h * center_y_ratio

    left = max(0, min(im_w - win_w, cx - win_w / 2.0))
    top = max(0, min(im_h - win_h, cy - win_h / 2.0))
    return (int(left), int(top), int(left + win_w), int(top + win_h))

def render_scene_frames(scene, num_frames, intro_card, outro_card, badge_overlay, target_aspect=16.0/9.0):
    stype = scene["type"]
    frames = []

    if stype == "intro_dashboard":
        dash_raw = Image.open("assets/dashboard_preview_en.jpg").convert("RGBA")
        dw, dh = dash_raw.size
        split_frame = int(num_frames * 0.42)
        fade_frames = int(num_frames * 0.10)

        for f in range(num_frames):
            if f < split_frame:
                z = 1.0 + 0.04 * (f / split_frame)
                box = get_crop_box(WIDTH, HEIGHT, target_aspect, z, 0.5, 0.5)
                frame = intro_card.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
            elif f < split_frame + fade_frames:
                alpha = (f - split_frame) / float(fade_frames)
                z1 = 1.0 + 0.04
                b1 = get_crop_box(WIDTH, HEIGHT, target_aspect, z1, 0.5, 0.5)
                f1 = intro_card.crop(b1).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                z2 = 1.0 + 0.05 * alpha
                b2 = get_crop_box(dw, dh, target_aspect, z2, 0.5, 0.45)
                f2 = dash_raw.crop(b2).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame = Image.blend(f1, f2, alpha)
                badge_fade = badge_overlay.copy()
                badge_fade.putalpha(int(255 * alpha))
                frame.paste(badge_fade, (0, 0), badge_fade)
            else:
                dash_prog = (f - split_frame - fade_frames) / float(num_frames - split_frame - fade_frames)
                z = 1.05 + 0.05 * dash_prog
                box = get_crop_box(dw, dh, target_aspect, z, 0.5, 0.45)
                frame = dash_raw.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
            frames.append(frame.convert("RGB"))

    elif stype == "outro":
        for f in range(num_frames):
            prog = f / float(num_frames)
            z = 1.0 + 0.04 * prog
            box = get_crop_box(WIDTH, HEIGHT, target_aspect, z, 0.5, 0.5)
            frame = outro_card.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
            frame.paste(badge_overlay, (0, 0), badge_overlay)
            frames.append(frame.convert("RGB"))

    else:
        src = Image.open(scene["img"]).convert("RGBA")
        sw, sh = src.size

        if stype == "gauges":
            for f in range(num_frames):
                p = f / float(num_frames)
                z = 1.35 + 0.15 * p
                cx = 0.35 + 0.25 * p
                cy = 0.38
                box = get_crop_box(sw, sh, target_aspect, z, cx, cy)
                frame = src.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
                frames.append(frame.convert("RGB"))

        elif stype == "grace_period":
            for f in range(num_frames):
                p = f / float(num_frames)
                z = 1.30 + 0.12 * p
                cx = 0.45
                cy = 0.22 - 0.04 * p
                box = get_crop_box(sw, sh, target_aspect, z, cx, cy)
                frame = src.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
                frames.append(frame.convert("RGB"))

        elif stype == "sockets":
            for f in range(num_frames):
                p = f / float(num_frames)
                z = 1.32 + 0.14 * p
                cx = 0.58
                cy = 0.62 + 0.02 * p
                box = get_crop_box(sw, sh, target_aspect, z, cx, cy)
                frame = src.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
                frames.append(frame.convert("RGB"))

        elif stype == "calculator":
            for f in range(num_frames):
                p = f / float(num_frames)
                z = 1.35 + 0.14 * p
                cx = 0.38
                cy = 0.72 + 0.06 * p
                box = get_crop_box(sw, sh, target_aspect, z, cx, cy)
                frame = src.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
                frames.append(frame.convert("RGB"))

        elif stype == "modal":
            for f in range(num_frames):
                p = f / float(num_frames)
                z = 1.16 + 0.12 * p
                cx = 0.50
                cy = 0.40 + 0.12 * p
                box = get_crop_box(sw, sh, target_aspect, z, cx, cy)
                frame = src.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
                frames.append(frame.convert("RGB"))

        elif stype == "shutdown":
            for f in range(num_frames):
                p = f / float(num_frames)
                z = 1.25 + 0.15 * p
                cx = 0.25
                cy = 0.42 + 0.08 * p
                box = get_crop_box(sw, sh, target_aspect, z, cx, cy)
                frame = src.crop(box).resize((WIDTH, HEIGHT), Image.Resampling.BILINEAR)
                frame.paste(badge_overlay, (0, 0), badge_overlay)
                frames.append(frame.convert("RGB"))

    return frames

def build_master_audio(timeline, total_duration, bg_music_file, output_audio):
    print("Building master mixed audio soundtrack...")
    inputs = []
    filter_chains = []
    mix_inputs = []

    for i, item in enumerate(timeline):
        audio_path = os.path.join(AUDIO_DIR, item["audio"])
        inputs.extend(["-i", audio_path])
        delay_ms = int(item["start_time"] * 1000)
        filter_chains.append(f"[{i}:a]adelay={delay_ms}|{delay_ms},volume=1.35[a{i}]")
        mix_inputs.append(f"[a{i}]")

    bg_index = len(timeline)
    inputs.extend(["-i", bg_music_file])
    filter_chains.append(f"[{bg_index}:a]volume=0.32,atrim=0:{total_duration}[abg]")
    mix_inputs.append("[abg]")

    filter_str = ";".join(filter_chains) + f";{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:normalize=0,volume=1.1[aout]"

    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filter_str, "-map", "[aout]", "-t", str(total_duration), "-c:a", "aac", "-b:a", "192k", output_audio]
    subprocess.run(cmd, check=True)
    print(f"Master audio saved to {output_audio}")

def generate_gif_preview(video_path, gif_path):
    print("Generating optimized animated GIF preview for README...")
    cmd = [
        "ffmpeg", "-y", "-ss", "00:00:08", "-t", "5", "-i", video_path,
        "-vf", "fps=12,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        gif_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Animated GIF preview saved to {gif_path}")

async def main():
    t0 = time.time()
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(SCRATCH_DIR, exist_ok=True)

    await ensure_audio()

    current_time = 0.0
    timeline = []
    for sc in SCENES_DEF:
        audio_path = os.path.join(AUDIO_DIR, sc["audio"])
        dur = get_audio_duration(audio_path)
        padding = 0.4 if sc["id"] != "s1" else 0.35
        scene_dur = dur + padding
        
        timeline.append({
            **sc,
            "speech_duration": dur,
            "scene_duration": scene_dur,
            "start_time": current_time,
            "end_time": current_time + scene_dur,
            "num_frames": int(scene_dur * FPS)
        })
        current_time += scene_dur

    total_duration = current_time
    print(f"Total Video Duration: {total_duration:.2f} seconds ({len(timeline)} scenes)")

    ass_file = os.path.join(SCRATCH_DIR, "subtitles.ass")
    generate_ass_subtitles(timeline, ass_file)

    bg_music_file = os.path.join(SCRATCH_DIR, "bg_music.wav")
    generate_background_music(total_duration + 2.0, bg_music_file)

    master_audio = os.path.join(SCRATCH_DIR, "master_audio.m4a")
    build_master_audio(timeline, total_duration, bg_music_file, master_audio)

    print("Rendering title cards and badge overlays...")
    intro_card = build_card("intro")
    outro_card = build_card("outro")
    badge_overlays = {}
    for sc in timeline:
        badge_overlays[sc["id"]] = render_badge_overlay(sc["badge_tag"], sc["badge_title"], sc["badge_sub"])

    output_mp4 = os.path.join(OUTPUT_DIR, "ups_monitor_showcase.mp4")
    print(f"Rendering {int(total_duration * FPS)} video frames and piping to FFmpeg...")

    ass_filter_path = ass_file.replace("\\", "/").replace(":", "\\:")

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-i", master_audio,
        "-vf", f"ass={ass_filter_path}",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-shortest",
        output_mp4
    ]

    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    total_frames = sum(sc["num_frames"] for sc in timeline)
    frames_rendered = 0

    for sc in timeline:
        sc_id = sc["id"]
        n_frames = sc["num_frames"]
        badge = badge_overlays[sc_id]
        
        frames = render_scene_frames(sc, n_frames, intro_card, outro_card, badge)
        for frame in frames:
            proc.stdin.write(frame.tobytes())
            frames_rendered += 1

        pct = (frames_rendered / total_frames) * 100
        print(f"Scene {sc_id} finished ({frames_rendered}/{total_frames} frames - {pct:.1f}%)")

    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed with exit code {proc.returncode}")

    print(f"\nSUCCESS! Video saved to: {output_mp4}")
    file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"Final MP4 Size: {file_size_mb:.2f} MB")

    gif_path = os.path.join(OUTPUT_DIR, "ups_monitor_demo.gif")
    generate_gif_preview(output_mp4, gif_path)

    t1 = time.time()
    print(f"\nAll tasks completed successfully in {t1 - t0:.1f} seconds!")

if __name__ == "__main__":
    asyncio.run(main())
