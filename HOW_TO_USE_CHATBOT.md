# 🎯 ORBITUNE Chatbot - Strict Mode Guide

## 🔑 Key Concept: Strict Mode Separation

The chatbot now has **STRICT mode separation**:
- **Search Mode (🔍)** = ONLY YouTube song search
- **Chat Mode (💬)** = ONLY AI chatbot conversations

**No mixing!** Each mode does one thing perfectly.

---

## 🔍 Search Mode - YouTube Song Search

### What It Does:
- Searches YouTube for songs in real-time
- Shows live suggestions as you type
- Click a suggestion to generate 3D audio

### How to Use:
1. **Ensure you're in Search Mode** (blue badge at top)
2. Type any song name or artist: `"Imagine Dragons"`
3. YouTube suggestions appear automatically
4. Click a suggestion to generate 3D audio

### Behavior:
- ✅ Triggers YouTube API search
- ✅ Shows song thumbnails and details
- ✅ Real-time suggestions (updates as you type)
- ❌ Does NOT call chatbot API
- ❌ Does NOT have AI conversations

### Example Queries:
- `"Bohemian Rhapsody"`
- `"Arijit Singh"`
- `"Taylor Swift - Shake It Off"`
- `"Beatles"`

### Quick Hints (Click to search):
- 🔍 Bohemian Rhapsody
- 🔍 Imagine Dragons
- 🔍 Arijit Singh
- 🔍 Beatles

---

## 💬 Chat Mode - AI Conversations

### What It Does:
- Talks to Gemini AI chatbot
- Understands your mood and feelings
- Recommends songs from backend database
- Natural conversations about music

### How to Use:
1. **Press Tab** to switch to Chat Mode (purple badge)
2. Type anything: `"I'm feeling happy today!"`
3. Press Enter or click Send
4. AI responds with personalized message
5. If AI recommends songs, they appear as clickable cards

### Behavior:
- ✅ Sends message to Gemini AI backend
- ✅ Gets conversational responses
- ✅ Receives song recommendations from AI
- ✅ Opens chat window to show conversation
- ❌ Does NOT search YouTube
- ❌ Does NOT show YouTube suggestions

### Example Queries:
- `"Hey, how are you?"`
- `"I'm feeling energetic"`
- `"Recommend me some chill music"`
- `"What should I listen to for studying?"`
- `"I love romantic songs"`

### Quick Hints (Click to chat):
- 💬 I feel energetic
- 💬 Chill vibes
- 💬 Something romantic
- 💬 Recommend music

---

## ⌨️ Tab Key = Mode Switcher

### Switching Modes:
**Press Tab on your keyboard** to toggle between modes instantly!

### Visual Indicators:
**Search Mode:**
- Blue badge: `🔍 Search Mode`
- Blue border around input
- Placeholder: "🔍 Search for a song or artist..."
- Status: "Type to search songs"

**Chat Mode:**
- Purple badge: `💬 Chat Mode`
- Purple border around input
- Placeholder: "💬 Tell me what you're feeling or ask anything..."
- Status: "Ready to chat"

---

## 🎯 Complete User Flows

### Flow 1: Search for a Song
```
1. Start in Search Mode (default)
2. Type: "Imagine Dragons"
3. See YouTube suggestions appear
4. Click: "Imagine Dragons - Believer"
5. 3D audio processing starts
6. Song plays in 3D
```

### Flow 2: Chat with AI
```
1. Press Tab → Switch to Chat Mode
2. Type: "I'm feeling happy today!"
3. Press Enter
4. AI responds: "Yo! Happy vibes! 🎵 Want some upbeat tracks?"
5. Continue conversation or get recommendations
```

### Flow 3: Get AI Recommendations
```
1. Press Tab → Chat Mode
2. Type: "Recommend some romantic songs"
3. AI responds with song suggestions
4. Song cards appear below AI message
5. Click a song card to play it in 3D
```

### Flow 4: Quick Hints
```
Search Mode:
- Click "🔍 Bohemian Rhapsody" → YouTube search starts

Chat Mode:
- Click "💬 I feel energetic" → AI responds immediately
```

---

## 🔄 Mode Comparison

| Feature | Search Mode 🔍 | Chat Mode 💬 |
|---------|---------------|--------------|
| **Primary Function** | YouTube song search | AI chatbot conversation |
| **Input Trigger** | Type to search | Type to chat |
| **Response** | YouTube suggestions | AI text response |
| **Song Source** | YouTube | Backend database |
| **Real-time Updates** | Yes (as you type) | No (press Enter) |
| **API Called** | `/api/youtube/search` | `/api/chatbot/chat` |
| **Visual Feedback** | "Searching YouTube..." | "AI is thinking..." |

