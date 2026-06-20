# Read the file
with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact pattern after demo fallback return and before ydl_opts
old_block = '''        if any(keyword in query_lower for keyword in demo_keywords):
            print(f"[YTDL] Fast path: demo keyword detected, returning demo tracks")
            return self._search_demo_fallback(query, max_results)
        
        # Use search-specific options from config
        ydl_opts = YTDLP_SEARCH_OPTIONS.copy()'''

new_block = '''        if any(keyword in query_lower for keyword in demo_keywords):
            print(f"[YTDL] Fast path: demo keyword detected, returning demo tracks")
            return self._search_demo_fallback(query, max_results)
        
        # Check if running on HF Spaces (detect via environment variable)
        import os
        if os.environ.get('HF_SPACES') or os.environ.get('SPACE_ID') or 'huggingface.co' in os.environ.get('HOSTNAME', ''):
            print("[YTDL] HF Spaces detected, skipping yt-dlp, using Invidious fallback...")
            invidious_results = self._search_invidious(query, max_results)
            if invidious_results:
                return invidious_results
            return self._search_demo_fallback(query, max_results)
        
        # Use search-specific options from config
        ydl_opts = YTDLP_SEARCH_OPTIONS.copy()'''

if old_block in content:
    content = content.replace(old_block, new_block)
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Added HF Spaces detection')
else:
    print('Could not find block')
    # Debug: find the exact text
    idx = content.find('demo_keywords')
    if idx >= 0:
        print('Found demo_keywords at:', idx)
        print(repr(content[idx:idx+300]))