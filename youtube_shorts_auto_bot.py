#!/usr/bin/env python3
"""
100% Free Automated Daily YouTube Shorts Bot (US Kids/Family Infotainment Niche)
================================================================================
Pipeline Stages:
1. Viral Diagnostics Engine: Checks your last 10 uploaded Shorts via YouTube Data API v3,
   evaluates view velocity, like-to-view ratio (>4% target), and comment engagement,
   and diagnoses WHY any recent Short failed to go viral (weak hook, title length, niche fatigue).
2. Daily US Niche & Trend Analyzer (Gemini 2.5 Flash Free Tier + Google Trends RSS):
   Fetches live US trending topics and selects the highest-retention Family-Friendly / Kids-Safe
   curiosity niche (3D "What If" Science, Animal Mysteries, Space Secrets, Interactive Riddles).
3. Viral Shorts Scriptwriter: Writes a 45-55 second vertical Short script with:
   - 0-3s Scroll-Stopping Visual & Audio Hook
   - Fast-paced 6-scene visual storyboard (grade-4 US English for kids + adults)
   - Mid-video comment trigger & seamless loop ending (boosts >100% Average Percentage Viewed)
4. 100% Free Media Generation:
   - Voiceover + Word/Sentence Captions: Microsoft Edge Neural TTS (`edge-tts`, $0, no key needed)
   - 3D Pixar-Style Vertical Visuals (1080x1920): Pollinations.ai Flux model ($0, no key needed)
5. Automated Video Assembly (`moviepy` + `Pillow`):
   - Dynamic Ken Burns zoom-in effect on every scene
   - High-contrast center-screen yellow/white viral captions burned onto frames
6. Auto-Upload to YouTube (`google-api-python-client`):
   - Uploads Short with `#Shorts`, US SEO tags, and `selfDeclaredMadeForKids=False`
     (Family-Friendly General Audience setting to preserve full US RPM ad revenue).

Usage:
  python3 youtube_shorts_auto_bot.py              # Run full daily pipeline & upload
  python3 youtube_shorts_auto_bot.py --dry-run    # Generate MP4 locally without uploading
  python3 youtube_shorts_auto_bot.py --init-ci    # Generate GitHub Actions workflow & requirements.txt
"""

import argparse
import asyncio
import datetime
import json
import math
import os
import random
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("output_shorts")
TEMP_DIR = Path("temp_assets")
HISTORY_FILE = Path("viral_diagnostics_log.json")

# High-RPM, High-Retention US Family-Friendly Niches (appeals to kids + adults without COPPA ad penalty)
US_VIRAL_NICHES = [
    {
        "niche_id": "what_if_science",
        "name": "3D 'What If' Science & Space Mysteries",
        "description": "Mind-blowing hypothetical science questions explained simply with 3D Pixar-style visuals (e.g., 'What If You Fell Into Jupiter?', 'What If All Insects Vanished Tomorrow?').",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+8%",
    },
    {
        "niche_id": "animal_superpowers",
        "name": "Bizarre Animal Superpowers & Deep Ocean Secrets",
        "description": "Shocking real-life creatures that seem like aliens (e.g., 'The Immortal Jellyfish That Never Dies', 'Why Tardigrades Can Survive In Space').",
        "us_voice": "en-US-AriaNeural",
        "voice_rate": "+6%",
    },
    {
        "niche_id": "interactive_riddles",
        "name": "99% Fail Interactive Brain Teasers & Visual Riddles",
        "description": "Fast-paced survival or mystery riddles that force viewers to pause and comment their guess before the timer runs out.",
        "us_voice": "en-US-GuyNeural",
        "voice_rate": "+10%",
    },
    {
        "niche_id": "how_body_works",
        "name": "Weird Human Body Facts & Microscopic Adventures",
        "description": "Zooming inside the human body to explain weird everyday phenomena (e.g., 'What Actually Happens When Your Stomach Growls?').",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+8%",
    },
]


