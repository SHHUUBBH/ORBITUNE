"""Song service for ORBITUNE backend.

Handles:
- JSON persistence in BACKEND/data/songs.json
- Invoking the full AI-ML pipeline (download → separate → 3D process)
- Mapping metadata to API models
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import List, Optional, Tuple

from pydantic import ValidationError

from models import Song, YouTubeSearchResult

# Resolve paths
THIS_FILE = Path(__file__).resolve()
SERVICES_DIR = THIS_FILE.parent
BACKEND_DIR = SERVICES_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ML_DIR = PROJECT_ROOT / "AI-ML"
DATA_DIR = BACKEND_DIR / "data"
SONGS_JSON_PATH = DATA_DIR / "songs.json"

import sys

if str(AI_ML_DIR) not in sys.path:
    sys.path.append(str(AI_ML_DIR))

# Import AI-ML config + pipeline pieces
import config  # type: ignore
from audio_processor.youtube_downloader import YouTubeDownloader  # type: ignore
from audio_processor.source_separator import SourceSeparator  # type: ignore
from audio_processor.orbitune_final import ORBITUNE_Professional  # type: ignore


_json_lock = Lock()
_separator: Optional[SourceSeparator] = None
_processor: Optional[ORBITUNE_Professional] = None
_downloader: Optional[YouTubeDownloader] = None


def _ensure_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SONGS_JSON_PATH.exists():
        SONGS_JSON_PATH.write_text(
            json.dumps({"songs": [], "lastId": 0, "processingQueue": []}, indent=2),
            encoding="utf-8",
        )


def _load_songs_raw() -> dict:
    _ensure_files()
    with SONGS_JSON_PATH.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # Reset corrupt file
            return {"songs": [], "lastId": 0, "processingQueue": []}


def _save_songs_raw(payload: dict) -> None:
    _ensure_files()
    with SONGS_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _get_base_url() -> str:
    host = getattr(config, "API_HOST", "127.0.0.1")
    port = getattr(config, "API_PORT", 8000)
    return f"http://{host}:{port}"


def list_songs() -> List[Song]:
    """Return all songs from songs.json as Song models.

    If audioUrl/thumbnail are missing in stored data, compute them
    from config paths and API host/port.
    """

    with _json_lock:
        data = _load_songs_raw()

    base_url = _get_base_url()
    songs_out: List[Song] = []

    for item in data.get("songs", []):
        # Backfill URLs if absent
        song_id = item.get("id") or item.get("song_id")
        if not song_id:
            continue

        audio_url = item.get("audioUrl") or f"{base_url}/media/spatial/{song_id}/orbitune_3d_professional.wav"
        thumb_url = item.get("thumbnail") or f"{base_url}/media/thumbnails/{song_id}.jpg"

        merged = {
            "id": song_id,
            "title": item.get("title", "Unknown"),
            "artist": item.get("artist", "Unknown"),
            "album": item.get("album", "YouTube"),
            "duration": int(item.get("duration", 0) or 0),
            "thumbnail": thumb_url,
            "audioUrl": audio_url,
            "genre": item.get("genre"),
            "releaseYear": item.get("releaseYear"),
        }

        try:
            songs_out.append(Song(**merged))
        except ValidationError:
            # Skip invalid entries rather than crashing the API
            continue

    return songs_out



def _get_existing_song(song_id: str) -> Optional[Song]:
    """Return existing Song by id if present in songs.json.

    This reuses :func:`list_songs` so URLs and defaults are consistent
    with the public listing endpoint.
    """

    for song in list_songs():
        if song.id == song_id:
            return song
    return None


def _song_outputs_exist(song_id: str) -> bool:
    """Check whether core processed files exist for a given song.

    We consider a song "processed" only if the final 3D audio file and
    its metadata JSON are both present on disk.
    """

    spatial_path = config.STORAGE_DIR / "spatial" / song_id / "orbitune_3d_professional.wav"
    metadata_path = config.get_metadata_path(song_id)

    return spatial_path.is_file() and metadata_path.is_file()


def search_songs(query: str) -> List[YouTubeSearchResult]:
    downloader = _get_downloader()
    raw_results = downloader.search(query=query)

    results: List[YouTubeSearchResult] = []
    for item in raw_results:
        try:
            result = YouTubeSearchResult(
                songId=item["song_id"],
                videoId=item["video_id"],
                title=item.get("title", "Unknown"),
                artist=item.get("channel", "Unknown"),
                duration=int(item.get("duration", 0) or 0),
                durationString=item.get("duration_string", ""),
                thumbnail=item.get("thumbnail", ""),
            )
            results.append(result)
        except Exception:
            continue

    return results


def _get_downloader() -> YouTubeDownloader:
    global _downloader
    if _downloader is None:
        _downloader = YouTubeDownloader()
    return _downloader


def _get_separator() -> SourceSeparator:
    global _separator
    if _separator is None:
        _separator = SourceSeparator()
    return _separator


def _get_processor() -> ORBITUNE_Professional:
    global _processor
    if _processor is None:
        _processor = ORBITUNE_Professional(device=config.DEVICE)
    return _processor


def _extract_video_id(youtube_url: str) -> Optional[str]:
    """Extract YouTube video ID from common URL formats."""

    # Short youtu.be link
    match = re.search(r"youtu\.be/([\w-]{6,})", youtube_url)
    if match:
        return match.group(1)

    # Full watch URL
    match = re.search(r"v=([\w-]{6,})", youtube_url)
    if match:
        return match.group(1)

    return None


def create_song_from_youtube(*, query: Optional[str], youtube_url: Optional[str]) -> Song:
    """Run full pipeline for a YouTube query/URL and persist song metadata.

    Steps:
    - Determine video_id from URL or by searching query
    - Download highest quality audio + metadata
    - Separate into stems
    - Generate 3D spatial audio
    - Store/update song entry in songs.json
    - Return Song model for the new/updated song
    """

    if not query and not youtube_url:
        raise ValueError("Provide either query or youtubeUrl")

    downloader = _get_downloader()

    # 1) Determine video_id and initial metadata / song_id
    if youtube_url:
        video_id = _extract_video_id(youtube_url)
        if not video_id:
            raise ValueError("Could not extract video ID from YouTube URL")
        search_meta = None
        # Deterministic song_id from video_id
        song_id = downloader.generate_song_id(video_id)
    else:
        results = downloader.search(query=query or "")
        if not results:
            raise ValueError("No YouTube results found for query")
        first = results[0]
        video_id = first["video_id"]
        search_meta = first
        # Prefer song_id provided by search, fall back to generator
        song_id = first.get("song_id") or downloader.generate_song_id(video_id)

    # 1b) Fast path: if song already processed, reuse it instead of re-running pipeline
    if song_id:
        cached = _get_existing_song(song_id)
        if cached and _song_outputs_exist(song_id):
            return cached

    # 2) Download audio + metadata
    meta = downloader.download(video_id)
    if meta is None:
        raise RuntimeError("Download failed")

    # Ensure song_id matches downloader metadata
    song_id = meta["song_id"]

    # 3) Separate stems
    separator = _get_separator()
    sep_out = separator.separate(song_id)
    if sep_out is None:
        raise RuntimeError("Source separation failed")

    # 4) Process 3D audio
    processor = _get_processor()
    output_path = processor.process_song(song_id)

    # 5) Build song record
    base_url = _get_base_url()
    audio_url = f"{base_url}/media/spatial/{song_id}/orbitune_3d_professional.wav"
    thumb_url = f"{base_url}/media/thumbnails/{song_id}.jpg"

    # Prefer AI-ML metadata.json, but fall back to search metadata
    title = meta.get("title") or (search_meta or {}).get("title", "Unknown")
    artist = meta.get("artist") or (search_meta or {}).get("channel", "Unknown")
    album = meta.get("album") or title
    duration = int(meta.get("duration", 0) or 0)

    year: Optional[int] = None
    upload_date = meta.get("upload_date")
    if upload_date and len(upload_date) >= 4:
        try:
            year = int(upload_date[:4])
        except ValueError:
            year = None

    song_model = Song(
        id=song_id,
        title=title,
        artist=artist,
        album=album,
        duration=duration,
        thumbnail=thumb_url,
        audioUrl=audio_url,
        genre=None,
        releaseYear=year,
    )

    # 6) Persist into songs.json
    with _json_lock:
        data = _load_songs_raw()
        songs = data.get("songs", [])

        # Upsert by id
        updated = False
        for idx, item in enumerate(songs):
            if (item.get("id") or item.get("song_id")) == song_id:
                songs[idx] = {
                    **item,
                    "id": song_model.id,
                    "title": song_model.title,
                    "artist": song_model.artist,
                    "album": song_model.album,
                    "duration": song_model.duration,
                    "thumbnail": song_model.thumbnail,
                    "audioUrl": song_model.audioUrl,
                    "genre": song_model.genre,
                    "releaseYear": song_model.releaseYear,
                    "updatedAt": datetime.utcnow().isoformat(),
                }
                updated = True
                break

        if not updated:
            songs.append(
                {
                    "id": song_model.id,
                    "title": song_model.title,
                    "artist": song_model.artist,
                    "album": song_model.album,
                    "duration": song_model.duration,
                    "thumbnail": song_model.thumbnail,
                    "audioUrl": song_model.audioUrl,
                    "genre": song_model.genre,
                    "releaseYear": song_model.releaseYear,
                    "createdAt": datetime.utcnow().isoformat(),
                    "updatedAt": datetime.utcnow().isoformat(),
                }
            )

        data["songs"] = songs
        _save_songs_raw(data)

    return song_model
