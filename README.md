# ORBITUNE - 3D Spatial Audio API

AI-powered 3D spatial audio processing backend with source separation, genre detection, and HRTF-based spatialization.

## Features

- **Source Separation**: Demucs v4 for vocals/drums/bass/other separation
- **Genre Detection**: Google Gemini AI-powered genre classification
- **Spatial Audio**: HRTF-based 3D audio processing with 8-directional rotation
- **YouTube Integration**: Download and process audio from YouTube URLs
- **FastAPI Backend**: RESTful API with CORS support
- **Supabase Storage**: Cloud storage for processed audio and thumbnails

## Architecture

```
ORBITUNE/
├── BACKEND/           # FastAPI application
│   └── src/
│       ├── app.py           # Main FastAPI app
│       ├── routes/          # API endpoints
│       ├── services/        # Business logic
│       └── models.py        # Data models
├── AI-ML/             # Audio processing pipeline
│   ├── audio_processor/     # Core processing modules
│   ├── chatbot/             # AI chatbot service
│   ├── config.py            # Configuration
│   └── requirements.txt     # Python dependencies
├── Dockerfile         # Hugging Face Space deployment
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/songs/process` | Process YouTube URL to spatial audio |
| GET | `/api/songs` | List processed songs |
| GET | `/api/songs/{id}` | Get song details |
| POST | `/api/chatbot` | Chat with AI assistant |

## Local Development

```bash
# Install dependencies
pip install -r AI-ML/requirements.txt

# Run FastAPI server
uvicorn BACKEND.src.app:app --reload --port 8000
```

## Docker Deployment (Hugging Face Space)

```bash
docker build -t orbitune-api .
docker run -p 7860:7860 orbitune-api
```

The API runs on port 7860 (Hugging Face Spaces default).

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/service key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `HF_TOKEN` | Hugging Face token (for Demucs) |

## Tech Stack

- **Backend**: FastAPI, Uvicorn
- **Audio**: Demucs, Librosa, SoundFile, PyDub, Pedalboard
- **AI**: Google Generative AI (Gemini)
- **Storage**: Supabase
- **Deployment**: Docker, Hugging Face Spaces

## License

Proprietary - Copyright © 2025 Yuvraj Singh Kushwah & Subhro Pal