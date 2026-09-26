"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              ORBITUNE - Main Chatbot Service                                ║
║                                                                              ║
║  COPYRIGHT © 2025 Yuvraj Singh Kushwah & Subhro Pal. All Rights Reserved.   ║
║                                                                              ║
║  PROPRIETARY AI/ML IMPLEMENTATION - TRADE SECRETS PROTECTED                 ║
║                                                                              ║
║  This module orchestrates ORBITUNE's conversational AI system powered by    ║
║  Gemini Flash 2.0 with proprietary prompt engineering and intent detection. ║
║                                                                              ║
║  Protected Trade Secrets:                                                   ║
║  • Proprietary prompt engineering structures for Gemini AI                  ║
║  • Intent detection confidence scoring methodology                          ║
║  • User profiling and preference extraction algorithms                      ║
║  • Conversation memory management system                                    ║
║  • Hybrid search/chat mode orchestration logic                              ║
║                                                                              ║
║  Unauthorized extraction or replication is STRICTLY PROHIBITED.             ║
║                                                                              ║
║  Contact: yuvrajsk.bpl@gmail.com | shubhropal62@gmail.com                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

Main Chatbot Service for ORBITUNE
Orchestrates intent detection, user profiling, memory, and response generation
"""

from typing import Dict, Tuple, Optional, List
from pathlib import Path
import sys
import json

# Add parent directories to path
BASE_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = BASE_DIR.parent / "BACKEND"
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BACKEND_DIR / "src") not in sys.path:
    sys.path.append(str(BACKEND_DIR / "src"))

from chatbot.intent_detector import IntentDetector
from chatbot.user_profiler import UserProfiler
from chatbot.conversation_memory import ConversationMemory
from chatbot.response_generator import ResponseGenerator
from chatbot.utils import sanitize_message, Timer


class ChatbotService:
    """
    Main chatbot service that coordinates all components
    
    Flow:
    1. Receive user message
    2. Detect intent (search vs chat)
    3. Get user profile and conversation context
    4. Generate appropriate response
    5. Update memory and profile
    6. Return response with metadata
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize chatbot service
        
        Args:
            data_dir: Directory containing data files (BACKEND/data/)
        """
        self.data_dir = data_dir
        
        # Initialize components
        print("\n🤖 Initializing ORBITUNE Chatbot...")
        
        # Paths
        songs_path = BASE_DIR.parent / "BACKEND" / "src" / "data" / "songs.json"
        profiles_path = data_dir / "user_profiles.json"
        history_path = data_dir / "chat_history.json"
        
        # Create data dir if needed
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.intent_detector = IntentDetector(songs_data_path=songs_path)
        self.user_profiler = UserProfiler(profiles_path)
        self.conversation_memory = ConversationMemory(history_path)
        self.response_generator = ResponseGenerator()
        
        # Load songs database for search
        self.songs_db = self._load_songs_db(songs_path)
        
        print("✅ Chatbot initialized and ready!\n")
    
    def _load_songs_db(self, songs_path: Path) -> List[Dict]:
        """Load songs database"""
        try:
            if songs_path.exists():
                with open(songs_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('songs', [])
        except Exception as e:
            print(f"⚠️  Could not load songs database: {e}")
        return []
    
    def process_message(self, user_id: str, message: str) -> Dict:
        """
        Process incoming message and generate response
        
        Args:
            user_id: User ID
            message: User's message
        
        Returns:
            Dict with response, intent, metadata, and song results (if applicable)
        """
        timer = Timer()
        with timer:
            # Sanitize input
            message = sanitize_message(message)
            
            if not message:
                return {
                    'response': "Yo send me something! 😅",
                    'intent': 'chat',
                    'confidence': 1.0,
                    'processing_time_ms': 0
                }
            
            # 1. Detect intent
            intent, confidence, intent_metadata = self.intent_detector.detect(message)
            
            # 2. Get user context
            user_context = self._build_user_context(user_id)
            
            # 3. Handle based on intent
            if intent == 'search':
                response, song_results = self._handle_search_intent(
                    user_id, message, user_context
                )
            elif intent == 'hybrid':
                response, song_results = self._handle_hybrid_intent(
                    user_id, message, user_context
                )
            else:  # chat
                response = self._handle_chat_intent(
                    user_id, message, user_context
                )
                song_results = []
            
            # 4. Update conversation memory
            self.conversation_memory.add_message(
                user_id, message, 'user', intent, intent_metadata
            )
            self.conversation_memory.add_message(
                user_id, response, 'bot', intent, 
                {'song_results': song_results} if song_results else {}
            )
            
            # 5. Extract preferences from message
            self.user_profiler.extract_preferences_from_message(user_id, message)
            
            # 6. Return response with metadata
            processing_time = timer.elapsed_ms
            
            return {
                'response': response,
                'intent': intent,
                'confidence': confidence,
                'song_results': song_results,
                'processing_time_ms': round(processing_time, 2),
                'intent_metadata': intent_metadata
            }
    
    def _build_user_context(self, user_id: str) -> Dict:
        """Build comprehensive user context"""
        # Get profile summary
        profile_summary = self.user_profiler.get_profile_summary(user_id)
        
        # Get recent songs
        recent_songs = self.user_profiler.get_recent_songs(user_id, limit=5)
        
        # Get conversation context
        conversation_history = self.conversation_memory.get_conversation_context(user_id)
        
        # Get conversation style
        conversation_style = self.conversation_memory.get_conversation_style(user_id)
        
        return {
            'profile_summary': profile_summary,
            'recent_songs': recent_songs,
            'conversation_history': conversation_history,
            'conversation_style': conversation_style
        }
    
    def _handle_search_intent(self, user_id: str, message: str, context: Dict) -> Tuple[str, List[Dict]]:
        """
        Handle song search intent
        
        Returns:
            Tuple of (response, song_results)
        """
        # Extract search query
        search_query = self.intent_detector.extract_search_query(message)
        
        if not search_query:
            search_query = message
        
        # Search songs
        found_songs = self._search_songs(search_query)
        
        # Generate response
        response = self.response_generator.generate_song_search_response(
            search_query, found_songs
        )
        
        return response, found_songs[:10]  # Return top 10 results
    
    def _handle_hybrid_intent(self, user_id: str, message: str, context: Dict) -> Tuple[str, List[Dict]]:
        """
        Handle hybrid intent (search + chat)
        
        Examples:
        - "play something chill"
        - "find me happy songs"
        - "recommend music for studying"
        """
        # Extract mood/vibe from message
        from chatbot.utils import extract_mood, parse_time_context
        
        mood = extract_mood(message)
        time_context = parse_time_context(message)
        
        # Get personalized recommendations
        rec_context = self.user_profiler.get_recommendations_context(user_id)
        
        # Search based on mood/context or user preferences
        if mood:
            found_songs = self._search_songs_by_mood(mood)
        elif time_context:
            found_songs = self._search_songs_by_context(time_context)
        else:
            # Use user's favorite genres
            favorite_genres = rec_context.get('favorite_genres', [])
            if favorite_genres:
                found_songs = self._search_songs_by_genre(favorite_genres[0])
            else:
                found_songs = self.songs_db[:5]  # Return first 5 songs
        
        # Generate personalized response
        if mood or time_context:
            response = self.response_generator.generate_response(
                message, 'hybrid', context
            )
        else:
            response = self.response_generator.generate_recommendation_response(rec_context)
        
        return response, found_songs[:10]
    
    def _handle_chat_intent(self, user_id: str, message: str, context: Dict) -> str:
        """
        Handle pure chat intent
        
        Returns:
            Response string
        """
        response = self.response_generator.generate_response(
            message, 'chat', context
        )
        return response
    
    def _search_songs(self, query: str) -> List[Dict]:
        """
        Search songs by query (title, artist, etc.)
        
        Simple fuzzy search implementation
        """
        from chatbot.utils import fuzzy_match_score
        
        query_lower = query.lower()
        results = []
        
        for song in self.songs_db:
            title = song.get('title', '').lower()
            artist = song.get('artist', '').lower()
            album = song.get('album', '').lower()
            
            # Calculate match scores
            title_score = fuzzy_match_score(query_lower, title)
            artist_score = fuzzy_match_score(query_lower, artist)
            album_score = fuzzy_match_score(query_lower, album)
            
            max_score = max(title_score, artist_score, album_score)
            
            if max_score > 0.3:  # Threshold for match
                results.append({
                    'song': song,
                    'score': max_score
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return [r['song'] for r in results]
    
    def _search_songs_by_mood(self, mood: str) -> List[Dict]:
        """Search songs by mood"""
        # This is simplified - in production, you'd use genre/audio features
        mood_genre_map = {
            'happy': ['Pop', 'Bollywood', 'Dance'],
            'sad': ['Ballad', 'Acoustic', 'Soul'],
            'calm': ['Acoustic', 'Classical', 'Ambient'],
            'energetic': ['Dance', 'Electronic', 'Rock'],
            'romantic': ['R&B', 'Soul', 'Ballad']
        }
        
        genres = mood_genre_map.get(mood, [])
        if genres:
            return self._search_songs_by_genre(genres[0])
        
        return self.songs_db[:5]
    
    def _search_songs_by_context(self, context: str) -> List[Dict]:
        """Search songs by time context (workout, study, etc.)"""
        context_genre_map = {
            'workout': ['Dance', 'Electronic', 'Hip Hop'],
            'study': ['Classical', 'Ambient', 'Acoustic'],
            'party': ['Dance', 'Pop', 'Electronic'],
            'chill': ['Acoustic', 'R&B', 'Soul']
        }
        
        genres = context_genre_map.get(context, [])
        if genres:
            return self._search_songs_by_genre(genres[0])
        
        return self.songs_db[:5]
    
    def _search_songs_by_genre(self, genre: str) -> List[Dict]:
        """Search songs by genre"""
        genre_lower = genre.lower()
        matching_songs = []
        
        for song in self.songs_db:
            song_genre = song.get('genre') or ''
            song_genre = str(song_genre).lower()
            if genre_lower in song_genre or song_genre in genre_lower:
                matching_songs.append(song)
        
        # Return matching songs or random songs if no matches
        return matching_songs[:10] if matching_songs else self.songs_db[:5]
    
    def track_song_play(self, user_id: str, song_data: Dict):
        """
        Track when a user plays a song
        
        Args:
            user_id: User ID
            song_data: Song information
        """
        self.user_profiler.add_listening_event(user_id, song_data)
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Get full user profile"""
        return self.user_profiler.get_or_create_profile(user_id)
    
    def get_conversation_history(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_memory.get_recent_messages(user_id, limit)
    
    def clear_conversation_history(self, user_id: str):
        """Clear conversation history for user"""
        self.conversation_memory.clear_history(user_id)


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Initialize chatbot
    data_dir = Path(__file__).resolve().parent.parent.parent / "BACKEND" / "data"
    chatbot = ChatbotService(data_dir)
    
    # Test conversation
    test_user = "test_user_123"
    
    test_messages = [
        "Hey what's up?",
        "Play something chill",
        "I love Arijit Singh!",
        "Find Paaro",
        "What's my favorite genre?"
    ]
    
    print("\n🎭 Testing Chatbot Service:\n")
    for msg in test_messages:
        print(f"User: {msg}")
        result = chatbot.process_message(test_user, msg)
        print(f"Bot [{result['intent']}]: {result['response']}")
        if result.get('song_results'):
            print(f"   🎵 Found {len(result['song_results'])} songs")
        print(f"   ⏱️  {result['processing_time_ms']:.2f}ms\n")