---

## 🎨 UI Elements Explained

### Mode Badge (Top of Input)
Shows current mode with icon and text:
- `🔍 Search Mode` = Blue background
- `💬 Chat Mode` = Purple background

### Tab Hint
"Press `Tab` to switch" - Always visible reminder

### Input Placeholder
Changes based on mode:
- Search: "🔍 Search for a song or artist..."
- Chat: "💬 Tell me what you're feeling or ask anything..."

### Input Border Color
- Search Mode: Blue glow
- Chat Mode: Purple glow

### Status Indicator (Above Input)
Shows what's happening:
- Search Mode:
  - "Type to search songs" (idle)
  - "Searching YouTube..." (searching)
- Chat Mode:
  - "Ready to chat" (idle)
  - "AI is thinking..." (processing)

### Quick Hints (Below Input)
Mode-specific quick actions:
- Search: 🔍 Song names
- Chat: 💬 Conversation starters

---

## 🚀 Pro Tips

### For Search Mode:
1. **Type at least 3 characters** for suggestions to appear
2. **Suggestions update live** as you type more
3. **Click any suggestion** to start 3D processing
4. **Press Enter without clicking** to acknowledge search (suggestions remain)

### For Chat Mode:
1. **Be conversational** - AI understands natural language
2. **Describe your mood** - AI tailors recommendations
3. **Ask questions** - AI can explain music concepts
4. **Click song cards** - If AI suggests songs, click to play

### General:
1. **Tab is your friend** - Switch modes anytime
2. **Watch the indicators** - Know which mode you're in
3. **Use quick hints** - Fast way to try features
4. **Backend must be running** - Chat mode needs API server

---

## ❓ FAQ

### Q: Can I search for songs in Chat Mode?
**A:** No! Chat Mode is strictly for AI conversations. Press Tab to switch to Search Mode.

### Q: Can I chat with AI in Search Mode?
**A:** No! Search Mode is strictly for YouTube search. Press Tab to switch to Chat Mode.

### Q: What if I want AI to search YouTube?
**A:** In Chat Mode, tell AI what you want (e.g., "Find me happy songs"). AI will recommend songs from the backend database. If you want YouTube search, switch to Search Mode.

### Q: Do the quick hints work in any mode?
**A:** No! Hints change based on mode:
- Search Mode: Song search hints (🔍)
- Chat Mode: Conversation hints (💬)

### Q: What happens if backend is down?
**A:** 
- Search Mode: Still works (uses YouTube API directly)
- Chat Mode: Shows error message: "Please make sure backend server is running!"

### Q: Can AI recommend songs it finds on YouTube?
**A:** No. AI recommends from your backend database. For YouTube search, use Search Mode and click suggestions.

---

## 🔧 Technical Details

### Search Mode Implementation:
```typescript
// Only searches when in Search Mode
triggerSearch(value) {
  if (inputMode !== 'search') return; // Guard clause
  // ... YouTube search logic
}
```

### Chat Mode Implementation:
```typescript
// Only chats when in Chat Mode
if (inputMode === 'chat') {
  await sendChatMessage(userId, input);
  // ... chatbot response handling
}
```

### Mode Switching:
```typescript
// Tab key handler
if (e.key === 'Tab') {
  e.preventDefault();
  setInputMode(prev => prev === 'search' ? 'chat' : 'search');
}
```

---

## ✅ Summary

### Search Mode (🔍):
- **ONE JOB**: YouTube song search
- **INPUT**: Song names, artists
- **OUTPUT**: YouTube suggestions
- **ACTION**: Click to generate 3D audio

### Chat Mode (💬):
- **ONE JOB**: AI chatbot conversations
- **INPUT**: Natural language, moods, questions
- **OUTPUT**: AI text responses, song recommendations
- **ACTION**: Continue conversation or click song cards

### Tab Key:
- **ONE JOB**: Switch between modes instantly

**Simple. Clean. Perfect.** 🎯

---

## 🎊 You're Ready!

1. Start both servers (backend + frontend)
2. Open http://localhost:5173/dashboard
3. See Search Mode by default
4. Press Tab to switch to Chat Mode
5. Enjoy your perfect music companion!

🎵 Happy listening! ✨