# ---------------------------------------------------------------------------
# Stage 1: YouTube API Client & Viral Diagnostics Engine
# ---------------------------------------------------------------------------
def get_youtube_service():
    """Builds an authenticated YouTube Data API v3 service using OAuth2 Refresh Token."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    client_id = os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YT_CLIENT_SECRET")
    refresh_token = os.environ.get("YT_REFRESH_TOKEN")

    if not (client_id and client_secret and refresh_token):
        print("[!] YouTube OAuth env vars (YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN) not set.")
        return None

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly",
        ],
    )
    return build("youtube", "v3", credentials=creds)


def analyze_past_shorts(youtube) -> Dict:
    """
    Fetches the last 10 Shorts on the channel, checks views, like ratio, and comment ratio,
    and diagnoses WHY any video underperformed so today's script fixes those exact issues.
    """
    diagnostics = {
        "analyzed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "recent_videos": [],
        "avg_views": 0,
        "best_niche_hint": None,
        "why_not_viral_diagnosis": [],
        "improvement_directives": [
            "Start with a 3-second visual shock question ('Stop scrolling if you...', 'What happens if...').",
            "Keep sentences under 10 words at a Grade-4 US English reading level so kids and adults stay hooked.",
            "Include a 3-second countdown or comment challenge in Scene 4 to boost YouTube algorithm engagement.",
            "Make the final sentence connect seamlessly back into the first sentence for an infinite loop.",
        ],
    }

    if youtube is None:
        diagnostics["why_not_viral_diagnosis"].append(
            "No YouTube channel connected yet — running baseline US Viral Shorts optimization."
        )
        return diagnostics

    try:
        # 1. Get user's uploads playlist ID
        channels_resp = youtube.channels().list(part="contentDetails,statistics", mine=True).execute()
        items = channels_resp.get("items", [])
        if not items:
            return diagnostics

        uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

        # 2. Fetch last 10 uploaded videos
        playlist_resp = (
            youtube.playlistItems()
            .list(part="snippet,contentDetails", playlistId=uploads_playlist_id, maxResults=10)
            .execute()
        )
        video_ids = [item["contentDetails"]["videoId"] for item in playlist_resp.get("items", [])]
        if not video_ids:
            return diagnostics

        # 3. Fetch detailed statistics for these videos
        stats_resp = (
            youtube.videos()
            .list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
            .execute()
        )

        total_views = 0
        low_like_ratio_count = 0
        low_comment_count = 0
        long_title_count = 0

        for vid in stats_resp.get("items", []):
            title = vid["snippet"]["title"]
            stats = vid.get("statistics", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))

            like_rate = (likes / views * 100.0) if views > 0 else 0.0
            comment_rate = (comments / views * 100.0) if views > 0 else 0.0

            total_views += views
            if views > 100 and like_rate < 3.5:
                low_like_ratio_count += 1
            if views > 100 and comment_rate < 0.15:
                low_comment_count += 1
            if len(title) > 60:
                long_title_count += 1

            diagnostics["recent_videos"].append(
                {
                    "title": title,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "like_rate_pct": round(like_rate, 2),
                    "comment_rate_pct": round(comment_rate, 3),
                }
            )

        count = len(diagnostics["recent_videos"])
        diagnostics["avg_views"] = int(total_views / count) if count else 0

        # 4. Diagnose why videos aren't going viral & generate corrective actions
        if low_like_ratio_count >= 2:
            diagnostics["why_not_viral_diagnosis"].append(
                "Low Like-to-View Ratio (<3.5%): Viewers are swiping away before the payoff."
            )
            diagnostics["improvement_directives"].append(
                "CRITICAL FIX: Reveal a mini mind-blowing twist at the 15-second mark and add a quick visual callout ('Double tap to save this crazy fact!')."
            )

        if low_comment_count >= 2:
            diagnostics["why_not_viral_diagnosis"].append(
                "Low Comment Engagement (<0.15%): Shorts algorithm needs comments to push into the 100k+ seed pool."
            )
            diagnostics["improvement_directives"].append(
                "CRITICAL FIX: Ask a polarizing or interactive question in Scene 4 ('Which door would you pick: A or B? Comment below!')."
            )

        if long_title_count >= 2:
            diagnostics["why_not_viral_diagnosis"].append(
                "Titles are getting truncated on mobile screens (>60 characters)."
            )
            diagnostics["improvement_directives"].append(
                "CRITICAL FIX: Keep the title strictly under 50 characters including #Shorts and 1 curiosity emoji."
            )

        if diagnostics["avg_views"] < 1500 and count >= 3:
            diagnostics["why_not_viral_diagnosis"].append(
                f"Average views ({diagnostics['avg_views']}) stuck in initial seed test (<1,500 views): Opening 3-second hook isn't stopping the swipe."
            )
            diagnostics["improvement_directives"].append(
                "CRITICAL FIX: Open with an extreme visual contrast ('Never touch this...', 'What happens if you...') in the very first 2 seconds."
            )

        # Save local diagnostics report
        HISTORY_FILE.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
        print(f"[+] Viral Diagnostics complete: Avg Views = {diagnostics['avg_views']}")

    except Exception as exc:
        print(f"[!] Warning during past video analysis: {exc}")

    return diagnostics


# ---------------------------------------------------------------------------
# Stage 2: Daily US Trends + Free Gemini API Niche & Script Generator
# ---------------------------------------------------------------------------
def fetch_us_google_trends() -> List[str]:
    """Fetches real-time US Google Trends RSS feed (100% free, no API key required)."""
    url = "https://trends.google.com/trending/rss?geo=US"
    trends = []
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item/title"):
                if item.text:
                    trends.append(item.text.strip())
    except Exception as exc:
        print(f"[!] Could not fetch US Google Trends RSS ({exc}), using evergreen viral pool.")
    return trends[:12]


def generate_daily_short_plan(diagnostics: Dict, us_trends: List[str]) -> Dict:
    """
    Uses Google Gemini Free API (`gemini-2.5-flash`) to pick the best US niche for today,
    incorporate the Viral Diagnostics feedback, and write a 6-scene 50-second Short script.
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    selected_niche = random.choice(US_VIRAL_NICHES)
    recent_titles = [v["title"] for v in diagnostics.get("recent_videos", [])]

    prompt = f"""
You are an elite US YouTube Shorts Viral Showrunner specializing in high-retention Family-Friendly 3D Animated Shorts (appealing to both kids aged 8-15 and US adults, similar to Zack D. Films, Bright [...]

TODAY'S US GOOGLE TRENDS:
{json.dumps(us_trends)}

CANDIDATE HIGH-RPM US NICHES:
{json.dumps(US_VIRAL_NICHES, indent=2)}

RECENTLY UPLOADED TITLES (DO NOT REPEAT THESE):
{json.dumps(recent_titles)}

VIRAL DIAGNOSTICS FROM PAST VIDEOS (MUST FIX THESE IN TODAY'S SCRIPT):
Diagnosis: {json.dumps(diagnostics.get('why_not_viral_diagnosis', []))}
Directives: {json.dumps(diagnostics.get('improvement_directives', []))}

TASK:
1. Pick the single highest-potential niche for today from CANDIDATE HIGH-RPM US NICHES (blend with a safe curiosity angle from TODAY'S US GOOGLE TRENDS if relevant, or pick an ultra-viral evergreen mystery).
2. Create a 45-to-55 second YouTube Short script broken into exactly 6 fast-paced scenes (total spoken words: 115 to 135 words).
3. Follow these viral rules strictly:
   - Scene 1 (0-3 sec): Extreme scroll-stopping curiosity hook ("Have you ever wondered...", "What would happen if...", "Never touch this strange object if...").
   - Scene 4: Include a quick interactive question prompting viewers to comment ("What would you do? Tell me in the comments!").
   - Scene 6: Deliver the mind-blowing payoff AND end with a phrase that grammatically loops back into Scene 1 ("...and that is exactly why you have to ask...").
   - Every `image_prompt` must specify: "3D Pixar Disney animation style, vibrant lighting, ultra-detailed, vertical 9:16 composition, expressive characters, no text, no watermarks".

Return ONLY valid JSON matching this exact schema:
{{
  "niche_id": "what_if_science",
  "niche_name": "3D 'What If' Science & Space Mysteries",
  "us_voice": "en-US-ChristopherNeural",
  "voice_rate": "+8%",
  "title": "What If You Swallowed A Cloud? ☁️ #Shorts",
  "description": "Full US SEO description with #Shorts #curiosity #science #whatif #animation",
  "tags": ["shorts", "what if", "science facts", "3d animation", "curiosity", "fun facts"],
  "viral_fix_applied": "Brief explanation of how this script fixes past viral bottlenecks",
  "scenes": [
    {{
      "scene_number": 1,
      "spoken_text": "What would actually happen if you jumped out of a plane and tried to eat a cloud?",
      "caption_highlight": "EAT A CLOUD?! ☁️",
      "image_prompt": "3D Pixar Disney animation style, a curious young skydiver floating next to a glowing fluffy white cumulus cloud in a bright blue sky, vibrant cinematic lighting, vertical 9:16 composition, expressive characters, no text, no watermarks"
    }}
  ]
}}
"""

    if gemini_api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.85,
                    "responseMimeType": "application/json",
                },
            }
            resp = requests.post(url, json=payload, timeout=45)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            plan = json.loads(raw_text)
            print(f"[+] Gemini generated today's Short: {plan.get('title')}")
            return plan
        except Exception as exc:
            print(f"[!] Gemini API call failed ({exc}), trying 100% free keyless Pollinations Text AI...")

    # 100% Free Keyless AI Fallback (Pollinations Text API - requires ZERO API keys!)
    try:
        print("[*] Generating fresh US Viral Short script via keyless Pollinations Text AI...")
        resp = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [
                    {"role": "system", "content": "You are a viral US YouTube Shorts scriptwriter. Output ONLY valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                "model": "openai",
                "jsonMode": True,
            },
            timeout=45,
        )
        if resp.status_code == 200:
            raw_json = resp.text.strip()
            if raw_json.startswith("```"):
                raw_json = raw_json.strip("`").removeprefix("json").strip()
            plan = json.loads(raw_json)
            if isinstance(plan, dict) and "scenes" in plan and len(plan["scenes"]) >= 6:
                print(f"[+] Keyless AI generated today's Short: {plan.get('title')}")
                return plan
    except Exception as exc:
        print(f"[!] Keyless AI fallback note ({exc}), selecting from built-in viral episode bank.")

    # Built-in fallback plan (useful for offline testing or if GEMINI_API_KEY is not yet set)
    return {
        "niche_id": selected_niche["niche_id"],
        "niche_name": selected_niche["name"],
        "us_voice": selected_niche["us_voice"],
        "voice_rate": selected_niche["voice_rate"],
        "title": "Why You Can Never Dig Through The Earth 🌍 #Shorts",
        "description": (
            "What would happen if you tried to dig a tunnel straight through the center of the Earth? "
            "Find out why the deepest hole ever dug had to stop! #Shorts #whatif #science #curiosity #animation #facts"
        ),
        "tags": ["shorts", "what if", "science facts", "earth mysteries", "3d animation", "curiosity"],
        "viral_fix_applied": "Applied 3-second extreme curiosity hook + mid-video comment question + infinite loop ending.",
        "scenes": [
            {
                "scene_number": 1,
                "spoken_text": "What would actually happen if you tried to dig a tunnel straight through the Earth?",
                "caption_highlight": "DIG THROUGH EARTH?! 🌍",
                "image_prompt": "3D Pixar Disney animation style, cute adventurous kid holding a glowing futuristic laser drill standing over a glowing deep hole in the ground, vibrant cinematic lighting, vertical 9:16 composition, expressive characters, no text, no watermarks",
            },
            {
                "scene_number": 2,
                "spoken_text": "At just thirty feet down, you would pass all house foundations and underground pipes.",
                "caption_highlight": "30 FEET DOWN 👇",
                "image_prompt": "3D Pixar animation style, underground cross section showing glowing pipes, tree roots, and colorful soil layers with a tiny explorer tunneling down, vertical 9:16 composition, vibrant lighting, no text, no watermarks",
            },
            {
                "scene_number": 3,
                "spoken_text": "At seven miles deep, you reach the Kola Superdeep Borehole, the deepest hole humans ever dug!",
                "caption_highlight": "7.5 MILES DEEP! 🔥",
                "image_prompt": "3D Pixar animation style, massive scientific drill rig glowing inside a deep subterranean cavern with red hot glowing crystals, vertical 9:16 composition, no text, no watermarks",
            },
            {
                "scene_number": 4,
                "spoken_text": "Down here, solid rock hits three hundred and fifty degrees and acts like sticky plastic! How deep do you think you could survive? Comment below!",
                "caption_highlight": "MELTING ROCK! 🌋",
                "image_prompt": "3D Pixar animation style, glowing orange molten plastic-like rock bubbling around a heat-shielded futuristic drill pod underground, dramatic lighting, vertical 9:16 composition, expressive characters, no text, no watermarks",
            },
            {
                "scene_number": 5,
                "spoken_text": "If you somehow wore an indestructible suit and jumped in, gravity would pull you at eighteen thousand miles per hour!",
                "caption_highlight": "18,000 MPH! 🚀",
                "image_prompt": "3D Pixar animation style, hero in a glowing silver space suit zooming fast through a futuristic glowing tunnel near the bright golden core of the Earth, vertical 9:16 composition, vibrant lighting, no text, no watermarks",
            },
            {
                "scene_number": 6,
                "spoken_text": "In just forty-two minutes you would pop out on the other side, which is why scientists still ask...",
                "caption_highlight": "42 MINUTES! ⏱️",
                "image_prompt": "3D Pixar animation style, explorer popping out of a glowing tunnel on the opposite side of the globe under a starry sky, vibrant colors, vertical 9:16 composition, no text, no watermarks",
            },
        ],
    }


