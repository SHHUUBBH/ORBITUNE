"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ORBITUNE Backend API                                ║
║                                                                              ║
║  COPYRIGHT © 2025 Yuvraj Singh Kushwah & Subhro Pal. All Rights Reserved.   ║
║                                                                              ║
║  PROPRIETARY AND CONFIDENTIAL - VIEWING ONLY FOR ACADEMIC EVALUATION        ║
║  Execution, copying, or distribution is STRICTLY PROHIBITED.                ║
║  See LICENSE file for full terms.                                           ║
║                                                                              ║
║  Contact: yuvrajsk.bpl@gmail.com | shubhropal62@gmail.com                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

ORBITUNE Backend API - FastAPI app

Exposes endpoints that drive the AI-ML 3D audio pipeline
and serve JSON data + local folder audio/thumbnails.
"""

from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Resolve important paths
THIS_FILE = Path(__file__).resolve()
SRC_DIR = THIS_FILE.parent
BACKEND_DIR = SRC_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
AI_ML_DIR = PROJECT_ROOT / "AI-ML"

# Make backend src and AI-ML importable
if str(SRC_DIR) not in sys.path:
    sys.path.append(str(SRC_DIR))
if str(AI_ML_DIR) not in sys.path:
    sys.path.append(str(AI_ML_DIR))

# Import shared audio config from AI-ML
import config  # type: ignore

from routes.songs import router as songs_router  # type: ignore
from routes.chatbot import router as chatbot_router  # type: ignore

app = FastAPI(title="ORBITUNE API", version="1.0.0")

# CORS so homepage (3000) and dashboard (5173) can call the API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static mounts for spatial audio and thumbnails
spatial_dir = config.STORAGE_DIR / "spatial"
thumbs_dir = config.THUMBNAILS_DIR
spatial_dir.mkdir(parents=True, exist_ok=True)
thumbs_dir.mkdir(parents=True, exist_ok=True)

app.mount("/media/spatial", StaticFiles(directory=spatial_dir), name="spatial")
app.mount("/media/thumbnails", StaticFiles(directory=thumbs_dir), name="thumbnails")

# API routes
app.include_router(songs_router, prefix="/api")
app.include_router(chatbot_router, prefix="/api")


@app.get("/health")
async def health_check() -> dict:
    """Simple health endpoint."""
    return {"status": "ok"}
