# 🎮 ORBITUNE Usage Guide

## 🚀 Getting Started

### Step 1: Start the Application
```powershell
.\START_ORBITUNE.ps1
```

You'll see a beautiful startup sequence:
```
    ██████╗ ██████╗ ██████╗ ██╗████████╗██╗   ██╗███╗   ██╗███████╗
   ██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝██║   ██║████╗  ██║██╔════╝
   ██║   ██║██████╔╝██████╔╝██║   ██║   ██║   ██║██╔██╗ ██║█████╗  
   ██║   ██║██╔══██╗██╔══██╗██║   ██║   ██║   ██║██║╚██╗██║██╔══╝  
   ╚██████╔╝██║  ██║██████╔╝██║   ██║   ╚██████╔╝██║ ╚████║███████╗
    ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝
                                                                      
            🎵 3D Audio Experience with AI Companion 🤖
```

### Step 2: Wait for Services
The script automatically:
- ✅ Checks your system
- ✅ Installs dependencies
- ✅ Starts backend server
- ✅ Starts frontend server
- ✅ Opens your browser

### Step 3: You're Ready!
Dashboard opens at: **http://localhost:5173/dashboard**

---

## 🎯 Using the Two Modes

### 🔍 Search Mode (Find Music)

**When to use:** You know what song you want

**How it looks:**
```
┌────────────────────────────────────────┐
│  🔍 Search Mode                        │
│  ─────────────────────────────────────│
│  Type: "Bohemian Rhapsody"            │
│                                        │
│  Suggestions appear instantly:         │
│  ▸ Bohemian Rhapsody - Queen          │
│  ▸ Bohemian Rhapsody Live - Queen     │
│  ▸ Bohemian Rhapsody Cover - Panic!   │
└────────────────────────────────────────┘
```

**Steps:**
1. Make sure you're in Search Mode (badge shows 🔍)
2. Type a song name or artist
3. See real-time YouTube suggestions
4. Click a suggestion
5. Wait 30-60 seconds for 3D processing
6. Enjoy spatial audio!

**Example queries:**
- "Bohemian Rhapsody"
- "Ed Sheeran Shape of You"
- "Billie Eilish"
- "Imagine Dragons Believer"

---

### 💬 Chat Mode (Talk to AI)

**When to use:** You want recommendations or conversation

**How it looks:**
```
┌────────────────────────────────────────┐
│  💬 Chat Mode                          │
│  ─────────────────────────────────────│
│  You: "I'm feeling happy today!"      │
│                                        │
│  AI: "That's wonderful! Based on      │
│       your mood, I recommend some     │
│       upbeat songs..."                │
│                                        │
│  Suggestions:                          │
│  🎵 Happy - Pharrell Williams         │
│  🎵 Walking on Sunshine - Katrina     │
└────────────────────────────────────────┘
```

**Steps:**
1. Make sure you're in Chat Mode (badge shows 💬)
2. Type your mood or question
3. Get AI-powered recommendations
4. Click song suggestions to generate 3D audio

**Example queries:**
- "I'm feeling sad"
- "Recommend some workout music"
- "I need music for studying"
- "What's good for a road trip?"
- "I'm in love!"
- "Give me some chill vibes"

---

## ⌨️ Keyboard Shortcuts

### Essential Shortcuts

| Press | What Happens |
|-------|--------------|
| **Tab** | Switch between 🔍 Search and 💬 Chat |
| **Ctrl+Space** | Show/Hide Debug Panel (developers) |
| **Enter** | Send your message |

### Visual Example

```
Current Mode: 🔍 Search Mode

Press Tab ↓

Current Mode: 💬 Chat Mode

Press Tab ↓

Current Mode: 🔍 Search Mode

(Toggle anytime!)
```

---

## 🐛 Developer Debug Panel

### Hidden by Default

The debug panel is **hidden** to keep the UI clean for users.

### How to Open

**Press:** `Ctrl` + `Space` (both keys together)

### What You'll See

```
┌──────────────────────────────────────┐
│ 🎵 Audio Debug Info             [✕] │
│ Press Ctrl+Space to toggle           │
│ ────────────────────────────────────│
│ Track: Bohemian Rhapsody             │
│ Audio URL: ✓ Set                     │
│ State (Context): ▶️ Playing          │
│ State (Element): ▶️ Playing          │
│ Ready State: HAVE_ENOUGH_DATA (4)    │
│ Network State: NETWORK_IDLE (1)      │
│ Volume: 100%                         │
│ Muted: 🔊 No                         │
│ Time: 45.2s / 354.0s                 │
│ Source: ✓                            │
└──────────────────────────────────────┘
```

### When to Use

- ✅ Audio not playing? Check the debug panel
- ✅ Troubleshooting playback issues
- ✅ Understanding audio state
- ✅ Checking network/buffer status

### How to Close

- Press `Ctrl+Space` again
- Or click the **✕** button

---

## 🎵 Complete User Journey

### Scenario 1: "I Know What I Want"

