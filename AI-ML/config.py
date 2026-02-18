"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              ORBITUNE - Audio Processing Configuration                      ║
║                                                                              ║
║  COPYRIGHT © 2025 Yuvraj Singh Kushwah & Subhro Pal. All Rights Reserved.   ║
║                                                                              ║
║  PROPRIETARY AND CONFIDENTIAL - TRADE SECRETS PROTECTED                     ║
║  This file contains proprietary configuration parameters and optimization   ║
║  settings that are protected as trade secrets. Any unauthorized use,        ║
║  copying, or disclosure is strictly prohibited and may result in legal      ║
║  action with damages up to ₹20,00,000 (INR) or $150,000 (USD).             ║
║                                                                              ║
║  Protected Trade Secrets Include:                                           ║
║  • Htdemucs configuration parameters (shifts, overlap)                      ║
║  • Audio quality settings optimized for 3D spatialization                   ║
║  • YouTube download bypass configurations                                   ║
║  • GPU/CPU processing optimization parameters                               ║
║                                                                              ║
║  Contact: yuvrajsk.bpl@gmail.com | shubhropal62@gmail.com                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

ORBITUNE - Audio Processing Configuration
Centralized settings for all audio processing operations
"""

import os
import torch
from pathlib import Path

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
except ImportError:
    print("ℹ️  python-dotenv not installed, using system environment variables only")

# =============================================================================
# BASE PATHS
# =============================================================================
BASE_DIR = Path(__file__).parent.parent  # ORBITUNE root directory
STORAGE_DIR = BASE_DIR / "STORAGE"
AI_ML_DIR = BASE_DIR / "AI-ML"

# Storage subdirectories
RAW_AUDIO_DIR = STORAGE_DIR / "raw_audio"
PROCESSED_AUDIO_DIR = STORAGE_DIR / "processed"
CACHE_DIR = STORAGE_DIR / "cache"
THUMBNAILS_DIR = STORAGE_DIR / "thumbnails"
MODELS_DIR = AI_ML_DIR / "models"

# Aliases for compatibility
STORAGE_BASE = str(STORAGE_DIR)
AUDIO_SAMPLE_RATE = 48000  # Same as SAMPLE_RATE

# Create directories if they don't exist
for directory in [RAW_AUDIO_DIR, PROCESSED_AUDIO_DIR, CACHE_DIR, THUMBNAILS_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# =============================================================================
# GPU/DEVICE CONFIGURATION
# =============================================================================
# Auto-detect best device (GPU if available, else CPU)
USE_GPU = torch.cuda.is_available()
DEVICE = torch.device('cuda' if USE_GPU else 'cpu')

# GPU Memory management
if USE_GPU:
    GPU_NAME = torch.cuda.get_device_name(0)
    GPU_MEMORY_GB = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    # Reserve some memory for system
    MAX_GPU_MEMORY_USAGE = 0.9  # Use max 90% of GPU memory
else:
    GPU_NAME = "CPU"
    GPU_MEMORY_GB = 0

print(f"🔧 Device: {DEVICE}")
print(f"🎮 Using: {GPU_NAME}")
if USE_GPU:
    print(f"💾 GPU Memory: {GPU_MEMORY_GB:.2f} GB")

# =============================================================================
# AUDIO QUALITY SETTINGS (HIGHEST QUALITY)
# =============================================================================
SAMPLE_RATE = 48000  # 48kHz - Professional studio quality
BIT_DEPTH = 24       # 24-bit - Studio standard
AUDIO_FORMAT = 'wav' # Lossless format
CHANNELS = 2         # Stereo

# =============================================================================
# YOUTUBE DOWNLOAD SETTINGS
# =============================================================================
# Download best available audio quality (multiple fallbacks for reliability)
YOUTUBE_AUDIO_QUALITY = 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best'
MAX_SONG_DURATION = 600  # 10 minutes max (prevents downloading long videos)
YOUTUBE_SEARCH_MAX_RESULTS = 10

# Retry settings for YouTube downloads
YOUTUBE_MAX_RETRIES = 3
YOUTUBE_RETRY_SLEEP = 2  # seconds between retries

# yt-dlp options for best quality with YouTube bypass
YTDLP_OPTIONS = {
    'format': YOUTUBE_AUDIO_QUALITY,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '0',  # Best quality
    }],
    'postprocessor_args': [
        '-ar', str(SAMPLE_RATE),  # Sample rate
        '-ac', str(CHANNELS),      # Channels (stereo)
    ],
    'quiet': False,
    'no_warnings': False,
    'extract_audio': True,
    # Retry and error handling
    'retries': YOUTUBE_MAX_RETRIES,
    'fragment_retries': YOUTUBE_MAX_RETRIES,
    'skip_unavailable_fragments': True,
    'ignoreerrors': False,
    'no_color': False,
    # Critical options to bypass YouTube restrictions
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
            'player_skip': ['configs', 'webpage'],
        }
    },
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
    },
}

# =============================================================================
# DEMUCS (SOURCE SEPARATION) SETTINGS
# =============================================================================
DEMUCS_MODEL = 'htdemucs'  # Highest quality model (Hybrid Transformer Demucs)
# Available models: 'htdemucs', 'htdemucs_ft', 'mdx_extra', 'mdx_extra_q'
# htdemucs = Best overall quality
# htdemucs_ft = Fine-tuned version (slightly better on some songs)

DEMUCS_SHIFTS = 10 if USE_GPU else 1  # More shifts = better quality but slower
# Shifts: Number of random shifts for equivariant stabilization
# 1 = Fast, lower quality
# 5 = Good balance
# 10 = Best quality (GPU recommended)

DEMUCS_OVERLAP = 0.25  # Overlap between audio chunks (0.25 = 25%)
DEMUCS_SPLIT = True    # Split audio into chunks (reduces memory usage)

# Stem names that Demucs outputs
DEMUCS_STEMS = ['vocals', 'drums', 'bass', 'other']

# =============================================================================
# 16D SPATIAL AUDIO SETTINGS
# =============================================================================

# Room Presets (user can choose)
SPATIAL_PRESETS = {
    'concert_hall': {
        'name': 'Concert Hall',
        'description': 'Large venue with rich reverb',
        'room_size': 'large',
        'reverb_time': 2.8,
        'early_reflections': 12,
        'width_factor': 1.8,
        'positions': {
            'vocals': {'x': 0, 'y': 2.0, 'z': -2.5},   # Center, elevated, close
            'drums': {'x': 0, 'y': 0.5, 'z': -6.0},    # Center back
            'bass': {'x': -2.5, 'y': 0, 'z': -5.0},    # Left back
            'other': {'x': 2.5, 'y': 0.5, 'z': -5.0},  # Right back
        }
    },
    'studio': {
        'name': 'Recording Studio',
        'description': 'Intimate, dry, precise sound',
        'room_size': 'small',
        'reverb_time': 0.6,
        'early_reflections': 4,
        'width_factor': 1.2,
        'positions': {
            'vocals': {'x': 0, 'y': 1.5, 'z': -1.5},
            'drums': {'x': 0, 'y': 0, 'z': -3.0},
            'bass': {'x': -1.5, 'y': 0, 'z': -2.5},
            'other': {'x': 1.5, 'y': 0, 'z': -2.5},
        }
    },
    'arena': {
        'name': 'Stadium Arena',
        'description': 'Massive space with epic reverb',
        'room_size': 'huge',
        'reverb_time': 4.0,
        'early_reflections': 16,
        'width_factor': 2.5,
        'positions': {
            'vocals': {'x': 0, 'y': 3.0, 'z': -3.0},
            'drums': {'x': 0, 'y': 0.5, 'z': -10.0},
            'bass': {'x': -4.0, 'y': 0, 'z': -8.0},
            'other': {'x': 4.0, 'y': 0.5, 'z': -8.0},
        }
    },
    'club': {
        'name': 'Night Club',
        'description': 'Tight, punchy, bass-heavy',
        'room_size': 'medium',
        'reverb_time': 1.2,
        'early_reflections': 6,
        'width_factor': 1.5,
        'positions': {
            'vocals': {'x': 0, 'y': 1.8, 'z': -2.0},
            'drums': {'x': 0, 'y': 0, 'z': -4.0},
            'bass': {'x': -2.0, 'y': 0, 'z': -3.5},
            'other': {'x': 2.0, 'y': 0, 'z': -3.5},
        }
    },
    'acoustic': {
        'name': 'Acoustic Space',
        'description': 'Natural, warm, unplugged feel',
        'room_size': 'medium',
        'reverb_time': 1.5,
        'early_reflections': 8,
        'width_factor': 1.4,
        'positions': {
            'vocals': {'x': 0, 'y': 1.5, 'z': -1.8},
            'drums': {'x': 0, 'y': 0, 'z': -3.5},
            'bass': {'x': -1.8, 'y': 0, 'z': -3.0},
            'other': {'x': 1.8, 'y': 0, 'z': -3.0},
        }
    }
}

# Default preset
DEFAULT_SPATIAL_PRESET = 'concert_hall'

# =============================================================================
# PROCESSING SETTINGS
# =============================================================================
# Multi-threading for CPU operations
NUM_WORKERS = 4  # Parallel processing threads

# Processing queue
MAX_QUEUE_SIZE = 50  # Maximum songs in processing queue
PROCESSING_TIMEOUT = 600  # 10 minutes timeout per song

# =============================================================================
# API SERVER SETTINGS
# =============================================================================
API_HOST = '127.0.0.1'  # localhost
API_PORT = 8000
API_RELOAD = True  # Auto-reload on code changes (dev mode)

# =============================================================================
# GEMINI API CONFIGURATION (Genre Detection)
# =============================================================================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')  # Set your API key in environment
GEMINI_MODEL = 'models/gemini-2.0-flash'  # Gemini 2.0 Flash model

# =============================================================================
# PROFESSIONAL AUDIO PROCESSING SETTINGS
# =============================================================================
# HRTF Settings for realistic 3D positioning
HRTF_DISTANCE_MIN = 0.5  # meters (closest sound can be)
HRTF_DISTANCE_MAX = 10.0  # meters (farthest sound)
HRTF_DEFAULT_DISTANCE = 2.0  # meters (default listening distance)

# Rotation settings for smooth, observable movement
ROTATION_SPEED_SLOW = 0.5  # rotations per song duration
ROTATION_SPEED_MEDIUM = 1.5  # rotations per song duration
ROTATION_SPEED_FAST = 3.0  # rotations per song duration
ROTATION_SMOOTHNESS = 0.95  # 0.90–0.97 recommended: ULTRA-SMOOTH motion, ultra-realistic

# Room acoustics for realism
ROOM_SIZE_SMALL = 20  # cubic meters
ROOM_SIZE_MEDIUM = 100  # cubic meters
ROOM_SIZE_LARGE = 500  # cubic meters
AIR_ABSORPTION_COEFFICIENT = 0.0001  # Realistic air absorption

# Professional mastering settings - REALISTIC 3D / COMFORTABLE LISTENING
# Optimized profile for ultra-realistic, engaging 3D audio:
#   - LUFS at -14: Professional streaming standard (Spotify/Apple Music)
#   - Peak ceiling -0.5 dB: Maximum impact while preventing true peaks
#   - Stereo width 1.15: Slight enhancement to complement HRTF spatial width
MASTER_LOUDNESS_LUFS = -14.0  # Target loudness for engaging, alive playback
MASTER_PEAK_CEILING = -0.5    # dB peak ceiling (more headroom for louder masters)
MASTER_STEREO_WIDTH = 1.08    # Natural width - let HRTF create the 3D space

# =============================================================================
# LOGGING
# =============================================================================
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = AI_ML_DIR / 'audio_processor.log'

# =============================================================================
# FILE NAMING CONVENTIONS
# =============================================================================
def get_song_directory(song_id: str) -> Path:
    """Get directory for a specific song's processed files"""
    return PROCESSED_AUDIO_DIR / song_id

