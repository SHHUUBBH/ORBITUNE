"""
ORBITUNE - YouTube Audio Downloader
Downloads highest quality audio from YouTube with metadata
"""

import yt_dlp
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import requests
from tqdm import tqdm

# Import config
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import (
    RAW_AUDIO_DIR, THUMBNAILS_DIR, YTDLP_OPTIONS,
    MAX_SONG_DURATION, YOUTUBE_SEARCH_MAX_RESULTS,
    get_raw_audio_path, get_metadata_path, get_thumbnail_path
)


class YouTubeDownloader:
    """
    Downloads audio from YouTube in highest quality
    
    Features:
    - Search YouTube for songs
    - Download best available audio quality
    - Extract and save metadata
    - Download thumbnails
    - Generate unique song IDs
    """
    
    def __init__(self):
        """Initialize YouTube downloader"""
        self.download_dir = RAW_AUDIO_DIR
        self.thumbnails_dir = THUMBNAILS_DIR
        
        print("🎵 YouTube Downloader initialized")
        print(f"📁 Download directory: {self.download_dir}")
    
    def generate_song_id(self, video_id: str) -> str:
        """
        Generate unique song ID from YouTube video ID
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Unique song ID (hash)
        """
        # Use MD5 hash of video ID for shorter ID
        return hashlib.md5(video_id.encode()).hexdigest()[:12]
    
    def search(self, query: str, max_results: int = YOUTUBE_SEARCH_MAX_RESULTS) -> List[Dict]:
        """
        Search YouTube for songs
        
        Args:
            query: Search query (e.g. "shape of you ed sheeran")
            max_results: Maximum number of results to return
            
        Returns:
            List of song dictionaries with metadata
        """
        print(f"\n🔍 Searching YouTube for: '{query}'")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Don't download, just get info
            'default_search': 'ytsearch',  # Use YouTube search
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['configs', 'webpage'],
                }
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search YouTube
                search_results = ydl.extract_info(
                    f"ytsearch{max_results}:{query}",
                    download=False
                )
                
                results = []
                for entry in search_results.get('entries', []):
                    if not entry:
                        continue
                    
                    duration = entry.get('duration', 0)
                    if duration:
                        duration = int(duration)  # Convert to int if it's a float
                    
                    # Filter out videos longer than max duration
                    if duration and duration > MAX_SONG_DURATION:
                        continue
                    
                    video_id = entry['id']
                    song_id = self.generate_song_id(video_id)
                    
                    result = {
                        'song_id': song_id,
                        'video_id': video_id,
                        'title': entry.get('title', 'Unknown'),
                        'channel': entry.get('channel', entry.get('uploader', 'Unknown')),
                        'duration': duration,
                        'duration_string': self._format_duration(duration),
                        'thumbnail': entry.get('thumbnail', ''),
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': int(entry.get('view_count', 0) or 0),
                    }
                    
                    results.append(result)
                
                print(f"✅ Found {len(results)} results")
                return results
                
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def _format_duration(self, seconds) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS"""
        if seconds is None:
            return "0:00"
        seconds = int(seconds)  # Convert to int in case it's a float
        if seconds < 3600:
            return f"{seconds // 60}:{seconds % 60:02d}"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours}:{minutes:02d}:{secs:02d}"
    
    def download(self, video_id: str, song_title: str = None) -> Optional[Dict]:
        """
        Download audio from YouTube in highest quality
        
        Args:
            video_id: YouTube video ID
            song_title: Optional custom song title
            
        Returns:
            Dictionary with song metadata and file paths
        """
        song_id = self.generate_song_id(video_id)
        output_dir = self.download_dir / song_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📥 Downloading: {video_id}")
        print(f"💾 Song ID: {song_id}")
        
        # Setup yt-dlp options with custom output path
        ydl_opts = YTDLP_OPTIONS.copy()
        ydl_opts['outtmpl'] = str(output_dir / 'original.%(ext)s')
        
        # Add progress hook
        ydl_opts['progress_hooks'] = [self._progress_hook]
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                print("📊 Extracting metadata...")
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
                    download=True
                )
                
                # Prepare metadata
                metadata = {
                    'song_id': song_id,
                    'video_id': video_id,
                    'title': info.get('title', song_title or 'Unknown'),
                    'artist': info.get('artist', info.get('creator', info.get('channel', 'Unknown'))),
                    'album': info.get('album', info.get('title', 'YouTube')),
                    'duration': info.get('duration', 0),
                    'duration_string': self._format_duration(info.get('duration', 0)),
                    'channel': info.get('channel', 'Unknown'),
                    'upload_date': info.get('upload_date', ''),
                    'view_count': int(info.get('view_count', 0) or 0),
                    'like_count': int(info.get('like_count', 0) or 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:500],  # First 500 chars
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'downloaded_at': datetime.now().isoformat(),
                    'audio_file': str(get_raw_audio_path(song_id)),
                    'sample_rate': 48000,
                    'channels': 2,
                    'format': 'wav',
                }
                
                # Save metadata to JSON
                metadata_path = get_metadata_path(song_id)
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Download thumbnail
                if info.get('thumbnail'):
                    self._download_thumbnail(info['thumbnail'], song_id)
                
                print(f"✅ Downloaded successfully!")
                print(f"📄 Title: {metadata['title']}")
                print(f"🎤 Artist: {metadata['artist']}")
                print(f"⏱️  Duration: {metadata['duration_string']}")
                print(f"📁 Saved to: {output_dir}")
                
                return metadata
                
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def _progress_hook(self, d):
        """Progress callback for yt-dlp"""
        if d['status'] == 'downloading':
            # Show download progress
            if 'downloaded_bytes' in d and 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                print(f"\r⬇️  Downloading: {percent:.1f}%", end='', flush=True)
        elif d['status'] == 'finished':
            print("\n✅ Download complete, converting to WAV...")
    
    def _download_thumbnail(self, thumbnail_url: str, song_id: str) -> bool:
        """
        Download and save song thumbnail
        
        Args:
            thumbnail_url: URL of thumbnail image
            song_id: Unique song ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            thumbnail_path = get_thumbnail_path(song_id)
            
            # Download image
            response = requests.get(thumbnail_url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Save to file
            with open(thumbnail_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print(f"🖼️  Thumbnail saved: {thumbnail_path.name}")
            return True
            
        except Exception as e:
            print(f"⚠️  Thumbnail download failed: {e}")
            return False
    
    def get_video_info(self, video_id: str) -> Optional[Dict]:
        """
        Get video information without downloading
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video metadata
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'player_skip': ['configs', 'webpage'],
                }
            },
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(
                    f"https://www.youtube.com/watch?v={video_id}",
                    download=False
                )
                
                return {
                    'video_id': video_id,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'thumbnail': info.get('thumbnail'),
                    'channel': info.get('channel'),
                    'view_count': int(info.get('view_count', 0) or 0),
                }
        except Exception as e:
            print(f"❌ Info extraction error: {e}")
            return None
    
    def is_downloaded(self, video_id: str) -> bool:
        """
        Check if a song is already downloaded
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if already downloaded, False otherwise
        """
        song_id = self.generate_song_id(video_id)
        audio_path = get_raw_audio_path(song_id)
        metadata_path = get_metadata_path(song_id)
        
        return audio_path.exists() and metadata_path.exists()


# =============================================================================
# USAGE EXAMPLE / TESTING
# =============================================================================
if __name__ == "__main__":
    print("="*70)
    print("🎵 ORBITUNE - YouTube Downloader Test")
    print("="*70)
    
    downloader = YouTubeDownloader()
    
    # Example 1: Search for a song
    query = input("\n🔍 Enter search query (e.g., 'shape of you ed sheeran'): ").strip()
    
    if query:
        results = downloader.search(query, max_results=5)
        
        if results:
            print(f"\n📋 Search Results:")
            print("-" * 70)
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   Channel: {result['channel']}")
                print(f"   Duration: {result['duration_string']}")
                print(f"   Song ID: {result['song_id']}")
                print()
            
            # Ask user to download one
            choice = input(f"Enter number to download (1-{len(results)}) or 0 to skip: ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(results):
                selected = results[int(choice) - 1]
                
                # Check if already downloaded
                if downloader.is_downloaded(selected['video_id']):
                    print(f"\n⚠️  Song already downloaded (ID: {selected['song_id']})")
                else:
                    # Download the selected song
                    metadata = downloader.download(selected['video_id'])
                    
                    if metadata:
                        print("\n" + "="*70)
                        print("✅ DOWNLOAD COMPLETE!")
                        print("="*70)
                        print(f"Song ID: {metadata['song_id']}")
                        print(f"Title: {metadata['title']}")
                        print(f"Artist: {metadata['artist']}")
                        print(f"File: {metadata['audio_file']}")
                        print("="*70)
    else:
        print("❌ No query provided")