```
1. Start app: .\START_ORBITUNE.ps1
   ↓
2. Dashboard opens automatically
   ↓
3. Press Tab → Switch to 🔍 Search Mode
   ↓
4. Type: "Bohemian Rhapsody"
   ↓
5. Click first suggestion
   ↓
6. Wait for processing (see progress)
   ↓
7. Song plays in 3D! 🎧
```

### Scenario 2: "Recommend Me Something"

```
1. Start app: .\START_ORBITUNE.ps1
   ↓
2. Dashboard opens automatically
   ↓
3. Already in 💬 Chat Mode (default)
   ↓
4. Type: "I'm feeling energetic!"
   ↓
5. AI suggests songs
   ↓
6. Click a suggestion
   ↓
7. 3D audio generates and plays! 🎧
```

### Scenario 3: "Audio Not Working?"

```
1. Press Ctrl+Space
   ↓
2. Debug panel appears
   ↓
3. Check:
   • Audio URL: Should be ✓
   • Ready State: Should be HAVE_ENOUGH_DATA
   • Network State: Should be NETWORK_IDLE
   • Any errors shown?
   ↓
4. Fix issue or check backend logs
   ↓
5. Press Ctrl+Space to hide panel
```

---

## 🎨 Understanding the Interface

### Mode Indicator Badge

**Search Mode:**
```
┌─────────────────┐
│ 🔍 Search Mode  │  ← Blue/Cyan colors
└─────────────────┘
```

**Chat Mode:**
```
┌─────────────────┐
│ 💬 Chat Mode    │  ← Purple/Pink colors
└─────────────────┘
```

### Input Placeholder Changes

**Search Mode:**
> "Search for a song or artist..."

**Chat Mode:**
> "Tell me how you're feeling or what music you'd like..."

### Visual Feedback

**Typing in Search Mode:**
- Suggestions appear in real-time
- YouTube results show instantly

**Typing in Chat Mode:**
- No suggestions (waiting for Enter)
- AI responds after you press Enter

---

## 💡 Pro Tips

### 🎧 Audio Quality
- Use **headphones** for best 3D experience
- High-quality YouTube videos = better audio
- Allow full processing time (don't rush!)

### ⚡ Performance
- First startup: 2-5 minutes (installing dependencies)
- Next startups: Use `.\START_ORBITUNE.ps1 -SkipDependencies`
- Only 10-20 seconds!

### 🔍 Search Tips
- Be specific: "Song - Artist" works best
- Try official videos for better quality
- Use exact song titles when possible

### 💬 Chat Tips
- Describe your mood in detail
- Ask for specific genres
- Tell the AI your preferences
- Build a conversation over time

### 🐛 Debugging
- Can't hear audio? Check debug panel
- Backend issues? Check the backend window
- Frontend issues? Check browser console (F12)

---

## 🛑 Stopping the Application

### Method 1: Close Windows
Simply close the two PowerShell windows that opened:
- 🐍 Backend Server window
- ⚛️ Frontend Dashboard window

### Method 2: Ctrl+C
In each PowerShell window:
1. Click in the window
2. Press `Ctrl + C`
3. Wait for graceful shutdown

---

## 📊 What's Happening Behind the Scenes

### When You Search a Song

```
You type → YouTube API → Suggestions appear
   ↓
You click → Download audio → Separate stems
   ↓
Process 3D → Spatial audio → Play!
```

**Time:** ~30-60 seconds

### When You Chat with AI

```
You type → Gemini AI → Analyze intent
   ↓
Generate → Recommend → Display songs
```

**Time:** ~2-5 seconds

---

## 🎉 Fun Things to Try

### Mood-Based Exploration
```
"I'm feeling nostalgic" → Get classics
"I need energy" → Get upbeat tracks
"Feeling romantic" → Get love songs
"Need focus" → Get lo-fi/ambient
```

### Genre Discovery
```
"Introduce me to jazz"
"What's good in EDM?"
"Best country songs?"
"Show me classical music"
```

### Conversational AI
```
You: "I like rock music"
AI: "Great! Any specific era?"
You: "80s rock"
AI: "Here are some 80s rock classics..."
```

---

## 📚 Additional Resources

- **Full Documentation**: [README.md](README.md)
- **Quick Reference**: [QUICK_START.md](QUICK_START.md)
- **Technical Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

---

## ⚠️ Common Questions

**Q: Why does 3D processing take so long?**
A: We're separating audio into stems (vocals, drums, bass, other) and creating spatial positioning. Quality takes time!

**Q: Can I skip the processing?**
A: No, but once processed, songs are saved and play instantly next time.

**Q: Debug panel won't appear?**
A: Make sure a track is loaded first. Panel only appears when audio is active.

**Q: How do I know which mode I'm in?**
A: Look at the badge at the top of the input area: 🔍 Search or 💬 Chat

**Q: Can I use both modes together?**
A: They're separate for clarity. Press Tab to switch anytime!

---

<div align="center">

**🎵 Enjoy Your 3D Audio Journey! 🚀**

Made with ❤️ for music lovers and developers

</div>
