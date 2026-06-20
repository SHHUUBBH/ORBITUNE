# Read the file
with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update the Invidious fallback to call demo fallback when all instances fail
old_invidious_end = '''        print("[ERROR] All Invidious instances failed")
        return []'''

new_invidious_end = '''        print("[ERROR] All Invidious instances failed")
        print("[YTDL] Trying demo fallback...")
        return self._search_demo_fallback(query, max_results)'''

if old_invidious_end in content:
    content = content.replace(old_invidious_end, new_invidious_end)
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated Invidious fallback to call demo fallback')
else:
    print('Could not find Invidious fallback end')