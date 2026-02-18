# 🚀 ORBITUNE - Quick Start Guide

## Start the Project (One Command)

```powershell
.\START_ORBITUNE.ps1
```

That's it! The script handles everything automatically.

---

## ⚡ Quick Access

Once started, open:
- **Dashboard**: http://localhost:5173/dashboard
- **API Docs**: http://127.0.0.1:8000/docs

---

## ⌨️ Keyboard Shortcuts

| Key | Function |
|-----|----------|
| **Tab** | Switch Search/Chat Mode |
| **Ctrl+Space** | Toggle Debug Panel |
| **Enter** | Send Message |

---

## 🎯 Two Modes

### 🔍 Search Mode
- Search YouTube songs
- Get instant suggestions
- Generate 3D audio

**Example**: Type "Bohemian Rhapsody" → Click suggestion → Enjoy 3D audio

### 💬 Chat Mode  
- Talk to AI companion
- Get mood-based recommendations
- Natural conversations

**Example**: Type "I'm feeling happy!" → Get personalized song suggestions

---

## 🎮 How to Use

### Step 1: Start Application
```powershell
.\START_ORBITUNE.ps1
```

### Step 2: Open Dashboard
Browser opens automatically to http://localhost:5173/dashboard

### Step 3: Try It Out

**Chat Mode:**
1. Press **Tab** (if not already in Chat Mode)
2. Type: "Hey, recommend me some chill music"
3. Get AI recommendations

**Search Mode:**
1. Press **Tab** (to switch to Search Mode)
2. Type any song name
3. Click a suggestion
4. Wait 30-60 seconds for 3D processing
5. Play and enjoy!

---

## 🐛 Debug Panel (Developers Only)

**Hidden by default** for a clean UI.

**To reveal:**
- Press **Ctrl+Space**

**Shows:**
- Audio state
- Network status
- Buffer info
- Error messages
- Real-time diagnostics

**To hide:**
- Press **Ctrl+Space** again
- Or click the **✕** button

---

## 🛑 Stop the Application

Close the PowerShell windows that opened, or press **Ctrl+C** in each window.

---

## 🔧 Script Options

```powershell
# Fast startup (skip dependency installation)
.\START_ORBITUNE.ps1 -SkipDependencies

# Start backend only
.\START_ORBITUNE.ps1 -BackendOnly

# Start frontend only  
.\START_ORBITUNE.ps1 -FrontendOnly
```

---

## ⚠️ Common Issues

### Backend won't start?
```powershell
# Check if port is busy
netstat -ano | findstr :8000

# Kill the process if needed
taskkill /PID <PID> /F
```

### Frontend won't start?
```powershell
# Reinstall dependencies
cd FRONTEND\dashboard\orbitune-sonic-verse-main
npm install
```

### Chatbot not responding?
```powershell
# Check backend health
curl http://127.0.0.1:8000/api/chatbot/health
```

---

## 📋 System Requirements

- **Python 3.8+** - [Download](https://www.python.org/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Windows PowerShell** (pre-installed on Windows)

---

## 🎉 What You Get

✅ YouTube to 3D Audio conversion  
✅ AI Music Companion (Gemini Flash 2.0)  
✅ Real-time audio visualization  
✅ Mood-based recommendations  
✅ Tab key mode switching  
✅ Hidden developer debug panel  
✅ One-command startup  
✅ Automatic dependency management  
✅ Health checks and auto-recovery  

---

## 💡 Pro Tips

1. **Use headphones** for the best 3D audio experience
2. **Wait patiently** during 3D processing (30-60 seconds)
3. **Press Ctrl+Space** if audio isn't playing to see debug info
4. **Use Tab** to quickly switch between modes
5. **Ask the AI** for recommendations based on your mood

---

## 📚 Full Documentation

For complete documentation, see [README.md](README.md)

---

**Enjoy ORBITUNE! 🎵✨🚀**
