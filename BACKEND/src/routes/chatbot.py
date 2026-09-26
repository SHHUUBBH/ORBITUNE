"""
Chatbot API Routes for ORBITUNE
Endpoints for chat interactions, history, profiles, and tracking
"""

from fastapi import APIRouter, HTTPException
from pathlib import Path
import sys

# Setup paths
THIS_FILE = Path(__file__).resolve()
SRC_DIR = THIS_FILE.parent.parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ML_DIR = PROJECT_ROOT / "AI-ML"

# Add to sys.path
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))
if str(AI_ML_DIR) not in sys.path:
    sys.path.append(str(AI_ML_DIR))

# Import models
from models import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatMessage,
    ConversationHistoryResponse,
    UserProfileResponse,
    TrackPlayRequest,
    ChatFeedbackRequest,
    Song
)

# Import chatbot service
from chatbot.chatbot_service import ChatbotService

# Initialize chatbot service
DATA_DIR = BACKEND_DIR / "data"
chatbot_service = None

def get_chatbot_service() -> ChatbotService:
    """Get or create chatbot service instance"""
    global chatbot_service
    if chatbot_service is None:
        chatbot_service = ChatbotService(DATA_DIR)
    return chatbot_service


# Create router
router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post("/chat", response_model=ChatMessageResponse)
async def send_message(request: ChatMessageRequest):
    """
    Send a message to the chatbot and get response
    
    This endpoint:
    1. Detects user intent (search, chat, hybrid)
    2. Generates personalized response using Gemini Flash 2.0
    3. Returns song results if intent is search/hybrid
    4. Updates conversation history and user profile
    """
    try:
        chatbot = get_chatbot_service()
        
        # Process message
        result = chatbot.process_message(request.userId, request.message)
        
        # Convert song results to Song models
        song_results = []
        for song_dict in result.get('song_results', []):
            # Ensure thumbnail URL is valid (not external CDN)
            if song_dict.get('thumbnail') and 'saavncdn.com' in song_dict.get('thumbnail', ''):
                # Replace with local thumbnail or placeholder
                song_id = song_dict.get('id', '')
                song_dict['thumbnail'] = f"http://127.0.0.1:8000/media/thumbnails/{song_id}.jpg"
            song_results.append(Song(**song_dict))
        
        return ChatMessageResponse(
            response=result['response'],
            intent=result['intent'],
            confidence=result['confidence'],
            songResults=song_results,
            processingTimeMs=result['processing_time_ms'],
            metadata=result.get('intent_metadata', {})
        )
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/history/{user_id}", response_model=ConversationHistoryResponse)
async def get_conversation_history(user_id: str, limit: int = 50):
    """
    Get conversation history for a user
    
    Args:
        user_id: User ID
        limit: Maximum number of messages to return (default: 50)
    """
    try:
        chatbot = get_chatbot_service()
        
        # Get messages
        messages = chatbot.get_conversation_history(user_id, limit=limit)
        
        # Convert to ChatMessage models
        chat_messages = []
        for msg in messages:
            chat_messages.append(ChatMessage(
                id=msg['id'],
                userId=user_id,
                message=msg['message'],
                sender=msg['sender'],
                intent=msg.get('intent', 'chat'),
                timestamp=msg['timestamp'],
                metadata=msg.get('metadata', {})
            ))
        
        return ConversationHistoryResponse(
            messages=chat_messages,
            totalCount=len(chat_messages)
        )
        
    except Exception as e:
        print(f"❌ History retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/profile/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(user_id: str):
    """
    Get user profile with listening analytics and preferences
    
    Returns:
        User profile with favorite genres, artists, listening patterns, etc.
    """
    try:
        chatbot = get_chatbot_service()
        
        # Get profile
        profile = chatbot.get_user_profile(user_id)
        
        return UserProfileResponse(
            userId=user_id,
            profileSummary=chatbot.user_profiler.get_profile_summary(user_id),
            favoriteGenres=profile.get('music_preferences', {}).get('favorite_genres', []),
            favoriteArtists=profile.get('music_preferences', {}).get('favorite_artists', []),
            totalSongsListened=profile.get('listening_patterns', {}).get('total_songs', 0),
            discoveryScore=profile.get('music_preferences', {}).get('discovery_score', 0.5),
            listeningPatterns=profile.get('listening_patterns', {})
        )
        
    except Exception as e:
        print(f"❌ Profile retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.post("/track-play")
async def track_song_play(request: TrackPlayRequest):
    """
    Track when a user plays a song
    
    This updates the user's listening history and profile analytics
    """
    try:
        chatbot = get_chatbot_service()
        
        # Track the play
        song_data = {
            'songId': request.songId,
            'title': request.title,
            'artist': request.artist,
            'genre': request.genre,
            'duration': request.duration
        }
        
        chatbot.track_song_play(request.userId, song_data)
        
        return {"status": "success", "message": "Song play tracked"}
        
    except Exception as e:
        print(f"❌ Track play error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to track play: {str(e)}")


@router.post("/feedback")
async def submit_feedback(request: ChatFeedbackRequest):
    """
    Submit feedback on a chatbot response
    
    This helps improve the chatbot over time
    """
    try:
        # Store feedback (you can implement this based on your needs)
        # For now, just log it
        print(f"📝 Feedback from {request.userId} on message {request.messageId}: {request.feedback}")
        if request.comment:
            print(f"   Comment: {request.comment}")
        
        return {
            "status": "success",
            "message": "Feedback received"
        }
        
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.delete("/history/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for a user
    """
    try:
        chatbot = get_chatbot_service()
        chatbot.clear_conversation_history(user_id)
        
        return {
            "status": "success",
            "message": "Conversation history cleared"
        }
        
    except Exception as e:
        print(f"❌ Clear history error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear history: {str(e)}")


@router.get("/health")
async def chatbot_health():
    """Check if chatbot service is healthy"""
    try:
        chatbot = get_chatbot_service()
        
        return {
            "status": "healthy",
            "gemini_available": chatbot.response_generator.api_available,
            "components": {
                "intent_detector": True,
                "user_profiler": True,
                "conversation_memory": True,
                "response_generator": True
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
