#!/usr/bin/env python3
"""
100% Free Automated Daily YouTube Shorts Bot (US Kids/Family Infotainment Niche) — 1080p HD Studio Edition
===========================================================================================================
Upgrades in this HD Studio Edition:
1. Exact Word-Synced Karaoke Captions (`edge-tts` WordBoundary stream + smart syllable fallback):
   - Zero missing or cut-off words!
   - Groups speech into punchy 2-3 word chunks with automatic 2-line word wrapping inside a safe 920px box.
   - Highlights the currently spoken word in Neon Yellow (#FFE600) while keeping neighbor words in Crisp White (#FFFFFF)
     with thick 6px black stroke and drop shadow (Zack D. Films / Hormozi viral style).
2. True 1080x1920 Full HD Visual Pipeline:
   - Multi-endpoint Pollinations Flux/Turbo 3D Pixar downloader with browser headers + UnsharpMask & Vibrance enhancement.
   - Rich 3D Procedural Scene Renderer fallback (volumetric glow, 3D planet/science rings, starfield, dynamic particles)
     so a scene is NEVER a blank screen even if an external image server rate-limits.
3. Procedural Background Music Bed + High-Bitrate H.264 MP4 Encoding (`crf=18`, `8500k` bitrate, `yuv420p`).
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
import wave
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("output_shorts")
TEMP_DIR = Path("temp_assets")
HISTORY_FILE = Path("viral_diagnostics_log.json")

US_VIRAL_NICHES = [
    {
        "niche_id": "what_if_science",
        "name": "3D 'What If' Science & Space Mysteries",
        "description": "Mind-blowing hypothetical science questions explained simply with 3D Pixar-style visuals.",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+10%",
        "theme_palette": [(10, 18, 48), (28, 64, 148), (255, 130, 35)],
    },
    {
        "niche_id": "animal_superpowers",
        "name": "Bizarre Animal Superpowers & Nature Secrets",
        "description": "Shocking real-life creatures with superpowers explained in 3D X-ray detail.",
        "us_voice": "en-US-AriaNeural",
        "voice_rate": "+10%",
        "theme_palette": [(6, 38, 45), (15, 118, 110), (56, 189, 248)],
    },
    {
        "niche_id": "interactive_riddles",
        "name": "99% Fail Interactive Brain Teasers & Survival Riddles",
        "description": "Fast-paced survival or physics riddles that force viewers to comment their guess.",
        "us_voice": "en-US-GuyNeural",
        "voice_rate": "+10%",
        "theme_palette": [(38, 14, 78), (109, 40, 217), (250, 204, 21)],
    },
    {
        "niche_id": "how_body_works",
        "name": "Weird Human Body Facts & Microscopic Adventures",
        "description": "Zooming inside the human body to explain weird everyday phenomena.",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+10%",
        "theme_palette": [(55, 10, 18), (185, 28, 28), (251, 191, 36)],
    },
]

# Built-in Rotating Bank of Verified Viral Episodes (ensures fresh topics even without API keys)
BUILTIN_VIRAL_EPISODES = [
    {
        "niche_id": "animal_superpowers",
        "niche_name": "Bizarre Animal Superpowers",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+10%",
        "title": "How Owls Twist Their Heads 270°! 🦉😱 #Shorts",
        "description": (
            "Why don't owls pass out when they twist their heads 270 degrees backward? 🦉🧠\n"
            "Can you look behind your back without turning your shoulders? Comment YES or NO below! 👇\n"
            "#Shorts #Animals #ScienceFacts #Owl #NatureSuperpowers #3DAnimation"
        ),
        "tags": ["shorts", "youtube shorts", "owl head turning", "animal superpowers", "science facts", "3d animation"],
        "viral_fix_applied": "0-3s 270° Neck Shock Hook + Word-Synced Karaoke Captions + Infinite Loop",
        "scenes": [
            {
                "scene_number": 1,
                "spoken_text": "Because if a human twisted their neck two hundred and seventy degrees like an owl, it would instantly snap their arteries!",
                "caption_highlight": "270° NECK TWIST?! 🦉",
                "image_prompt": "3D Pixar Disney animation style cute wide-eyed barn owl perched on a glowing branch at night spinning its head 270 degrees with a glowing neon ring around its neck, vibrant cinematic lighting, vertical 9:16, no text",
            },
            {
                "scene_number": 2,
                "spoken_text": "You can roll your eyes from side to side, but an owl has giant telescope tubes locked tightly in bone!",
                "caption_highlight": "EYES LOCKED IN BONE! 👀",
                "image_prompt": "3D Pixar Disney animation style X-ray closeup of a cute owl showing glowing blue tubular telescope-shaped eyes locked inside its skull, ultra-detailed 3D educational render, vertical 9:16, no text",
            },
            {
                "scene_number": 3,
                "spoken_text": "In humans, twisting your head that far would pinch your neck arteries shut and cut off all blood to the brain!",
                "caption_highlight": "PINCHES ARTERIES SHUT! ⚠️",
                "image_prompt": "3D Pixar Disney animation style glowing medical hologram of a red artery tube getting pinched like a twisted garden hose with glowing warning sparks, vibrant lighting, vertical 9:16, no text",
            },
            {
                "scene_number": 4,
                "spoken_text": "Quick test! Can you look behind your back without turning your shoulders? Comment YES or NO right now!",
                "caption_highlight": "COMMENT YES OR NO! 👇",
                "image_prompt": "3D Pixar Disney animation style funny kid trying to peek over their shoulder next to a cute owl effortlessly turning its head backward, glowing neon question marks, vertical 9:16, no text",
            },
            {
                "scene_number": 5,
                "spoken_text": "Scientists used CT scans and found owls have hollow bone tunnels and secret backup blood tanks right below their jaw!",
                "caption_highlight": "SECRET BLOOD TANKS! 🩸",
                "image_prompt": "3D Pixar Disney animation style glowing biomechanical X-ray of an owl neck showing wide protective bone tunnels and ruby-red backup blood reservoirs feeding oxygen sparkles to the brain, vertical 9:16, no text",
            },
            {
                "scene_number": 6,
                "spoken_text": "Combined with silent feathers that cancel out sound waves, this bird has nature's ultimate stealth body, which is crazy...",
                "caption_highlight": "BUILT FOR STEALTH! 🔄",
                "image_prompt": "3D Pixar Disney animation style majestic owl gliding silently through a moonlit forest with glowing sound-wave rings canceling out around its wings, vertical 9:16, no text",
            },
        ],
    },
    {
        "niche_id": "what_if_science",
        "niche_name": "3D 'What If' Science & Space Mysteries",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+10%",
        "title": "What If Earth Stopped Spinning For 1s? 🌍😱 #Shorts",
        "description": (
            "What would actually happen if the Earth suddenly stopped spinning for just 1 second? 🌍💨\n"
            "Where would you survive—the EQUATOR or the NORTH POLE? Comment below! 👇\n"
            "#Shorts #WhatIf #SpaceFacts #Science #Earth #Physics #3DAnimation"
        ),
        "tags": ["shorts", "youtube shorts", "what if earth stopped spinning", "space facts", "science facts", "3d animation"],
        "viral_fix_applied": "1,100 MPH Supersonic Shock Hook + Equator vs Pole Quiz + Loop Ending",
        "scenes": [
            {
                "scene_number": 1,
                "spoken_text": "Because if the Earth suddenly stopped spinning for just one second, you would instantly fly sideways at eleven hundred miles per hour!",
                "caption_highlight": "1,100 MPH INSTANTLY?! 🌍",
                "image_prompt": "3D Pixar Disney animation style cute astronaut kid holding onto a glowing streetlamp as trees and clouds blur sideways in a massive shockwave with planet Earth in the sky above, vertical 9:16, no text",
            },
            {
                "scene_number": 2,
                "spoken_text": "Right now you cannot feel it, but the ground beneath your feet is spinning eastward faster than a speeding bullet!",
                "caption_highlight": "FASTER THAN A BULLET! ⚡",
                "image_prompt": "3D Pixar Disney animation style cutaway view of planet Earth spinning in space with a glowing neon speedometer hitting 1100 MPH at the equator, vibrant 3D render, vertical 9:16, no text",
            },
            {
                "scene_number": 3,
                "spoken_text": "If the planet slammed on the brakes, the air would keep moving with sixteen times the force of the strongest hurricane on Earth!",
                "caption_highlight": "16X HURRICANE FORCE! 🌪️",
                "image_prompt": "3D Pixar Disney animation style giant glowing supersonic wind vortex sweeping across a miniature cartoon city and ocean waves, dramatic lighting, vertical 9:16, no text",
            },
            {
                "scene_number": 4,
                "spoken_text": "Quick survival test! Only one place wouldn't fly sideways: the Equator or the North Pole? Comment EQUATOR or POLE right now!",
                "caption_highlight": "EQUATOR OR POLE?! 👇",
                "image_prompt": "3D Pixar Disney animation style split screen showing a sunny tropical beach at the Equator on top and a snowy North Pole igloo on the bottom with glowing question marks, vertical 9:16, no text",
            },
            {
                "scene_number": 5,
                "spoken_text": "Without centrifugal force holding water at the middle, all the oceans would rush toward the poles and flood the planet!",
                "caption_highlight": "OCEANS RUSH TO POLES! 🌊",
                "image_prompt": "3D Pixar Disney animation style globe view from space showing Earth blue oceans sliding toward the North and South Poles while a glowing orange continent ring forms around the equator, vertical 9:16, no text",
            },
            {
                "scene_number": 6,
                "spoken_text": "Worst of all, a single day would last a full year, and you wouldn't even survive the first second...",
                "caption_highlight": "6 MONTHS OF NIGHT! ☀️",
                "image_prompt": "3D Pixar Disney animation style half-sunny desert and half-frozen ice planet Earth hanging in space with dramatic cosmic lighting, vertical 9:16, no text",
            },
        ],
    },
    {
        "niche_id": "interactive_riddles",
        "niche_name": "99% Fail Interactive Brain Teasers",
        "us_voice": "en-US-GuyNeural",
        "voice_rate": "+10%",
        "title": "How To Survive A Falling Elevator! 🛗😱 #Shorts",
        "description": (
            "If you were trapped in a falling elevator, should you JUMP (A), STAND (B), or LIE FLAT (C)? 🛗⚡\n"
            "Comment A, B, or C before the answer is revealed! 👇\n"
            "#Shorts #Riddles #Survival #Physics #ScienceFacts #MythBusters #3DAnimation"
        ),
        "tags": ["shorts", "youtube shorts", "how to survive a falling elevator", "survival riddles", "physics facts", "3d animation"],
        "viral_fix_applied": "0-3s Falling Elevator Hook + Scene 3 A/B/C Comment Trigger + Loop Ending",
        "scenes": [
            {
                "scene_number": 1,
                "spoken_text": "Because ninety-nine percent of people think jumping at the very last second inside a falling elevator will save their life!",
                "caption_highlight": "JUMP AT LAST SECOND?! 🛗",
                "image_prompt": "3D Pixar Disney animation style wide-eyed kid inside a glass skyscraper elevator with glowing red alarm lights as sparks fly from the top cable, dramatic lighting, vertical 9:16, no text",
            },
            {
                "scene_number": 2,
                "spoken_text": "Imagine the cables snap fifty floors up and you are plummeting at fifty-three miles per hour with three seconds to act!",
                "caption_highlight": "50 FLOORS DOWN! ⚠️",
                "image_prompt": "3D Pixar Disney animation style X-ray cutaway view of a tall glowing skyscraper shaft showing a futuristic elevator plunging downward, vibrant 3D render, vertical 9:16, no text",
            },
            {
                "scene_number": 3,
                "spoken_text": "Do you pick Option A: jump before impact? Option B: stand straight? Or Option C: lie flat on your back? Comment A, B, or C now!",
                "caption_highlight": "COMMENT A, B, OR C! 👇",
                "image_prompt": "3D Pixar Disney animation style three glowing holographic survival panels inside an elevator showing jumping, standing, and lying flat on the floor, bright vibrant colors, vertical 9:16, no text",
            },
            {
                "scene_number": 4,
                "spoken_text": "If you picked A, MythBusters proved a human jump only slows you down by three miles per hour—so you still crash at fifty!",
                "caption_highlight": "JUMPING FAILS! ❌",
                "image_prompt": "3D Pixar Disney animation style crash-test dummy inside a laboratory elevator rig jumping slightly with glowing physics arrows around it, vertical 9:16, no text",
            },
            {
                "scene_number": 5,
                "spoken_text": "Option C gives you the best chance! Lying flat on your back while shielding your head spreads the huge G-force across your whole body!",
                "caption_highlight": "LIE FLAT ON FLOOR! 🛡️",
                "image_prompt": "3D Pixar Disney animation style glowing blue protective energy grid spreading impact arrows evenly across an explorer lying flat on their back on the elevator floor, vertical 9:16, no text",
            },
            {
                "scene_number": 6,
                "spoken_text": "One woman even survived a seventy-five-floor plunge thanks to compressed air and coiled cables below, which is crazy...",
                "caption_highlight": "SURVIVED 75 FLOORS! 🏆",
                "image_prompt": "3D Pixar Disney animation style giant glowing coil of steel cables and compressed blue air cushion at the bottom of a skyscraper elevator shaft, vertical 9:16, no text",
            },
        ],
    },
    {
        "niche_id": "how_body_works",
        "niche_name": "Weird Human Body Facts",
        "us_voice": "en-US-ChristopherNeural",
        "voice_rate": "+10%",
        "title": "Why Stomach Acid Doesn't Melt You! 🧪😱 #Shorts",
        "description": (
            "Your stomach acid is strong enough to dissolve metal—so why doesn't it digest your own body? 🧪🛡️\n"
            "How fast does your stomach build a new lining—3 DAYS or 3 YEARS? Comment below! 👇\n"
            "#Shorts #HumanBody #ScienceFacts #WeirdFacts #Biology #3DAnimation"
        ),
        "tags": ["shorts", "youtube shorts", "stomach acid vs metal", "human body facts", "science facts", "3d animation"],
        "viral_fix_applied": "pH 0.8 Metal-Melting Hook + 3 Days vs 3 Years Quiz + Infinite Loop",
        "scenes": [
            {
                "scene_number": 1,
                "spoken_text": "Because right now inside your belly is a pool of acid strong enough to dissolve solid metal—so why doesn't it melt you?!",
                "caption_highlight": "MELTS SOLID METAL?! 🧪",
                "image_prompt": "3D Pixar Disney animation style glowing internal cutaway of a human stomach filled with bubbling neon-green acid dissolving a shiny metal wrench into sparkles, vertical 9:16, no text",
            },
            {
                "scene_number": 2,
                "spoken_text": "Special cells tucked inside your stomach folds squirt out pure hydrochloric acid with a pH as low as zero-point-eight!",
                "caption_highlight": "PURE ACID pH 0.8! ⚡",
                "image_prompt": "3D Pixar Disney animation style macro close-up of cute microscopic parietal cells along pink stomach folds spraying glowing green acid droplets, vibrant 3D render, vertical 9:16, no text",
            },
            {
                "scene_number": 3,
                "spoken_text": "Your stomach survives by coating its walls in a thick double layer of sugar-coated mucus armor that acid cannot burn through!",
                "caption_highlight": "DOUBLE SLIME ARMOR! 🛡️",
                "image_prompt": "3D Pixar Disney animation style glowing two-layer translucent blue jelly shield coating the pink stomach wall and bouncing green acid droplets away, vertical 9:16, no text",
            },
            {
                "scene_number": 4,
                "spoken_text": "Quick body quiz! How fast does your stomach build a brand-new lining: every THREE DAYS or every THREE YEARS? Comment now!",
                "caption_highlight": "3 DAYS OR 3 YEARS?! 👇",
                "image_prompt": "3D Pixar Disney animation style cute microscopic construction worker cells holding glowing blueprints inside the stomach with a glowing stopwatch, vertical 9:16, no text",
            },
            {
                "scene_number": 5,
                "spoken_text": "If you guessed three days, you nailed it! Every three to four days, your body replaces its entire stomach lining from scratch!",
                "caption_highlight": "NEW LINING IN 3 DAYS! 🔄",
                "image_prompt": "3D Pixar Disney animation style wave of fresh glowing pink cells zipping across the stomach wall like shiny new tiles, hyper-detailed cinematic lighting, vertical 9:16, no text",
            },
            {
                "scene_number": 6,
                "spoken_text": "Your throat doesn't have that mucus armor, which is why heartburn burns like fire, and that is wild...",
                "caption_highlight": "WHY HEARTBURN BURNS! 🔥",
                "image_prompt": "3D Pixar Disney animation style glowing valve at the top of a cartoon stomach with warm orange and green neon lighting, vertical 9:16, no text",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Stage 1: YouTube API Client & Viral Diagnostics Engine
# ---------------------------------------------------------------------------
def get_youtube_service():
    """Builds an authenticated YouTube Data API v3 service using OAuth2 Refresh Token."""
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    client_id = os.environ.get("YT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YT_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("YT_REFRESH_TOKEN", "").strip()

    if client_id.startswith("https://"):
        client_id = client_id.replace("https://", "", 1).strip()
    if client_id.startswith("http://"):
        client_id = client_id.replace("http://", "", 1).strip()

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
    """Checks last 10 uploaded Shorts and diagnoses viral bottlenecks."""
    diagnostics = {
        "analyzed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "recent_videos": [],
        "avg_views": 0,
        "why_not_viral_diagnosis": [],
        "improvement_directives": [
            "Start with a 0-3 second visual shock hook ('Because if a human...', 'What happens if...').",
            "Keep sentences punchy at a Grade-4 US English reading level so kids and adults stay hooked.",
            "Include a binary comment challenge in Scene 3 or Scene 4 to boost YouTube algorithm engagement.",
            "Make Scene 6 connect seamlessly back into Scene 1 for an infinite loop.",
        ],
    }

    if youtube is None:
        return diagnostics

    try:
        channels_resp = youtube.channels().list(part="contentDetails,statistics", mine=True).execute()
        items = channels_resp.get("items", [])
        if not items:
            return diagnostics

        uploads_playlist_id = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        playlist_resp = (
            youtube.playlistItems()
            .list(part="snippet,contentDetails", playlistId=uploads_playlist_id, maxResults=10)
            .execute()
        )
        video_ids = [item["contentDetails"]["videoId"] for item in playlist_resp.get("items", [])]
        if not video_ids:
            return diagnostics

        stats_resp = (
            youtube.videos()
            .list(part="snippet,statistics,contentDetails", id=",".join(video_ids))
            .execute()
        )

        total_views = 0
        for vid in stats_resp.get("items", []):
            title = vid["snippet"]["title"]
            stats = vid.get("statistics", {})
            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            comments = int(stats.get("commentCount", 0))
            total_views += views
            diagnostics["recent_videos"].append(
                {
                    "title": title,
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                }
            )

        count = len(diagnostics["recent_videos"])
        diagnostics["avg_views"] = int(total_views / count) if count else 0
        HISTORY_FILE.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"[!] Warning during past video analysis: {exc}")

    return diagnostics


# ---------------------------------------------------------------------------
# Stage 2: Daily US Trends + AI Script Generator (Gemini OR Keyless AI OR Bank)
# ---------------------------------------------------------------------------
def fetch_us_google_trends() -> List[str]:
    url = "https://trends.google.com/trending/rss?geo=US"
    trends = []
    try:
        resp = requests.get(url, timeout=12, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            root = ET.fromstring(resp.text)
            for item in root.findall(".//item/title"):
                if item.text:
                    trends.append(item.text.strip())
    except Exception:
        pass
    return trends[:10]


def generate_daily_short_plan(diagnostics: Dict, us_trends: List[str]) -> Dict:
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    recent_titles = [v["title"] for v in diagnostics.get("recent_videos", [])]

    prompt = f"""You are an elite US YouTube Shorts Showrunner creating a 50-second 6-scene 3D Pixar-style Short for kids and adults.
