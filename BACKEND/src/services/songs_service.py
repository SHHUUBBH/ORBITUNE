"""Song service for ORBITUNE backend.

Handles:
- Supabase database persistence for song metadata
- Invoking the full AI-ML pipeline (download → separate → 3D process)
- Mapping metadata to API models
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import List, Optional

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

# Import AI-ML config (lightweight)
import config  # type: ignore

# Lazy imports: heavy ML modules (torch/demucs) loaded only when needed
YouTubeDownloader = None
SourceSeparator = None
ORBITUNE_Professional = None

# Import Supabase storage utility
from services.storage import upload_audio_file, insert_song_metadata, fetch_all_songs, _get_client, upload_thumbnail_bytes


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
    """Return all songs from Supabase database as Song models.

    Fetches from Supabase songs table ordered by newest first.
    """

    # Fetch from Supabase database
    db_songs = fetch_all_songs()

    songs_out: List[Song] = []

    for item in db_songs:
        song_id = item.get("id")
        if not song_id:
            continue

        audio_url = item.get("audio_url")
        thumb_url = item.get("image_url")

        if not audio_url:
            continue

        merged = {
            "id": song_id,
            "title": item.get("title", "Unknown"),
            "artist": item.get("artist", "Unknown"),
            "album": item.get("album", "YouTube"),
            "duration": int(item.get("duration", 0) or 0),
            "thumbnail": thumb_url,
            "audioUrl": audio_url,
            "genre": item.get("genre"),
            "releaseYear": item.get("release_year"),
        }

        try:
            songs_out.append(Song(**merged))
        except ValidationError:
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
    """Check whether song has been processed and stored in database.

    We consider a song "processed" if it exists in Supabase songs table with an audio_url.
    """
    try:
        client = _get_client()
        response = client.table("songs").select("audio_url").eq("id", song_id).execute()
        return bool(response.data and response.data[0].get("audio_url"))
    except Exception:
        return False


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


def _get_downloader():
    global _downloader, YouTubeDownloader
    if _downloader is None:
        if YouTubeDownloader is None:
            from audio_processor.youtube_downloader import YouTubeDownloader as YD  # type: ignore
            YouTubeDownloader = YD
        _downloader = YouTubeDownloader()
    return _downloader


def _get_separator():
    global _separator, SourceSeparator
    if _separator is None:
        if SourceSeparator is None:
            from audio_processor.source_separator import SourceSeparator as SS  # type: ignore
            SourceSeparator = SS
        _separator = SourceSeparator()
    return _separator


def _get_processor():
    global _processor, ORBITUNE_Professional
    if _processor is None:
        if ORBITUNE_Professional is None:
            from audio_processor.orbitune_final import ORBITUNE_Professional as OP  # type: ignore
            ORBITUNE_Professional = OP
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

    # 5) Compress WAV to MP3 (avoid 50MB Supabase limit) then upload
    import subprocess
    mp3_path = output_path.replace('.wav', '.mp3')
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', output_path,
            '-codec:a', 'libmp3lame', '-b:a', '320k',
            mp3_path
        ], check=True, capture_output=True)
        audio_url = upload_audio_file(mp3_path, song_id)
    finally:
        # Clean up local files
        for p in (output_path, mp3_path):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except OSError:
                pass
    # Use the thumbnail from the downloader metadata (YouTube thumbnail URL)
    # Fall back to Supabase path if available
    thumb_url = meta.get("thumbnail", "")
    if not thumb_url:
        thumb_url = ""

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

    # 6) Persist metadata into Supabase database
    insert_song_metadata(
        song_id=song_id,
        title=title,
        artist=artist,
        audio_url=audio_url,
        image_url=thumb_url,
        album=album,
        duration=duration,
        genre=None,
        release_year=year,
    )

    # Also keep local JSON for backward compatibility
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


# ---------------------------------------------------------------------------
# Playback position persistence
# ---------------------------------------------------------------------------

_POSITIONS_PATH = DATA_DIR / "playback_positions.json"
_positions_lock = Lock()


def _ensure_positions_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _POSITIONS_PATH.exists():
        _POSITIONS_PATH.write_text("{}", encoding="utf-8")


def _load_positions() -> dict:
    _ensure_positions_file()
    with _positions_lock:
        with _POSITIONS_PATH.open("r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}


def _save_positions(data: dict) -> None:
    _ensure_positions_file()
    with _positions_lock:
        with _POSITIONS_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def save_playback_position(song_id: str, position: float, saved_at: str) -> None:
    """Persist a playback position for a song."""
    data = _load_positions()
    data[song_id] = {"position": position, "savedAt": saved_at}
    _save_positions(data)


def get_playback_position(song_id: str) -> Optional[dict]:
    """Return the saved playback position dict or None."""
    data = _load_positions()
    return data.get(song_id)


# ---------------------------------------------------------------------------
# File upload: extract ID3 tags and store in Supabase
# ---------------------------------------------------------------------------

def create_song_from_upload(file_bytes: bytes, filename: str) -> Song:
    """Process an uploaded audio file: extract metadata, upload to Supabase, persist.

    Steps:
    - Generate a unique song_id from filename + content hash
    - Extract ID3 tags (title, artist, album, year, album art) using mutagen
    - Upload audio file to Supabase
    - Upload album art thumbnail to Supabase (if found)
    - Insert metadata into Supabase database
    - Return Song model
    """
    import hashlib
    import io

    # Generate song_id from content hash
    content_hash = hashlib.md5(file_bytes).hexdigest()[:12]
    song_id = content_hash

    # Extract metadata from ID3 tags
    title, artist, album, year, album_art = _extract_id3_tags(file_bytes, filename)

    # Upload audio to Supabase
    ext = Path(filename).suffix.lower().lstrip(".")
    content_type_map = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "m4a": "audio/mp4",
        "aac": "audio/mp4",
    }
    content_type = content_type_map.get(ext, "audio/mpeg")
    audio_url = upload_audio_bytes(file_bytes, song_id, content_type)

    # Upload thumbnail if we extracted album art
    thumb_url = ""
    if album_art:
        thumb_url = upload_thumbnail_bytes(album_art, song_id)

    # If no album art, use a placeholder
    if not thumb_url:
        thumb_url = ""

    # Get duration estimate (file size / bitrate approximation)
    duration = len(file_bytes) // 16000  # rough estimate for MP3

    # Persist to Supabase database
    insert_song_metadata(
        song_id=song_id,
        title=title,
        artist=artist,
        audio_url=audio_url,
        image_url=thumb_url,
        album=album,
        duration=duration,
        genre=None,
        release_year=year,
    )

    song_model = Song(
        id=song_id,
        title=title,
        artist=artist,
        album=album,
        duration=duration,
        thumbnail=thumb_url if thumb_url else None,
        audioUrl=audio_url,
        genre=None,
        releaseYear=year,
    )

    print(f"[UPLOAD] Song created: {title} by {artist} (id={song_id})")
    return song_model


def _extract_id3_tags(file_bytes: bytes, filename: str):
    """Extract metadata from audio file ID3 tags using mutagen.

    Returns:
        (title, artist, album, year, album_art_bytes)
    """
    title = Path(filename).stem
    artist = "Unknown Artist"
    album = "Unknown Album"
    year = None
    album_art = None

    try:
        from mutagen.mp3 import MP3
        from mutagen.mp4 import MP4
        from mutagen.oggvorbis import OggVorbis
        from mutagen.flac import FLAC

        ext = Path(filename).suffix.lower()
        audio_file = io.BytesIO(file_bytes)

        tags = None
        if ext == ".mp3":
            audio = MP3(audio_file)
            tags = audio.tags
        elif ext in (".m4a", ".aac"):
            audio = MP4(audio_file)
            tags = audio.tags
        elif ext == ".ogg":
            audio = OggVorbis(audio_file)
            tags = audio.tags
        elif ext == ".flac":
            audio = FLAC(audio_file)
            tags = audio.tags
        else:
            # Try MP3 as fallback
            audio_file.seek(0)
            audio = MP3(audio_file)
            tags = audio.tags

        if tags is None:
            print(f"[UPLOAD] No tags found in {filename}")
            return title, artist, album, year, album_art

        # Extract text tags (MP3/ID3v2)
        if ext == ".mp3":
            title = str(tags.get("TIT2", [title]))
            artist = str(tags.get("TPE1", [artist]))
            album = str(tags.get("TALB", [album]))
            year_str = str(tags.get("TDRC", tags.get("TYE", [""])))
            if year_str and year_str.isdigit():
                year = int(year_str)
            # Album art
            if "APIC:" in tags:
                album_art = tags["APIC:"].data

        # Extract text tags (MP4/iTunes)
        elif ext in (".m4a", ".aac"):
            title = str(tags.get("\xa9nam", [title])) if "\xa9nam" in tags else title
            artist = str(tags.get("\xa9ART", [artist])) if "\xa9ART" in tags else artist
            album = str(tags.get("\xa9alb", [album])) if "\xa9alb" in tags else album
            year_str = str(tags.get("\xa9day", [""])) if "\xa9day" in tags else ""
            if year_str and year_str.isdigit():
                year = int(year_str)
            # Album art (covr atom)
            if "covr" in tags:
                album_art = tags["covr"][0]

        # Extract text tags (OGG Vorbis)
        elif ext == ".ogg":
            title = str(tags.get("title", [title])) if "title" in tags else title
            artist = str(tags.get("artist", [artist])) if "artist" in tags else artist
            album = str(tags.get("album", [album])) if "album" in tags else album
            year_str = str(tags.get("date", [""])) if "date" in tags else ""
            if year_str and year_str.isdigit():
                year = int(year_str)
            if "metadata_block_picture" in tags:
                try:
                    from mutagen.flac import Picture
                    import base64
                    pic_data = base64.b64decode(tags["metadata_block_picture"][0])
                    pic = Picture()
                    pic.parse(pic_data)
                    album_art = pic.data
                except Exception:
                    pass

        # FLAC
        elif ext == ".flac":
            title = str(tags.get("title", [title])) if "title" in tags else title
            artist = str(tags.get("artist", [artist])) if "artist" in tags else artist
            album = str(tags.get("album", [album])) if "album" in tags else album
            year_str = str(tags.get("date", [""])) if "date" in tags else ""
            if year_str and year_str.isdigit():
                year = int(year_str)
            if tags.pictures:
                album_art = tags.pictures[0].data

        # Clean up extracted values
        if title and title.startswith("["):
            title = Path(filename).stem
        if artist and artist.startswith("["):
            artist = "Unknown Artist"
        if album and album.startswith("["):
            album = "Unknown Album"

        print(f"[UPLOAD] Extracted tags: title={title}, artist={artist}, album={album}, year={year}, has_art={album_art is not None}")

    except ImportError:
        print("[UPLOAD] mutagen not installed, using filename as title")
    except Exception as e:
        print(f"[UPLOAD] Error extracting tags: {e}")

    return title, artist, album, year, album_art
