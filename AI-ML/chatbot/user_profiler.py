"""
User Profiler for ORBITUNE Chatbot
Analyzes listening habits and builds personalized user profiles
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path
import json
import sys

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from chatbot.utils import get_time_of_day, get_day_period


class UserProfiler:
    """
    Builds and maintains user profiles based on listening history and interactions
    """
    
    def __init__(self, profiles_path: Path):
        """
        Initialize user profiler
        
        Args:
            profiles_path: Path to user_profiles.json
        """
        self.profiles_path = profiles_path
        self.profiles_cache: Dict[str, Dict] = {}
        self._load_profiles()
    
    def _load_profiles(self):
        """Load existing profiles from disk"""
        try:
            if self.profiles_path.exists():
                with open(self.profiles_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.profiles_cache = data.get('profiles', {})
                print(f"✅ Loaded {len(self.profiles_cache)} user profiles")
            else:
                self.profiles_cache = {}
                self._save_profiles()
        except Exception as e:
            print(f"⚠️  Error loading profiles: {e}")
            self.profiles_cache = {}
    
    def _save_profiles(self):
        """Save profiles to disk"""
        try:
            self.profiles_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.profiles_path, 'w', encoding='utf-8') as f:
                json.dump({'profiles': self.profiles_cache}, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving profiles: {e}")
    
    def get_or_create_profile(self, user_id: str) -> Dict:
        """Get existing profile or create new one"""
        if user_id not in self.profiles_cache:
            self.profiles_cache[user_id] = self._create_empty_profile(user_id)
            self._save_profiles()
        return self.profiles_cache[user_id]
    
    def _create_empty_profile(self, user_id: str) -> Dict:
        """Create empty profile structure"""
        return {
            'userId': user_id,
            'name': None,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'listening_history': [],  # List of {songId, timestamp, duration, genre, artist}
            'genre_stats': {},  # {genre: count}
            'artist_stats': {},  # {artist: count}
            'listening_patterns': {
                'by_time_of_day': {'morning': 0, 'afternoon': 0, 'evening': 0, 'night': 0},
                'by_day_period': {'weekday': 0, 'weekend': 0, 'workday': 0, 'weeknight': 0},
                'total_songs': 0,
                'total_listen_time': 0
            },
            'music_preferences': {
                'favorite_genres': [],
                'favorite_artists': [],
                'mood_preferences': {},  # {mood: count}
                'discovery_score': 0.5  # 0 = only familiar, 1 = very adventurous
            },
            'conversation_insights': {
                'mentioned_preferences': [],  # List of {preference, timestamp}
                'topics_discussed': [],  # List of topics
                'personality_traits': []  # Inferred traits (casual, enthusiastic, etc.)
            }
        }
    
    def add_listening_event(self, user_id: str, song_data: Dict):
        """
        Add a listening event to user's history
        
        Args:
            user_id: User ID
            song_data: Dict with songId, title, artist, genre, duration
        """
        profile = self.get_or_create_profile(user_id)
        
        # Add to listening history
        event = {
            'songId': song_data.get('songId'),
            'title': song_data.get('title'),
            'artist': song_data.get('artist'),
            'genre': song_data.get('genre'),
            'duration': song_data.get('duration', 0),
            'timestamp': datetime.now().isoformat(),
            'time_of_day': get_time_of_day(),
            'day_period': get_day_period()
        }
        
        profile['listening_history'].append(event)
        
        # Keep only last 500 listens for performance
        if len(profile['listening_history']) > 500:
            profile['listening_history'] = profile['listening_history'][-500:]
        
        # Update stats
        self._update_stats(profile)
        
        # Update last active
        profile['last_active'] = datetime.now().isoformat()
        
        self._save_profiles()
    
    def _update_stats(self, profile: Dict):
        """Recalculate all stats from listening history"""
        history = profile['listening_history']
        
        if not history:
            return
        
        # Genre stats
        genre_counter = Counter()
        artist_counter = Counter()
        
        # Time patterns
        time_of_day_counter = Counter()
        day_period_counter = Counter()
        
        total_duration = 0
        
        for event in history:
            genre = event.get('genre')
            artist = event.get('artist')
            duration = event.get('duration', 0)
            
            if genre:
                genre_counter[genre] += 1
            if artist:
                artist_counter[artist] += 1
            
            time_of_day = event.get('time_of_day')
            if time_of_day:
                time_of_day_counter[time_of_day] += 1
            
            day_period = event.get('day_period')
            if day_period:
                day_period_counter[day_period] += 1
            
            total_duration += duration
        
        # Update genre stats
        profile['genre_stats'] = dict(genre_counter)
        profile['artist_stats'] = dict(artist_counter)
        
        # Update listening patterns
        profile['listening_patterns']['by_time_of_day'] = dict(time_of_day_counter)
        profile['listening_patterns']['by_day_period'] = dict(day_period_counter)
        profile['listening_patterns']['total_songs'] = len(history)
        profile['listening_patterns']['total_listen_time'] = total_duration
        
        # Update favorite genres (top 5)
        top_genres = genre_counter.most_common(5)
        profile['music_preferences']['favorite_genres'] = [g[0] for g in top_genres if g[0]]
        
        # Update favorite artists (top 5)
        top_artists = artist_counter.most_common(5)
        profile['music_preferences']['favorite_artists'] = [a[0] for a in top_artists if a[0]]
        
        # Calculate discovery score (variety of music)
        unique_artists = len(set(e.get('artist') for e in history if e.get('artist')))
        unique_genres = len(set(e.get('genre') for e in history if e.get('genre')))
        total_plays = len(history)
        
        if total_plays > 0:
            artist_variety = unique_artists / min(total_plays, 50)  # Normalize to 50 plays
            genre_variety = unique_genres / min(total_plays, 20)  # Normalize to 20 plays
            discovery_score = (artist_variety + genre_variety) / 2
            profile['music_preferences']['discovery_score'] = min(discovery_score, 1.0)
    
    def add_conversation_insight(self, user_id: str, insight_type: str, content: str):
        """
        Add insights from conversation
        
        Args:
            user_id: User ID
            insight_type: Type of insight ('preference', 'topic', 'trait')
            content: The actual content
        """
        profile = self.get_or_create_profile(user_id)
        
        if insight_type == 'preference':
            profile['conversation_insights']['mentioned_preferences'].append({
                'preference': content,
                'timestamp': datetime.now().isoformat()
            })
            # Keep only last 50
            if len(profile['conversation_insights']['mentioned_preferences']) > 50:
                profile['conversation_insights']['mentioned_preferences'] = \
                    profile['conversation_insights']['mentioned_preferences'][-50:]
        
        elif insight_type == 'topic':
            if content not in profile['conversation_insights']['topics_discussed']:
                profile['conversation_insights']['topics_discussed'].append(content)
        
        elif insight_type == 'trait':
            if content not in profile['conversation_insights']['personality_traits']:
                profile['conversation_insights']['personality_traits'].append(content)
        
        self._save_profiles()
    
    def get_profile_summary(self, user_id: str) -> str:
        """
        Generate human-readable profile summary for chatbot context
        
        Returns:
            String summarizing user's profile
        """
        profile = self.get_or_create_profile(user_id)
        
        summary_parts = []
        
        # Listening stats
        total_songs = profile['listening_patterns']['total_songs']
        if total_songs > 0:
            summary_parts.append(f"Listened to {total_songs} songs")
        
        # Favorite genres
        fav_genres = profile['music_preferences']['favorite_genres']
        if fav_genres:
            genres_str = ', '.join(fav_genres[:3])
            summary_parts.append(f"Loves: {genres_str}")
        
        # Favorite artists
        fav_artists = profile['music_preferences']['favorite_artists']
        if fav_artists:
            artists_str = ', '.join(fav_artists[:2])
            summary_parts.append(f"Top artists: {artists_str}")
        
        # Discovery score
        discovery = profile['music_preferences']['discovery_score']
        if discovery > 0.7:
            summary_parts.append("Very adventurous listener")
        elif discovery < 0.3:
            summary_parts.append("Prefers familiar music")
        
        # Time preferences
        time_prefs = profile['listening_patterns']['by_time_of_day']
        if time_prefs:
            most_active_time = max(time_prefs, key=time_prefs.get)
            summary_parts.append(f"Most active: {most_active_time}")
        
        # Mentioned preferences
        mentioned = profile['conversation_insights']['mentioned_preferences']
        if mentioned:
            recent_prefs = mentioned[-3:]  # Last 3 preferences
            prefs_str = ', '.join([p['preference'] for p in recent_prefs])
            summary_parts.append(f"Mentioned: {prefs_str}")
        
        if summary_parts:
            return ' | '.join(summary_parts)
        else:
            return "New user, no listening history yet"
    
    def get_recent_songs(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Get recent songs listened to"""
        profile = self.get_or_create_profile(user_id)
        history = profile['listening_history'][-limit:]
        return history
    
    def get_recommendations_context(self, user_id: str) -> Dict:
        """
        Get context for making personalized recommendations
        
        Returns:
            Dict with recommendation hints
        """
        profile = self.get_or_create_profile(user_id)
        
        # Get current time context
        current_time = get_time_of_day()
        current_period = get_day_period()
        
        # Find what user usually listens to at this time
        time_prefs = profile['listening_patterns']['by_time_of_day']
        period_prefs = profile['listening_patterns']['by_day_period']
        
        context = {
            'current_time': current_time,
            'current_period': current_period,
            'favorite_genres': profile['music_preferences']['favorite_genres'][:3],
            'favorite_artists': profile['music_preferences']['favorite_artists'][:3],
            'discovery_score': profile['music_preferences']['discovery_score'],
            'recent_songs': self.get_recent_songs(user_id, 3)
        }
        
        return context
    
    def extract_preferences_from_message(self, user_id: str, message: str):
        """
        Extract and store music preferences mentioned in message
        
        Examples:
        - "I love jazz" -> preference: "loves jazz"
        - "not into metal" -> preference: "dislikes metal"
        - "Arijit Singh is my favorite" -> preference: "favorite artist: Arijit Singh"
        """
        message_lower = message.lower()
        
        # Love/like patterns
        love_patterns = ['i love', 'i really like', 'i adore', 'im into', "i'm into", 'favorite', 'favourite']
        dislike_patterns = ['i hate', 'not into', "don't like", 'dislike', 'not a fan']
        
        for pattern in love_patterns:
            if pattern in message_lower:
                # Extract what comes after
                idx = message_lower.index(pattern)
                rest = message[idx + len(pattern):].strip()
                if rest:
                    self.add_conversation_insight(user_id, 'preference', f"loves {rest}")
        
        for pattern in dislike_patterns:
            if pattern in message_lower:
                idx = message_lower.index(pattern)
                rest = message[idx + len(pattern):].strip()
                if rest:
                    self.add_conversation_insight(user_id, 'preference', f"dislikes {rest}")


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Test profiler
    test_path = Path("test_user_profiles.json")
    profiler = UserProfiler(test_path)
    
    # Simulate listening events
    profiler.add_listening_event('user123', {
        'songId': 'abc123',
        'title': 'Paaro',
        'artist': 'Aditya Rikhari',
        'genre': 'Bollywood',
        'duration': 218
    })
    
    profiler.add_listening_event('user123', {
        'songId': 'def456',
        'title': 'Bolna',
        'artist': 'Arijit Singh',
        'genre': 'Bollywood',
        'duration': 127
    })
    
    # Add conversation insights
    profiler.extract_preferences_from_message('user123', "I love Arijit Singh's voice!")
    profiler.extract_preferences_from_message('user123', "Not into heavy metal though")
    
    # Get summary
    summary = profiler.get_profile_summary('user123')
    print(f"\n📊 Profile Summary:\n{summary}\n")
    
    # Get recommendations context
    rec_context = profiler.get_recommendations_context('user123')
    print(f"🎯 Recommendation Context:\n{json.dumps(rec_context, indent=2)}\n")
    
    # Cleanup
    test_path.unlink()
