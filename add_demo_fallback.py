# Read the file
with open(r'AI-ML/audio_processor/youtube_downloader.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add a demo fallback method after _search_invidious
demo_fallback_method = '''

    def _search_demo_fallback(self, query: str, max_results: int = YOUTUBE_SEARCH_MAX_RESULTS) -> List[Dict]:
        """
        Ultimate fallback: return the 4 demo tracks that are pre-loaded in the system.
        This ensures search always returns something usable for demo purposes.
        """
        print(f"[YTDL] Demo fallback for: '{query}'")
        
        # The 4 demo tracks that exist in Supabase
        demo_tracks = [
            {
                'song_id': '0951e67dd6c8',
                'video_id': 'demo-tu',
                'title': 'Tu',
                'channel': 'Talwiinder, Sanjoy',
                'duration': 240,
                'duration_string': '4:00',
                'thumbnail': 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/0951e67dd6c8.jpg',
                'url': 'https://www.youtube.com/watch?v=demo-tu',
                'view_count': 0,
            },
            {
                'song_id': '2f4318853dfa',
                'video_id': 'demo-voodoo',
                'title': 'Voodoo',
                'channel': 'Badshah, J Balvin, Tainy',
                'duration': 200,
                'duration_string': '3:20',
                'thumbnail': 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/2f4318853dfa.jpg',
                'url': 'https://www.youtube.com/watch?v=demo-voodoo',
                'view_count': 0,
            },
            {
                'song_id': 'e6fe274df9d1',
                'video_id': 'demo-sunflower',
                'title': 'Sunflower - Spider-Man: Into the Spider-Verse',
                'channel': 'Post Malone, Swae Lee, Carter Lang',
                'duration': 158,
                'duration_string': '2:38',
                'thumbnail': 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/e6fe274df9d1.jpg',
                'url': 'https://www.youtube.com/watch?v=demo-sunflower',
                'view_count': 0,
            },
            {
                'song_id': 'f1608ba400be',
                'video_id': 'demo-blinding-lights',
                'title': 'Blinding Lights',
                'channel': 'The Weeknd',
                'duration': 200,
                'duration_string': '3:20',
                'thumbnail': 'https://knsvfyoaggnyvtniitxp.supabase.co/storage/v1/object/public/orbitune-audio/f1608ba400be.jpg',
                'url': 'https://www.youtube.com/watch?v=demo-blinding-lights',
                'view_count': 0,
            }
        ]
        
        # Filter by query (simple case-insensitive match)
        filtered = []
        query_lower = query.lower()
        for track in demo_tracks:
            if query_lower in track['title'].lower() or query_lower in track['channel'].lower():
                filtered.append(track)
        
        # If no matches, return all demo tracks (up to max_results)
        if not filtered:
            filtered = demo_tracks[:max_results]
        else:
            filtered = filtered[:max_results]
        
        print(f"[YTDL] Demo fallback returned {len(filtered)} results for: '{query}'")
        return filtered

'''

# Insert after _search_invidious method
insert_marker = '        print("[ERROR] All Invidious instances failed")\n        return []'
new_content = content.replace(
    insert_marker,
    insert_marker + '\n' + demo_fallback_method
)

if insert_marker in content:
    with open(r'AI-ML/audio_processor/youtube_downloader.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('Added demo fallback method')
else:
    print('Could not find insert marker')