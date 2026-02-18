
> **⚠️ ORBITUNE PROPRIETARY LICENSE & TERMS OF USE**
> 
> **COPYRIGHT © 2026 Yuvraj Singh Kushwah & Subhro Pal. All Rights Reserved.**
> 
> This project and all its components are **STRICTLY CONFIDENTIAL** and **PROPRIETARY**. 
> All code, algorithms, UI designs, documentation, and methodologies are the exclusive 
> intellectual property of the copyright holders.
> 
> **🚫 NO PART OF THIS PROJECT IS OPEN SOURCE.**
> 
> Viewing is permitted **ONLY** for:
> - ✓ Academic verification and evaluation purposes
> - ✓ Assessment of technical competence for Jagran Lakecity University
> 
> **STRICTLY PROHIBITED:**
> - ❌ Execution, compilation, or deployment
> - ❌ Copying, reproduction, or distribution
> - ❌ Commercial use or derivative works
> - ❌ Reverse engineering or data mining
> 
> **⚖️ Violations will result in legal action with penalties up to ₹20,00,000 (INR) or $150,000 (USD).**
> 
> 📄 See the [LICENSE](./LICENSE) file for complete terms, penalties, and contact information.

# 🎵 ORBITUNE - 3D Audio Experience with AI Companion

![ORBITUNE Banner](https://img.shields.io/badge/ORBITUNE-3D%20Audio-blueviolet?style=for-the-badge&logo=music)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Node.js](https://img.shields.io/badge/Node.js-16+-green?style=flat-square&logo=node.js)
![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.108-009688?style=flat-square&logo=fastapi)

ORBITUNE is an innovative 3D audio platform that transforms YouTube music into immersive spatial audio experiences. Powered by AI, it features intelligent music recommendations, real-time audio visualization, and a conversational interface.

---

## ✨ Features

### 🎧 Core Features
- **3D Audio Processing**: Convert any YouTube video into spatial 3D audio
- **AI Music Companion**: Gemini Flash 2.0 powered chatbot for personalized recommendations
- **Dual Mode Interface**: Switch between Search and Chat modes with Tab key
- **Real-time Visualization**: Dynamic audio visualizations and waveforms
- **Smart Stem Separation**: Professional-grade vocal, drums, bass, and instrumental separation
- **Developer Debug Panel**: Toggle audio diagnostics with Ctrl+Space (hidden by default)

### 🤖 AI Capabilities
- Mood-based music recommendations
- Natural language conversations
- Intent detection and user profiling
- Conversation memory and context awareness
- Song suggestions based on feelings and preferences

### 🎨 UI/UX
- Beautiful glassmorphic design
- Smooth animations and transitions
- Responsive layout for all screen sizes
- Particle effects and dynamic backgrounds
- Keyboard shortcuts for power users

---

## 🚀 Quick Start (One Command)

### Prerequisites
Ensure you have the following installed:
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **Git** (optional) - [Download](https://git-scm.com/)

### Start Everything at Once

```powershell
# Clone the repository (if not already done)
git clone <your-repo-url>
cd ORBITUNE

# Run the startup script
.\START_ORBITUNE.ps1
```

That's it! The script will:
1. ✅ Check system requirements
2. ✅ Create Python virtual environment
3. ✅ Install all dependencies (Python & Node.js)
4. ✅ Start backend server (Port 8000)
5. ✅ Start frontend dashboard (Port 5173)
6. ✅ Perform health checks
7. ✅ Open browser automatically

### Script Options

```powershell
# Skip dependency installation (faster startup if already installed)
.\START_ORBITUNE.ps1 -SkipDependencies

# Start backend only
.\START_ORBITUNE.ps1 -BackendOnly

# Start frontend only
.\START_ORBITUNE.ps1 -FrontendOnly
```

---

## 🎮 How to Use

### Access the Application
Once started, open your browser to:
- **Dashboard**: http://localhost:5173/dashboard
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| **Tab** | Switch between Search Mode 🔍 and Chat Mode 💬 |
| **Ctrl+Space** | Toggle Developer Debug Panel (hidden by default) |
| **Enter** | Send message/search query |

### Using Search Mode 🔍
1. Press **Tab** to switch to Search Mode
2. Type a song name or artist (e.g., "Bohemian Rhapsody")
3. Select from real-time YouTube suggestions
4. Wait for 3D audio processing (~30-60 seconds)
5. Enjoy immersive 3D spatial audio!

### Using Chat Mode 💬
1. Press **Tab** to switch to Chat Mode
2. Tell the AI how you're feeling (e.g., "I'm feeling happy today!")
3. Get personalized song recommendations
4. Ask questions about music, artists, or genres
5. The AI learns your preferences over time

### Developer Debug Panel
- **Hidden by default** for clean UI
- Press **Ctrl+Space** to reveal audio diagnostics
- Shows real-time audio state, network status, buffering info
- Perfect for troubleshooting playback issues
- Press **Ctrl+Space** again or click ✕ to hide

---

## 📁 Project Structure

```
ORBITUNE/
├── AI-ML/                          # AI & Machine Learning modules
│   ├── audio_processor/            # 3D audio processing pipeline
│   ├── chatbot/                    # Gemini AI chatbot service
│   ├── models/                     # Audio processing models
│   └── requirements.txt            # Python dependencies
├── BACKEND/                        # FastAPI backend
│   └── src/
│       ├── routes/                 # API endpoints
│       ├── services/               # Business logic
│       ├── app.py                  # Main FastAPI app
│       └── models.py               # Data models
├── FRONTEND/                       # React frontend
│   └── dashboard/
│       └── orbitune-sonic-verse-main/
│           ├── src/
│           │   ├── components/     # React components
│           │   ├── pages/          # Page components
│           │   ├── lib/            # Utilities & API
│           │   └── contexts/       # React contexts
│           └── package.json        # Node.js dependencies
├── STORAGE/                        # Generated audio files
├── .env                            # Environment variables
└── START_ORBITUNE.ps1             # One-command startup script ⭐
```

---

## 🔧 Manual Setup (Alternative)

If you prefer manual setup or want to understand each step:

### Backend Setup

```powershell
# 1. Create virtual environment
cd ORBITUNE
python -m venv AI-ML\venv

# 2. Activate virtual environment
AI-ML\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r AI-ML\requirements.txt

# 4. Start backend server
cd BACKEND\src
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup

```powershell
# 1. Navigate to frontend directory
cd FRONTEND\dashboard\orbitune-sonic-verse-main

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

---

## 🌐 API Endpoints

### Chatbot Endpoints
- `POST /api/chatbot/chat` - Send message to AI
- `GET /api/chatbot/history/{user_id}` - Get conversation history
- `GET /api/chatbot/profile/{user_id}` - Get user profile
- `GET /api/chatbot/health` - Health check

### Song Endpoints
- `GET /api/songs` - List all processed songs
- `POST /api/songs/from-youtube` - Create 3D audio from YouTube
- `GET /api/youtube/search` - Search YouTube

---

## 🛠️ Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Gemini Flash 2.0** - AI chatbot engine
- **Demucs** - Audio stem separation
- **Librosa** - Audio analysis
- **yt-dlp** - YouTube downloading

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations
- **Radix UI** - UI components
- **Lucide React** - Icons

---

## 🐛 Troubleshooting

### Backend Not Starting?

**Check Python version:**
```powershell
python --version
# Should be 3.8 or higher
```

**Check if port 8000 is in use:**
```powershell
netstat -ano | findstr :8000
# If occupied, kill the process:
taskkill /PID <PID_NUMBER> /F
```

**Verify .env file:**
```powershell
cat .env
# Should contain:
# GEMINI_API_KEY=your_api_key_here
```

### Frontend Not Starting?

**Check Node.js version:**
```powershell
node --version
# Should be 16 or higher
```

**Clear node_modules and reinstall:**
```powershell
cd FRONTEND\dashboard\orbitune-sonic-verse-main
Remove-Item -Recurse -Force node_modules
npm install
```

### Chatbot Not Responding?

**Test backend health:**
```powershell
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

### 3D Audio Processing Fails?

**Common causes:**
- Invalid YouTube URL
- Age-restricted video
- Copyright-blocked content
- Network issues

**Check backend logs** in the PowerShell window for detailed error messages.

### Debug Panel Not Appearing?

- Make sure a track is currently loaded
- Press **Ctrl+Space** (not Ctrl alone or Space alone)
- Check browser console (F12) for errors

---

## 📊 Performance Tips

### For Faster Startup
```powershell
# Skip dependency checks if already installed
.\START_ORBITUNE.ps1 -SkipDependencies
```

### For Better 3D Audio Quality
- Use high-quality YouTube videos (1080p or higher)
- Allow full processing time (30-60 seconds)
- Use headphones or quality speakers for best experience

### For Development
- Backend auto-reloads on file changes
- Frontend has hot module replacement
- Use debug panel (Ctrl+Space) for audio diagnostics

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Demucs** for state-of-the-art audio separation
- **Google Gemini** for powerful AI capabilities
- **yt-dlp** for reliable YouTube downloading
- **React** and **FastAPI** communities for excellent documentation

---

## �‍💻 Creators & Copyright Holders

<div align="center">

### **Yuvraj Singh Kushwah**
📧 [yuvrajsk.bpl@gmail.com](mailto:yuvrajsk.bpl@gmail.com)  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/yuvraj-singh-kushwah-2b88b8366/)  
🌐 [Portfolio Website](https://web-portfolio-yuvraj.vercel.app/)

### **Subhro Pal**
📧 [shubhropal62@gmail.com](mailto:shubhropal62@gmail.com)  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/subhro-pal-b00a60356/)  
🌐 [Portfolio Website](https://subhroportfolio.netlify.app)

---

**For licensing inquiries, permission requests, or to report violations, contact the creators directly.**

</div>

---

## 📧 Support

**⚠️ IMPORTANT: This project is proprietary. Support is provided ONLY for academic evaluation purposes.**

If you encounter issues during academic review:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review backend and frontend logs
3. Contact the creators via email (see above)

**Note:** Execution, deployment, or commercial use support will NOT be provided as these activities violate the license terms.

---

## 🎉 What's New

### Version 1.0.0
- ✅ One-command startup script
- ✅ Hidden debug panel (Ctrl+Space to toggle)
- ✅ Gemini Flash 2.0 integration
- ✅ Tab key mode switching
- ✅ Improved 3D audio processing
- ✅ Real-time audio visualization
- ✅ Mood-based recommendations
- ✅ Comprehensive error handling
- ✅ Health checks and auto-recovery

---

## ⚖️ Legal Notice

**ORBITUNE™** is a trademark of Yuvraj Singh Kushwah & Subhro Pal.

This project contains **TRADE SECRETS** including proprietary algorithms, AI implementations, 
and audio processing techniques. Any unauthorized disclosure, use, or reproduction is 
strictly prohibited and will result in immediate legal action.

Protected components include:
- 🔒 Dynamic Distance Variation formula
- 🔒 HRTF binaural processing implementation
- 🔒 Gemini AI prompt engineering structures
- 🔒 Genre-aware spatial positioning strategies
- 🔒 Htdemucs configuration optimizations
- 🔒 Dual-mode interface architecture

**Jurisdiction:** Courts of Bhopal, Madhya Pradesh, India

---

<div align="center">

**© 2025 Yuvraj Singh Kushwah & Subhro Pal. All Rights Reserved.**

🎵 **ORBITUNE - Redefining 3D Audio Excellence** 🚀

**Made with ❤️ and Innovation**

[📄 View Full License](./LICENSE) · [📧 Contact Creators](#-creators--copyright-holders) · [⚖️ Report Violation](mailto:yuvrajsk.bpl@gmail.com)

</div>