# ---------------------------------------------------------------------------
# Stage 3: 100% Free Voiceover (`edge-tts`) & AI Image Generation (`Pollinations`)
# ---------------------------------------------------------------------------
async def synthesize_scene_audio(text: str, voice: str, rate: str, out_path: Path):
    """Generates free neural US English voiceover using Microsoft Edge TTS (`edge-tts`)."""
    import edge_tts

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(str(out_path))


def download_free_ai_image(prompt: str, out_path: Path, seed: int):
    """
    Downloads a free 1080x1920 vertical AI illustration from Pollinations.ai (Flux model, $0, no key).
    Includes automatic retry and procedural fallback canvas if offline.
    """
    encoded_prompt = urllib.parse.quote(prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        f"?width=1080&height=1920&seed={seed}&model=flux&nologo=true"
    )
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=45)
            if resp.status_code == 200 and len(resp.content) > 5000:
                out_path.write_bytes(resp.content)
                return
        except Exception as exc:
            print(f"[!] Image download attempt {attempt + 1} failed: {exc}")
            time.sleep(2)

    # Fallback: create a vibrant gradient poster if network is unavailable
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (1080, 1920), color=(20, 30, 70))
    draw = ImageDraw.Draw(img)
    for y in range(1920):
        r = int(20 + (y / 1920) * 60)
        g = int(30 + (y / 1920) * 100)
        b = int(90 + (y / 1920) * 140)
        draw.line([(0, y), (1080, y)], fill=(r, g, b))
    img.save(out_path)


