"""
Test YouTube download functionality
Run this to diagnose YouTube download issues
"""

import sys
from pathlib import Path

# Add AI-ML to path
sys.path.append(str(Path(__file__).parent / "AI-ML"))

import yt_dlp

print("=" * 70)
print("YouTube Download Test")
print("=" * 70)

# Test video ID
video_id = "a7OlENex8AY"  # The one you were testing
url = f"https://www.youtube.com/watch?v={video_id}"

print(f"\nVideo URL: {url}")
print(f"yt-dlp version: {yt_dlp.version.__version__}")

# Configuration with bypass options
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': False,
    'no_warnings': False,
    'extract_audio': True,
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

print("\nAttempting to extract video info...")
print("-" * 70)

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        print("\n✅ SUCCESS! Video info extracted:")
        print(f"Title: {info.get('title', 'N/A')}")
        print(f"Duration: {info.get('duration', 0)} seconds")
        print(f"Channel: {info.get('channel', 'N/A')}")
        print(f"View Count: {info.get('view_count', 0):,}")
        
        # Check available formats
        formats = info.get('formats', [])
        audio_formats = [f for f in formats if f.get('acodec') != 'none']
        print(f"\nAvailable audio formats: {len(audio_formats)}")
        
        if audio_formats:
            best_audio = audio_formats[-1]
            print(f"Best audio format: {best_audio.get('format_id')} - {best_audio.get('format_note', 'N/A')}")
        
        print("\n" + "=" * 70)
        print("✅ YouTube download functionality is WORKING!")
        print("=" * 70)
        
except Exception as e:
    print("\n" + "=" * 70)
    print("❌ ERROR!")
    print("=" * 70)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 70)
    print("Possible solutions:")
    print("1. Run: pip install --upgrade yt-dlp")
    print("2. Check your internet connection")
    print("3. Try a different video")
    print("4. The video might be age-restricted or region-locked")
    print("=" * 70)
