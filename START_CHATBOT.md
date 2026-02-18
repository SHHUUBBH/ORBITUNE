# 🚀 ORBITUNE Chatbot Startup Guide

## Overview
The chatbot is now fully integrated! You can switch between **Search Mode** and **Chat Mode** using the **Tab** key.

## Features Implemented ✅
1. **Tab Key Switching**: Press Tab to toggle between Search and Chat modes
2. **Visual Mode Indicators**: Clear badges showing current mode (Search 🔍 or Chat 💬)
3. **Gemini AI Integration**: Powered by Gemini Flash 2.0 for natural conversations
4. **Smart Intent Detection**: Automatically detects if you want to search songs or chat
5. **Song Recommendations**: AI can suggest songs based on your mood

## How to Use

### Search Mode (🔍)
- Search for songs on YouTube
- Get instant suggestions while typing
- Click a song to generate 3D audio

### Chat Mode (💬)
- Talk to the AI about your mood, feelings, or music preferences
- Ask for song recommendations
- Get personalized music suggestions
- Have natural conversations about music

### Switching Modes
**Press the Tab key** on your keyboard to switch between modes!

## Starting the Application

### 1. Start the Backend Server (Python)

```powershell
# Navigate to the BACKEND directory
cd "D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\BACKEND\src"

# Activate virtual environment (if you have one)
# For example: 
# ..\..\..\AI-ML\venv\Scripts\Activate.ps1

# Install dependencies if not already installed
pip install -r ..\..\AI-ML\requirements.txt

# Start the FastAPI server
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

**Expected output:**
```
🤖 Initializing ORBITUNE Chatbot...
✅ Loaded environment variables from D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\.env
✅ Gemini Flash 2.0 initialized for chatbot
✅ Chatbot initialized and ready!

INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Start the Frontend Dashboard (React/Vite)

Open a **new terminal** and run:

```powershell
# Navigate to the dashboard directory
cd "D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\FRONTEND\dashboard\orbitune-sonic-verse-main"

# Install dependencies if not already installed
npm install

# Start the development server
npm run dev
```

**Expected output:**
```
VITE v5.x.x ready in xxx ms

➜  Local:   http://localhost:5173/
```

### 3. Open the Application
Open your browser and go to: **http://localhost:5173/dashboard**

## Testing the Chatbot

### Test Chat Mode:
1. Press **Tab** to switch to Chat Mode (💬)
2. Try these messages:
   - "Hey, how are you?"
   - "I'm feeling happy today"
   - "Recommend me some chill music"
   - "What's trending?"

### Test Search Mode:
1. Press **Tab** to switch to Search Mode (🔍)
2. Type a song name or artist
3. Click on a suggestion to generate 3D audio

## Troubleshooting

### Chatbot not responding?
**Check if backend is running:**
```powershell
# Test the chatbot health endpoint
curl http://127.0.0.1:8000/api/chatbot/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "gemini_available": true,
  "components": {
    "intent_detector": true,
    "user_profiler": true,
    "conversation_memory": true,
    "response_generator": true
  }
}
```

### Error: "GEMINI_API_KEY not found"
**Check your .env file:**
```powershell
# View the .env file
cat "D:\YUVRAJ\YUVRAJ PROJECTS\ORBITUNE_front\ORBITUNE\.env"
```

Make sure it contains:
```
GEMINI_API_KEY=AIzaSyDezZ6Egk35D7DUiJEkp9DEjbDhQZCNYwE
```

### Port 8000 already in use?
```powershell
# Find and kill the process using port 8000
netstat -ano | findstr :8000
# Note the PID and kill it
taskkill /PID <PID> /F
```

## API Endpoints

### Chatbot Endpoints
- `POST /api/chatbot/chat` - Send message to chatbot
- `GET /api/chatbot/history/{user_id}` - Get conversation history
- `GET /api/chatbot/profile/{user_id}` - Get user profile
- `GET /api/chatbot/health` - Check chatbot health

### Song Endpoints
- `GET /api/songs` - Get all processed songs
- `POST /api/songs/from-youtube` - Create 3D audio from YouTube
- `GET /api/youtube/search` - Search YouTube for songs

## Architecture

```
┌─────────────────────────────────────────┐
│          React Frontend (5173)          │
│  ┌─────────────────────────────────┐   │
│  │   ConversationalInput.tsx       │   │
│  │   - Tab key switching           │   │
│  │   - Mode indicators             │   │
│  │   - YouTube search OR chatbot   │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTP Requests
               ▼
┌─────────────────────────────────────────┐
│        FastAPI Backend (8000)           │
│  ┌─────────────────────────────────┐   │
│  │   /api/chatbot/chat             │   │
│  │   - Receives user message       │   │
│  │   - Calls ChatbotService        │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│     AI-ML/chatbot/chatbot_service.py    │
│  ┌─────────────────────────────────┐   │
│  │   Intent Detection              │   │
│  │   User Profiling                │   │
│  │   Conversation Memory           │   │
│  │   Response Generation (Gemini)  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## What's New? 🎉

### Frontend Changes:
- ✅ Added Tab key handler in `ConversationalInput.tsx`
- ✅ Mode indicator badges (Search/Chat)
- ✅ Color-coded input borders
- ✅ Different placeholders for each mode
- ✅ Loading state ("AI is thinking...")
- ✅ Chat mode calls `/api/chatbot/chat` endpoint
- ✅ Search mode calls YouTube API

### Backend Integration:
- ✅ Added `sendChatMessage()` function in `api.ts`
- ✅ Proper error handling with user-friendly messages
- ✅ Message display in chat window
- ✅ Song recommendations from chatbot

### Visual Improvements:
- ✅ "Press Tab to switch" hint
- ✅ Mode-specific icons (🔍 Search, 💬 Chat)
- ✅ Animated loading indicators
- ✅ Smooth mode transitions

## Need Help?
If you encounter any issues:
1. Check if both servers are running (backend on 8000, frontend on 5173)
2. Verify .env file has GEMINI_API_KEY
3. Check browser console for errors (F12)
4. Check backend terminal for error messages

Enjoy your intelligent music companion! 🎵✨