def get_raw_audio_path(song_id: str) -> Path:
    """Get path for raw downloaded audio"""
    return RAW_AUDIO_DIR / song_id / f"original.{AUDIO_FORMAT}"

def get_stem_path(song_id: str, stem_name: str) -> Path:
    """Get path for a separated stem"""
    return PROCESSED_AUDIO_DIR / song_id / f"{stem_name}.{AUDIO_FORMAT}"

def get_metadata_path(song_id: str) -> Path:
    """Get path for song metadata JSON"""
    return RAW_AUDIO_DIR / song_id / "metadata.json"

def get_thumbnail_path(song_id: str) -> Path:
    """Get path for song thumbnail"""
    return THUMBNAILS_DIR / f"{song_id}.jpg"

def get_stems_dir(song_id: str) -> str:
    """Get directory containing separated stems for a song"""
    return str(PROCESSED_AUDIO_DIR / song_id)

# =============================================================================
# PRINT CONFIGURATION SUMMARY
# =============================================================================
def print_config():
    """Print current configuration"""
    print("\n" + "="*70)
    print("🎵 ORBITUNE AUDIO PROCESSING CONFIGURATION")
    print("="*70)
    print(f"Device: {DEVICE} ({GPU_NAME})")
    if USE_GPU:
        print(f"GPU Memory: {GPU_MEMORY_GB:.2f} GB")
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    print(f"Bit Depth: {BIT_DEPTH}-bit")
    print(f"Demucs Model: {DEMUCS_MODEL}")
    print(f"Demucs Shifts: {DEMUCS_SHIFTS} ({'High Quality' if DEMUCS_SHIFTS >= 5 else 'Fast'})")
    print(f"Default Spatial Preset: {SPATIAL_PRESETS[DEFAULT_SPATIAL_PRESET]['name']}")
    print(f"Storage Directory: {STORAGE_DIR}")
    print("="*70 + "\n")

if __name__ == "__main__":
    print_config()
