import React, { createContext, useContext, useReducer, ReactNode, useEffect } from 'react';
import { MusicState, MusicAction, Song, Playlist } from '@/types/music';
import { mockSongs } from '@/data/mockSongs';
import { fetchSongs } from '@/lib/api';

const STORAGE_KEY = 'orbitune-music-state';

// Load persisted state from localStorage
const loadPersistedState = (): Partial<MusicState> => {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            const parsed = JSON.parse(stored);
            // Convert date strings back to Date objects
            if (parsed.playlists) {
                parsed.playlists = parsed.playlists.map((pl: Playlist) => ({
                    ...pl,
                    createdAt: new Date(pl.createdAt),
                    updatedAt: new Date(pl.updatedAt),
                }));
            }
            return parsed;
        }
    } catch (error) {
        console.error('Failed to load persisted state:', error);
    }
    return {};
};

const initialState: MusicState = {
    currentSong: null,
    isPlaying: false,
    queue: [],
    recentSongs: [],
    favoriteSongs: [],
    playlists: [],
    allSongs: mockSongs,
    currentTime: 0,
    volume: 70,
    ...loadPersistedState(), // Merge persisted data
};

function musicReducer(state: MusicState, action: MusicAction): MusicState {
    switch (action.type) {
        case 'PLAY_SONG':
            return {
                ...state,
                currentSong: action.payload,
                isPlaying: true,
                currentTime: 0,
            };

        case 'PAUSE':
            return { ...state, isPlaying: false };

        case 'RESUME':
            return { ...state, isPlaying: true };

        case 'NEXT_SONG': {
            const currentIndex = state.queue.findIndex(s => s.id === state.currentSong?.id);
            const nextSong = state.queue[currentIndex + 1] || state.queue[0];
            return {
                ...state,
                currentSong: nextSong,
                currentTime: 0,
            };
        }

        case 'PREVIOUS_SONG': {
            const currentIndex = state.queue.findIndex(s => s.id === state.currentSong?.id);
            const prevSong = state.queue[currentIndex - 1] || state.queue[state.queue.length - 1];
            return {
                ...state,
                currentSong: prevSong,
                currentTime: 0,
            };
        }

        case 'ADD_TO_FAVORITES': {
            const isAlreadyFavorite = state.favoriteSongs.some(s => s.id === action.payload.id);
            if (isAlreadyFavorite) return state;
            return {
                ...state,
                favoriteSongs: [...state.favoriteSongs, action.payload],
            };
        }

        case 'REMOVE_FROM_FAVORITES':
            return {
                ...state,
                favoriteSongs: state.favoriteSongs.filter(s => s.id !== action.payload),
            };

        case 'ADD_TO_RECENT': {
            const filtered = state.recentSongs.filter(s => s.id !== action.payload.id);
            return {
                ...state,
                recentSongs: [action.payload, ...filtered].slice(0, 20), // Keep last 20
            };
        }

        case 'CREATE_PLAYLIST': {
            const newPlaylist: Playlist = {
                id: Date.now().toString(),
                name: action.payload.name,
                description: action.payload.description,
                songs: [],
                createdAt: new Date(),
                updatedAt: new Date(),
            };
            return {
                ...state,
                playlists: [...state.playlists, newPlaylist],
            };
        }

        case 'ADD_TO_PLAYLIST': {
            return {
                ...state,
                playlists: state.playlists.map(pl =>
                    pl.id === action.payload.playlistId
                        ? { ...pl, songs: [...pl.songs, action.payload.song], updatedAt: new Date() }
                        : pl
                ),
            };
        }

        case 'REMOVE_FROM_PLAYLIST': {
            return {
                ...state,
                playlists: state.playlists.map(pl =>
                    pl.id === action.payload.playlistId
                        ? { ...pl, songs: pl.songs.filter(s => s.id !== action.payload.songId), updatedAt: new Date() }
                        : pl
                ),
            };
        }

        case 'SET_QUEUE':
            return { ...state, queue: action.payload };

        case 'UPDATE_TIME':
            return { ...state, currentTime: action.payload };

        case 'SET_VOLUME':
            return { ...state, volume: action.payload };

        case 'SET_ALL_SONGS':
            return { ...state, allSongs: action.payload };

        default:
            return state;
    }
}

const MusicContext = createContext<{
    state: MusicState;
    dispatch: React.Dispatch<MusicAction>;
    clearPersistedData: () => void;
} | undefined>(undefined);

export function MusicProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(musicReducer, initialState);

    // Initial load: try to hydrate songs from backend API (fallback to mockSongs)
    useEffect(() => {
        let cancelled = false;

        (async () => {
            const apiSongs = await fetchSongs();
            if (!cancelled && apiSongs.length > 0) {
                dispatch({ type: 'SET_ALL_SONGS', payload: apiSongs });
            }
        })();

        return () => {
            cancelled = true;
        };
    }, []);

    // Save state to localStorage whenever it changes
    useEffect(() => {
        try {
            const stateToPersist = {
                favoriteSongs: state.favoriteSongs,
                recentSongs: state.recentSongs,
                playlists: state.playlists,
                volume: state.volume,
            };
            localStorage.setItem(STORAGE_KEY, JSON.stringify(stateToPersist));
        } catch (error) {
            console.error('Failed to persist state:', error);
        }
    }, [state.favoriteSongs, state.recentSongs, state.playlists, state.volume]);

    // Add to recent when a song is played
    useEffect(() => {
        if (state.currentSong && state.isPlaying) {
            dispatch({ type: 'ADD_TO_RECENT', payload: state.currentSong });
        }
    }, [state.currentSong, state.isPlaying]);

    // Function to clear persisted data (useful for debugging)
    const clearPersistedData = () => {
        localStorage.removeItem(STORAGE_KEY);
        window.location.reload();
    };

    return (
        <MusicContext.Provider value={{ state, dispatch, clearPersistedData }}>
            {children}
        </MusicContext.Provider>
    );
}

export function useMusic() {
    const context = useContext(MusicContext);
    if (!context) {
        throw new Error('useMusic must be used within MusicProvider');
    }
    return context;
}
