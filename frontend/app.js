const artistsEl = document.getElementById("artists");
const albumsEl = document.getElementById("albums");
const tracksEl = document.getElementById("tracks");
const searchEl = document.getElementById("search");
const promptEl = document.getElementById("prompt");
const generateBtn = document.getElementById("generateBtn");
const audioEl = document.getElementById("audio");
const nowPlayingEl = document.getElementById("nowPlaying");

let artists = [];

async function api(path) {
  const res = await fetch(path);
  return res.json();
}

async function postJson(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return res.json();
}

function renderArtists(list) {
  artistsEl.innerHTML = "";
  list.forEach((a) => {
    const li = document.createElement("li");
    li.className = "item";
    li.textContent = a.name;
    li.onclick = async () => {
      const albums = await api(`/api/artists/${a.id}/albums`);
      renderAlbums(albums);
      tracksEl.innerHTML = "";
    };
    artistsEl.appendChild(li);
  });
}

function renderAlbums(list) {
  albumsEl.innerHTML = "";
  list.forEach((al) => {
    const div = document.createElement("div");
    div.className = "card";
    div.onclick = async () => {
      const tracks = await api(`/api/albums/${al.id}/tracks`);
      renderTracks(tracks);
    };

    const img = document.createElement("img");
    img.src = `/media/${al.cover_path}`;

    div.appendChild(img);
    albumsEl.appendChild(div);
  });
}

function renderTracks(list) {
  tracksEl.innerHTML = "";
  list.forEach((t) => {
    const li = document.createElement("li");
    li.className = "item";
    li.textContent = t.title;
    li.onclick = () => {
      audioEl.src = `/media/${t.audio_path}`;
      audioEl.play();
      nowPlayingEl.textContent = `Now playing: ${t.title}`;
    };
    tracksEl.appendChild(li);
  });
}

searchEl.addEventListener("input", () => {
  const q = searchEl.value.toLowerCase();
  renderArtists(artists.filter((a) => a.name.toLowerCase().includes(q)));
});

generateBtn.addEventListener("click", async () => {
  if (!promptEl.value.trim()) return alert("Enter a prompt first");
  generateBtn.disabled = true;
  generateBtn.textContent = "Generating...";
  await postJson("/api/generate", { prompt: promptEl.value });
  artists = await api("/api/artists");
  renderArtists(artists);
  generateBtn.disabled = false;
  generateBtn.textContent = "Generate";
});

async function load() {
  artists = await api("/api/artists");
  renderArtists(artists);
}

load();
