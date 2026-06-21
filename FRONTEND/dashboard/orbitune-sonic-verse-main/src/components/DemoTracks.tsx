import { Play, Pause, Headphones } from 'lucide-react';
import { demoTracks } from '@/data/demoTracks';
import { useMusic } from '@/contexts/MusicContext';

const DemoTracks = () => {
  const { state, dispatch } = useMusic();

  const handlePlayDemo = (track: typeof demoTracks[0]) => {
    if (state.currentSong?.id === track.id && state.isPlaying) {
      dispatch({ type: 'PAUSE' });
    } else {
      dispatch({ type: 'PLAY_SONG', payload: track });
      dispatch({ type: 'SET_QUEUE', payload: demoTracks });
    }
  };

  return (
    <section className="mb-6 sm:mb-8 lg:mb-12">
      {/* Section Header */}
      <div className="mb-4 sm:mb-5 lg:mb-6">
        <div className="flex items-center gap-2 sm:gap-3 mb-1 sm:mb-2">
          <Headphones className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
          <h2 className="text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gradient font-orbitron">
            Demo Tracks
          </h2>
        </div>
        <p className="text-[10px] xs:text-xs sm:text-sm lg:text-base text-muted-foreground font-electrolize">
          Experience ORBITUNE with these pre-processed 3D audio tracks
        </p>
      </div>

      {/* Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-5">
        {demoTracks.map((track) => {
          const isPlaying = state.currentSong?.id === track.id && state.isPlaying;

          return (
            <div
              key={track.id}
              onClick={() => handlePlayDemo(track)}
              className="group cursor-pointer glass hover:glass-strong rounded-xl sm:rounded-2xl overflow-hidden transition-all duration-300 hover:scale-[1.03] hover:shadow-xl hover:shadow-primary/10 border border-white/5 hover:border-primary/30"
            >
              {/* Thumbnail */}
              <div className="relative aspect-square overflow-hidden">
                <img
                  src={track.thumbnail}
                  alt={track.title}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                />
                {/* Overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />

                {/* Play/Pause Button */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-primary/90 backdrop-blur-sm flex items-center justify-center shadow-lg shadow-primary/30 transition-transform duration-300 group-hover:scale-110">
                    {isPlaying ? (
                      <Pause className="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="white" />
                    ) : (
                      <Play className="w-5 h-5 sm:w-6 sm:h-6 text-white ml-0.5" fill="white" />
                    )}
                  </div>
                </div>

                {/* Now Playing indicator */}
                {isPlaying && (
                  <div className="absolute top-2 right-2 sm:top-3 sm:right-3">
                    <div className="flex items-center gap-1 glass-strong px-2 py-1 rounded-full">
                      <div className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
                      <span className="text-[8px] sm:text-[9px] text-primary font-semibold">Playing</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-3 sm:p-4">
                <h3 className="font-semibold font-orbitron text-xs sm:text-sm lg:text-base truncate text-foreground group-hover:text-primary transition-colors">
                  {track.title}
                </h3>
                <p className="text-[10px] sm:text-xs text-muted-foreground font-electrolize truncate mt-0.5 sm:mt-1">
                  {track.artist}
                </p>
                <div className="flex items-center gap-2 mt-1.5 sm:mt-2">
                  <span className="text-[9px] sm:text-[10px] text-primary/70 font-electrolize">
                    {Math.floor(track.duration / 60)}:{(track.duration % 60).toString().padStart(2, '0')}
                  </span>
                  <span className="text-[9px] sm:text-[10px] text-muted-foreground/50">•</span>
                  <span className="text-[9px] sm:text-[10px] text-primary/70 font-electrolize">
                    3D Audio
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default DemoTracks;
