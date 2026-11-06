# -*- coding: utf-8 -*-
"""
DaVinci Resolve Automated Timeline Builder for UPS ExeGate SpecialPro Monitor Showcase
Can be run:
1. Outside Resolve (with DaVinci Resolve running): python tools/build_davinci_showcase.py
2. Inside Resolve: Workspace -> Scripts -> Utility -> Build_UPS_Showcase
"""

import os
import sys

# Setup environment for standalone execution
script_api = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
script_lib = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
modules_path = os.path.join(script_api, "Modules")

if "RESOLVE_SCRIPT_API" not in os.environ:
    os.environ["RESOLVE_SCRIPT_API"] = script_api
if "RESOLVE_SCRIPT_LIB" not in os.environ:
    os.environ["RESOLVE_SCRIPT_LIB"] = script_lib
if modules_path not in sys.path:
    sys.path.append(modules_path)

resolve = None

# 1. Try connecting via DaVinciResolveScript (external)
try:
    import DaVinciResolveScript as dvr_script
    resolve = dvr_script.scriptapp("Resolve")
except Exception:
    pass

# 2. Try global bmd object (internal menu/console)
if not resolve:
    try:
        resolve = bmd.scriptapp("Resolve")  # noqa: F821
    except Exception:
        pass

if not resolve:
    print("=" * 60)
    print("[-] DaVinci Resolve is not running or not accessible.")
    print("[-] Please start DaVinci Resolve first, then run this script.")
    print("[-] Or launch DaVinci Resolve and run it via:")
    print("    Workspace -> Scripts -> Utility -> Build_UPS_Showcase")
    print("=" * 60)
    sys.exit(1)

print("[+] Successfully connected to DaVinci Resolve API!")
product_name = resolve.GetProductName()
version = resolve.GetVersionString()
print(f"[+] Connected to: {product_name} v{version}")

# Project Manager
pm = resolve.GetProjectManager()
project_name = "UPS_Monitor_Showcase"

# Check if project already exists
project = pm.LoadProject(project_name)
if not project:
    print(f"[+] Creating new project: {project_name}")
    project = pm.CreateProject(project_name)
else:
    print(f"[+] Loaded existing project: {project_name}")

if not project:
    print(f"[-] Failed to create/load project '{project_name}'.")
    sys.exit(1)

# Project Settings: 1080p 30fps
project.SetSetting("timelineFrameRate", "30")
project.SetSetting("timelinePlaybackFrameRate", "30")
project.SetSetting("timelineResolutionWidth", "1920")
project.SetSetting("timelineResolutionHeight", "1080")

media_pool = project.GetMediaPool()
root_folder = media_pool.GetRootFolder()

# Base project directory
base_dir = r"D:\_CODE_2026_\UPS ExeGate SpecialPro UNB-1200"
video_path = os.path.join(base_dir, r"assets\demo_original.mp4")
audio_master = os.path.join(base_dir, r"scratch_video\live_master_audio.m4a")
bg_music = os.path.join(base_dir, r"scratch_audio\bg_music.wav")
intro_img = os.path.join(base_dir, r"scratch_video\intro_card.png")
outro_img = os.path.join(base_dir, r"scratch_video\live_outro.png")

media_files = [video_path, audio_master, bg_music, intro_img, outro_img]
valid_media = [f for f in media_files if os.path.exists(f)]

print(f"[+] Importing {len(valid_media)} media assets into Media Pool...")
imported_items = media_pool.ImportMedia(valid_media)
print(f"[+] Successfully imported {len(imported_items)} clips into Media Pool.")

# Create Timeline
timeline_name = "UPS_Showcase_Timeline"
timeline = None
# Check if timeline already exists
for i in range(1, project.GetTimelineCount() + 1):
    tl = project.GetTimelineByIndex(i)
    if tl and tl.GetName() == timeline_name:
        timeline = tl
        break

if not timeline:
    print(f"[+] Creating new timeline: {timeline_name}")
    timeline = media_pool.CreateEmptyTimeline(timeline_name)
else:
    print(f"[+] Using existing timeline: {timeline_name}")

project.SetCurrentTimeline(timeline)

# Add media to timeline
# Get imported clip mapping
clip_dict = {}
for clip in root_folder.GetClipList():
    clip_dict[clip.GetName()] = clip

print("[+] Available clips in Media Pool:")
for name in clip_dict:
    print(f"    - {name}")

# Populate timeline tracks
if "demo_original.mp4" in clip_dict:
    print("[+] Adding screen recording (demo_original.mp4) to timeline...")
    media_pool.AppendToTimeline([clip_dict["demo_original.mp4"]])

if "live_master_audio.m4a" in clip_dict:
    print("[+] Adding master audio (voiceover + ducked music) to timeline...")
    media_pool.AppendToTimeline([clip_dict["live_master_audio.m4a"]])

# Add markers for chapters
markers = [
    (0, "Cyan", "Intro & Live Telemetry", "Overview and AVR Boost live demonstration"),
    (510, "Blue", "Power Flow Scheme", "Interactive energy distribution diagram"),
    (1050, "Green", "Grid Analytics", "Historical incidents and energy cost tracking"),
    (1560, "Yellow", "Settings & Scaling", "UPS model presets and battery auto-detection"),
    (2160, "Red", "Graceful Auto-Shutdown", "Safe PC shutdown mechanism with abort countdown"),
    (2430, "Pink", "Outro & GitHub MIT", "Open Source release & repository links"),
]

print("[+] Adding chapter markers...")
for frame, color, name, note in markers:
    try:
        timeline.AddMarker(frame, color, name, note, 30)
    except Exception as e:
        print(f"    Note: Marker at frame {frame} ({name}): {e}")

# Save project
pm.SaveProject()
print("=" * 60)
print(f"[SUCCESS] DaVinci Resolve project '{project_name}' is ready!")
print("Timeline 'UPS_Showcase_Timeline' configured with 1080p 30fps and chapter markers.")
print("Switch to the 'Edit' or 'Fairlight' page in DaVinci Resolve to view and refine.")
print("=" * 60)
