import json
import random
from typing import Any, Dict

from openai import OpenAI

client = OpenAI()

def _fallback_pack(prompt: str) -> Dict[str, Any]:
    # If the AI call fails, we still return something usable.
    return {
        "artist": {
            "name": f"{random.choice(['Neon','Velvet','Solar','Echo'])} {random.choice(['Runners','Bloom','District','Static'])}",
            "bio": f"Generated from prompt: {prompt}. A fictional artist for the Fake Spotify project.",
            "genres": "electronic, indie"
        },
        "album": {
            "title": random.choice(["Soft Machines", "Midnight Sketches", "Glass Signals"]),
            "year": 2024
        },
        "tracks": [
            {"title": "First Light", "duration_sec": 198},
            {"title": "Side Street", "duration_sec": 212},
            {"title": "After Hours", "duration_sec": 187},
            {"title": "Satellite Heart", "duration_sec": 205},
            {"title": "Blue Noise", "duration_sec": 193},
        ],
    }

def generate_artist_pack(prompt: str) -> Dict[str, Any]:
    system = (
        "You generate fictional music catalog data for a school project. "
        "Return ONLY valid JSON that matches the schema exactly. No markdown."
    )

    user = f"""
Create ONE fictional music artist pack from this prompt: "{prompt}"

Return JSON with this schema:
{{
  "artist": {{
    "name": "string",
    "bio": "string (1-2 sentences)",
    "genres": "comma-separated string"
  }},
  "album": {{
    "title": "string",
    "year": integer (between 1990 and 2025)
  }},
  "tracks": [
    {{ "title": "string", "duration_sec": integer (120-260) }},
    ... exactly 6 tracks total
  ]
}}

Rules:
- Make names unique-ish and believable.
- No real artists.
- No profanity.
- JSON only.
""".strip()

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.9,
        )
        content = resp.choices[0].message.content.strip()

        data = json.loads(content)  # will throw if not valid JSON

        # light validation
        assert "artist" in data and "album" in data and "tracks" in data
        assert isinstance(data["tracks"], list) and len(data["tracks"]) == 6
        return data
    except Exception:
        return _fallback_pack(prompt)