# ---------------------------------------------------------------------------
# Stage 4: Automated Video Assembly (Ken Burns Zoom + Viral Captions)
# ---------------------------------------------------------------------------
def render_caption_overlay_frame(
    base_img_path: Path,
    spoken_text: str,
    highlight_badge: str,
    progress: float,
) -> "np.ndarray":
    """
    Applies a smooth Ken Burns zoom-in (`1.0x -> 1.12x`) and draws bold, high-contrast
    center-lower viral captions + top curiosity badge using Pillow (no ImageMagick needed!).
    """
    import numpy as np
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(base_img_path).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)

    # Smooth Ken Burns zoom-in
    zoom = 1.0 + 0.12 * progress
    crop_w = int(1080 / zoom)
    crop_h = int(1920 / zoom)
    left = (1080 - crop_w) // 2
    top = (1920 - crop_h) // 2
    img = img.crop((left, top, left + crop_w, top + crop_h)).resize(
        (1080, 1920), Image.Resampling.LANCZOS
    )

    draw = ImageDraw.Draw(img, "RGBA")

    # Load clean bold font (fallback to default if DejaVuSans-Bold is not in standard path)
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    font_large = None
    font_badge = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_large = ImageFont.truetype(fp, 58)
            font_badge = ImageFont.truetype(fp, 48)
            break
    if font_large is None:
        font_large = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    # 1. Draw Top Highlight Badge (e.g., "DIG THROUGH EARTH?! 🌍")
    if highlight_badge:
        draw.rounded_rectangle(
            [(140, 180), (940, 290)],
            radius=28,
            fill=(255, 215, 0, 235),
            outline=(0, 0, 0, 255),
            width=5,
        )
        draw.text(
            (540, 235),
            highlight_badge.upper(),
            font=font_badge,
            fill=(15, 15, 15, 255),
            anchor="mm",
        )

    # 2. Progressive Word-Chunk Subtitle Box in the Safe Center-Lower Zone (y = 1320..1580)
    words = spoken_text.split()
    chunk_size = 5
    chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]
    if chunks:
        idx = min(int(progress * len(chunks)), len(chunks) - 1)
        active_chunk = chunks[idx].upper()

        # Semi-transparent dark pill backdrop for maximum readability
        draw.rounded_rectangle(
            [(80, 1340), (1000, 1520)],
            radius=32,
            fill=(0, 0, 0, 190),
            outline=(255, 255, 255, 90),
            width=3,
        )
        # Draw text with thick black stroke + bright white/yellow fill
        draw.text(
            (540, 1430),
            active_chunk,
            font=font_large,
            fill=(255, 255, 100, 255),
            anchor="mm",
            stroke_width=4,
            stroke_fill=(0, 0, 0, 255),
        )

    return np.array(img)


