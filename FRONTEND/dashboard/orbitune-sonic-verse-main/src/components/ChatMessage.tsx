import { Music, Sparkles, User } from 'lucide-react';
import SongCard from './SongCard';
import { useMusic } from '@/contexts/MusicContext';
import { Song } from '@/types/music';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'song' | 'mood';
  content: string;
  timestamp: Date;
  songs?: Array<{
    title: string;
    artist: string;
    album: string;
    duration: number;
  }>;
}

const ChatMessage = ({ message }: { message: Message }) => {
  const isUser = message.type === 'user';
  const { state, dispatch } = useMusic();

  const handlePlaySong = (song: { title: string; artist: string; album: string; duration: number }) => {
    // Try to find the song in the library first
    let foundSong = state.allSongs.find(
      s => s.title.toLowerCase() === song.title.toLowerCase() &&
        s.artist.toLowerCase() === song.artist.toLowerCase()
    );

    // If not found, create a temporary song object
    if (!foundSong) {
      foundSong = {
        id: `temp-${Date.now()}`,
        title: song.title,
        artist: song.artist,
        album: song.album,
        duration: song.duration,
        thumbnail: '', // No thumbnail for chatbot suggestions
        genre: 'Unknown',
        releaseYear: new Date().getFullYear(),
      } as Song;
    }

    // Set the queue with all suggested songs
    if (message.songs && message.songs.length > 0) {
      const queue = message.songs.map((s, index) => {
        const existingSong = state.allSongs.find(
          existing => existing.title.toLowerCase() === s.title.toLowerCase() &&
            existing.artist.toLowerCase() === s.artist.toLowerCase()
        );

        if (existingSong) return existingSong;

        return {
          id: `temp-${Date.now()}-${index}`,
          title: s.title,
          artist: s.artist,
          album: s.album,
          duration: s.duration,
          thumbnail: '',
          genre: 'Unknown',
          releaseYear: new Date().getFullYear(),
        } as Song;
      });

      dispatch({ type: 'SET_QUEUE', payload: queue });
    }

    // Play the selected song
    dispatch({ type: 'PLAY_SONG', payload: foundSong });
  };

  return (
    <div className={`flex gap-4 animate-fade-in ${isUser ? 'flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isUser
        ? 'bg-gradient-to-br from-primary to-secondary'
        : 'glass-strong border border-white/20'
        }`}>
        {isUser ? (
          <User className="w-5 h-5" />
        ) : (
          <Sparkles className="w-5 h-5 text-accent" />
        )}
      </div>

      {/* Message content */}
      <div className={`flex-1 max-w-2xl ${isUser ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
        <div className={`glass-strong rounded-3xl p-4 ${isUser ? 'rounded-tr-sm' : 'rounded-tl-sm'}`}>
          <p className="text-foreground leading-relaxed">{message.content}</p>
        </div>

        {/* Song suggestions */}
        {/* Song suggestions */}
        {message.songs && message.songs.length > 0 && (
          <div className="space-y-3 w-full">
            {message.songs.map((song, i) => (
              <SongCard
                key={i}
                title={song.title}
                artist={song.artist}
                album={song.album}
                duration={song.duration}
                onPlay={() => handlePlaySong(song)}
              />
            ))}
          </div>
        )}
        <span className="text-xs text-muted-foreground px-2">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
};

export default ChatMessage;
