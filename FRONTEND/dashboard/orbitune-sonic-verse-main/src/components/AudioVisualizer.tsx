import { useEffect, useRef, useState } from 'react';

interface AudioVisualizerProps {
  audioElement: HTMLAudioElement | null;
  isPlaying: boolean;
  size?: number;
}

const AudioVisualizer = ({ audioElement, isPlaying, size = 120 }: AudioVisualizerProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const analyserRef = useRef<AnalyserNode | null>(null);
  const dataArrayRef = useRef<Uint8Array | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<MediaElementAudioSourceNode | null>(null);
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    if (!audioElement) {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      return;
    }

    // Initialize Web Audio API
    const initAudio = async () => {
      try {
        // Create audio context only once
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
        }

        const audioContext = audioContextRef.current;

        // Resume context if suspended (required for autoplay policies)
        if (audioContext.state === 'suspended') {
          await audioContext.resume();
        }

        // Create source only once per audio element
        if (!sourceRef.current) {
          try {
            sourceRef.current = audioContext.createMediaElementSource(audioElement);
          } catch (error: any) {
            // If source already exists, this will throw - that's okay
            if (!error.message?.includes('already')) {
              throw error;
            }
            return;
          }
        }

        // Create analyser
        if (!analyserRef.current) {
          analyserRef.current = audioContext.createAnalyser();
          analyserRef.current.fftSize = 256;
          analyserRef.current.smoothingTimeConstant = 0.85;
          
          // Connect: audio element -> analyser -> destination
          // This ensures both visualization AND audible output
          sourceRef.current.connect(analyserRef.current);
          analyserRef.current.connect(audioContext.destination);
        }

        const bufferLength = analyserRef.current.frequencyBinCount;
        dataArrayRef.current = new Uint8Array(bufferLength);
        setIsInitialized(true);
      } catch (error) {
        console.error('Error initializing audio context:', error);
      }
    };

    initAudio();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [audioElement]);

  useEffect(() => {
    if (!isInitialized || !isPlaying || !analyserRef.current || !dataArrayRef.current) {
      return;
    }

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const analyser = analyserRef.current;
    const dataArray = dataArrayRef.current;
    const bufferLength = dataArray.length;

    const draw = () => {
      if (!isPlaying) return;

      animationRef.current = requestAnimationFrame(draw);

      analyser.getByteFrequencyData(dataArray);

      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Calculate bar dimensions
      const barCount = 64;
      const radius = size * 0.35;
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const barWidth = 3;
      const barSpacing = (Math.PI * 2) / barCount;

      // Draw circular bars
      for (let i = 0; i < barCount; i++) {
        const dataIndex = Math.floor((i / barCount) * bufferLength);
        const value = dataArray[dataIndex] || 0;
        const barHeight = (value / 255) * (radius * 0.6);

        const angle = i * barSpacing - Math.PI / 2;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        const endX = centerX + Math.cos(angle) * (radius + barHeight);
        const endY = centerY + Math.sin(angle) * (radius + barHeight);

        // Create gradient for each bar
        const gradient = ctx.createLinearGradient(x, y, endX, endY);
        const hue = (i / barCount) * 360;
        gradient.addColorStop(0, `hsla(${hue}, 80%, 60%, 0.8)`);
        gradient.addColorStop(1, `hsla(${(hue + 60) % 360}, 90%, 70%, 0.9)`);

        ctx.beginPath();
        ctx.strokeStyle = gradient;
        ctx.lineWidth = barWidth;
        ctx.lineCap = 'round';
        ctx.moveTo(x, y);
        ctx.lineTo(endX, endY);
        ctx.stroke();

        // Add glow effect
        ctx.shadowBlur = 10;
        ctx.shadowColor = `hsla(${hue}, 80%, 60%, 0.5)`;
      }

      // Draw center circle
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius * 0.2, 0, Math.PI * 2);
      const centerGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 0.2);
      centerGradient.addColorStop(0, 'rgba(139, 92, 246, 0.8)');
      centerGradient.addColorStop(1, 'rgba(236, 72, 153, 0.4)');
      ctx.fillStyle = centerGradient;
      ctx.fill();
      ctx.shadowBlur = 20;
      ctx.shadowColor = 'rgba(139, 92, 246, 0.8)';
    };

    draw();

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isInitialized, isPlaying, size]);

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <canvas
        ref={canvasRef}
        width={size * 2}
        height={size * 2}
        style={{
          width: `${size}px`,
          height: `${size}px`,
        }}
        className="absolute inset-0"
      />
    </div>
  );
};

export default AudioVisualizer;
