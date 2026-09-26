// Song and music app types
export interface Song {
    id: string;
    title: string;
    artist: string;
    album: string;
    duration: number; // in seconds
    thumbnail: string; // image URL
    audioUrl?: string;
    genre?: string;
    releaseYear?: number;
}

export interface Playlist {
    id: string;
    name: string;
    description?: string;
    songs: Song[];
    thumbnail?: string;
    createdAt: Date;
    updatedAt: Date;
}

export interface MusicState {
    currentSong: Song | null;
    isPlaying: boolean;
    queue: Song[];
    recentSongs: Song[];
    favoriteSongs: Song[];
    playlists: Playlist[];
    allSongs: Song[];
    currentTime: number;
    volume: number;
}

export type MusicAction =
    | { type: 'PLAY_SONG'; payload: Song }
    | { type: 'PAUSE' }
    | { type: 'RESUME' }
    | { type: 'NEXT_SONG' }
    | { type: 'PREVIOUS_SONG' }
    | { type: 'ADD_TO_FAVORITES'; payload: Song }
    | { type: 'REMOVE_FROM_FAVORITES'; payload: string }
    | { type: 'ADD_TO_RECENT'; payload: Song }
    | { type: 'CREATE_PLAYLIST'; payload: { name: string; description?: string } }
    | { type: 'ADD_TO_PLAYLIST'; payload: { playlistId: string; song: Song } }
    | { type: 'REMOVE_FROM_PLAYLIST'; payload: { playlistId: string; songId: string } }
    | { type: 'SET_QUEUE'; payload: Song[] }
    | { type: 'UPDATE_TIME'; payload: number }
    | { type: 'SET_VOLUME'; payload: number }
    | { type: 'SET_ALL_SONGS'; payload: Song[] };
