from typing import List, Optional

from pydantic import BaseModel


class Song(BaseModel):
    id: str
    title: str
    artist: str
    album: str
    duration: int  # seconds
    thumbnail: Optional[str] = None
    audioUrl: Optional[str] = None
    genre: Optional[str] = None
    releaseYear: Optional[int] = None


class SongsResponse(BaseModel):
    songs: List[Song]


class CreateFromYouTubeRequest(BaseModel):
    query: Optional[str] = None
    youtubeUrl: Optional[str] = None


class YouTubeSearchResult(BaseModel):
    songId: str
    videoId: str
    title: str
    artist: str
    duration: int
    durationString: str
    thumbnail: Optional[str] = None


class YouTubeSearchResponse(BaseModel):
    results: List[YouTubeSearchResult]


class Playlist(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    songIds: List[str] = []
    createdAt: str
    updatedAt: str


class PlaylistsResponse(BaseModel):
    playlists: List[Playlist]


# ==============================
# CHATBOT MODELS
# ==============================

class ChatMessageRequest(BaseModel):
    userId: str
    message: str


class ChatMessageResponse(BaseModel):
    response: str
    intent: str  # 'search', 'chat', 'hybrid'
    confidence: float
    songResults: Optional[List[Song]] = []
    processingTimeMs: float
    metadata: Optional[dict] = {}


class ChatMessage(BaseModel):
    id: str
    userId: str
    message: str
    sender: str  # 'user' | 'bot'
    intent: str  # 'search' | 'chat' | 'hybrid'
    timestamp: str
    metadata: Optional[dict] = {}


class ConversationHistoryResponse(BaseModel):
    messages: List[ChatMessage]
    totalCount: int


class UserProfileResponse(BaseModel):
    userId: str
    profileSummary: str
    favoriteGenres: List[str]
    favoriteArtists: List[str]
    totalSongsListened: int
    discoveryScore: float
    listeningPatterns: dict


class TrackPlayRequest(BaseModel):
    userId: str
    songId: str
    title: str
    artist: str
    genre: Optional[str] = None
    duration: int


class ChatFeedbackRequest(BaseModel):
    userId: str
    messageId: str
    feedback: str  # 'helpful' | 'not_helpful' | 'inappropriate'
    comment: Optional[str] = None
