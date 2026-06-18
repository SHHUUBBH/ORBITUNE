import { useMusic } from '@/contexts/MusicContext';
import heroImage from '@/assets/orbitune-hero.jpg';
import { Music2 } from 'lucide-react';
import MusicVisualizer from '@/components/MusicVisualizer';

const HeroSection = () => {
  const { state } = useMusic();
  const { currentSong, isPlaying } = state;

  // Use current song thumbnail if playing, otherwise default hero image
  const backgroundImage = currentSong && isPlaying ? currentSong.thumbnail : heroImage;
  const showSongInfo = currentSong && isPlaying;

  return (
    <div className="relative mb-3 xs:mb-4 sm:mb-6 lg:mb-8 overflow-hidden rounded-lg xs:rounded-xl sm:rounded-2xl lg:rounded-3xl">
      {/* Hero image with overlay */}
      <div className="relative h-[180px] xs:h-[220px] sm:h-[260px] md:h-[320px] lg:h-[380px] xl:h-[460px]">
        <img
          src={backgroundImage}
          alt={showSongInfo ? currentSong.title : "ORBITUNE 3D Audio Visualization"}
          className="w-full h-full object-cover transition-all duration-700"
        />
        {/* Black transparent overlay when music is playing */}
        {isPlaying && (
          <div className="absolute inset-0 bg-black/40" />
        )}
        {/* Music visualizer overlay - behind gradient */}
        {isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center opacity-85">
            <MusicVisualizer 
              audioElement={document.querySelector('audio')}
              isPlaying={true}
              variant="bars"
              size={1400}
              barCount={140}
              color="rgb(168, 85, 247)"
            />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-background via-background/50 to-transparent" />
      </div>

      {/* Content overlay */}
      <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-2 xs:px-3 sm:px-4 md:px-6">
        {showSongInfo ? (
          // Currently playing song info
          <div className="animate-scale-in space-y-2 xs:space-y-3 sm:space-y-4 lg:space-y-5 max-w-4xl mx-auto w-full">
            <div className="flex items-center justify-center gap-1 xs:gap-1.5 sm:gap-2 lg:gap-3">
              <Music2 className="w-3 h-3 xs:w-4 xs:h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-primary animate-pulse" />
              <span className="text-[8px] xs:text-[9px] sm:text-[10px] md:text-xs lg:text-sm font-semibold text-primary/90 glass-strong px-2 xs:px-3 sm:px-4 lg:px-5 py-1 xs:py-1.5 sm:py-2 lg:py-2.5 rounded-full font-electrolize uppercase tracking-wider border border-primary/20">
                Now Playing
              </span>
            </div>
            
            <h2
              className="text-lg xs:text-xl sm:text-2xl md:text-3xl lg:text-4xl xl:text-5xl 2xl:text-6xl font-bold text-gradient font-orbitron leading-tight px-1 xs:px-2 sm:px-4 max-w-4xl mx-auto break-words"
              style={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
              }}
            >
              {currentSong.title}
            </h2>
            
            <p className="text-[10px] xs:text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl 2xl:text-2xl text-foreground/95 glass px-2 xs:px-3 sm:px-4 md:px-5 lg:px-7 py-1.5 xs:py-2 sm:py-2.5 lg:py-3.5 rounded-full font-electrolize inline-block max-w-xl mx-auto truncate">
              {currentSong.artist}
            </p>
            
            <div className="flex items-center gap-1 xs:gap-1.5 sm:gap-2 lg:gap-3 justify-center flex-wrap pt-0.5 xs:pt-1 sm:pt-2">
              <span className="text-[8px] xs:text-[9px] sm:text-[10px] md:text-xs lg:text-sm text-foreground/75 glass px-1.5 xs:px-2 sm:px-3 lg:px-4 py-0.5 xs:py-1 sm:py-1.5 lg:py-2 rounded-full font-electrolize border border-white/10">
                {currentSong.album}
              </span>
              {currentSong.releaseYear && (
                <span className="text-[8px] xs:text-[9px] sm:text-[10px] md:text-xs lg:text-sm text-foreground/75 glass px-1.5 xs:px-2 sm:px-3 lg:px-4 py-0.5 xs:py-1 sm:py-1.5 lg:py-2 rounded-full font-electrolize border border-white/10">
                  {currentSong.releaseYear}
                </span>
              )}
              {currentSong.genre && (
                <span className="text-[8px] xs:text-[9px] sm:text-[10px] md:text-xs lg:text-sm text-foreground/75 glass px-1.5 xs:px-2 sm:px-3 lg:px-4 py-0.5 xs:py-1 sm:py-1.5 lg:py-2 rounded-full font-electrolize border border-white/10">
                  {currentSong.genre}
                </span>
              )}
            </div>
          </div>
        ) : (
          // Default hero content
          <div className="space-y-2 xs:space-y-3 sm:space-y-4 lg:space-y-5 xl:space-y-6 max-w-4xl mx-auto w-full">
            <h2 className="text-xl xs:text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-bold text-gradient animate-scale-in font-orbitron leading-tight px-1 xs:px-2 sm:px-4">
              Feel Music in 3D
            </h2>
            
            <p className="text-[10px] xs:text-xs sm:text-sm md:text-base lg:text-lg xl:text-xl text-foreground/95 glass px-2 xs:px-3 sm:px-4 md:px-5 lg:px-6 xl:px-8 py-1.5 xs:py-2 sm:py-2.5 lg:py-3 xl:py-4 rounded-full animate-fade-in font-electrolize max-w-3xl mx-auto" style={{ animationDelay: '0.2s' }}>
              Revolutionary spatial audio that places you inside the music
            </p>

            {/* Feature badges */}
            <div className="flex items-center justify-center gap-1.5 xs:gap-2 sm:gap-3 lg:gap-4 animate-fade-in flex-wrap" style={{ animationDelay: '0.4s' }}>
              <div className="flex items-center gap-1 xs:gap-1.5 sm:gap-2 glass-strong px-1.5 xs:px-2 sm:px-2.5 lg:px-4 py-1 xs:py-1.5 sm:py-2 rounded-full border border-accent/20">
                <div className="w-1 h-1 xs:w-1.5 xs:h-1.5 sm:w-2 sm:h-2 rounded-full bg-accent animate-pulse" />
                <span className="text-[8px] xs:text-[9px] sm:text-[10px] md:text-xs lg:text-sm font-medium text-foreground/90 font-electrolize">
                  AI-Powered
                </span>
              </div>
              <div className="flex items-center gap-1 xs:gap-1.5 sm:gap-2 glass-strong px-1.5 xs:px-2 sm:px-2.5 lg:px-4 py-1 xs:py-1.5 sm:py-2 rounded-full border border-primary/20">
                <div className="w-1 h-1 xs:w-1.5 xs:h-1.5 sm:w-2 sm:h-2 rounded-full bg-primary animate-pulse" style={{ animationDelay: '0.2s' }} />
                <span className="text-[8px] xs:text-[9px] sm:text-[10px] md:text-xs lg:text-sm font-medium text-foreground/90 font-electrolize">
                  3D Spatial
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HeroSection;
