import { useEffect, useRef } from 'react';

interface MusicVisualizerProps {
  audioElement: HTMLAudioElement | null;
  isPlaying: boolean;
  variant?: 'bars' | 'circular';
  size?: number;
  barCount?: number;
  color?: string;
}

// Global audio context and analyser to prevent multiple MediaElementSource creation
let globalAudioContext: AudioContext | null = null;
let globalAnalyser: AnalyserNode | null = null;
let globalDataArray: Uint8Array | null = null;

const MusicVisualizer = ({ 
  audioElement, 
  isPlaying, 
  variant = 'bars',
  size = 64,
  barCount = 32,
  color = '#8b5cf6'
}: MusicVisualizerProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    if (!audioElement || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas resolution
    canvas.width = size * 2; // Higher resolution
    canvas.height = size * 2;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;

    // Create audio context and analyser (only once globally)
    if (!globalAudioContext || !globalAnalyser) {
      try {
        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        globalAudioContext = new AudioContext();
        const source = globalAudioContext.createMediaElementSource(audioElement);
        globalAnalyser = globalAudioContext.createAnalyser();
        globalAnalyser.fftSize = 256;
        source.connect(globalAnalyser);
        globalAnalyser.connect(globalAudioContext.destination);
        
        const bufferLength = globalAnalyser.frequencyBinCount;
        globalDataArray = new Uint8Array(bufferLength);
      } catch (error) {
        console.error('Audio context error:', error);
        return;
      }
    }

    const draw = () => {
      if (!ctx || !globalAnalyser || !globalDataArray) return;

      globalAnalyser.getByteFrequencyData(globalDataArray);
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      if (variant === 'bars') {
        drawBars(ctx, globalDataArray, canvas.width, canvas.height, barCount, color);
      } else {
        drawCircular(ctx, globalDataArray, canvas.width, canvas.height, color);
      }

      if (isPlaying) {
        animationFrameRef.current = requestAnimationFrame(draw);
      }
    };

    if (isPlaying) {
      draw();
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [audioElement, isPlaying, variant, size, barCount, color]);

  return (
    <canvas 
      ref={canvasRef}
      className="pointer-events-none"
    />
  );
};

// Draw bar visualizer
const drawBars = (
  ctx: CanvasRenderingContext2D, 
  dataArray: Uint8Array, 
  width: number, 
  height: number,
  barCount: number,
  color: string
) => {
  const barWidth = width / barCount;
  const centerY = height / 2;

  for (let i = 0; i < barCount; i++) {
    const dataIndex = Math.floor((i / barCount) * dataArray.length);
    const value = Math.max(dataArray[dataIndex] / 255, 0.1);
    const barHeight = value * (height / 2) * 0.35; // Reduced from 0.5 to 0.35

    const x = i * barWidth;
    
    // Rainbow gradient - each bar has different colors with transparency
    const hue = (i / barCount) * 360;
    const gradient = ctx.createLinearGradient(x, centerY - barHeight, x, centerY + barHeight);
    gradient.addColorStop(0, `hsla(${hue}, 90%, 65%, 0.25)`);
    gradient.addColorStop(0.5, `hsla(${(hue + 60) % 360}, 95%, 75%, 0.4)`);
    gradient.addColorStop(1, `hsla(${hue}, 90%, 65%, 0.25)`);

    ctx.fillStyle = gradient;
    ctx.fillRect(x + barWidth * 0.25, centerY - barHeight, barWidth * 0.5, barHeight * 2);
  }
};

// Draw circular visualizer
const drawCircular = (
  ctx: CanvasRenderingContext2D, 
  dataArray: Uint8Array, 
  width: number, 
  height: number,
  color: string
) => {
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 4;
  const bars = 64;

  for (let i = 0; i < bars; i++) {
    const dataIndex = Math.floor((i / bars) * dataArray.length);
    const value = dataArray[dataIndex] / 255;
    const barLength = value * radius * 0.8;

    const angle = (i / bars) * Math.PI * 2;
    const x1 = centerX + Math.cos(angle) * radius;
    const y1 = centerY + Math.sin(angle) * radius;
    const x2 = centerX + Math.cos(angle) * (radius + barLength);
    const y2 = centerY + Math.sin(angle) * (radius + barLength);

    const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
    
    // Vibrant RGB gradient - purple to pink to cyan
    const hue = (i / bars) * 360; // Rainbow effect
    gradient.addColorStop(0, `hsl(${hue}, 70%, 50%)`);
    gradient.addColorStop(1, `hsl(${(hue + 60) % 360}, 80%, 60%)`);

    ctx.strokeStyle = gradient;
    ctx.lineWidth = (width / bars) * 0.8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  // Center circle with gradient
  const centerGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 0.3);
  centerGradient.addColorStop(0, 'rgba(168, 85, 247, 0.5)');
  centerGradient.addColorStop(1, 'rgba(236, 72, 153, 0.2)');
  
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius * 0.3, 0, Math.PI * 2);
  ctx.fillStyle = centerGradient;
  ctx.fill();
};

export default MusicVisualizer;
