"""Supabase cloud storage utility for ORBITUNE."""

import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
SUPABASE_BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "orbitune-audio")

# Initialize Supabase client
_supabase: Optional[Client] = None


def _get_client() -> Client:
    """Get or create Supabase client singleton."""
    global _supabase
    if _supabase is None:
        _supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _supabase


def upload_audio_file(local_file_path: str, song_id: str) -> str:
    """
    Upload a local audio file to Supabase bucket and return the public URL.

    Args:
        local_file_path: Path to the local audio file
        song_id: Unique identifier for the song (used as the object name)

    Returns:
        Public URL of the uploaded file

    Raises:
        Exception: If upload fails
    """
    client = _get_client()
    file_path = Path(local_file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Local file not found: {local_file_path}")

    object_name = f"{song_id}/orbitune_3d_professional.wav"

    try:
        with open(file_path, "rb") as f:
            client.storage.from_(SUPABASE_BUCKET_NAME).upload(
                object_name,
                f,
                file_options={"content-type": "audio/mpeg"},
            )

        public_url = client.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(object_name)
        return public_url

    except Exception as e:
        raise RuntimeError(f"Failed to upload to Supabase: {e}") from e

    finally:
        # Always clean up local file to prevent memory leaks
        try:
            if file_path.exists():
                os.remove(file_path)
        except OSError:
            pass  # Ignore cleanup errors


def delete_audio_file(song_id: str) -> bool:
    """
    Delete an audio file from Supabase bucket.

    Args:
        song_id: Unique identifier for the song

    Returns:
        True if deletion was successful, False otherwise
    """
    client = _get_client()
    object_name = f"{song_id}/orbitune_3d_professional.mp3"

    try:
        client.storage.from_(SUPABASE_BUCKET_NAME).remove([object_name])
        return True
    except Exception:
        return False


def insert_song_metadata(
    song_id: str,
    title: str,
    artist: str,
    audio_url: str,
    image_url: str,
    album: Optional[str] = None,
    duration: int = 0,
    genre: Optional[str] = None,
    release_year: Optional[int] = None,
) -> bool:
    """
    Insert song metadata into Supabase database table.

    Args:
        song_id: Unique identifier for the song
        title: Song title
        artist: Artist name
        audio_url: Public Supabase storage URL for audio
        image_url: Public Supabase storage URL for thumbnail
        album: Album name (optional)
        duration: Duration in seconds (optional)
        genre: Genre (optional)
        release_year: Release year (optional)

    Returns:
        True if insertion was successful, False otherwise
    """
    client = _get_client()

    try:
        now = datetime.utcnow().isoformat()
        data = {
            "id": song_id,
            "title": title,
            "artist": artist,
            "album": album,
            "duration": duration,
            "audio_url": audio_url,
            "image_url": image_url,
            "genre": genre,
            "release_year": release_year,
            "created_at": now,
            "updated_at": now,
        }

        # Use upsert to handle both insert and update
        client.table("songs").upsert(data, on_conflict="id").execute()
        return True

    except Exception as e:
        print(f"[Supabase] Failed to insert song metadata: {e}")
        return False


def fetch_all_songs() -> list:
    """
    Fetch all songs from Supabase database, ordered by newest first.

    Returns:
        List of song dictionaries
    """
    client = _get_client()

    try:
        response = client.table("songs") \
            .select("*") \
            .order("created_at", desc=True) \
            .execute()

        return response.data or []

    except Exception as e:
        print(f"[Supabase] Failed to fetch songs: {e}")
        return []


def upload_thumbnail_bytes(image_bytes: bytes, song_id: str) -> str:
    """
    Upload thumbnail image bytes to Supabase bucket and return public URL.

    Args:
        image_bytes: Raw image bytes (JPEG/PNG)
        song_id: Unique identifier for the song

    Returns:
        Public URL of the uploaded thumbnail
    """
    client = _get_client()
    object_name = f"{song_id}/thumbnail.jpg"

    try:
        client.storage.from_(SUPABASE_BUCKET_NAME).upload(
            object_name,
            image_bytes,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
        public_url = client.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(object_name)
        return public_url
    except Exception as e:
        print(f"[Supabase] Failed to upload thumbnail: {e}")
        return ""


def upload_audio_bytes(audio_bytes: bytes, song_id: str, content_type: str = "audio/mpeg") -> str:
    """
    Upload audio bytes to Supabase bucket and return public URL.

    Args:
        audio_bytes: Raw audio file bytes
        song_id: Unique identifier for the song
        content_type: MIME type of the audio

    Returns:
        Public URL of the uploaded audio
    """
    client = _get_client()
    object_name = f"{song_id}/orbitune_3d_professional.wav"

    try:
        client.storage.from_(SUPABASE_BUCKET_NAME).upload(
            object_name,
            audio_bytes,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        public_url = client.storage.from_(SUPABASE_BUCKET_NAME).get_public_url(object_name)
        return public_url
    except Exception as e:
        print(f"[Supabase] Failed to upload audio: {e}")
        return ""