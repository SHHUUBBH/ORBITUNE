import { useEffect, useState } from 'react';

interface AudioDebuggerProps {
  audioRef: React.RefObject<HTMLAudioElement>;
  currentTrack: any;
  isPlaying: boolean;
}

const AudioDebugger = ({ audioRef, currentTrack, isPlaying }: AudioDebuggerProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const [debugInfo, setDebugInfo] = useState({
    readyState: 0,
    networkState: 0,
    paused: true,
    ended: false,
    currentSrc: '',
    volume: 0,
    muted: false,
    duration: 0,
    currentTime: 0,
    error: null as string | null,
  });

  // Toggle debug panel with Ctrl+Space
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Space to toggle debug panel
      if (e.ctrlKey && e.code === 'Space') {
        e.preventDefault();
        setIsVisible(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateDebugInfo = () => {
      setDebugInfo({
        readyState: audio.readyState,
        networkState: audio.networkState,
        paused: audio.paused,
        ended: audio.ended,
        currentSrc: audio.currentSrc || audio.src || 'none',
        volume: audio.volume,
        muted: audio.muted,
        duration: audio.duration || 0,
        currentTime: audio.currentTime || 0,
        error: audio.error ? `${audio.error.code}: ${audio.error.message}` : null,
      });
    };

    // Update immediately
    updateDebugInfo();

    // Listen for state changes
    const events = [
      'loadstart',
      'loadedmetadata',
      'loadeddata',
      'canplay',
      'canplaythrough',
      'playing',
      'pause',
      'ended',
      'error',
      'stalled',
      'suspend',
      'waiting',
    ];

    events.forEach(event => {
      audio.addEventListener(event, updateDebugInfo);
    });

    const interval = setInterval(updateDebugInfo, 500);

    return () => {
      events.forEach(event => {
        audio.removeEventListener(event, updateDebugInfo);
      });
      clearInterval(interval);
    };
  }, [audioRef]);

  const readyStateText = ['HAVE_NOTHING', 'HAVE_METADATA', 'HAVE_CURRENT_DATA', 'HAVE_FUTURE_DATA', 'HAVE_ENOUGH_DATA'][debugInfo.readyState] || 'UNKNOWN';
  const networkStateText = ['NETWORK_EMPTY', 'NETWORK_IDLE', 'NETWORK_LOADING', 'NETWORK_NO_SOURCE'][debugInfo.networkState] || 'UNKNOWN';

  // Don't render if not visible
  if (!isVisible) return null;

  return (
    <div className="fixed top-20 right-4 z-[100] glass-strong p-4 rounded-lg text-xs max-w-sm border border-white/20 shadow-2xl animate-in fade-in slide-in-from-right duration-300">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-bold text-primary">🎵 Audio Debug Info</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-muted-foreground hover:text-foreground transition-colors"
          title="Close (or press Ctrl+Space)"
        >
          ✕
        </button>
      </div>
      <div className="text-[9px] text-muted-foreground mb-3 border-b border-white/10 pb-2">
        Press <kbd className="px-1 py-0.5 bg-white/10 rounded">Ctrl+Space</kbd> to toggle
      </div>
      <div className="space-y-1 font-mono text-[10px]">
        <div><strong>Track:</strong> {currentTrack?.title || 'None'}</div>
        <div><strong>Audio URL:</strong> {currentTrack?.audioUrl ? '✓ Set' : '✗ Missing'}</div>
        <div><strong>State (Context):</strong> {isPlaying ? '▶️ Playing' : '⏸️ Paused'}</div>
        <div><strong>State (Element):</strong> {debugInfo.paused ? '⏸️ Paused' : '▶️ Playing'}</div>
        <div><strong>Ready State:</strong> {readyStateText} ({debugInfo.readyState})</div>
        <div><strong>Network State:</strong> {networkStateText} ({debugInfo.networkState})</div>
        <div><strong>Volume:</strong> {(debugInfo.volume * 100).toFixed(0)}%</div>
        <div><strong>Muted:</strong> {debugInfo.muted ? '🔇 Yes' : '🔊 No'}</div>
        <div><strong>Time:</strong> {debugInfo.currentTime.toFixed(1)}s / {debugInfo.duration.toFixed(1)}s</div>
        <div><strong>Source:</strong> {debugInfo.currentSrc ? '✓' : '✗'}</div>
        {debugInfo.currentSrc && (
          <div className="text-[8px] break-all opacity-60">{debugInfo.currentSrc}</div>
        )}
        {debugInfo.error && (
          <div className="text-red-500"><strong>Error:</strong> {debugInfo.error}</div>
        )}
        {debugInfo.ended && (
          <div className="text-yellow-500"><strong>Status:</strong> Ended</div>
        )}
      </div>
    </div>
  );
};

export default AudioDebugger;
