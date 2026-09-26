"""
Fast Intent Detection for ORBITUNE Chatbot
Multi-stage approach: keyword check -> context analysis -> Gemini fallback
Target: <50ms for 90% of cases
"""

import re
from typing import Tuple, Dict, List, Optional
from pathlib import Path
import sys
import json

# Add parent directory to path for imports
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from chatbot.utils import Timer, normalize_text, extract_keywords, fuzzy_match_score


class IntentDetector:
    """
    Detects user intent with high accuracy and low latency
    
    Intents:
    - 'search': User wants to find/play a song
    - 'chat': User wants to have a conversation
    - 'hybrid': Both search and chat (e.g., "play something happy")
    """
    
    # Fast keyword sets for O(1) lookup
    SEARCH_KEYWORDS = {
        'play', 'find', 'search', 'listen', 'song', 'track', 'music',
        'artist', 'album', 'playlist', 'start', 'queue', 'add',
        'show', 'get', 'download', 'stream', 'put', 'gimme', 'give'
    }
    
    CHAT_KEYWORDS = {
        'how', 'why', 'what', 'when', 'where', 'who',
        'tell', 'recommend', 'suggest', 'think', 'feel',
        'like', 'love', 'hate', 'favorite', 'best', 'worst',
        'help', 'explain', 'describe', 'about', 'know'
    }
    
    # Hybrid patterns (search + preference)
    HYBRID_PATTERNS = [
        r'play .*(happy|sad|chill|energetic|calm|romantic|upbeat)',
        r'find .*(vibe|mood|feel)',
        r'something .*(happy|sad|chill|energetic|calm|romantic|upbeat)',
        r'music for .*(workout|study|sleep|party|relax)',
        r'(recommend|suggest) .*(song|music|track)',
    ]
    
    # Strong search indicators (imperative commands)
    COMMAND_PATTERNS = [
        r'^play\s+',
        r'^search\s+',
        r'^find\s+',
        r'^listen\s+',
        r'^put\s+on\s+',
        r'^start\s+',
        r'^queue\s+',
    ]
    
    # Question patterns (usually chat)
    QUESTION_PATTERNS = [
        r'^\s*(what|how|why|when|where|who|which|can|could|would|should|do|does|did|is|are|was|were)',
        r'\?$'
    ]
    
    def __init__(self, songs_data_path: Optional[Path] = None):
        """
        Initialize intent detector
        
        Args:
            songs_data_path: Path to songs.json for fuzzy matching
        """
        self.songs_cache: List[Dict] = []
        self.artists_cache: set = set()
        self.titles_cache: set = set()
        
        # Load songs data if provided
        if songs_data_path and songs_data_path.exists():
            self._load_songs_cache(songs_data_path)
        
        # Compile regex patterns for speed
        self.hybrid_regex = [re.compile(p, re.IGNORECASE) for p in self.HYBRID_PATTERNS]
        self.command_regex = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_PATTERNS]
        self.question_regex = [re.compile(p, re.IGNORECASE) for p in self.QUESTION_PATTERNS]
    
    def _load_songs_cache(self, songs_path: Path):
        """Load songs data for context analysis"""
        try:
            with open(songs_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.songs_cache = data.get('songs', [])
                
                # Build fast lookup sets
                for song in self.songs_cache:
                    artist = song.get('artist', '').lower()
                    title = song.get('title', '').lower()
                    
                    if artist:
                        self.artists_cache.add(artist)
                    if title:
                        self.titles_cache.add(title)
                
                print(f"✅ Intent detector loaded {len(self.songs_cache)} songs for matching")
        except Exception as e:
            print(f"⚠️  Could not load songs cache: {e}")
    
    def detect(self, message: str) -> Tuple[str, float, Dict]:
        """
        Detect intent with confidence score
        
        Args:
            message: User message
        
        Returns:
            Tuple of (intent, confidence, metadata)
            - intent: 'search', 'chat', or 'hybrid'
            - confidence: 0.0 to 1.0
            - metadata: Additional context (keywords, matches, etc.)
        """
        timer = Timer()
        with timer:
            # Stage 1: Fast keyword check (~10ms)
            intent, confidence, metadata = self._fast_keyword_check(message)
            
            # Stage 2: Context analysis if not confident (~30ms)
            if confidence < 0.8:
                intent, confidence, metadata = self._context_analysis(message, intent, confidence, metadata)
            
            # Add timing info
            metadata['detection_time_ms'] = round(timer.elapsed_ms, 2)
        
        return intent, confidence, metadata
    
    def _fast_keyword_check(self, message: str) -> Tuple[str, float, Dict]:
        """
        Stage 1: Fast keyword-based detection
        Target: ~10ms
        """
        normalized = normalize_text(message)
        words = normalized.split()
        first_words = set(words[:5])  # Check first 5 words for speed
        
        metadata = {
            'method': 'keyword_check',
            'keywords_found': []
        }
        
        # Check for hybrid patterns first (most specific)
        for pattern in self.hybrid_regex:
            if pattern.search(message):
                metadata['pattern_match'] = 'hybrid'
                return 'hybrid', 0.85, metadata
        
        # Check for command patterns (strong search indicators)
        for pattern in self.command_regex:
            if pattern.search(message):
                metadata['pattern_match'] = 'command'
                return 'search', 0.95, metadata
        
        # Check for question patterns (strong chat indicators)
        for pattern in self.question_regex:
            if pattern.search(message):
                metadata['pattern_match'] = 'question'
                return 'chat', 0.90, metadata
        
        # Keyword scoring
        search_score = sum(1 for w in first_words if w in self.SEARCH_KEYWORDS)
        chat_score = sum(1 for w in first_words if w in self.CHAT_KEYWORDS)
        
        metadata['search_keywords'] = search_score
        metadata['chat_keywords'] = chat_score
        
        # Determine intent based on scores
        if search_score > chat_score:
            confidence = min(0.7 + (search_score * 0.1), 0.95)
            return 'search', confidence, metadata
        elif chat_score > search_score:
            confidence = min(0.7 + (chat_score * 0.1), 0.95)
            return 'chat', confidence, metadata
        else:
            # No clear winner
            return 'chat', 0.5, metadata
    
    def _context_analysis(self, message: str, prev_intent: str, prev_confidence: float, metadata: Dict) -> Tuple[str, float, Dict]:
        """
        Stage 2: Context analysis with song/artist matching
        Target: ~30ms additional
        """
        metadata['method'] = 'context_analysis'
        normalized = normalize_text(message)
        
        # Check for song/artist mentions
        song_matches = []
        artist_matches = []
        
        # Fast fuzzy matching against cache
        if self.songs_cache:
            for song in self.songs_cache[:100]:  # Check top 100 for speed
                title = song.get('title', '').lower()
                artist = song.get('artist', '').lower()
                
                title_score = fuzzy_match_score(normalized, title)
                artist_score = fuzzy_match_score(normalized, artist)
                
                if title_score > 0.5:
                    song_matches.append({'title': title, 'score': title_score})
                if artist_score > 0.5:
                    artist_matches.append({'artist': artist, 'score': artist_score})
        
        # Update metadata
        if song_matches:
            metadata['song_matches'] = song_matches[:3]
        if artist_matches:
            metadata['artist_matches'] = artist_matches[:3]
        
        # If we found strong matches, it's likely a search
        max_song_score = max([m['score'] for m in song_matches], default=0)
        max_artist_score = max([m['score'] for m in artist_matches], default=0)
        
        if max_song_score > 0.7 or max_artist_score > 0.7:
            confidence = max(max_song_score, max_artist_score, 0.85)
            return 'search', confidence, metadata
        
        # Check for music-related nouns
        music_nouns = {'song', 'track', 'music', 'artist', 'album', 'playlist', 'band', 'singer'}
        has_music_noun = any(noun in normalized for noun in music_nouns)
        
        if has_music_noun and prev_intent == 'search':
            # Boost search confidence if music-related
            return 'search', min(prev_confidence + 0.15, 0.90), metadata
        
        # Check message length and structure
        word_count = len(normalized.split())
        
        # Very short messages with search keywords are likely searches
        if word_count <= 3 and prev_intent == 'search':
            return 'search', min(prev_confidence + 0.1, 0.85), metadata
        
        # Longer messages with questions are likely chat
        if word_count > 8 and '?' in message:
            return 'chat', 0.85, metadata
        
        # Return previous intent with slight confidence boost
        return prev_intent, min(prev_confidence + 0.05, 0.80), metadata
    
    def is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = {
            'hi', 'hello', 'hey', 'yo', 'sup', 'whats up', "what's up",
            'howdy', 'hola', 'good morning', 'good afternoon', 'good evening'
        }
        normalized = normalize_text(message)
        return any(greeting in normalized for greeting in greetings)
    
    def is_farewell(self, message: str) -> bool:
        """Check if message is a farewell"""
        farewells = {
            'bye', 'goodbye', 'see you', 'later', 'peace', 'cya',
            'take care', 'good night', 'gotta go', 'catch you'
        }
        normalized = normalize_text(message)
        return any(farewell in normalized for farewell in farewells)
    
    def extract_search_query(self, message: str) -> Optional[str]:
        """
        Extract search query from message
        
        Examples:
        - "play Paaro" -> "Paaro"
        - "find songs by Arijit Singh" -> "Arijit Singh"
        - "search for sad songs" -> "sad songs"
        """
        normalized = normalize_text(message)
        
        # Remove common command words
        remove_words = [
            'play', 'find', 'search', 'listen', 'to', 'for', 'get', 'me',
            'some', 'a', 'the', 'by', 'from', 'song', 'songs', 'music', 'track'
        ]
        
        words = normalized.split()
        query_words = [w for w in words if w not in remove_words]
        
        if query_words:
            return ' '.join(query_words)
        
        return None


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    detector = IntentDetector()
    
    test_messages = [
        "play Paaro",
        "find songs by Arijit Singh",
        "what's your favorite genre?",
        "recommend something happy",
        "how are you doing today?",
        "play something chill for studying",
        "tell me about jazz music",
        "search for Bolna",
        "what kind of music do you like?"
    ]
    
    print("\\n🧪 Testing Intent Detection:\\n")
    for msg in test_messages:
        intent, confidence, metadata = detector.detect(msg)
        time_ms = metadata.get('detection_time_ms', 0)
        print(f"Message: '{msg}'")
        print(f"  → Intent: {intent} (confidence: {confidence:.2f}) [{time_ms:.2f}ms]")
        print()
