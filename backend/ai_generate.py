import json
import os
import re
from pathlib import Path
from typing import Any, Dict
import random
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, NotFound


# Force-load backend/.env
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found.")

genai.configure(api_key=GEMINI_API_KEY)


def _extract_json(text: str) -> Dict[str, Any]:
    """
    Gemini sometimes returns JSON wrapped in ```json fences.
    This tries hard to extract the JSON object.
    """
    text = text.strip()

    # Remove ```json ... ``` fences if present
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if fence_match:
        text = fence_match.group(1).strip()

    # If still not pure JSON, attempt to find first {...} block
    if not text.startswith("{"):
        brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(1).strip()

    return json.loads(text)


def generate_artist_pack(prompt: str):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

        instructions = f"""
Return ONLY valid JSON (no markdown, no commentary).

Create ONE fictional music artist pack from this prompt: "{prompt}"

Schema:
{{
  "artist": {{
    "name": "string",
    "bio": "string (1-2 sentences)",
    "genres": "comma-separated string"
  }},
  "album": {{
    "title": "string",
    "year": integer (1990-2025)
  }},
  "tracks": [
    {{ "title": "string", "duration_sec": integer (120-260) }}
  ]
}}

Rules:
- Exactly 6 tracks
- No real artists
- JSON only
""".strip()

        resp = model.generate_content(
            instructions,
            generation_config={"temperature": 0.9},
        )

        data = _extract_json(resp.text)

        if "tracks" not in data or not isinstance(data["tracks"], list) or len(data["tracks"]) != 6:
            raise ValueError("Bad model output")

        return data

    except (ResourceExhausted, NotFound, ValueError):
        return fallback_pack(prompt)

def fallback_pack(prompt: str):
    vibes = ["dreamy", "gritty", "uplifting", "moody", "glitchy", "sunlit"]
    genres = ["indie pop", "synthwave", "lo-fi", "hip-hop", "house", "alt rock"]
    artist = f"{random.choice(['Neon','Solar','Velvet','Echo','Paper','Midnight'])} {random.choice(['Bloom','Runners','Static','Avenue','Garden','District'])}"
    album = f"{random.choice(vibes).title()} {random.choice(['Signals','Sketches','Rooms','Stories','Lines','Days'])}"
    tracks = [
        {"title": f"{random.choice(['First','After','Side','Glass','Late','Blue'])} {random.choice(['Light','Hours','Street','Noise','Dream','Reply'])}",
         "duration_sec": random.randint(120, 260)}
        for _ in range(6)
    ]
    return {
        "artist": {"name": artist, "bio": f"Generated from prompt: {prompt}.", "genres": f"{random.choice(genres)}, {random.choice(genres)}"},
        "album": {"title": album, "year": random.randint(1990, 2025)},
        "tracks": tracks
    }

