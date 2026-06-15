import { useState } from 'react';
import { useMusic } from '@/contexts/MusicContext';
import { demoTracks } from '@/data/demoTracks';
import { Button } from '@/components/ui/button';
import { Play, Pause } from 'lucide-react';
import { cn } from '@/lib/utils';

const FeaturedTracks = () => {
  const { state, dispatch } = useMusic();
  const [playingDemoId, setPlayingDemoId] = useState<string | null>(null);

  const handlePlayDemo = (track: typeof demoTracks[0]) => {
    if (playingDemoId === track.id && state.isPlaying) {
      dispatch({ type: 'PAUSE' });
      setPlayingDemoId(null);
    } else {
      // Play the demo track immediately - bypasses backend processing
      dispatch({ type: 'PLAY_SONG', payload: track });
      dispatch({ type: 'SET_QUEUE', payload: demoTracks });
      setPlayingDemoId(track.id);
    }
  };

  return (
    <section className="mb-16 xs:mb-20 sm:mb-24 lg:mb-32">
      <div className="max-w-5xl mx-auto">
        {/* Section Header */}
        <div className="mb-4 xs:mb-5 sm:mb-6 lg:mb-8 flex items-center justify-between">
          <div>
            <h2 className="text-base xs:text-lg sm:text-xl md:text-2xl lg:text-3xl font-bold text-gradient font-orbitron mb-1 xs:mb-1.5 sm:mb-2">
              Featured Tracks
            </h2>
            <p className="text-[10px] xs:text-xs sm:text-sm lg:text-base text-muted-foreground font-electrolize">
              Instant 3D audio demos — no processing wait
            </p>
          </div>
          <span className="glass px-3 py-1 rounded-full border border-white/10 text-xs font-electrolize text-muted-foreground">
            {demoTracks.length} tracks
          </span>
        </div>

        {/* Demo Tracks Grid */}
        <div className="grid grid-cols-1 xs:grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3 xs:gap-4 lg:gap-5">
          {demoTracks.map((track) => {
            const isPlaying = state.currentSong?.id === track.id && state.isPlaying;
            const isThisPlaying = playingDemoId === track.id && state.isPlaying;

            return (
              <article
                key={track.id}
                className={cn(
                  "glass-strong rounded-xl lg:rounded-2xl xl:rounded-3xl p-3 sm:p-4 lg:p-5 xl:p-6 cursor-pointer transition-all group border border-white/5 hover:border-white/20 hover:scale-[1.01]",
                  isThisPlaying && "ring-2 ring-primary shadow-lg shadow-primary/20 bg-primary/5"
                )}
                onClick={() => handlePlayDemo(track)}
              >
                {/* Thumbnail */}
                <div className="relative aspect-square rounded-lg overflow-hidden mb-3 lg:mb-4">
                  <img
                    src={track.thumbnail}
                    alt={track.title}
                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    onError={(e) => {
                      e.currentTarget.src = '';
                      e.currentTarget.style.background = 'linear-gradient(135deg, rgb(139, 92, 246), rgb(236, 72, 153), rgb(251, 146, 60))';
                    }}
                  />
                  {/* Play/Pause overlay */}
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <Button
                      size="icon"
                      variant={isThisPlaying ? "default" : "default"}
                      className={cn(
                        "w-12 h-12 xs:w-14 xs:h-14 sm:w-16 sm:h-16 rounded-full shadow-2xl transition-all",
                        isThisPlaying 
                          ? "bg-red-500 hover:bg-red-600" 
                          : "bg-gradient-to-r from-primary via-secondary to-accent hover:scale-110"
                      )}
                      onClick={(e) => {
                        e.stopPropagation();
                        handlePlayDemo(track);
                      }}
                    >
                      {isThisPlaying ? (
                        <Pause className="w-5 h-5 xs:w-6 xs:h-6 sm:w-7 sm:h-7 ml-0.5" />
                      ) : (
                        <Play className="w-5 h-5 xs:w-6 xs:h-6 sm:w-7 sm:h-7 ml-1" />
                      )}
                    </Button>
                  </div>
                  
                  {/* 3D Badge */}
                  <div className="absolute bottom-2 left-2 px-2 py-1 rounded-full bg-black/70 backdrop-blur-sm">
                    <span className="text-[8px] xs:text-[9px] font-bold text-white font-electrolize tracking-wider">
                      3D SPATIAL
                    </span>
                  </div>
                </div>

                {/* Track Info */}
                <div className="space-y-1.5 xs:space-y-2">
                  <h3 className={cn(
                    "font-semibold truncate font-orbitron text-xs xs:text-sm sm:text-base transition-colors",
                    isThisPlaying && "text-primary"
                  )}>
                    {track.title}
                  </h3>
                  <p className="text-[9px] xs:text-[10px] sm:text-xs text-muted-foreground truncate font-electrolize">
                    {track.artist}
                  </p>
                  <div className="flex items-center gap-2 text-[9px] xs:text-[10px] text-muted-foreground/70 font-electrolize">
                    <span className="glass px-2 py-0.5 rounded border border-white/10">
                      Demo
                    </span>
                    <span>•</span>
                    <span>{Math.floor((track.duration || 0) / 60)}:{(track.duration % 60).toString().padStart(2, '0')}</span>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default FeaturedTracks;