from fastapi import APIRouter, HTTPException

from models import Song, SongsResponse, CreateFromYouTubeRequest, YouTubeSearchResponse
from services.songs_service import list_songs, create_song_from_youtube, search_songs

router = APIRouter(tags=["songs"])


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
