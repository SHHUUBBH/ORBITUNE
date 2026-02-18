import { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Repeat, Repeat1, Shuffle, Heart, ListPlus, Maximize2, Minimize2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { useMusic } from '@/contexts/MusicContext';
import { toast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';
import MusicVisualizer from '@/components/MusicVisualizer';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';

const MusicPlayer = () => {
  const { state, dispatch } = useMusic();
  const [volume, setVolume] = useState(state.volume);
  const [previousVolume, setPreviousVolume] = useState(state.volume);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [repeatMode, setRepeatMode] = useState<'off' | 'all' | 'one'>('off');
  const [isShuffle, setIsShuffle] = useState(false);
  const [showPlaylistDialog, setShowPlaylistDialog] = useState(false);
  const [newPlaylistName, setNewPlaylistName] = useState('');
  const [newPlaylistDescription, setNewPlaylistDescription] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [dragTime, setDragTime] = useState(0);
  const [isExpanded, setIsExpanded] = useState(false);

  const currentTrack = state.currentSong;
  const isPlaying = state.isPlaying;
  const currentTime = state.currentTime;
  const isLiked = currentTrack ? state.favoriteSongs.some(s => s.id === currentTrack.id) : false;

  useEffect(() => {
    setVolume(state.volume);
  }, [state.volume]);

  // Keep underlying audio element volume in sync with slider / state
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const normalized = Math.min(Math.max(volume, 0), 100) / 100;
    audio.volume = normalized;
  }, [volume]);

// Sync current track change to audio element (but do NOT reset on pause/play)
useEffect(() => {
  const audio = audioRef.current;
  if (!audio || !currentTrack) return;

  const src = currentTrack.audioUrl;
  if (!src) {
    // If no audio URL, do not try to play
    return;
  }

  // Ensure CORS/preload attributes are set before assigning src
  audio.crossOrigin = 'anonymous';
  audio.preload = 'auto';

  // If the audio element is already pointing at this src, do not
  // reinitialize it. This prevents unintended restarts when other
  // state changes cause this effect to re-run.
  const currentSrc = audio.currentSrc || audio.src;
  if (currentSrc && (currentSrc === src || currentSrc.endsWith(src))) {
    return;
  }

  // When the *track* actually changes, start from the beginning
  audio.src = src;
  audio.currentTime = 0;
  audio.load();

  // Apply current volume to new source
  const normalized = Math.min(Math.max(volume, 0), 100) / 100;
  audio.volume = normalized;

  // Autoplay when ready if state says so
  const onCanPlay = () => {
    if (isPlaying) {
      void audio.play().catch((err) => {
        console.error('Audio play error', err);
      });
    }
  };

  audio.addEventListener('canplay', onCanPlay, { once: true });
  return () => {
    audio.removeEventListener('canplay', onCanPlay);
  };
}, [currentTrack]);

  // Sync play/pause state with audio element
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !currentTrack || !currentTrack.audioUrl) return;

    if (isPlaying) {
      void audio.play().catch((err) => {
        console.error('Audio play error', err);
      });
    } else {
      audio.pause();
    }
  }, [isPlaying, currentTrack]);

  // Attach audio event listeners for time updates and ended
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      // Avoid state churn while the user is dragging the thumb
      if (!isDragging) {
        dispatch({ type: 'UPDATE_TIME', payload: Math.floor(audio.currentTime) });
      }
    };

    const handleEnded = () => {
      if (repeatMode === 'one') {
        audio.currentTime = 0;
        void audio.play().catch(() => undefined);
      } else if (repeatMode === 'all' || state.queue.length > 0) {
        dispatch({ type: 'NEXT_SONG' });
      }
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [dispatch, repeatMode, state.queue.length, isDragging]);

  const handlePlayPause = async () => {
    if (!currentTrack) return;
    
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      dispatch({ type: 'PAUSE' });
    } else {
      // Ensure we have a user interaction to resume audio context
      try {
        // This user gesture allows audio context to resume
        if (audio.paused) {
          await audio.play();
        }
      } catch (error) {
        console.error('Play error:', error);
      }
      dispatch({ type: 'RESUME' });
    }
  };

  const handleNext = () => {
    if (state.queue.length > 0) {
      dispatch({ type: 'NEXT_SONG' });
    }
  };

  const handlePrevious = () => {
    if (state.queue.length > 0) {
      dispatch({ type: 'PREVIOUS_SONG' });
    }
  };

  const handleLike = () => {
    if (!currentTrack) return;
    if (isLiked) {
      dispatch({ type: 'REMOVE_FROM_FAVORITES', payload: currentTrack.id });
    } else {
      dispatch({ type: 'ADD_TO_FAVORITES', payload: currentTrack });
    }
  };

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0];
    setVolume(newVolume);
    dispatch({ type: 'SET_VOLUME', payload: newVolume });
  };

  const toggleMute = () => {
    if (volume > 0) {
      setPreviousVolume(volume);
      setVolume(0);
      dispatch({ type: 'SET_VOLUME', payload: 0 });
    } else {
      const restoreVolume = previousVolume > 0 ? previousVolume : 70;
      setVolume(restoreVolume);
      dispatch({ type: 'SET_VOLUME', payload: restoreVolume });
    }
  };

  const toggleRepeat = () => {
    setRepeatMode((prev) => {
      if (prev === 'off') return 'all';
      if (prev === 'all') return 'one';
      return 'off';
    });
  };

  // Handle seek bar drag (visual update only)
  const handleTimeChange = (value: number[]) => {
    if (!currentTrack) return;
    setIsDragging(true);
    const clamped = Math.max(0, Math.min(value[0], currentTrack.duration));
    setDragTime(clamped);
  };

  // Handle seek bar release (actual seek)
  const handleTimeCommit = (value: number[]) => {
    if (!currentTrack) return;
    const clamped = Math.max(0, Math.min(value[0], currentTrack.duration));
    
    const audio = audioRef.current;
    if (audio) {
      audio.currentTime = clamped;
    }
    dispatch({ type: 'UPDATE_TIME', payload: clamped });
    setIsDragging(false);
  };

  const handleCreatePlaylist = () => {
    const name = newPlaylistName.trim();
    if (!name) return;

    dispatch({
      type: 'CREATE_PLAYLIST',
      payload: { name, description: newPlaylistDescription },
    });

    toast({
      title: 'Playlist created',
      description: `"${name}" has been added to your library.`,
    });

    setNewPlaylistName('');
    setNewPlaylistDescription('');
  };

  const handleAddToPlaylist = (playlistId: string) => {
    if (!currentTrack) return;

    dispatch({
      type: 'ADD_TO_PLAYLIST',
      payload: { playlistId, song: currentTrack },
    });

    const playlist = state.playlists.find((pl) => pl.id === playlistId);
    if (playlist) {
      toast({
        title: 'Added to playlist',
        description: `"${currentTrack.title}" was added to ${playlist.name}.`,
      });
    }

    setShowPlaylistDialog(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const shuffleQueue = () => {
    if (!currentTrack || state.allSongs.length === 0) return;

    const others = state.allSongs.filter((song) => song.id !== currentTrack.id);
    const shuffled = [...others];

    for (let i = shuffled.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }

    dispatch({ type: 'SET_QUEUE', payload: [currentTrack, ...shuffled] });
  };

  const resetQueue = () => {
    if (state.allSongs.length === 0) return;

    if (!currentTrack) {
      dispatch({ type: 'SET_QUEUE', payload: state.allSongs });
      return;
    }

    const others = state.allSongs.filter((song) => song.id !== currentTrack.id);
    dispatch({ type: 'SET_QUEUE', payload: [currentTrack, ...others] });
  };

  const toggleShuffle = () => {
    if (state.allSongs.length === 0) return;

    setIsShuffle((prev) => {
      const next = !prev;
      if (next) {
        shuffleQueue();
      } else {
        resetQueue();
      }
      return next;
    });
  };

  if (!currentTrack) {
    return (
      <div className="fixed bottom-0 left-0 right-0 z-50">
        <audio ref={audioRef} style={{ display: 'none' }} />
        <div className="glass-strong border-t border-white/10 backdrop-blur-2xl px-6 py-4">
          <div className="text-center text-muted-foreground font-electrolize text-sm">
            Select a song to begin your 3D audio journey
          </div>
        </div>
      </div>
    );
  }

  const displayTime = isDragging ? dragTime : currentTime;
  const progress = currentTrack.duration > 0 ? (displayTime / currentTrack.duration) * 100 : 0;

  return (
    <div className={cn(
      "fixed left-0 right-0 z-50 transition-all duration-300",
      isExpanded ? "bottom-0 top-0" : "bottom-0"
    )}>
      <audio ref={audioRef} crossOrigin="anonymous" preload="auto" style={{ display: 'none' }} />
      
      {/* Backdrop for expanded mode */}
      {isExpanded && (
        <div 
          className="absolute inset-0 bg-black/80 backdrop-blur-xl"
          onClick={() => setIsExpanded(false)}
        />
      )}

      <div className={cn(
        "relative glass-strong border-t border-white/10 backdrop-blur-2xl transition-all duration-300",
        isExpanded ? "h-full flex flex-col" : "h-auto"
      )}>
        {/* Animated gradient background */}
        <div 
          className="absolute inset-0 opacity-10 pointer-events-none transition-all duration-1000"
          style={{
            background: isPlaying 
              ? 'radial-gradient(circle at 50% 50%, rgba(139, 92, 246, 0.4), rgba(236, 72, 153, 0.3), transparent)'
              : 'transparent',
          }}
        />

        {/* Expanded Player View */}
        {isExpanded && (
          <div className="relative z-10 flex-1 flex flex-col items-center justify-center p-8 pb-32">
            {/* Large Album Art */}
            <div className="relative mb-8 group">
              <div 
                className="w-80 h-80 rounded-3xl overflow-hidden shadow-2xl shadow-primary/30 transition-transform duration-300"
                style={{
                  transform: isPlaying ? 'scale(1.02)' : 'scale(1)',
                }}
              >
                {currentTrack.thumbnail ? (
                  <img 
                    src={currentTrack.thumbnail} 
                    alt={currentTrack.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-gradient-to-br from-primary via-secondary to-accent" />
                )}
              </div>
              
              {/* 3D Audio Badge */}
              <div className="absolute -bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full bg-gradient-to-r from-primary to-secondary shadow-lg">
                <div className="flex items-center gap-2 text-xs font-bold text-white">
                  <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                  <span>3D SPATIAL AUDIO</span>
                </div>
              </div>
            </div>

            {/* Track Info - Centered */}
            <div className="text-center mb-8 max-w-xl">
              <h2 className="text-3xl font-bold font-orbitron mb-2 text-gradient">
                {currentTrack.title}
              </h2>
              <p className="text-xl text-muted-foreground font-electrolize">
                {currentTrack.artist}
              </p>
              {currentTrack.album && (
                <p className="text-sm text-muted-foreground/70 mt-1">
                  {currentTrack.album}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Compact Player View */}
        {!isExpanded && (
          <>
            {/* Progress bar */}
            <div className="px-6 pt-2 relative z-10">
              <Slider
                value={[displayTime]}
                max={currentTrack.duration}
                step={1}
                onValueChange={handleTimeChange}
                onValueCommit={handleTimeCommit}
                className="cursor-pointer [&>span:first-child]:h-1 [&_[role=slider]]:w-3 [&_[role=slider]]:h-3"
              />
            </div>

            <div className="px-6 py-3 flex items-center justify-between gap-4 relative z-10">
              {/* Track Info - Left */}
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="relative w-14 h-14 rounded-lg overflow-hidden flex-shrink-0 bg-black/20">
                  {isPlaying ? (
                    <div className="w-full h-full flex items-center justify-center">
                      <MusicVisualizer 
                        audioElement={audioRef.current}
                        isPlaying={isPlaying}
                        variant="circular"
                        size={56}
                        color="rgb(139, 92, 246)"
                      />
                    </div>
                  ) : (
                    currentTrack.thumbnail ? (
                      <img 
                        src={currentTrack.thumbnail} 
                        alt={currentTrack.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-primary via-secondary to-accent" />
                    )
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate font-orbitron text-sm">
                    {currentTrack.title}
                  </h3>
                  <p className="text-xs text-muted-foreground truncate font-electrolize">
                    {currentTrack.artist}
                  </p>
                </div>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLike}
                  className="shrink-0 hover:scale-110 transition-transform"
                >
                  <Heart className={cn(
                    "w-4 h-4 transition-all",
                    isLiked && "fill-red-500 text-red-500"
                  )} />
                </Button>
              </div>

              {/* Controls - Center */}
              <div className="flex flex-col items-center gap-2">
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleShuffle}
                    className={cn(
                      "w-8 h-8 hover:scale-110 transition-all",
                      isShuffle && "text-primary"
                    )}
                  >
                    <Shuffle className="w-3.5 h-3.5" />
                  </Button>

                  <Button 
                    variant="ghost" 
                    size="icon"
                    onClick={handlePrevious}
                    className="w-8 h-8 hover:scale-110 transition-all"
                  >
                    <SkipBack className="w-4 h-4" />
                  </Button>

                  <Button
                    size="icon"
                    onClick={handlePlayPause}
                    className="h-10 w-10 rounded-full bg-gradient-to-r from-primary via-secondary to-accent hover:scale-110 transition-all shadow-lg"
                  >
                    {isPlaying ? (
                      <Pause className="w-5 h-5" />
                    ) : (
                      <Play className="w-5 h-5 ml-0.5" />
                    )}
                  </Button>

                  <Button 
                    variant="ghost" 
                    size="icon"
                    onClick={handleNext}
                    className="w-8 h-8 hover:scale-110 transition-all"
                  >
                    <SkipForward className="w-4 h-4" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={toggleRepeat}
                    className={cn(
                      "w-8 h-8 hover:scale-110 transition-all",
                      repeatMode !== 'off' && "text-primary"
                    )}
                  >
                    {repeatMode === 'one' ? (
                      <Repeat1 className="w-3.5 h-3.5" />
                    ) : (
                      <Repeat className="w-3.5 h-3.5" />
                    )}
                  </Button>
                </div>

                <div className="flex items-center gap-2 text-[10px] text-muted-foreground font-mono">
                  <span>{formatTime(displayTime)}</span>
                  <div className="w-20 h-1 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-primary to-secondary transition-all"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <span>{formatTime(currentTrack.duration)}</span>
                </div>
              </div>

              {/* Small Bar Visualizer - Between Controls and Volume */}
              <div className="flex items-center justify-center px-4">
                <div className="w-32 h-12 rounded-lg overflow-hidden bg-black/20 flex items-center justify-center">
                  <MusicVisualizer 
                    audioElement={audioRef.current}
                    isPlaying={isPlaying}
                    variant="bars"
                    size={128}
                    barCount={32}
                    color="rgb(139, 92, 246)"
                  />
                </div>
              </div>

              {/* Volume & Actions - Right */}
              <div className="flex items-center gap-2 flex-1 justify-end">
                <Dialog open={showPlaylistDialog} onOpenChange={setShowPlaylistDialog}>
                  <DialogTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="icon"
                      className="w-8 h-8 hover:scale-110 transition-all"
                    >
                      <ListPlus className="w-4 h-4" />
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="sm:max-w-[500px]">
                    <DialogHeader>
                      <DialogTitle>Add to Playlist</DialogTitle>
                      <DialogDescription>
                        Add "{currentTrack.title}" to a playlist or create a new one
                      </DialogDescription>
                    </DialogHeader>

                    <ScrollArea className="max-h-[300px] pr-4">
                      <div className="space-y-2">
                        {state.playlists.length === 0 ? (
                          <p className="text-sm text-muted-foreground text-center py-4">
                            No playlists yet. Create one below!
                          </p>
                        ) : (
                          state.playlists.map((playlist) => (
                            <button
                              key={playlist.id}
                              onClick={() => handleAddToPlaylist(playlist.id)}
                              className="w-full p-3 rounded-lg glass hover:glass-strong transition-all text-left"
                            >
                              <div className="font-semibold font-orbitron">{playlist.name}</div>
                              <div className="text-sm text-muted-foreground font-electrolize">
                                {playlist.songs.length} songs
                              </div>
                            </button>
                          ))
                        )}
                      </div>
                    </ScrollArea>

                    <div className="space-y-4 pt-4 border-t">
                      <h4 className="font-semibold font-orbitron">Create New Playlist</h4>
                      <div className="space-y-2">
                        <Label htmlFor="playlist-name">Playlist Name</Label>
                        <Input
                          id="playlist-name"
                          placeholder="My Awesome Playlist"
                          value={newPlaylistName}
                          onChange={(e) => setNewPlaylistName(e.target.value)}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="playlist-description">Description (optional)</Label>
                        <Input
                          id="playlist-description"
                          placeholder="Songs that make me feel..."
                          value={newPlaylistDescription}
                          onChange={(e) => setNewPlaylistDescription(e.target.value)}
                        />
                      </div>
                      <Button
                        onClick={handleCreatePlaylist}
                        className="w-full"
                        disabled={!newPlaylistName.trim()}
                      >
                        Create Playlist
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleMute}
                  className="w-8 h-8 hover:scale-110 transition-all"
                >
                  {volume === 0 ? (
                    <VolumeX className="w-4 h-4" />
                  ) : (
                    <Volume2 className="w-4 h-4" />
                  )}
                </Button>

                <div className="w-24">
                  <Slider
                    value={[volume]}
                    max={100}
                    step={1}
                    onValueChange={handleVolumeChange}
                    className="cursor-pointer"
                  />
                </div>

                <span className="text-xs text-muted-foreground font-mono w-8 text-right">
                  {volume}%
                </span>
              </div>
            </div>
          </>
        )}

        {/* Expanded Mode Controls - Bottom */}
        {isExpanded && (
          <div className="relative z-10 px-8 pb-8">
            {/* Progress Bar */}
            <div className="mb-6">
              <Slider
                value={[displayTime]}
                max={currentTrack.duration}
                step={1}
                onValueChange={handleTimeChange}
                onValueCommit={handleTimeCommit}
                className="cursor-pointer"
              />
              <div className="flex justify-between text-sm text-muted-foreground font-mono mt-2">
                <span>{formatTime(displayTime)}</span>
                <span>{formatTime(currentTrack.duration)}</span>
              </div>
            </div>

            {/* Controls */}
            <div className="flex items-center justify-between max-w-2xl mx-auto mb-4">
              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={handleLike}
                  className="hover:scale-110 transition-transform"
                >
                  <Heart className={cn(
                    "w-5 h-5 transition-all",
                    isLiked && "fill-red-500 text-red-500"
                  )} />
                </Button>
                
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleShuffle}
                  className={cn(
                    "hover:scale-110 transition-all",
                    isShuffle && "text-primary"
                  )}
                >
                  <Shuffle className="w-5 h-5" />
                </Button>
              </div>

              <div className="flex items-center gap-4">
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={handlePrevious}
                  className="hover:scale-110 transition-all"
                >
                  <SkipBack className="w-6 h-6" />
                </Button>

                <Button
                  size="icon"
                  onClick={handlePlayPause}
                  className="h-16 w-16 rounded-full bg-gradient-to-r from-primary via-secondary to-accent hover:scale-110 transition-all shadow-2xl"
                >
                  {isPlaying ? (
                    <Pause className="w-8 h-8" />
                  ) : (
                    <Play className="w-8 h-8 ml-1" />
                  )}
                </Button>

                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={handleNext}
                  className="hover:scale-110 transition-all"
                >
                  <SkipForward className="w-6 h-6" />
                </Button>
              </div>

              <div className="flex items-center gap-4">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={toggleRepeat}
                  className={cn(
                    "hover:scale-110 transition-all",
                    repeatMode !== 'off' && "text-primary"
                  )}
                >
                  {repeatMode === 'one' ? (
                    <Repeat1 className="w-5 h-5" />
                  ) : (
                    <Repeat className="w-5 h-5" />
                  )}
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setIsExpanded(false)}
                  className="hover:scale-110 transition-all"
                >
                  <Minimize2 className="w-5 h-5" />
                </Button>
              </div>
            </div>

            {/* Volume Control - Centered */}
            <div className="flex items-center justify-center gap-4 max-w-md mx-auto">
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleMute}
                className="hover:scale-110 transition-all"
              >
                {volume === 0 ? (
                  <VolumeX className="w-5 h-5" />
                ) : (
                  <Volume2 className="w-5 h-5" />
                )}
              </Button>

              <Slider
                value={[volume]}
                max={100}
                step={1}
                onValueChange={handleVolumeChange}
                className="flex-1 cursor-pointer"
              />

              <span className="text-sm text-muted-foreground font-mono w-12 text-right">
                {volume}%
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MusicPlayer;
