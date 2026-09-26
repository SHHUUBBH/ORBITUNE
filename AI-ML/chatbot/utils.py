"""
Utility functions for ORBITUNE chatbot
"""

import time
import hashlib
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache
import json


class Timer:
    """Simple timer for performance monitoring"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.time()
    
    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0


class ResponseCache:
    """Simple in-memory cache for common queries"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if exists and not expired"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() < entry['expires']:
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Cache a value with TTL"""
        # Clean old entries if cache is full
        if len(self.cache) >= self.max_size:
            self._clean_expired()
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['expires'])
                del self.cache[oldest_key]
        
        self.cache[key] = {
            'value': value,
            'expires': datetime.now() + timedelta(seconds=self.ttl_seconds)
        }
    
    def _clean_expired(self):
        """Remove expired entries"""
        now = datetime.now()
        expired_keys = [k for k, v in self.cache.items() if now >= v['expires']]
        for key in expired_keys:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache"""
        self.cache.clear()


def hash_text(text: str) -> str:
    """Generate hash for text (for caching keys)"""
    return hashlib.md5(text.lower().encode()).hexdigest()


def normalize_text(text: str) -> str:
    """Normalize text for comparison"""
    # Lowercase, remove extra spaces
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text"""
    # Remove punctuation, split into words
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    # Remove common stop words
    stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords


def fuzzy_match_score(query: str, target: str) -> float:
    """
    Simple fuzzy matching score between two strings
    Returns score between 0 and 1
    """
    query = normalize_text(query)
    target = normalize_text(target)
    
    if query == target:
        return 1.0
    
    if query in target or target in query:
        return 0.8
    
    # Check word overlap
    query_words = set(query.split())
    target_words = set(target.split())
    
    if not query_words or not target_words:
        return 0.0
    
    overlap = len(query_words & target_words)
    total = len(query_words | target_words)
    
    return overlap / total if total > 0 else 0.0


def truncate_text(text: str, max_length: int = 150, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_duration(seconds: int) -> str:
    """Format duration in seconds to MM:SS"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes}:{secs:02d}"


def get_time_of_day() -> str:
    """Get current time of day category"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def get_day_period() -> str:
    """Get day period for context"""
    day = datetime.now().strftime("%A")
    hour = datetime.now().hour
    
    if day in ["Saturday", "Sunday"]:
        return "weekend"
    elif 9 <= hour < 17:
        return "workday"
    else:
        return "weeknight"


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON, return default on error"""
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def sanitize_message(message: str) -> str:
    """Sanitize user message"""
    # Remove excessive whitespace
    message = re.sub(r'\s+', ' ', message.strip())
    # Limit length
    message = truncate_text(message, max_length=500)
    return message


def generate_message_id() -> str:
    """Generate unique message ID"""
    timestamp = datetime.now().isoformat()
    return hashlib.md5(timestamp.encode()).hexdigest()[:12]


def parse_time_context(text: str) -> Optional[str]:
    """Parse time-related context from text"""
    text_lower = text.lower()
    
    time_keywords = {
        'morning': ['morning', 'breakfast', 'wake up', 'sunrise'],
        'afternoon': ['afternoon', 'lunch', 'midday'],
        'evening': ['evening', 'dinner', 'sunset'],
        'night': ['night', 'late', 'sleep', 'bedtime'],
        'workout': ['workout', 'gym', 'exercise', 'run', 'jog'],
        'party': ['party', 'celebration', 'dance'],
        'chill': ['chill', 'relax', 'calm', 'unwind'],
        'focus': ['focus', 'work', 'study', 'concentrate']
    }
    
    for context, keywords in time_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return context
    
    return None


def extract_mood(text: str) -> Optional[str]:
    """Extract mood from text"""
    text_lower = text.lower()
    
    mood_keywords = {
        'happy': ['happy', 'joyful', 'excited', 'upbeat', 'cheerful', 'energetic'],
        'sad': ['sad', 'down', 'melancholy', 'depressed', 'blue'],
        'calm': ['calm', 'peaceful', 'relaxed', 'chill', 'tranquil'],
        'angry': ['angry', 'mad', 'frustrated', 'intense', 'aggressive'],
        'romantic': ['romantic', 'love', 'intimate', 'sensual'],
        'motivated': ['motivated', 'pumped', 'determined', 'focused', 'driven']
    }
    
    for mood, keywords in mood_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return mood
    
    return None


# Global cache instance
response_cache = ResponseCache(max_size=100, ttl_seconds=300)
