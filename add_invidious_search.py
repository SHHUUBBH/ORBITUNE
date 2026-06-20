import re

# Read the file
with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add the Invidious search helper method after the generate_song_id method
invidual_method = '''
    def _search_invidious(self, query: str, max_results: int = YOUTUBE_SEARCH_MAX_RESULTS) -> List[Dict]:
        """
        Fallback search using public Invidious instances.
        More reliable on restricted networks like HF Spaces.
        """
        print(f"[YTDL] Fallback search via Invidious for: '{query}'")
        
        # Public Invidious instances (more reliable than direct YouTube on restricted networks)
        invidious_instances = [
            'https://yewtu.be',
            'https://inv.nadeko.net',
            'https://inv.tux.pizza',
            'https://invidious.snopyta.org',
            'https://y.com.sb',
        ]
        
        for instance in invidious_instances:
            try:
                url = f"{instance}/api/v1/search"
                params = {
                    'q': query,
                    'type': 'video',
                    'page': 1,
                }
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                }
                response = requests.get(url, params=params, headers=headers, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data[:max_results]:
                    if item.get('type') != 'video':
                        continue
                    video_id = item.get('videoId', '')
                    if not video_id:
                        continue
                    
                    duration = item.get('lengthSeconds', 0)
                    if duration and duration > MAX_SONG_DURATION:
                        continue
                    
                    song_id = self.generate_song_id(video_id)
                    
                    result = {
                        'song_id': song_id,
                        'video_id': video_id,
                        'title': item.get('title', 'Unknown'),
                        'channel': item.get('author', 'Unknown'),
                        'duration': duration,
                        'duration_string': self._format_duration(duration),
                        'thumbnail': item.get('videoThumbnails', [{}])[-1].get('url', '') if item.get('videoThumbnails') else '',
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'view_count': int(item.get('viewCount', 0) or 0),
                    }
                    results.append(result)
                
                print(f"[OK] Invidious search found {len(results)} results via {instance}")
                return results
                
            except Exception as e:
                print(f"[WARN] Invidious instance {instance} failed: {e}")
                continue
        
        print("[ERROR] All Invidious instances failed")
        return []

'''

# Find the position after generate_song_id method and insert the new method
insert_pos = content.find('    def search(self, query: str, max_results: int = YOUTUBE_SEARCH_MAX_RESULTS)')
if insert_pos >= 0:
    content = content[:insert_pos] + invidual_method + '\n' + content[insert_pos:]
    
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added Invidious search method')
else:
    print('Could not find insert position')