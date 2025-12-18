from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from ai_generate import generate_artist_pack


from db import init_db, get_conn

BASE_DIR = Path(__file__).parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"
MEDIA_DIR = BASE_DIR / "media"

app = FastAPI(title="Fake Spotify API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/artists")
def list_artists():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, bio, genres, image_path FROM artists ORDER BY id DESC"
        ).fetchall()
    return [dict(r) for r in rows]

@app.get("/api/artists/{artist_id}/albums")
def list_albums(artist_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, artist_id, title, year, cover_path
            FROM albums
            WHERE artist_id = ?
            ORDER BY id DESC
            """,
            (artist_id,),
        ).fetchall()
    return [dict(r) for r in rows]

@app.get("/api/albums/{album_id}/tracks")
def list_tracks(album_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, album_id, title, duration_sec, audio_path, popularity
            FROM tracks
            WHERE album_id = ?
            ORDER BY id ASC
            """,
            (album_id,),
        ).fetchall()
    return [dict(r) for r in rows]

# media (covers/audio)
MEDIA_DIR.mkdir(exist_ok=True)
(MEDIA_DIR / "covers").mkdir(exist_ok=True)
(MEDIA_DIR / "audio").mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory=str(MEDIA_DIR)), name="media")

# serve frontend
@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/api/generate")
def generate(req: GenerateRequest):
    pack = generate_artist_pack(req.prompt)

    # reuse existing assets (simple): cover1/2 + preview1/2/3
    cover = "covers/cover1.jpg"
    audio_choices = ["audio/preview1.mp3", "audio/preview2.mp3", "audio/preview3.mp3"]

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO artists (name, bio, genres, image_path) VALUES (?, ?, ?, ?)",
            (
                pack["artist"]["name"],
                pack["artist"]["bio"],
                pack["artist"]["genres"],
                None,
            ),
        )
        artist_id = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO albums (artist_id, title, year, cover_path) VALUES (?, ?, ?, ?)",
            (
                artist_id,
                pack["album"]["title"],
                int(pack["album"]["year"]),
                cover,
            ),
        )
        album_id = cur.lastrowid

        for i, t in enumerate(pack["tracks"]):
            conn.execute(
                "INSERT INTO tracks (album_id, title, duration_sec, audio_path, popularity) VALUES (?, ?, ?, ?, ?)",
                (
                    album_id,
                    t["title"],
                    int(t["duration_sec"]),
                    audio_choices[i % len(audio_choices)],
                    50,
                ),
            )

    return {"artist_id": artist_id, "album_id": album_id, "pack": pack}
