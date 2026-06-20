# Read the file
with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the search method and modify it to add Invidious fallback
old_search_ending = '''                print(f"[ERROR] Search error: {e}")
                return []


    def _format_duration'''

new_search_ending = '''                error_msg = str(e)
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

if old_search_ending in content:
    content = content.replace(old_search_ending, new_search_ending)
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated search method with Invidious fallback')
else:
    print('Could not find search method ending')
    # Debug: show context around the area
    idx = content.find('def _format_duration')
    if idx >= 0:
        print('Found _format_duration at:', idx)
        print('Context:', content[idx-200:idx+100])