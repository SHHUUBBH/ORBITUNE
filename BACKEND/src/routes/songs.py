from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, File

from models import (
    Song,
    SongsResponse,
    CreateFromYouTubeRequest,
    YouTubeSearchResponse,
    PlaybackPositionRequest,
    PlaybackPositionResponse,
)
from services.songs_service import (
    list_songs,
    create_song_from_youtube,
    create_song_from_upload,
    search_songs,
    save_playback_position,
    get_playback_position,
)

router = APIRouter(tags=["songs"])


# ---------------------------------------------------------------------------
# Playback position endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/songs/{song_id}/playback-position",
    response_model=PlaybackPositionResponse,
)
def get_position(song_id: str):
    """Return the last saved playback position for a song."""
    pos = get_playback_position(song_id)
    if pos is None:
        raise HTTPException(status_code=404, detail="No saved position")
    return PlaybackPositionResponse(
        songId=song_id,
        position=pos["position"],
        savedAt=pos["savedAt"],
    )


@router.post(
    "/songs/{song_id}/playback-position",
    response_model=PlaybackPositionResponse,
)
def save_position(song_id: str, body: PlaybackPositionRequest):
    """Persist a playback position for a song (used for resume and tracking)."""
    ts = datetime.now(timezone.utc).isoformat()
    save_playback_position(song_id, body.position, ts)
    return PlaybackPositionResponse(
        songId=song_id,
        position=body.position,
        savedAt=ts,
    )



@router.get("/songs", response_model=SongsResponse)
def get_songs() -> SongsResponse:
    songs = list_songs()
    return SongsResponse(songs=songs)


@router.get("/youtube/search", response_model=YouTubeSearchResponse)
def youtube_search(query: str) -> YouTubeSearchResponse:
    results = search_songs(query=query)
    return YouTubeSearchResponse(results=results)


@router.post("/songs/from-youtube", response_model=Song)
def post_song_from_youtube(payload: CreateFromYouTubeRequest) -> Song:
    if not payload.youtubeUrl and not payload.query:
        raise HTTPException(status_code=400, detail="Provide query or youtubeUrl")

    try:
        song = create_song_from_youtube(query=payload.query, youtube_url=payload.youtubeUrl)
        return song
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to process song") from exc


@router.post("/songs/upload", response_model=Song)
async def upload_song(file: UploadFile = File(...)):
    """Upload an audio file (MP3, WAV, etc.) and extract metadata automatically."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed = {".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"}
    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if f".{ext}" not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {', '.join(allowed)}")

    try:
        file_bytes = await file.read()
        if len(file_bytes) > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(status_code=400, detail="File too large (max 100MB)")
        song = create_song_from_upload(file_bytes=file_bytes, filename=file.filename)
        return song
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process upload: {exc}") from exc
