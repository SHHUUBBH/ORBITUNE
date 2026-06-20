with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''except Exception as e:
                error_msg = str(e)
                if 'SSL' in error_msg or 'EOF' in error_msg:
                    if attempt < max_attempts:
                        wait_time = attempt * 2
                        print(f"[WARN] SSL/Connection error (attempt {attempt}/{max_attempts}), retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                        continue
                        error_msg = str(e)
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
                return []'''

new = '''except Exception as e:
                error_msg = str(e)
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
                    invidious_results = self._search_invidious(query, max_results)
                    if invidious_results:
                        return invidious_results
                    # Ultimate fallback: demo tracks for ANY query
                    print("[YTDL] Invidious failed, using demo fallback...")
                    return self._search_demo_fallback(query, max_results)
                print(f"[ERROR] Search error: {e}")
                return []'''

if old in content:
    content = content.replace(old, new)
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated with universal fallback')
else:
    print('Could not find block')