def build_short_video(plan: Dict) -> Path:
    """Generates audio + visuals for all 6 scenes and compiles the final 1080x1920 MP4 Short."""
    from moviepy.editor import AudioFileClip, VideoClip, concatenate_videoclips

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    voice = plan.get("us_voice", "en-US-ChristopherNeural")
    rate = plan.get("voice_rate", "+8%")
    clips = []

    for scene in plan["scenes"]:
        s_num = scene["scene_number"]
        spoken = scene["spoken_text"]
        badge = scene.get("caption_highlight", "")
        img_prompt = scene["image_prompt"]

        audio_path = TEMP_DIR / f"scene_{s_num}.mp3"
        img_path = TEMP_DIR / f"scene_{s_num}.jpg"

        print(f"  -> Scene {s_num}: Generating US Voiceover & 3D Pixar Visual...")
        asyncio.run(synthesize_scene_audio(spoken, voice, rate, audio_path))
        download_free_ai_image(img_prompt, img_path, seed=random.randint(1000, 999999))

        audio_clip = AudioFileClip(str(audio_path))
        duration = max(audio_clip.duration + 0.15, 2.5)

        def make_frame(t, img_p=img_path, txt=spoken, bdg=badge, dur=duration):
            prog = min(max(t / dur, 0.0), 0.999)
            return render_caption_overlay_frame(img_p, txt, bdg, prog)

        video_clip = VideoClip(make_frame, duration=duration).set_audio(audio_clip)
        clips.append(video_clip)

    final_clip = concatenate_videoclips(clips, method="compose")
    date_slug = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out_video = OUTPUT_DIR / f"viral_short_{date_slug}.mp4"

    print(f"[+] Rendering final 1080x1920 YouTube Short to {out_video}...")
    final_clip.write_videofile(
        str(out_video),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
    )
    return out_video


