from db import init_db, get_conn

def main():
    init_db()

    # wipe existing data (so you can re-run seed safely)
    with get_conn() as conn:
        conn.execute("DELETE FROM tracks")
        conn.execute("DELETE FROM albums")
        conn.execute("DELETE FROM artists")

        # --- Artist 1
        cur = conn.execute(
            "INSERT INTO artists (name, bio, genres, image_path) VALUES (?, ?, ?, ?)",
            (
                "Neon Drift",
                "A late-night synthwave project with glossy hooks and retro-futuristic vibes.",
                "synthwave, electronic, retro",
                None,
            ),
        )
        artist1_id = cur.lastrowid

        cur = conn.execute(
            "INSERT INTO albums (artist_id, title, year, cover_path) VALUES (?, ?, ?, ?)",
            (artist1_id, "Midnight Signals", 2024, "covers/cover1.jpg"),
        )
        album1_id = cur.lastrowid

        tracks1 = [
            ("Streetlights", 198, "audio/preview1.mp3", 72),
            ("Afterimage", 214, "audio/preview2.mp3", 65),
            ("VHS Dreams", 187, "audio/preview3.mp3", 80),
            ("Night Drive", 205, "audio/preview1.mp3", 77),
            ("Static Hearts", 192, "audio/preview2.mp3", 61),
            ("Glowline", 176, "audio/preview3.mp3", 70),
        ]
        for title, dur, audio, pop in tracks1:
            conn.execute(
                "INSERT INTO tracks (album_id, title, duration_sec, audio_path, popularity) VALUES (?, ?, ?, ?, ?)",
                (album1_id, title, dur, audio, pop),
            )

