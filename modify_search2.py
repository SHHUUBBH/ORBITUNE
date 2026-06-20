# Read the file
with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the exact pattern and replace
old = '''        print(f"[ERROR] Search error: {e}")
                return []
        
        return []
    
    def _format_duration'''

new = '''                error_msg = str(e)
                if 'SSL' in error_msg or 'EOF' in error_msg:
                    if attempt < max_attempts:
                        wait_time = attempt * 2
                        print(f"[WARN] SSL/Connection error (attempt {attempt}/{max_attempts}), retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                # If all yt-dlp attempts fail, try Invidious fallback
                if attempt >= max_attempts:
                    print("[YTDL] All yt-dlp attempts failed, trying Invidious fallback...")
                    return self._search_invidious(query, max_results)
                print(f"[ERROR] Search error: {e}")
                return []
    
    def _format_duration'''

if old in content:
    content = content.replace(old, new)
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated search method with Invidious fallback')
else:
    print('Pattern not found, trying alternative...')
    # Try with single return
    old2 = '''        print(f"[ERROR] Search error: {e}")
                return []
    
    def _format_duration'''
    if old2 in content:
        content = content.replace(old2, new)
        with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Updated with alternative pattern')
    else:
        print('Alternative pattern not found either')