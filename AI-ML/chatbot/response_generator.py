"""
Response Generator for ORBITUNE Chatbot
Powered by Gemini Flash 2.0 with friendly, casual personality
"""

from typing import Dict, Optional, List
from pathlib import Path
import sys
import os

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# Gemini AI
try:
    import google.generativeai as genai
    from config import GEMINI_API_KEY
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not installed")

from chatbot.utils import response_cache, hash_text, get_time_of_day, extract_mood


class ResponseGenerator:
    """
    Generates conversational responses using Gemini Flash 2.0
    
    Features:
    - Friend-like personality (casual, warm, enthusiastic)
    - Context-aware responses
    - Caching for common queries
    - Streaming support for faster perceived response
    """
    
    def __init__(self):
        """Initialize response generator with Gemini"""
        self.model = None
        self.api_available = False
        
        if GEMINI_AVAILABLE and GEMINI_API_KEY:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Use Gemini 2.0 Flash
                self.model = genai.GenerativeModel('models/gemini-2.0-flash')
                self.api_available = True
                print("✅ Gemini 2.0 Flash initialized for chatbot")
            except Exception as e:
                print(f"⚠️  Gemini initialization error: {e}")
                self.api_available = False
        else:
            print("⚠️  Gemini API not available (set GEMINI_API_KEY environment variable)")
    
    def _build_system_prompt(self, user_context: Dict) -> str:
        """
        Build system prompt with user context
        
        Args:
            user_context: Dict with user profile, recent songs, conversation context
        
        Returns:
            System prompt string
        """
        time_of_day = get_time_of_day()
        
        # Base personality
        base_prompt = f"""You are ORBITUNE's AI music buddy - a super chill, enthusiastic friend who LOVES music and vibes. 

🎭 YOUR PERSONALITY:
- Talk like a CLOSE FRIEND: casual, warm, supportive
- Use friendly slang naturally: "dude", "bro", "yo", "man", "honestly", "like"
- Get EXCITED about music: "Yooo that's fire!", "This slaps!", "Absolute banger!"
- Be genuinely curious: "What's the vibe today?", "Feeling adventurous?"
- Share music knowledge CASUALLY: "Fun fact: this artist...", "Oh dude, you gotta hear..."
- Use emojis naturally but DON'T overdo it: 🎵 🔥 ✨ 💯 🎧 😎 

⚡ YOUR BEHAVIOR:
- Keep responses SHORT (1-3 sentences usually, max 5)
- Be PROACTIVE: suggest songs based on mood/time/context
- REMEMBER everything they told you: "Last week you loved that jazz track!"
- Match their energy: if they're excited → be excited, if they're chill → be chill
- Current time context: It's {time_of_day} right now

🚫 NEVER:
- Be overly formal or robotic
- Write long paragraphs
- Say things like "As an AI..." or "I'm here to help"
- Give generic responses
- Repeat the same phrases too much

"""
        
        # Add user context if available
        if user_context:
            profile_summary = user_context.get('profile_summary', '')
            recent_songs = user_context.get('recent_songs', [])
            conversation_history = user_context.get('conversation_history', '')
            conversation_style = user_context.get('conversation_style', {})
            
            if profile_summary:
                base_prompt += f"\n👤 USER PROFILE:\n{profile_summary}\n"
            
            if recent_songs:
                songs_str = ', '.join([f"{s.get('title', 'Unknown')} by {s.get('artist', 'Unknown')}" 
                                      for s in recent_songs[-3:]])
                base_prompt += f"\n🎵 RECENTLY PLAYED:\n{songs_str}\n"
            
            if conversation_history:
                base_prompt += f"\n💬 RECENT CONVERSATION:\n{conversation_history}\n"
            
            # Adapt to user's style
            style = conversation_style.get('style', 'neutral')
            if style == 'casual':
                base_prompt += "\n(User is very casual - match their vibe with casual language!)\n"
            elif style == 'formal':
                base_prompt += "\n(User is more formal - keep it friendly but slightly less slang)\n"
        
        return base_prompt
    
    def generate_response(
        self, 
        user_message: str, 
        intent: str,
        user_context: Optional[Dict] = None,
        use_cache: bool = True
    ) -> str:
        """
        Generate response to user message
        
        Args:
            user_message: User's message
            intent: Message intent ('chat', 'search', 'hybrid')
            user_context: User profile and conversation context
            use_cache: Whether to use cached responses
        
        Returns:
            Bot response string
        """
        # Check cache first
        if use_cache:
            cache_key = hash_text(f"{user_message}_{intent}")
            cached = response_cache.get(cache_key)
            if cached:
                return cached
        
        # Handle special cases
        if self._is_greeting(user_message):
            return self._generate_greeting_response(user_context)
        
        if self._is_farewell(user_message):
            return self._generate_farewell_response()
        
        # Generate contextual response
        if not self.api_available:
            return self._generate_fallback_response(user_message, intent, user_context)
        
        try:
            # Build prompt
            system_prompt = self._build_system_prompt(user_context or {})
            
            # Add intent-specific guidance
            if intent == 'search' or intent == 'hybrid':
                system_prompt += "\n\n⚠️ USER WANTS TO FIND/PLAY MUSIC - acknowledge and be enthusiastic about helping them!\n"
            
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nYou (respond as ORBITUNE's buddy):"
            
            # Generate with Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.9,  # Creative and varied
                    'max_output_tokens': 150,  # Keep it short
                    'top_p': 0.95,
                    'top_k': 40
                }
            )
            
            bot_response = response.text.strip()
            
            # Cache the response
            if use_cache:
                response_cache.set(cache_key, bot_response)
            
            return bot_response
            
        except Exception as e:
            print(f"⚠️  Gemini generation error: {e}")
            return self._generate_fallback_response(user_message, intent, user_context)
    
    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'yo', 'sup', 'whats up', "what's up", 'howdy']
        message_lower = message.lower().strip()
        return any(message_lower.startswith(g) for g in greetings) or message_lower in greetings
    
    def _is_farewell(self, message: str) -> bool:
        """Check if message is a farewell"""
        farewells = ['bye', 'goodbye', 'see you', 'later', 'peace', 'cya', 'gotta go']
        message_lower = message.lower().strip()
        return any(farewell in message_lower for farewell in farewells)
    
    def _generate_greeting_response(self, user_context: Optional[Dict]) -> str:
        """Generate personalized greeting"""
        time = get_time_of_day()
        
        greetings = {
            'morning': ["Yo good morning! ☀️", "Hey! Morning vibes, what's good?", "Morning dude! Ready for some tunes?"],
            'afternoon': ["Hey! What's up?", "Yo! How's it going?", "Hey dude! What's the vibe?"],
            'evening': ["Hey! Evening vibes 🌆", "Yo! How's your evening?", "What's up! Chilling?"],
            'night': ["Hey! Late night session? 🌙", "Yo! Night owl vibes", "What's good! Can't sleep?"]
        }
        
        import random
        base_greeting = random.choice(greetings.get(time, greetings['afternoon']))
        
        # Add personalization if we have context
        if user_context and user_context.get('profile_summary'):
            recent_songs = user_context.get('recent_songs', [])
            if recent_songs:
                return f"{base_greeting} Wanna continue where we left off? 🎵"
        
        return f"{base_greeting} What are you in the mood for?"
    
    def _generate_farewell_response(self) -> str:
        """Generate farewell response"""
        import random
        farewells = [
            "Peace out! Catch you later 🎵",
            "See ya dude! Keep vibing ✨",
            "Later! Come back anytime 🎧",
            "Bye bro! Stay awesome 💯",
            "Catch you later! Keep the music playing 🔥"
        ]
        return random.choice(farewells)
    
    def _generate_fallback_response(self, message: str, intent: str, user_context: Optional[Dict]) -> str:
        """Generate fallback response when Gemini is unavailable"""
        import random
        
        if intent == 'search' or intent == 'hybrid':
            responses = [
                "I got you! Let me find that for you 🎵",
                "On it! Searching for some fire tracks 🔥",
                "Bet! Let me pull that up ✨",
                "Say less! Finding that right now 💯"
            ]
        else:
            # Extract mood if present
            mood = extract_mood(message)
            
            if mood:
                responses = [
                    f"I feel you on that {mood} vibe! 🎵",
                    f"{mood.capitalize()} mood? I got the perfect vibes for that",
                    f"Oh for sure, {mood} energy! Let's find something that matches"
                ]
            else:
                responses = [
                    "Yo I feel you! Music is life 🎵",
                    "For real! That's what I'm talking about 💯",
                    "Honestly same! Music just hits different 🔥",
                    "Yoo that's dope! Tell me more ✨"
                ]
        
        return random.choice(responses)
    
    def generate_song_search_response(self, query: str, found_songs: List[Dict]) -> str:
        """
        Generate response for song search results
        
        Args:
            query: User's search query
            found_songs: List of songs found
        
        Returns:
            Response string
        """
        if not found_songs:
            return f"Hmm, couldn't find anything for '{query}' 🤔 Try something else? Or describe the vibe you want!"
        
        count = len(found_songs)
        
        if count == 1:
            song = found_songs[0]
            return f"Found it! {song.get('title')} by {song.get('artist')} 🎵 This one's fire!"
        else:
            responses = [
                f"Yo! Found {count} bangers for you 🔥",
                f"Nice! Got {count} tracks that match 💯",
                f"Here you go! {count} songs for ya ✨",
                f"Found {count} hits! Check these out 🎧"
            ]
            import random
            return random.choice(responses)
    
    def generate_recommendation_response(self, context: Dict) -> str:
        """
        Generate personalized recommendation
        
        Args:
            context: User context for recommendations
        
        Returns:
            Recommendation string
        """
        time = get_time_of_day()
        favorite_genres = context.get('favorite_genres', [])
        
        if favorite_genres:
            genre = favorite_genres[0]
            return f"Based on your {genre} vibes, I got some fresh tracks for you! 🔥"
        
        time_suggestions = {
            'morning': "Morning energy! Got some uplifting tracks to start your day ☀️",
            'afternoon': "Afternoon vibes! Here's something to keep you going 🎵",
            'evening': "Evening chill! Got some smooth tracks for unwinding 🌆",
            'night': "Late night mood! These hits will keep you company 🌙"
        }
        
        return time_suggestions.get(time, "Got some fire recommendations for you! 🔥")


# Example usage
if __name__ == "__main__":
    generator = ResponseGenerator()
    
    # Test responses
    test_cases = [
        ("Hey what's up?", 'chat', None),
        ("Play some chill music", 'hybrid', {'profile_summary': 'Loves: Bollywood, Pop'}),
        ("I love Arijit Singh!", 'chat', None),
        ("Find songs by Dua Lipa", 'search', None),
    ]
    
    print("\n🤖 Testing Response Generator:\n")
    for message, intent, context in test_cases:
        response = generator.generate_response(message, intent, context)
        print(f"User: {message}")
        print(f"Bot [{intent}]: {response}\n")
