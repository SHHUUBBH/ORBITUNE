"""
ORBITUNE - AI Genre Detection
Uses Gemini AI to detect music genre for adaptive processing
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional, Tuple

sys.path.append(str(Path(__file__).parent.parent))
from config import GEMINI_API_KEY, GEMINI_MODEL, get_metadata_path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Genre detection disabled.")


class GenreDetector:
    """
    Detect music genre using Gemini AI
    
    Uses song metadata (title, artist, description) to intelligently
    determine the genre and recommend optimal spatial audio settings
    """
    
    # Genre-specific audio processing profiles
    GENRE_PROFILES = {
'rock': {
            'name': 'Rock',
            'rotation_speed': 2.5,  # Increased for observable rotation
            'room_size': 'small',
            'reverb_amount': 0.04,  # Still fairly dry, but with a bit more space
            'bass_position': 'center_back',
            'vocals_distance': 2.0,
            'drums_spread': 1.5,
            'description': 'Crisp, clear, powerful 3D positioning'
        },
'pop': {
            'name': 'Pop',
            'rotation_speed': 3.0,  # Increased for clear rotation
            'room_size': 'small',
            'reverb_amount': 0.04,  # Still tight, but a touch more ambience
            'bass_position': 'center',
            'vocals_distance': 1.8,
            'drums_spread': 1.2,
            'description': 'Crystal clear vocals, tight spatial imaging'
        },
'edm': {
            'name': 'Electronic/EDM',
            'rotation_speed': 4.0,  # Fast, dramatic
            'room_size': 'medium',
            'reverb_amount': 0.05,  # A bit more tail for immersive feel
            'bass_position': 'everywhere',
            'vocals_distance': 2.0,  # Consistent distance
            'drums_spread': 2.0,
            'description': 'Punchy, clean, fast movement'
        },
'classical': {
            'name': 'Classical',
            'rotation_speed': 1.5,  # Slower but still observable
            'room_size': 'medium',
            'reverb_amount': 0.06,  # Slightly longer, natural hall feel
            'bass_position': 'back_left',
            'vocals_distance': 2.0,
            'drums_spread': 1.8,
            'description': 'Elegant, clear, natural space'
        },
'jazz': {
            'name': 'Jazz',
            'rotation_speed': 2.0,  # More observable
            'room_size': 'small',
            'reverb_amount': 0.03,  # Still intimate, but with a bit of room
            'bass_position': 'left',
            'vocals_distance': 2.0,
            'drums_spread': 1.0,
            'description': 'Intimate, dry, crystal clear'
        },
'hip_hop': {
            'name': 'Hip-Hop',
            'rotation_speed': 3.5,  # Fast, dramatic
            'room_size': 'small',
            'reverb_amount': 0.03,  # Mostly dry, slight ambience on tails
            'bass_position': 'front_center',
            'vocals_distance': 2.0,
            'drums_spread': 1.3,
            'description': 'Tight, punchy, clear vocals'
        },
'metal': {
            'name': 'Metal',
            'rotation_speed': 3.0,  # Aggressive movement
            'room_size': 'small',
            'reverb_amount': 0.04,  # Tight, but with a bit more tail
            'bass_position': 'wide',
            'vocals_distance': 2.0,
            'drums_spread': 1.8,
            'description': 'Aggressive, crisp, powerful'
        },
'acoustic': {
            'name': 'Acoustic',
            'rotation_speed': 2.0,  # More observable
            'room_size': 'small',
            'reverb_amount': 0.04,  # Natural and clear with a bit more room
            'bass_position': 'back_center',
            'vocals_distance': 2.0,
            'drums_spread': 0.8,
            'description': 'Warm, natural, crisp'
        },
'indie': {
            'name': 'Indie',
            'rotation_speed': 1.5,  # Clear movement
            'room_size': 'small',
            'reverb_amount': 0.04,  # Slightly more atmosphere, still clean
            'bass_position': 'left_back',
            'vocals_distance': 2.0,
            'drums_spread': 1.1,
            'description': 'Clear, artistic, clean imaging'
        }
    }
    
    def __init__(self):
        """Initialize genre detector"""
        self.api_available = GEMINI_AVAILABLE and bool(GEMINI_API_KEY)
        
        if self.api_available:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel(GEMINI_MODEL)
                print("✅ Gemini AI Genre Detector initialized")
            except Exception as e:
                print(f"⚠️  Gemini API error: {e}")
                self.api_available = False
        else:
            if not GEMINI_API_KEY:
                print("⚠️  GEMINI_API_KEY not set. Using fallback genre detection.")
            print("ℹ️  Genre detection: Using metadata-based fallback")
    
    def detect_genre(self, song_id: str) -> Tuple[str, float, Dict]:
        """
        Detect genre for a song
        
        Args:
            song_id: Song identifier
            
        Returns:
            Tuple of (genre, confidence, profile)
        """
        # Load metadata
        metadata_path = get_metadata_path(song_id)
        if not metadata_path.exists():
            print("⚠️  No metadata found, using default genre")
            return 'pop', 0.5, self.GENRE_PROFILES['pop']
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        title = metadata.get('title', 'Unknown')
        artist = metadata.get('artist', 'Unknown')
        description = metadata.get('description', '')[:300]  # First 300 chars
        
        print(f"\n🎵 Detecting genre for: {title}")
        print(f"🎤 Artist: {artist}")
        
        if self.api_available:
            genre, confidence = self._detect_with_gemini(title, artist, description)
        else:
            genre, confidence = self._detect_with_fallback(title, artist, description)
        
        profile = self.GENRE_PROFILES.get(genre, self.GENRE_PROFILES['pop'])
        
        print(f"🎯 Genre detected: {profile['name']} (confidence: {confidence:.0%})")
        print(f"📝 Profile: {profile['description']}")
        
        return genre, confidence, profile
    
    def _detect_with_gemini(self, title: str, artist: str, description: str) -> Tuple[str, float]:
        """Detect genre using Gemini AI"""
        prompt = f"""Analyze this music track and determine its primary genre.

