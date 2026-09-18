"""
Builds the definitive Master Showcase Video using the user's real screen recording.
Features:
- Live 1080p presentation framing
- Synchronized English voiceover matching user actions
- Synchronized Russian subtitles (ASS)
- Cyberpunk styled floating chapter badges
- Ambient electronic music ducked under speech
- High quality outro screen with GitHub links
"""

import os
import subprocess
import time

def main():
    t0 = time.time()
    os.makedirs("assets", exist_ok=True)
    os.makedirs("scratch_video", exist_ok=True)

    ass_path = "scratch_video/live_subtitles.ass"
    output_mp4 = "assets/ups_monitor_showcase.mp4"

    filter_complex = ";".join([
        "[1:v]fps=30,scale=1108:960:flags=lanczos,drawbox=x=0:y=0:w=1108:h=960:color=#00f2fe@0.35:t=1[app]",
        "[0:v][app]overlay=x=406:y=35:enable='lte(t,80.0)'[v1]",
        "[v1][2:v]overlay=x=0:y=0:enable='gte(t,80.0)'[v2]",
        "[v2][3:v]overlay=x=0:y=0:enable='between(t,0,21.5)'[v3]",
        "[v3][4:v]overlay=x=0:y=0:enable='between(t,21.5,38.0)'[v4]",
        "[v4][5:v]overlay=x=0:y=0:enable='between(t,38.0,54.5)'[v5]",
        "[v5][6:v]overlay=x=0:y=0:enable='between(t,54.5,80.0)'[v6]",
        f"[v6]ass=filename='{ass_path}'[vfinal]"
    ])

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0b0f19:s=1920x1080:d=87.5:r=30",
        "-i", "assets/demo_original.mp4",
        "-loop", "1", "-t", "87.5", "-i", "scratch_video/live_outro.png",
        "-loop", "1", "-t", "87.5", "-i", "scratch_video/live_badge_1.png",
        "-loop", "1", "-t", "87.5", "-i", "scratch_video/live_badge_2.png",
        "-loop", "1", "-t", "87.5", "-i", "scratch_video/live_badge_3.png",
        "-loop", "1", "-t", "87.5", "-i", "scratch_video/live_badge_4.png",
        "-i", "scratch_video/live_master_audio.m4a",
        "-filter_complex", filter_complex,
        "-map", "[vfinal]",
        "-map", "7:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-t", "87.5",
        output_mp4
    ]

    print("Rendering Master Showcase Video from real screen recording...")
    proc = subprocess.run(cmd, check=True)

    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"SUCCESS! Video created: {output_mp4} ({size_mb:.2f} MB)")

    # Generate optimized GIF preview from the live AVR BOOST scene
    print("Generating optimized animated GIF teaser for README...")
    gif_path = "assets/ups_monitor_demo.gif"
    gif_cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:06", "-t", "6.5",
        "-i", output_mp4,
        "-vf", "fps=14,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        gif_path
    ]
    subprocess.run(gif_cmd, check=True)
    gif_size_mb = os.path.getsize(gif_path) / (1024 * 1024)
    print(f"GIF preview saved: {gif_path} ({gif_size_mb:.2f} MB)")

    t1 = time.time()
    print(f"Entire render completed in {t1 - t0:.1f} seconds!")

if __name__ == "__main__":
    main()
