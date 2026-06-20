import { Play, Music, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SongCardProps {
  title: string;
  artist: string;
  album: string;
  duration: number;
  onPlay: () => void;
}

const SongCard = ({ title, artist, album, duration, onPlay }: SongCardProps) => {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="glass hover:glass-strong rounded-2xl p-4 flex items-center gap-4 group transition-all duration-300 hover:scale-[1.02] animate-fade-in">
      {/* Album art placeholder */}
      <div className="relative shrink-0">
        <div className="w-16 h-16 md:w-20 md:h-20 rounded-lg bg-gradient-to-br from-primary via-secondary to-accent flex items-center justify-center overflow-hidden">
          <Music className="w-8 h-8 text-white/80" />
        </div>
        
        {/* Hover play button */}
        <Button
          size="icon"
          onClick={onPlay}
          className="absolute inset-0 m-auto w-10 h-10 rounded-full bg-white/90 hover:bg-white opacity-0 group-hover:opacity-100 transition-all duration-300 scale-75 group-hover:scale-100"
        >
          <Play className="w-5 h-5 text-black ml-0.5" />
        </Button>
      </div>

      {/* Song info */}
      <div className="flex-1 min-w-0">
        <h4 className="font-semibold text-lg mb-1 truncate group-hover:text-gradient transition-all">
          {title}
        </h4>
        <p className="text-sm text-muted-foreground truncate mb-1">{artist}</p>
        <p className="text-xs text-muted-foreground/70 truncate">{album}</p>
      </div>

      {/* Duration and 3D badge */}
      <div className="flex flex-col items-end gap-2 shrink-0">
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <Clock className="w-3 h-3" />
          <span>{formatDuration(duration)}</span>
        </div>
        <div className="px-2 py-1 rounded-full glass text-xs font-medium">
          <span className="text-gradient">3D</span>
        </div>
      </div>
    </div>
  );
};

export default SongCard;