Title: {title}
Artist: {artist}
Description: {description}

Available genres: rock, pop, edm, classical, jazz, hip_hop, metal, acoustic, indie

Return ONLY a JSON object with this exact format:
{{
  "genre": "genre_name",
  "confidence": 0.95
}}

Choose the single best-fitting genre. Confidence should be 0.0-1.0."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            result = json.loads(text)
            genre = result.get('genre', 'pop').lower().replace(' ', '_').replace('/', '_')
            confidence = float(result.get('confidence', 0.8))
            
            # Validate genre
            if genre not in self.GENRE_PROFILES:
                print(f"⚠️  Unknown genre '{genre}', using fallback")
                genre = 'pop'
                confidence = 0.5
            
            return genre, confidence
            
        except Exception as e:
            print(f"⚠️  Gemini detection failed: {e}")
            return self._detect_with_fallback(title, artist, description)
    
    def _detect_with_fallback(self, title: str, artist: str, description: str) -> Tuple[str, float]:
        """Simple keyword-based genre detection"""
        text = f"{title} {artist} {description}".lower()
        
        # Genre keywords
        keywords = {
            'edm': ['edm', 'electronic', 'dubstep', 'house', 'techno', 'trance', 'bass drop'],
            'rock': ['rock', 'guitar', 'band', 'metal' 'punk'],
            'classical': ['classical', 'orchestra', 'symphony', 'piano', 'violin', 'beethoven', 'mozart'],
            'jazz': ['jazz', 'swing', 'blues', 'saxophone'],
            'hip_hop': ['hip hop', 'rap', 'trap', 'beat', 'rapper'],
            'metal': ['metal', 'heavy', 'death', 'black metal'],
            'acoustic': ['acoustic', 'unplugged', 'folk'],
            'indie': ['indie', 'alternative', 'underground']
        }
        
        # Count matches
        scores = {}
        for genre, words in keywords.items():
            score = sum(1 for word in words if word in text)
            if score > 0:
                scores[genre] = score
        
        if scores:
            genre = max(scores, key=scores.get)
            confidence = min(0.7, scores[genre] / 10)  # Max 70% confidence
            return genre, confidence
        
        # Default to pop
        return 'pop', 0.5


def main():
    """Test genre detector"""
    print("🎵 ORBITUNE - Genre Detector Test\n")
    
    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai not installed")
        print("Install: pip install google-generativeai")
        return
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY not set")
        print("Set it: $env:GEMINI_API_KEY='your-api-key'")
        return
    
    detector = GenreDetector()
    
    # Test with metadata
    from config import STORAGE_BASE
    processed_dir = Path(STORAGE_BASE) / "processed"
    
    if processed_dir.exists():
        song_ids = [d.name for d in processed_dir.iterdir() if d.is_dir()]
        if song_ids:
            song_id = song_ids[0]
            genre, conf, profile = detector.detect_genre(song_id)
            print(f"\n✅ Test complete!")


if __name__ == "__main__":
    main()
