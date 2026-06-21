const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export interface YoutubeSuggestion {
    id: string;
    title: string;
    artist: string;
    duration: number;
    thumbnail: string;
    url: string;
}

export interface Song {
    id: string;
    title: string;
    artist: string;
    album: string;
    duration: number;
    url?: string;
    thumbnail?: string;
    audioUrl?: string;
    audioPath?: string;
    spatialAudioPath?: string;
    genre?: string;
    releaseYear?: number;
}

export interface ChatResponse {
    response: string;
    intent: string;
    songs?: Song[];
}

/**
 * Fetch songs from the backend
 */
export async function fetchSongs(query?: string): Promise<Song[]> {
    try {
        const url = query
            ? `${API_BASE_URL}/api/songs?search=${encodeURIComponent(query)}`
            : `${API_BASE_URL}/api/songs`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.songs || [];
    } catch (error) {
        console.error('Error fetching songs:', error);
        return [];
    }
}

/**
 * Search YouTube for songs
 */
export async function searchYoutube(query: string): Promise<YoutubeSuggestion[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/youtube/search?query=${encodeURIComponent(query)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.results || [];
    } catch (error) {
        console.error('Error searching YouTube:', error);
        return [];
    }
}

/**
 * Alias for searchYoutube - used by ConversationalInput component
 */
export async function searchYoutubeSongs(query: string): Promise<YoutubeSuggestion[]> {
    return searchYoutube(query);
}

/**
 * Create a song from YouTube URL and convert to 3D audio
 */
export async function createSongFromYoutube(
    youtubeUrl: string,
    onProgress?: (step: number, total: number, description: string) => void
): Promise<Song | null> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/songs/from-youtube`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                youtubeUrl: youtubeUrl
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        return {
            id: data.id || Date.now().toString(),
            title: data.title || 'Unknown Title',
            artist: data.artist || 'Unknown Artist',
            album: data.album || '',
            duration: data.duration || 0,
            url: youtubeUrl,
            thumbnail: data.thumbnail,
            audioUrl: data.audioUrl,
            audioPath: data.audioUrl,
            spatialAudioPath: data.audioUrl,
            genre: data.genre,
            releaseYear: data.releaseYear,
        };
    } catch (error) {
        console.error('Error creating 3D audio from YouTube:', error);
        return null;
    }
}

/**
 * Get chat response from AI companion
 */
export async function getChatResponse(
    userId: string,
    userMessage: string,
    conversationHistory?: Array<{ role: string; content: string }>
): Promise<ChatResponse> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/chatbot/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: userId,
                message: userMessage,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        return {
            response: data.response || '',
            intent: data.intent || 'general',
            songs: data.songResults || [],
        };
    } catch (error) {
        console.error('Error getting chat response:', error);
        return {
            response: 'Sorry, I encountered an error. Please try again.',
            intent: 'error',
            songs: [],
        };
    }
}

/**
 * Send chat message to AI companion - alias for getChatResponse
 */
export async function sendChatMessage(
    userId: string,
    userMessage: string,
    conversationHistory?: Array<{ role: string; content: string }>
): Promise<ChatResponse> {
    return getChatResponse(userId, userMessage, conversationHistory);
}

/**
 * Get mood-based music recommendations
 */
export async function getMoodRecommendations(mood: string): Promise<Song[]> {
    try {
        const response = await fetch(`${API_BASE_URL}/api/recommendations/mood`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mood }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.songs || [];
    } catch (error) {
        console.error('Error getting mood recommendations:', error);
        return [];
    }
}

/**
 * Download audio file
 */
export async function downloadAudio(songId: string, type: 'audio' | 'spatial' = 'spatial'): Promise<Blob | null> {
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/download/${songId}?type=${type}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.blob();
    } catch (error) {
        console.error('Error downloading audio:', error);
        return null;
    }
}

/**
 * Upload an audio file and extract metadata automatically
 */
export async function uploadAudioFile(
    file: File,
    onProgress?: (step: number, total: number, description: string) => void
): Promise<Song | null> {
    try {
        onProgress?.(1, 3, 'Uploading file...');
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/songs/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
        }

        onProgress?.(3, 3, 'Processing complete');
        const data = await response.json();

        return {
            id: data.id || Date.now().toString(),
            title: data.title || 'Unknown Title',
            artist: data.artist || 'Unknown Artist',
            album: data.album || '',
            duration: data.duration || 0,
            thumbnail: data.thumbnail,
            audioUrl: data.audioUrl,
            genre: data.genre,
            releaseYear: data.releaseYear,
        };
    } catch (error) {
        console.error('Error uploading audio file:', error);
        return null;
    }
}

/**
 * Health check - verify API is available
 */
export async function healthCheck(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
        });

        return response.ok;
    } catch (error) {
        console.error('API health check failed:', error);
        return false;
    }
}

// ---------------------------------------------------------------------------
// Streaming & Playback Position API
// ---------------------------------------------------------------------------

/**
 * Build the streaming URL for a song, optionally starting at a given time.
 * The backend streams a valid WAV file starting from *startFrom* seconds.
 */
export function getStreamUrl(songId: string, startFrom: number = 0): string {
    return `${API_BASE_URL}/api/songs/${songId}/stream?start_from=${Math.max(0, startFrom)}`;
}

/**
 * Save a playback position for a song on the server.
 */
export async function savePlaybackPosition(
    songId: string,
    position: number
): Promise<void> {
    try {
        await fetch(`${API_BASE_URL}/api/songs/${songId}/playback-position`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ position }),
        });
    } catch (error) {
        console.error('Error saving playback position:', error);
    }
}

/**
 * Load the saved playback position for a song.
 * Returns the position in seconds, or 0 if none saved.
 */
export async function getPlaybackPosition(songId: string): Promise<number> {
    try {
        const response = await fetch(
            `${API_BASE_URL}/api/songs/${songId}/playback-position`
        );
        if (!response.ok) return 0;
        const data = await response.json();
        return data.position ?? 0;
    } catch (error) {
        console.error('Error loading playback position:', error);
        return 0;
    }
}
