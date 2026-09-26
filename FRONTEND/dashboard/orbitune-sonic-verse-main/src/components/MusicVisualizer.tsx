import { useEffect, useRef } from 'react';

interface MusicVisualizerProps {
  audioElement: HTMLAudioElement | null;
  isPlaying: boolean;
  variant?: 'bars' | 'circular';
  size?: number;
  width?: number;
  height?: number;
  barCount?: number;
  color?: string;
  className?: string;
}

// Global audio graph singleton
let globalAudioContext: AudioContext | null = null;
let globalAnalyser: AnalyserNode | null = null;
let globalSource: MediaElementAudioSourceNode | null = null;
let connectedElement: HTMLAudioElement | null = null;
let globalDataArray: Uint8Array | null = null;

const MusicVisualizer = ({ 
  audioElement, 
  isPlaying, 
  variant = 'bars',
  size = 64,
  width,
  height,
  barCount = 32,
  color = '#8b5cf6',
  className = 'pointer-events-none'
}: MusicVisualizerProps) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Determine actual canvas dimensions (respect custom width/height if given, else square size)
    const targetW = width || size;
    const targetH = height || (variant === 'bars' ? 180 : size);

    // Set internal resolution (2x for Retina / HiDPI crispness)
    canvas.width = targetW * 2;
    canvas.height = targetH * 2;
    canvas.style.width = width ? '100%' : `${targetW}px`;
    canvas.style.height = height ? '100%' : `${targetH}px`;

    // Attempt connecting Web Audio API to the audio element
    const targetAudio = audioElement || (document.getElementById('orbitune-audio') as HTMLAudioElement) || document.querySelector('audio');

    if (targetAudio) {
      try {
        if (!globalAudioContext) {
          const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
          globalAudioContext = new AudioContextClass();
        }

        // Resume audio context if suspended (browser autoplay policy)
        if (globalAudioContext.state === 'suspended' && isPlaying) {
          void globalAudioContext.resume().catch(() => undefined);
        }

        if (!globalAnalyser) {
          globalAnalyser = globalAudioContext.createAnalyser();
          globalAnalyser.fftSize = 256;
          globalAnalyser.smoothingTimeConstant = 0.8;
          globalDataArray = new Uint8Array(globalAnalyser.frequencyBinCount);
        }

        // Connect source only once per audio element to avoid InvalidStateError
        if (!globalSource || connectedElement !== targetAudio) {
          globalSource = globalAudioContext.createMediaElementSource(targetAudio);
          globalSource.connect(globalAnalyser);
          globalAnalyser.connect(globalAudioContext.destination);
          connectedElement = targetAudio;
        }
      } catch (err) {
        // Fallback: Web Audio API can throw cross-origin or already-connected errors
        console.debug('Visualizer audio node note:', err);
      }
    }

    // Animation state
    let framePhase = 0;

    const draw = () => {
      if (!ctx) return;

      framePhase += 0.05;
      let hasRealAudioData = false;

      // 1. Try reading real frequency data from AnalyserNode
      if (globalAnalyser && globalDataArray) {
        globalAnalyser.getByteFrequencyData(globalDataArray);
        // Check if there is non-zero frequency activity
        let sum = 0;
        for (let i = 0; i < Math.min(globalDataArray.length, 32); i++) {
          sum += globalDataArray[i];
        }
        if (sum > 10) {
          hasRealAudioData = true;
        }
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 2. If real frequency data is available, draw from it.
      // Otherwise, synthesize realistic dynamic frequency pulses synced with isPlaying.
      if (hasRealAudioData && globalDataArray) {
        if (variant === 'bars') {
          drawBars(ctx, globalDataArray, canvas.width, canvas.height, barCount, color);
        } else {
          drawCircular(ctx, globalDataArray, canvas.width, canvas.height, color);
        }
      } else if (isPlaying) {
        // Dynamic synthetic spectrum fallback (guarantees stunning visualization for any CORS/audio source)
        const syntheticData = new Uint8Array(barCount);
        for (let i = 0; i < barCount; i++) {
          const wave1 = Math.sin(framePhase * 2.5 + i * 0.4);
          const wave2 = Math.cos(framePhase * 1.8 - i * 0.25);
          const wave3 = Math.sin(framePhase * 4.0 + i * 0.8) * 0.5;
          const combined = (wave1 + wave2 + wave3 + 2.5) / 5.0; // Normalized 0..1
          syntheticData[i] = Math.floor(Math.max(0.15, Math.min(1.0, combined)) * 255);
        }

        if (variant === 'bars') {
          drawBars(ctx, syntheticData, canvas.width, canvas.height, barCount, color);
        } else {
          drawCircular(ctx, syntheticData, canvas.width, canvas.height, color);
        }
      } else {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
      }

      if (isPlaying) {
        animationFrameRef.current = requestAnimationFrame(draw);
      }
    };

    if (isPlaying) {
      // Resume context if needed
      if (globalAudioContext && globalAudioContext.state === 'suspended') {
        void globalAudioContext.resume().catch(() => undefined);
      }
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
      className={className}
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
  _color: string
) => {
  const barWidth = width / barCount;
  const centerY = height / 2;

  for (let i = 0; i < barCount; i++) {
    const dataIndex = Math.floor((i / barCount) * dataArray.length);
    const value = Math.max((dataArray[dataIndex] || 0) / 255, 0.08);
    const barHeight = value * (height / 2) * 0.55;

    const x = i * barWidth;
    
    // Vibrant audio gradient: purple/pink/cyan
    const hue = (i / barCount) * 280 + 240; // 240 (blue) to 520 (pink/purple)
    const gradient = ctx.createLinearGradient(x, centerY - barHeight, x, centerY + barHeight);
    gradient.addColorStop(0, `hsla(${hue % 360}, 95%, 65%, 0.35)`);
    gradient.addColorStop(0.5, `hsla(${(hue + 50) % 360}, 100%, 75%, 0.85)`);
    gradient.addColorStop(1, `hsla(${hue % 360}, 95%, 65%, 0.35)`);

    ctx.fillStyle = gradient;
    ctx.fillRect(x + barWidth * 0.15, centerY - barHeight, barWidth * 0.7, barHeight * 2);
  }
};

// Draw circular visualizer
const drawCircular = (
  ctx: CanvasRenderingContext2D, 
  dataArray: Uint8Array, 
  width: number, 
  height: number,
  _color: string
) => {
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 3.4;
  const bars = Math.min(dataArray.length, 48);

  for (let i = 0; i < bars; i++) {
    const dataIndex = Math.floor((i / bars) * dataArray.length);
    const value = Math.max((dataArray[dataIndex] || 0) / 255, 0.12);
    const barLength = value * radius * 0.9;

    const angle = (i / bars) * Math.PI * 2;
    const x1 = centerX + Math.cos(angle) * radius;
    const y1 = centerY + Math.sin(angle) * radius;
    const x2 = centerX + Math.cos(angle) * (radius + barLength);
    const y2 = centerY + Math.sin(angle) * (radius + barLength);

    const gradient = ctx.createLinearGradient(x1, y1, x2, y2);
    const hue = (i / bars) * 360;
    gradient.addColorStop(0, `hsl(${hue}, 85%, 60%)`);
    gradient.addColorStop(1, `hsl(${(hue + 60) % 360}, 95%, 70%)`);

    ctx.strokeStyle = gradient;
    ctx.lineWidth = Math.max(1.5, (width / bars) * 0.7);
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  // Center subtle glowing orb
  const centerGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 0.7);
  centerGradient.addColorStop(0, 'rgba(168, 85, 247, 0.45)');
  centerGradient.addColorStop(1, 'rgba(236, 72, 153, 0.05)');
  
  ctx.beginPath();
  ctx.arc(centerX, centerY, radius * 0.7, 0, Math.PI * 2);
  ctx.fillStyle = centerGradient;
  ctx.fill();
};

export default MusicVisualizer;