# ---------------------------------------------------------------------------
# Stage 5: Automated YouTube Upload (US Peak Time & High-RPM Safe Settings)
# ---------------------------------------------------------------------------
def upload_short_to_youtube(youtube, video_path: Path, plan: Dict) -> Optional[str]:
    """Uploads the generated MP4 Short to YouTube with US SEO metadata."""
    from googleapiclient.http import MediaFileUpload

    if youtube is None:
        print("[!] Skipping upload because YouTube OAuth credentials are not configured.")
        return None

    title = plan["title"]
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title[:85]} #Shorts"

    body = {
        "snippet": {
            "title": title[:100],
            "description": plan["description"],
            "tags": plan.get("tags", ["shorts", "curiosity", "facts", "animation"]),
            "categoryId": "27",  # 27 = Education / Infotainment (High US RPM!)
            "defaultLanguage": "en-US",
            "defaultAudioLanguage": "en-US",
        },
        "status": {
            "privacyStatus": "public",
            # IMPORTANT: Keep False so personalized ads, comments, and high US RPM remain active!
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  -> Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"[+] Successfully uploaded Short! URL: https://youtube.com/shorts/{video_id}")
    return video_id


# ---------------------------------------------------------------------------
# Helper: Generate GitHub Actions CI/CD Files (`--init-ci`)
# ---------------------------------------------------------------------------
def generate_ci_files():
    """Creates requirements.txt and .github/workflows/daily_shorts.yml for 100% free cloud execution."""
    reqs = "\n".join(
        [
            "edge-tts>=6.1.12",
            "moviepy==1.0.3",
            "Pillow>=10.0.0",
            "numpy>=1.24.0",
            "requests>=2.31.0",
            "google-api-python-client>=2.120.0",
            "google-auth-oauthlib>=1.2.0",
            "google-auth-httplib2>=0.2.0",
        ]
    )
    Path("requirements.txt").write_text(reqs + "\n", encoding="utf-8")

    workflow_dir = Path(".github/workflows")
    workflow_dir.mkdir(parents=True, exist_ok=True)
    workflow_yaml = """name: Daily Viral YouTube Shorts Bot (US Peak Hours)

on:
  schedule:
    # Runs automatically every day at 19:30 UTC (3:30 PM US Eastern Time / 1:00 AM IST)
    # Right when US schools finish and US mobile Shorts traffic peaks!
    - cron: '30 19 * * *'
  workflow_dispatch: # Allows manual 1-click run anytime from GitHub Actions tab

jobs:
  create-and-upload-short:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install FFmpeg & Fonts
        run: |
          sudo apt-get update
          sudo apt-get install -y ffmpeg fonts-dejavu-core

      - name: Install Python Dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Viral Diagnostics, Niche Analysis, Video Render & Upload
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          YT_CLIENT_ID: ${{ secrets.YT_CLIENT_ID }}
          YT_CLIENT_SECRET: ${{ secrets.YT_CLIENT_SECRET }}
          YT_REFRESH_TOKEN: ${{ secrets.YT_REFRESH_TOKEN }}
        run: |
          python3 youtube_shorts_auto_bot.py

      - name: Save Viral Diagnostics Log Artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: viral-diagnostics-report
          path: viral_diagnostics_log.json
"""
    (workflow_dir / "daily_shorts.yml").write_text(workflow_yaml, encoding="utf-8")
    print("[+] Created `requirements.txt` and `.github/workflows/daily_shorts.yml`!")


# ---------------------------------------------------------------------------
# Main Execution Entrypoint
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="100% Free Automated Daily YouTube Shorts Bot")
    parser.add_argument("--dry-run", action="store_true", help="Generate video locally without uploading")
    parser.add_argument("--init-ci", action="store_true", help="Create GitHub Actions workflow & requirements.txt")
    args = parser.parse_args()

    if args.init_ci:
        generate_ci_files()
        return

    print("=== STEP 1: Connecting to YouTube & Running Viral Diagnostics ===")
    youtube = None if args.dry_run else get_youtube_service()
    diagnostics = analyze_past_shorts(youtube)
    if diagnostics["why_not_viral_diagnosis"]:
        print("  -> Diagnostics Insights:")
        for item in diagnostics["why_not_viral_diagnosis"]:
            print(f"     * {item}")

    print("\n=== STEP 2: Analyzing US Trends & Generating Viral Short Script ===")
    us_trends = fetch_us_google_trends()
    plan = generate_daily_short_plan(diagnostics, us_trends)
    print(f"  -> Selected Niche: {plan['niche_name']}")
    print(f"  -> Title: {plan['title']}")
    print(f"  -> Viral Fix Applied: {plan.get('viral_fix_applied')}")

    print("\n=== STEP 3 & 4: Generating Free US Voiceover, 3D Visuals & Editing Short ===")
    video_path = build_short_video(plan)

    if args.dry_run:
        print(f"\n[+] Dry-run complete! Video saved at: {video_path}")
        return

    print("\n=== STEP 5: Uploading to YouTube Channel ===")
    upload_short_to_youtube(youtube, video_path, plan)


if __name__ == "__main__":
    main()