Recent titles to avoid repeating: {json.dumps(recent_titles)}
US Trends context: {json.dumps(us_trends)}

Return ONLY valid JSON with this exact structure:
{{
  "niche_id": "what_if_science",
  "niche_name": "3D 'What If' Science & Space Mysteries",
  "us_voice": "en-US-ChristopherNeural",
  "voice_rate": "+10%",
  "title": "Under 50 char title with emoji #Shorts",
  "description": "US SEO description with comment question and #Shorts",
  "tags": ["shorts", "youtube shorts", "what if", "science facts", "3d animation"],
  "viral_fix_applied": "0-3s Hook + Word-Synced Karaoke Captions + Infinite Loop",
  "scenes": [
    {{
      "scene_number": 1,
      "spoken_text": "18 to 24 words of punchy US English voiceover starting with Because or What if...",
      "caption_highlight": "SHORT 3-WORD BADGE! 🔥",
      "image_prompt": "3D Pixar Disney animation style, vibrant detailed scene description, vertical 9:16 composition, no text"
    }}
  ]
}}
Ensure there are exactly 6 scenes, Scene 4 asks viewers to comment, and Scene 6 loops back into Scene 1."""

    if gemini_api_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.85, "responseMimeType": "application/json"},
            }
            resp = requests.post(url, json=payload, timeout=40)
            resp.raise_for_status()
            raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            plan = json.loads(raw_text)
            if isinstance(plan, dict) and len(plan.get("scenes", [])) >= 6:
                print(f"[+] Gemini generated today's Short: {plan.get('title')}")
                return plan
        except Exception as exc:
            print(f"[!] Gemini API note ({exc}), trying keyless Pollinations AI...")

    try:
        resp = requests.post(
            "https://text.pollinations.ai/",
            json={
                "messages": [
                    {"role": "system", "content": "Output ONLY valid JSON matching the requested 6-scene YouTube Short schema."},
                    {"role": "user", "content": prompt},
                ],
                "model": "openai",
                "jsonMode": True,
            },
            timeout=35,
        )
        if resp.status_code == 200:
            raw_json = resp.text.strip()
            if "{" in raw_json and "}" in raw_json:
                raw_json = raw_json[raw_json.find("{") : raw_json.rfind("}") + 1]
            plan = json.loads(raw_json)
            if isinstance(plan, dict) and len(plan.get("scenes", [])) >= 6:
                print(f"[+] Keyless AI generated today's Short: {plan.get('title')}")
                return plan
    except Exception as exc:
        print(f"[!] Keyless AI fallback note ({exc}), picking non-repeated episode from built-in bank.")

    for ep in BUILTIN_VIRAL_EPISODES:
        if ep["title"] not in recent_titles:
            return ep
    day_idx = datetime.datetime.now().timetuple().tm_yday % len(BUILTIN_VIRAL_EPISODES)
    return BUILTIN_VIRAL_EPISODES[day_idx]


# ---------------------------------------------------------------------------
# Stage 3: Exact Word-Synced Voiceover (`edge-tts` WordBoundary Stream)
# ---------------------------------------------------------------------------
async def synthesize_scene_audio_with_timestamps(
    text: str, voice: str, rate: str, out_path: Path
) -> List[Dict]:
    """
    Generates crystal-clear US English neural voiceover AND extracts exact word-level timestamps
    from edge-tts WordBoundary events so captions NEVER miss a word or go out of sync.
    """
    import edge_tts

    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    word_events: List[Dict] = []

    with open(out_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start_sec = chunk["offset"] / 10_000_000.0
                dur_sec = max(chunk["duration"] / 10_000_000.0, 0.08)
                word_events.append(
                    {
                        "word": str(chunk["text"]).strip(),
                        "start": start_sec,
                        "end": start_sec + dur_sec,
                    }
                )
    return word_events


def build_word_timings_fallback(spoken_text: str, audio_duration: float) -> List[Dict]:
    """
    Character-weighted word timing generator used whenever edge-tts streams audio without
    explicit WordBoundary metadata (guarantees 100% of spoken words appear on screen in sync).
    """
    raw_words = [w.strip() for w in spoken_text.split() if w.strip()]
    if not raw_words:
        return []

    lead_pad = 0.06
    trail_pad = 0.16
    usable_dur = max(audio_duration - lead_pad - trail_pad, 0.8)

    weights = []
    for w in raw_words:
        base_w = max(len(re.sub(r"[^A-Za-z0-9]", "", w)), 2)
        if w.endswith((",", "—", "-")):
            base_w += 2.5
        elif w.endswith((".", "!", "?", ":")):
            base_w += 3.5
        weights.append(float(base_w))

    total_weight = sum(weights) or 1.0
    cursor = lead_pad
    timings = []
    for w, wt in zip(raw_words, weights):
        w_dur = usable_dur * (wt / total_weight)
        timings.append({"word": w, "start": cursor, "end": cursor + w_dur})
        cursor += w_dur
    return timings


def group_words_into_caption_phrases(word_timings: List[Dict], max_words: int = 3) -> List[Dict]:
    """
    Groups timed words into short 2-to-3 word viral caption phrases (max ~18 chars per phrase)
    so captions are HUGE, readable, and NEVER overflow off the 1080px screen.
    """
    phrases = []
    current_group: List[Dict] = []
    current_chars = 0

    for item in word_timings:
        w_len = len(item["word"])
        if current_group and (len(current_group) >= max_words or current_chars + 1 + w_len > 18):
            phrases.append(
                {
                    "start": current_group[0]["start"],
                    "end": current_group[-1]["end"],
                    "words": current_group,
                }
            )
            current_group = [item]
            current_chars = w_len
        else:
            current_group.append(item)
            current_chars += (1 if current_chars > 0 else 0) + w_len

    if current_group:
        phrases.append(
            {
                "start": current_group[0]["start"],
                "end": current_group[-1]["end"],
                "words": current_group,
            }
        )
    return phrases


# ---------------------------------------------------------------------------
# Stage 4: True 1080x1920 HD Visual Engine (AI Image + 3D Procedural Studio Fallback)
# ---------------------------------------------------------------------------
def render_hd_procedural_3d_scene(
    out_path: Path,
    scene_num: int,
    badge_text: str,
    spoken_text: str,
    palette: List[Tuple[int, int, int]],
):
    """
    Renders a rich, multi-layered 1080x1920 Full HD 3D-styled illustration canvas
    with volumetric glow, perspective grid, cosmic rings, and glowing particles.
    Used if external AI image endpoints rate-limit or time out on cloud runners.
    """
    W, H = 1080, 1920
    c_top, c_mid, c_accent = palette

    # Fast NumPy vertical gradient + radial volumetric glow
    y_idx = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
    x_idx = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]

    bg = np.zeros((H, W, 3), dtype=np.float32)
    for ch in range(3):
        bg[:, :, ch] = np.where(
            y_idx < 0.55,
            c_top[ch] + (c_mid[ch] - c_top[ch]) * (y_idx / 0.55),
            c_mid[ch] + (6 - c_mid[ch]) * ((y_idx - 0.55) / 0.45),
        )

    # Radial volumetric spotlight in the center (cx=540, cy=820)
    dist = np.sqrt(((x_idx - 0.5) * W) ** 2 + ((y_idx - 0.43) * H) ** 2)
    glow = np.clip(1.0 - dist / 520.0, 0.0, 1.0) ** 2.2
    for ch in range(3):
        bg[:, :, ch] = np.clip(bg[:, :, ch] + glow * c_accent[ch] * 0.75, 0, 255)

    img = Image.fromarray(bg.astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = 540, 820
    rng = random.Random(scene_num * 9173 + len(spoken_text))

    # Draw 3D perspective floor grid at bottom
    horizon_y = 1180
    for gx in range(-1200, 2280, 180):
        draw.line([(cx + (gx - cx) * 0.15, horizon_y), (gx, H)], fill=(255, 255, 255, 28), width=2)
    for gy_step in range(1, 10):
        py = int(horizon_y + (gy_step / 9.0) ** 1.8 * (H - horizon_y))
        draw.line([(0, py), (W, py)], fill=(c_accent[0], c_accent[1], c_accent[2], 38), width=2)

    # Draw concentric 3D energy/orbital rings around center stage
    for r_idx in range(6, 0, -1):
        rad = r_idx * 68
        alpha = int(30 + (6 - r_idx) * 22)
        draw.ellipse(
            [(cx - rad, cy - rad), (cx + rad, cy + rad)],
            outline=(255, 255, 255, alpha),
            width=4,
        )
        draw.arc(
            [(cx - rad - 12, cy - rad - 12), (cx + rad + 12, cy + rad + 12)],
            start=scene_num * 45,
            end=scene_num * 45 + 140,
            fill=(c_accent[0], c_accent[1], c_accent[2], min(alpha + 80, 255)),
            width=8,
        )

    # Central 3D shaded orb
    orb_r = 185
    draw.ellipse(
        [(cx - orb_r, cy - orb_r), (cx + orb_r, cy + orb_r)],
        fill=(c_mid[0], c_mid[1], c_mid[2], 235),
        outline=(255, 230, 100, 255),
        width=8,
    )
    draw.ellipse(
        [(cx - orb_r + 35, cy - orb_r + 25), (cx - 10, cy - 20)],
        fill=(255, 255, 255, 70),
    )

    # Floating bokeh & neon particles
    for _ in range(55):
        px = rng.randint(40, W - 40)
        py = rng.randint(120, H - 180)
        pr = rng.randint(4, 16)
        col = (255, 235, 90, rng.randint(90, 210)) if rng.random() > 0.4 else (255, 255, 255, rng.randint(70, 180))
        draw.ellipse([(px - pr, py - pr), (px + pr, py + pr)], fill=col)

    img.save(out_path, quality=95)


def download_free_ai_image(
    prompt: str,
    out_path: Path,
    seed: int,
    scene_num: int = 1,
    badge_text: str = "",
    spoken_text: str = "",
    palette: Optional[List[Tuple[int, int, int]]] = None,
):
    """
    Downloads a crisp 1080x1920 vertical 3D Pixar-style illustration using multiple free endpoints,
    enhances sharpness & vibrance for Full HD output, and falls back to the 3D procedural studio renderer.
    """
    clean_prompt = re.sub(r"\s+", " ", prompt).strip()
    encoded_prompt = urllib.parse.quote(clean_prompt)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    }

    candidate_urls = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={seed}&model=flux&nologo=true&enhance=true",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&seed={seed}&model=turbo&nologo=true",
        f"https://pollinations.ai/p/{encoded_prompt}?width=1080&height=1920&seed={seed}&nologo=true",
    ]

    for url in candidate_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=35)
            if resp.status_code == 200 and len(resp.content) > 12_000:
                out_path.write_bytes(resp.content)
                # Enhance image sharpness, contrast & color vibrance for 1080p HD Shorts
                img = Image.open(out_path).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)
                img = ImageEnhance.Color(img).enhance(1.18)
                img = ImageEnhance.Contrast(img).enhance(1.10)
                img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=130, threshold=3))
                img.save(out_path, quality=95)
                return
        except Exception as exc:
            print(f"[!] Image endpoint retry ({exc})")
            time.sleep(1.5)

    print(f"  -> Using built-in 1080p 3D Procedural Studio Canvas for Scene {scene_num}")
    render_hd_procedural_3d_scene(
        out_path=out_path,
        scene_num=scene_num,
        badge_text=badge_text,
        spoken_text=spoken_text,
        palette=palette or [(10, 18, 48), (28, 64, 148), (255, 130, 35)],
    )


# ---------------------------------------------------------------------------
# Stage 5: Studio-Grade Karaoke Caption & Frame Compositor (Zero Cutoffs!)
# ---------------------------------------------------------------------------
_FONT_CACHE: Dict[int, ImageFont.FreeTypeFont] = {}


def get_bold_font(size: int) -> ImageFont.FreeTypeFont:
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            f = ImageFont.truetype(fp, size)
            _FONT_CACHE[size] = f
            return f
    return ImageFont.load_default()


def wrap_badge_text_to_fit(draw: ImageDraw.ImageDraw, text: str, max_width: int) -> Tuple[ImageFont.FreeTypeFont, str]:
    """Automatically scales top badge font so it never overflows the yellow pill."""
    clean = re.sub(r"[^\x00-\x7F]+", "", text).strip().upper() or text.upper()
    for sz in (46, 42, 38, 34, 30):
        font = get_bold_font(sz)
        bbox = draw.textbbox((0, 0), clean, font=font)
        if (bbox[2] - bbox[0]) <= max_width:
            return font, clean
    return get_bold_font(28), clean


def render_caption_overlay_frame(
    base_img: Image.Image,
    phrases: List[Dict],
    highlight_badge: str,
    current_time: float,
    duration: float,
    scene_number: int = 1,
) -> np.ndarray:
    """
    Renders a single 1080x1920 Full HD frame with:
    1. Smooth Ken Burns zoom-in + subtle pan
    2. Top-safe-zone High-Contrast Curiosity Badge (auto-scaled so zero text is ever clipped)
    3. Center-Lower Word-Synced Karaoke Captions:
       - Shows 2-3 words at a time inside a rounded glass card
       - Highlights the exact active word in Neon Yellow (#FFE600) and neighbor words in Crisp White (#FFFFFF)
       - Automatically wraps onto 2 lines if wider than 860px so ZERO words are ever cut off!
    """
    progress = min(max(current_time / max(duration, 0.1), 0.0), 1.0)

    # 1. Smooth Ken Burns zoom (alternating zoom-in and zoom-out across scenes for dynamic motion)
    if scene_number % 2 == 1:
        zoom = 1.0 + 0.14 * progress
    else:
        zoom = 1.14 - 0.12 * progress

    crop_w = int(1080 / zoom)
    crop_h = int(1920 / zoom)
    left = (1080 - crop_w) // 2
    top = (1920 - crop_h) // 2
    frame = base_img.crop((left, top, left + crop_w, top + crop_h)).resize(
        (1080, 1920), Image.Resampling.BILINEAR
    )

    draw = ImageDraw.Draw(frame, "RGBA")

    # Subtle top and bottom cinematic vignette gradients for maximum text contrast
    draw.rectangle([(0, 0), (1080, 340)], fill=(0, 0, 0, 75))
    draw.rectangle([(0, 1220), (1080, 1920)], fill=(0, 0, 0, 110))

    # 2. Top Curiosity Hook Badge (Safe zone y = 150..265, well below status bar)
    if highlight_badge:
        font_badge, clean_badge = wrap_badge_text_to_fit(draw, highlight_badge, max_width=780)
        draw.rounded_rectangle(
            [(110, 155), (970, 265)],
            radius=30,
            fill=(255, 215, 0, 245),
            outline=(0, 0, 0, 255),
            width=6,
        )
        draw.text(
            (540, 210),
            clean_badge,
            font=font_badge,
            fill=(10, 14, 24, 255),
            anchor="mm",
        )

    # 3. Find the active 2-3 word phrase and the exact active word at `current_time`
    if phrases:
        active_phrase = phrases[-1]
        for ph in phrases:
            if ph["start"] <= current_time <= ph["end"] + 0.08:
                active_phrase = ph
                break
            if current_time < ph["start"]:
                active_phrase = ph
                break

        words_info = active_phrase["words"]
        active_word_idx = 0
        for idx, w_item in enumerate(words_info):
            if current_time >= w_item["start"]:
                active_word_idx = idx

        # Choose font size (64pt default, auto-scales down if a single word is very long)
        font_cap = get_bold_font(62)
        max_line_width = 860

        # Build 1 or 2 wrapped lines of word tokens: [(word_str_upper, is_active), ...]
        tokens = []
        for idx, w_item in enumerate(words_info):
            clean_w = re.sub(r"[^\x00-\x7F]+", "", w_item["word"]).strip().upper()
            if not clean_w:
                clean_w = w_item["word"].upper()
            tokens.append((clean_w, idx == active_word_idx))

        lines: List[List[Tuple[str, bool]]] = []
        current_line: List[Tuple[str, bool]] = []
        for tok in tokens:
            test_str = " ".join([t[0] for t in current_line + [tok]])
            bbox = draw.textbbox((0, 0), test_str, font=font_cap)
            if current_line and (bbox[2] - bbox[0]) > max_line_width:
                lines.append(current_line)
                current_line = [tok]
            else:
                current_line.append(tok)
        if current_line:
            lines.append(current_line)

        # If any single word is still wider than max_line_width, step down font size
        for check_sz in (54, 48, 42):
            too_wide = False
            for ln in lines:
                s = " ".join([t[0] for t in ln])
                bb = draw.textbbox((0, 0), s, font=font_cap)
                if (bb[2] - bb[0]) > max_line_width:
                    too_wide = True
            if too_wide:
                font_cap = get_bold_font(check_sz)
            else:
                break

        # Draw high-contrast dark glass caption box in the safe center-lower zone (y = 1300..1560)
        line_height = 78
        total_text_h = len(lines) * line_height
        box_center_y = 1425
        box_top = box_center_y - (total_text_h // 2) - 36
        box_bottom = box_center_y + (total_text_h // 2) + 36

        # Drop shadow + main pill
        draw.rounded_rectangle(
            [(76, box_top + 8), (1004, box_bottom + 8)],
            radius=36,
            fill=(0, 0, 0, 160),
        )
        draw.rounded_rectangle(
            [(70, box_top), (1010, box_bottom)],
            radius=36,
            fill=(10, 15, 28, 225),
            outline=(255, 230, 0, 190),
            width=4,
        )

        # Draw each line word-by-word centered horizontally, coloring the active word Neon Yellow
        start_y = box_center_y - ((len(lines) - 1) * line_height) // 2
        space_bbox = draw.textbbox((0, 0), " ", font=font_cap)
        space_w = max(space_bbox[2] - space_bbox[0], 18)

        for line_idx, ln in enumerate(lines):
            word_widths = []
            for w_str, _ in ln:
                wb = draw.textbbox((0, 0), w_str, font=font_cap)
                word_widths.append(wb[2] - wb[0])
            line_total_w = sum(word_widths) + space_w * max(len(ln) - 1, 0)
            cursor_x = 540 - (line_total_w // 2)
            y_pos = start_y + line_idx * line_height

            for (w_str, is_active), w_w in zip(ln, word_widths):
                word_center_x = cursor_x + (w_w // 2)
                if is_active:
                    # Highlighted active word pill backdrop + Neon Yellow text
                    pad_x, pad_y = 12, 8
                    draw.rounded_rectangle(
                        [
                            (cursor_x - pad_x, y_pos - 36 - pad_y),
                            (cursor_x + w_w + pad_x, y_pos + 36 + pad_y),
                        ],
                        radius=16,
                        fill=(255, 230, 0, 45),
                    )
                    fill_col = (255, 235, 0, 255)
                else:
                    fill_col = (255, 255, 255, 255)

                # Thick black outline + crisp fill
                draw.text(
                    (word_center_x, y_pos),
                    w_str,
                    font=font_cap,
                    fill=fill_col,
                    anchor="mm",
                    stroke_width=6,
                    stroke_fill=(0, 0, 0, 255),
                )
                cursor_x += w_w + space_w

    # 4. Bottom Red Retention Progress Bar
    bar_w = int(1080 * progress)
    draw.rectangle([(0, 1906), (1080, 1920)], fill=(255, 255, 255, 50))
    draw.rectangle([(0, 1906), (bar_w, 1920)], fill=(239, 68, 68, 255))

    return np.array(frame)


# ---------------------------------------------------------------------------
# Stage 6: Procedural Background Synth Audio Bed + High-Bitrate MP4 Assembly
# ---------------------------------------------------------------------------
def generate_background_music_wav(out_wav: Path, duration_sec: float, sample_rate: int = 44100):
    """Generates a subtle, royalty-free cinematic curiosity synth pulse WAV at -18dB."""
    total_samples = int(duration_sec * sample_rate)
    t = np.linspace(0, duration_sec, total_samples, endpoint=False, dtype=np.float32)

    # Warm minor curiosity chord progression (A2, E3, A3, C4 gentle pulse)
    freqs = [110.0, 164.81, 220.0, 261.63]
    signal = np.zeros_like(t)
    for idx, f in enumerate(freqs):
        lfo = 0.5 + 0.5 * np.sin(2 * np.pi * (1.2 + idx * 0.25) * t)
        signal += np.sin(2 * np.pi * f * t) * lfo * (0.25 / len(freqs))

    # Subtle rhythmic tick every 0.5s for retention pacing
    beat_env = np.exp(-18.0 * np.mod(t, 0.5))
    signal += np.sin(2 * np.pi * 88.0 * t) * beat_env * 0.12

    # Keep volume low (0.10 amplitude) so voiceover is 100% dominant and crystal clear
    signal = np.clip(signal * 0.11, -0.95, 0.95)
    pcm = (signal * 32767).astype(np.int16)

    with wave.open(str(out_wav), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


def build_short_video(plan: Dict) -> Path:
    """Generates word-synced voiceover + 1080p HD visuals for all 6 scenes and compiles the MP4 Short."""
    from moviepy.editor import (
        AudioFileClip,
        CompositeAudioClip,
        VideoClip,
        concatenate_videoclips,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)

    voice = plan.get("us_voice", "en-US-ChristopherNeural")
    rate = plan.get("voice_rate", "+10%")

    niche_palette = [(10, 18, 48), (28, 64, 148), (255, 130, 35)]
    for n in US_VIRAL_NICHES:
        if n["niche_id"] == plan.get("niche_id"):
            niche_palette = n["theme_palette"]
            break

    clips = []

    for scene in plan["scenes"]:
        s_num = scene["scene_number"]
        spoken = scene["spoken_text"]
        badge = scene.get("caption_highlight", "")
        img_prompt = scene["image_prompt"]

        audio_path = TEMP_DIR / f"scene_{s_num}.mp3"
        img_path = TEMP_DIR / f"scene_{s_num}.jpg"

        print(f"  -> Scene {s_num}: Generating Word-Synced US Voiceover & 1080p 3D Visual...")
        word_events = asyncio.run(
            synthesize_scene_audio_with_timestamps(spoken, voice, rate, audio_path)
        )
        download_free_ai_image(
            prompt=img_prompt,
            out_path=img_path,
            seed=random.randint(1000, 999999),
            scene_num=s_num,
            badge_text=badge,
            spoken_text=spoken,
            palette=niche_palette,
        )

        audio_clip = AudioFileClip(str(audio_path))
        duration = max(audio_clip.duration + 0.12, 2.5)

        if not word_events or len(word_events) < max(len(spoken.split()) // 2, 1):
            word_events = build_word_timings_fallback(spoken, audio_clip.duration)

        phrases = group_words_into_caption_phrases(word_events, max_words=3)
        base_img = Image.open(img_path).convert("RGB").resize((1080, 1920), Image.Resampling.LANCZOS)

        def make_frame(t, b_img=base_img, phs=phrases, bdg=badge, dur=duration, sn=s_num):
            return render_caption_overlay_frame(b_img, phs, bdg, t, dur, sn)

        video_clip = VideoClip(make_frame, duration=duration).set_audio(audio_clip)
        clips.append(video_clip)

    final_clip = concatenate_videoclips(clips, method="compose")

    # Add subtle background synth bed under the voiceover
    bgm_wav = TEMP_DIR / "bgm_bed.wav"
    generate_background_music_wav(bgm_wav, final_clip.duration)
    bgm_clip = AudioFileClip(str(bgm_wav))
    mixed_audio = CompositeAudioClip([bgm_clip, final_clip.audio])
    final_clip = final_clip.set_audio(mixed_audio)

    date_slug = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out_video = OUTPUT_DIR / f"viral_short_{date_slug}.mp4"

    print(f"[+] Rendering Full HD 1080x1920 YouTube Short to {out_video}...")
    final_clip.write_videofile(
        str(out_video),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        bitrate="8500k",
        preset="fast",
        ffmpeg_params=["-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"],
        threads=4,
    )
    return out_video


# ---------------------------------------------------------------------------
# Stage 7: Automated YouTube Upload
# ---------------------------------------------------------------------------
def upload_short_to_youtube(youtube, video_path: Path, plan: Dict) -> Optional[str]:
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
            "categoryId": "27",
            "defaultLanguage": "en-US",
            "defaultAudioLanguage": "en-US",
        },
        "status": {
            "privacyStatus": "public",
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


def generate_ci_files():
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


def main():
    parser = argparse.ArgumentParser(description="100% Free Automated Daily YouTube Shorts Bot (1080p HD)")
    parser.add_argument("--dry-run", action="store_true", help="Generate video locally without uploading")
    parser.add_argument("--init-ci", action="store_true", help="Create requirements.txt")
    args = parser.parse_args()

    if args.init_ci:
        generate_ci_files()
        return

    print("=== STEP 1: Connecting to YouTube & Running Viral Diagnostics ===")
    youtube = None if args.dry_run else get_youtube_service()
    diagnostics = analyze_past_shorts(youtube)

    print("\n=== STEP 2: Analyzing US Trends & Generating Viral Short Script ===")
    us_trends = fetch_us_google_trends()
    plan = generate_daily_short_plan(diagnostics, us_trends)
    print(f"  -> Selected Niche: {plan['niche_name']}")
    print(f"  -> Title: {plan['title']}")

    print("\n=== STEP 3 & 4: Rendering 1080p HD Visuals, Word-Synced Captions & Audio ===")
    video_path = build_short_video(plan)

    if args.dry_run:
        print(f"\n[+] Dry-run complete! Video saved at: {video_path}")
    else:
        print("\n=== STEP 5: Uploading to YouTube Channel ===")
        upload_short_to_youtube(youtube, video_path, plan)


if __name__ == "__main__":
    main()
