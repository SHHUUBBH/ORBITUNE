"""
Conversation Memory Manager for ORBITUNE Chatbot
Manages chat history with smart sliding window and long-term summarization
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path
import json
import sys

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from chatbot.utils import generate_message_id, truncate_text


class ConversationMemory:
    """
    Manages conversation history with efficient memory usage
    
    Features:
    - Sliding window: Keep last N messages in active context
    - Long-term summary: Compress old conversations into key facts
    - Fast retrieval: Optimized for chatbot context building
    """
    
    def __init__(self, history_path: Path, window_size: int = 15, max_history: int = 500):
        """
        Initialize conversation memory
        
        Args:
            history_path: Path to chat_history.json
            window_size: Number of recent messages to keep in active context
            max_history: Maximum total messages to store per user
        """
        self.history_path = history_path
        self.window_size = window_size
        self.max_history = max_history
        self.history_cache: Dict[str, List[Dict]] = {}  # {userId: [messages]}
        self._load_history()
    
    def _load_history(self):
        """Load chat history from disk"""
        try:
            if self.history_path.exists():
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history_cache = data.get('conversations', {})
                print(f"✅ Loaded chat history for {len(self.history_cache)} users")
            else:
                self.history_cache = {}
                self._save_history()
        except Exception as e:
            print(f"⚠️  Error loading chat history: {e}")
            self.history_cache = {}
    
    def _save_history(self):
        """Save chat history to disk"""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump({'conversations': self.history_cache}, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving chat history: {e}")
    
    def add_message(self, user_id: str, message: str, sender: str, intent: str = 'chat', metadata: Optional[Dict] = None) -> str:
        """
        Add a message to conversation history
        
        Args:
            user_id: User ID
            message: Message content
            sender: 'user' or 'bot'
            intent: Message intent ('search', 'chat', 'hybrid')
            metadata: Additional metadata (search results, etc.)
        
        Returns:
            Message ID
        """
        if user_id not in self.history_cache:
            self.history_cache[user_id] = []
        
        message_id = generate_message_id()
        
        msg_obj = {
            'id': message_id,
            'message': message,
            'sender': sender,
            'intent': intent,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.history_cache[user_id].append(msg_obj)
        
        # Trim old messages if exceeding max_history
        if len(self.history_cache[user_id]) > self.max_history:
            self.history_cache[user_id] = self.history_cache[user_id][-self.max_history:]
        
        self._save_history()
        return message_id
    
    def get_recent_messages(self, user_id: str, limit: Optional[int] = None) -> List[Dict]:
        """
        Get recent messages from conversation
        
        Args:
            user_id: User ID
            limit: Number of messages (default: window_size)
        
        Returns:
            List of recent messages
        """
        if user_id not in self.history_cache:
            return []
        
        limit = limit or self.window_size
        return self.history_cache[user_id][-limit:]
    
    def get_conversation_context(self, user_id: str, include_metadata: bool = False) -> str:
        """
        Build conversation context string for chatbot
        
        Args:
            user_id: User ID
            include_metadata: Include intent and metadata in context
        
        Returns:
            Formatted conversation history string
        """
        recent_messages = self.get_recent_messages(user_id)
        
        if not recent_messages:
            return "No previous conversation"
        
        context_parts = []
        
        for msg in recent_messages:
            sender = "User" if msg['sender'] == 'user' else "You"
            message = msg['message']
            
            if include_metadata:
                intent = msg.get('intent', 'chat')
                context_parts.append(f"{sender} [{intent}]: {message}")
            else:
                context_parts.append(f"{sender}: {message}")
        
        return "\n".join(context_parts)
    
    def get_conversation_summary(self, user_id: str) -> str:
        """
        Generate summary of older conversation (before the sliding window)
        
        Returns:
            Summary string of key facts from older messages
        """
        if user_id not in self.history_cache:
            return ""
        
        all_messages = self.history_cache[user_id]
        
        # If we have more messages than window, summarize the older ones
        if len(all_messages) > self.window_size:
            older_messages = all_messages[:-self.window_size]
            
            # Extract key facts (this is a simple version, could use Gemini for better summaries)
            key_facts = []
            
            for msg in older_messages:
                # Look for preference mentions
                if msg['sender'] == 'user':
                    message_lower = msg['message'].lower()
                    if any(word in message_lower for word in ['love', 'like', 'favorite', 'hate', 'dislike']):
                        key_facts.append(truncate_text(msg['message'], 80))
            
            if key_facts:
                # Keep only last 5 key facts
                return "Previous mentions: " + " | ".join(key_facts[-5:])
        
        return ""
    
    def get_full_context(self, user_id: str) -> Dict:
        """
        Get complete context including recent messages and summary
        
        Returns:
            Dict with recent_context, summary, and stats
        """
        recent_messages = self.get_recent_messages(user_id)
        summary = self.get_conversation_summary(user_id)
        
        stats = {
            'total_messages': len(self.history_cache.get(user_id, [])),
            'recent_count': len(recent_messages),
            'has_summary': bool(summary)
        }
        
        return {
            'recent_context': self.get_conversation_context(user_id),
            'summary': summary,
            'stats': stats
        }
    
    def clear_history(self, user_id: str):
        """Clear conversation history for a user"""
        if user_id in self.history_cache:
            self.history_cache[user_id] = []
            self._save_history()
    
    def get_last_user_message(self, user_id: str) -> Optional[Dict]:
        """Get the last message sent by user"""
        recent = self.get_recent_messages(user_id, limit=20)
        for msg in reversed(recent):
            if msg['sender'] == 'user':
                return msg
        return None
    
    def get_last_bot_message(self, user_id: str) -> Optional[Dict]:
        """Get the last message sent by bot"""
        recent = self.get_recent_messages(user_id, limit=20)
        for msg in reversed(recent):
            if msg['sender'] == 'bot':
                return msg
        return None
    
    def get_conversation_topics(self, user_id: str, limit: int = 50) -> List[str]:
        """
        Extract topics discussed in recent conversation
        
        Returns:
            List of topics (genres, artists, moods mentioned)
        """
        if user_id not in self.history_cache:
            return []
        
        recent = self.history_cache[user_id][-limit:]
        
        topics = []
        music_keywords = ['jazz', 'rock', 'pop', 'classical', 'hip hop', 'electronic', 
                         'bollywood', 'metal', 'country', 'indie', 'r&b', 'soul']
        mood_keywords = ['happy', 'sad', 'chill', 'energetic', 'calm', 'romantic', 
                        'upbeat', 'melancholy', 'peaceful']
        
        for msg in recent:
            if msg['sender'] == 'user':
                message_lower = msg['message'].lower()
                
                # Check for music genres
                for keyword in music_keywords:
                    if keyword in message_lower and keyword not in topics:
                        topics.append(keyword)
                
                # Check for moods
                for keyword in mood_keywords:
                    if keyword in message_lower and keyword not in topics:
                        topics.append(keyword)
        
        return topics
    
    def has_discussed_topic(self, user_id: str, topic: str, recent_count: int = 10) -> bool:
        """
        Check if a topic was discussed recently
        
        Args:
            user_id: User ID
            topic: Topic to search for
            recent_count: How many recent messages to check
        
        Returns:
            True if topic was mentioned
        """
        recent = self.get_recent_messages(user_id, limit=recent_count)
        topic_lower = topic.lower()
        
        for msg in recent:
            if topic_lower in msg['message'].lower():
                return True
        
        return False
    
    def get_conversation_style(self, user_id: str) -> Dict:
        """
        Analyze user's conversation style
        
        Returns:
            Dict with style indicators (casual, formal, enthusiastic, etc.)
        """
        if user_id not in self.history_cache:
            return {'style': 'unknown', 'indicators': []}
        
        user_messages = [m for m in self.history_cache[user_id][-30:] if m['sender'] == 'user']
        
        if not user_messages:
            return {'style': 'unknown', 'indicators': []}
        
        # Analyze style
        total_messages = len(user_messages)
        
        # Count style indicators
        casual_count = 0
        enthusiastic_count = 0
        question_count = 0
        
        for msg in user_messages:
            message = msg['message']
            message_lower = message.lower()
            
            # Casual indicators
            if any(word in message_lower for word in ['bro', 'dude', 'yo', 'lol', 'haha']):
                casual_count += 1
            
            # Enthusiastic indicators
            if any(char in message for char in ['!', '😊', '🔥', '✨', '💯']):
                enthusiastic_count += 1
            
            # Questions
            if '?' in message:
                question_count += 1
        
        # Determine style
        style = 'neutral'
        indicators = []
        
        if casual_count / total_messages > 0.3:
            style = 'casual'
            indicators.append('uses casual language')
        
        if enthusiastic_count / total_messages > 0.4:
            indicators.append('enthusiastic')
        
        if question_count / total_messages > 0.5:
            indicators.append('inquisitive')
        
        return {
            'style': style,
            'indicators': indicators,
            'stats': {
                'casual_ratio': round(casual_count / total_messages, 2),
                'enthusiastic_ratio': round(enthusiastic_count / total_messages, 2),
                'question_ratio': round(question_count / total_messages, 2)
            }
        }


# Example usage
if __name__ == "__main__":
    from pathlib import Path
    
    # Test memory manager
    test_path = Path("test_chat_history.json")
    memory = ConversationMemory(test_path, window_size=5)
    
    # Simulate conversation
    memory.add_message('user123', "Hey! What's up?", 'user', 'chat')
    memory.add_message('user123', "Yo! Not much, just vibing to some tunes 🎵", 'bot', 'chat')
    memory.add_message('user123', "Nice! Can you play some chill music?", 'user', 'hybrid')
    memory.add_message('user123', "For sure bro! Here's some chill vibes for you", 'bot', 'search', 
                       {'songs': ['song1', 'song2']})
    memory.add_message('user123', "I love Arijit Singh!", 'user', 'chat')
    memory.add_message('user123', "Yooo Arijit is fire! 🔥 His voice is amazing", 'bot', 'chat')
    
    # Get context
    context = memory.get_conversation_context('user123')
    print(f"\n💬 Conversation Context:\n{context}\n")
    
    # Get full context
    full_context = memory.get_full_context('user123')
    print(f"📊 Full Context:\n{json.dumps(full_context, indent=2)}\n")
    
    # Get conversation style
    style = memory.get_conversation_style('user123')
    print(f"🎭 Conversation Style:\n{json.dumps(style, indent=2)}\n")
    
    # Cleanup
    test_path.unlink()
