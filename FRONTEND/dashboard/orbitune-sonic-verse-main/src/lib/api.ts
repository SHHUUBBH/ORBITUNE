import { Song } from '@/types/music';
import { DEMO_TRACKS } from '@/data/demoSongs';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function fetchSongs(): Promise<Song[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/songs`, {
      headers: {
        'Accept': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data.songs || data;
  } catch (error) {
    console.warn('Backend unavailable, falling back to bundled demo tracks:', error);
    return DEMO_TRACKS.map(demo => ({
      id: demo.id,
      title: demo.title,
      artist: demo.artist,
      album: demo.album || 'Orbitune 3D Master',
      duration: demo.duration || 180,
      thumbnail: demo.imageUrl,
      audioUrl: demo.audioUrl,
      genre: '3D Spatial',
      releaseYear: 2025,
    }));
  }
}
