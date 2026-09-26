import React from 'react';
import { motion } from 'framer-motion';
import { Play, Headphones, Radio } from 'lucide-react';
import { useMusic } from '@/contexts/MusicContext';
import { DEMO_TRACKS, DemoTrack } from '@/data/demoSongs';
import { Song } from '@/types/music';

interface FeaturedTracksProps {
  onTrackSelect?: (track: DemoTrack) => void;
}

export const FeaturedTracks: React.FC<FeaturedTracksProps> = ({ onTrackSelect }) => {
  const { state, dispatch } = useMusic();
  const { currentSong, isPlaying } = state;

  const handlePlayDemo = (demo: DemoTrack) => {
    const songModel: Song = {
      id: demo.id,
      title: demo.title,
      artist: demo.artist,
      album: demo.album || 'Orbitune 3D Master',
      duration: demo.duration || 180,
      thumbnail: demo.imageUrl,
      audioUrl: demo.audioUrl,
      genre: '3D Spatial',
      releaseYear: 2025,
    };

    // Make sure it's in allSongs list so queue knows about it
    const exists = state.allSongs.some(s => s.id === songModel.id);
    if (!exists) {
      dispatch({ type: 'SET_ALL_SONGS', payload: [songModel, ...state.allSongs] });
    }

    // Immediately load into queue and play
    dispatch({ type: 'SET_QUEUE', payload: [songModel, ...state.allSongs.filter(s => s.id !== songModel.id)] });
    dispatch({ type: 'PLAY_SONG', payload: songModel });

    if (onTrackSelect) {
      onTrackSelect(demo);
    }
  };

  return (
    <section className="mb-8 xs:mb-10 sm:mb-12 lg:mb-16">
      {/* Section Header */}
      <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-4 sm:mb-6 gap-2">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
            </span>
            <span className="text-[10px] xs:text-xs font-semibold uppercase tracking-wider text-primary font-electrolize flex items-center gap-1.5">
              <Radio className="w-3.5 h-3.5 text-primary" /> 3D Audio Collection
            </span>
          </div>
          <h2 className="text-xl xs:text-2xl sm:text-3xl font-extrabold text-gradient font-orbitron tracking-tight">
            Featured 3D Master Tracks
          </h2>
          <p className="text-xs sm:text-sm text-muted-foreground font-electrolize mt-1 max-w-xl">
            Stream pre-processed 3D spatial and binaural master tracks instantly.
          </p>
        </div>

        <div className="hidden sm:flex items-center gap-2 text-xs font-electrolize text-muted-foreground glass px-3.5 py-1.5 rounded-full border border-white/10">
          <Headphones className="w-4 h-4 text-primary" />
          <span>Headphones recommended</span>
        </div>
      </div>

      {/* Grid of Featured Tracks */}
      <div className="grid grid-cols-1 xs:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3.5 sm:gap-4 lg:gap-5">
        {DEMO_TRACKS.map((track, idx) => {
          const isThisPlaying = currentSong?.id === track.id && isPlaying;
          const isThisActive = currentSong?.id === track.id;

          return (
            <motion.div
              key={track.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05, duration: 0.35 }}
              onClick={() => handlePlayDemo(track)}
              className={`group relative glass-strong rounded-xl sm:rounded-2xl p-3 sm:p-4 border transition-all duration-300 cursor-pointer overflow-hidden flex flex-col justify-between ${
                isThisActive
                  ? 'border-primary/60 shadow-[0_0_25px_rgba(168,85,247,0.35)] ring-1 ring-primary/40 bg-primary/10'
                  : 'border-white/10 hover:border-primary/40 hover:shadow-xl hover:translate-y-[-2px] hover:bg-white/[0.04]'
              }`}
            >
              {/* Top Image Container */}
              <div className="relative aspect-square w-full rounded-lg sm:rounded-xl overflow-hidden mb-3 bg-black/40">
                <img
                  src={track.imageUrl}
                  alt={track.title}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                  loading="lazy"
                />

                {/* Subtle gradient overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                {/* Hover / Active Play Button Overlay */}
                <div
                  className={`absolute inset-0 flex items-center justify-center transition-all duration-300 ${
                    isThisPlaying
                      ? 'bg-black/40 opacity-100'
                      : 'bg-black/30 opacity-0 group-hover:opacity-100'
                  }`}
                >
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center shadow-2xl transition-all duration-300 transform group-hover:scale-110 ${
                      isThisPlaying
                        ? 'bg-primary text-white ring-4 ring-primary/30 scale-105'
                        : 'bg-gradient-to-r from-primary to-secondary text-white'
                    }`}
                  >
                    {isThisPlaying ? (
                      <span className="flex gap-1 items-end h-4">
                        <span className="w-1 bg-white animate-[bounce_0.6s_infinite_100ms] rounded-full h-full"></span>
                        <span className="w-1 bg-white animate-[bounce_0.6s_infinite_300ms] rounded-full h-2/3"></span>
                        <span className="w-1 bg-white animate-[bounce_0.6s_infinite_200ms] rounded-full h-5/6"></span>
                      </span>
                    ) : (
                      <Play className="w-5 h-5 ml-0.5 fill-current" />
                    )}
                  </div>
                </div>

                {/* Audio Status Pill */}
                {isThisPlaying && (
                  <div className="absolute bottom-2 left-2 right-2 flex items-center justify-between px-2.5 py-1 rounded-md bg-black/75 backdrop-blur-sm border border-primary/30">
                    <span className="text-[10px] font-semibold text-primary font-electrolize flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" /> Playing
                    </span>
                    <span className="text-[9px] text-muted-foreground font-mono">3D Audio</span>
                  </div>
                )}
              </div>

              {/* Track Metadata */}
              <div className="flex flex-col">
                <h3
                  className={`font-semibold text-sm sm:text-base font-orbitron truncate transition-colors ${
                    isThisActive ? 'text-primary' : 'text-foreground group-hover:text-primary'
                  }`}
                  title={track.title}
                >
                  {track.title}
                </h3>
                <p className="text-xs text-muted-foreground font-electrolize truncate mt-1" title={track.artist}>
                  {track.artist}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
};

export default FeaturedTracks;
