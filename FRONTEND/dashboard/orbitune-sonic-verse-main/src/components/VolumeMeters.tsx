interface VolumeMeterProps {
  volume: number; // 0 to 100
  isPlaying?: boolean;
}

const VolumeMeters = ({ volume, isPlaying = false }: VolumeMeterProps) => {
  const meterCount = 5;
  const normalizedVolume = volume / 100;

  const getBarColor = (index: number) => {
    const threshold = (index + 1) / meterCount;
    
    if (normalizedVolume < threshold) {
      return 'bg-white/10';
    }
    
    if (threshold <= 0.6) {
      return 'bg-green-500';
    } else if (threshold <= 0.85) {
      return 'bg-yellow-500';
    } else {
      return 'bg-red-500';
    }
  };

  const getBarAnimation = (index: number) => {
    const threshold = (index + 1) / meterCount;
    if (isPlaying && normalizedVolume >= threshold) {
      return 'animate-pulse';
    }
    return '';
  };

  return (
    <div className="flex items-end gap-0.5 h-4">
      {Array.from({ length: meterCount }).map((_, i) => (
        <div
          key={i}
          className={`w-1 rounded-full transition-all duration-200 ${getBarColor(i)} ${getBarAnimation(i)}`}
          style={{
            height: `${((i + 1) / meterCount) * 100}%`,
          }}
        />
      ))}
    </div>
  );
};

export default VolumeMeters;
