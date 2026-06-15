import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Music, Loader2, Sparkles, Radio, Headphones, Zap } from 'lucide-react';

interface ProcessingModalProps {
  isOpen: boolean;
  songTitle: string;
  currentStep: number;
  totalSteps: number;
  stepDescription: string;
  onCancel?: () => void;
}

const funFacts = [
  "🎵 3D audio creates an immersive sphere of sound around you!",
  "🎧 Professional studios use spatial audio for cinematic experiences",
  "✨ Your brain processes 3D audio like real-world sound sources",
  "🎼 We separate audio into 4 distinct stems: vocals, drums, bass & instruments",
  "🚀 ORBITUNE uses AI-powered source separation technology",
  "🎭 Each stem is positioned in 3D space for maximum immersion",
  "🌟 3D audio works best with headphones or surround sound systems",
  "🎹 The processing preserves the original audio quality while adding depth",
  "💫 Spatial positioning creates the illusion of sound coming from specific locations",
  "🎪 This technology is used in VR games and immersive theater experiences"
];

const ProcessingModal = ({ 
  isOpen, 
  songTitle, 
  currentStep, 
  totalSteps, 
  stepDescription,
  onCancel 
}: ProcessingModalProps) => {
  const [currentFact, setCurrentFact] = useState(0);
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number; delay: number }>>([]);
  const progress = (currentStep / totalSteps) * 100;

  // Rotate fun facts every 5 seconds
  useEffect(() => {
    if (!isOpen) return;
    
    const interval = setInterval(() => {
      setCurrentFact((prev) => (prev + 1) % funFacts.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [isOpen]);

  // Generate particles
  useEffect(() => {
    if (!isOpen) return;

    const generateParticles = () => {
      const newParticles = Array.from({ length: 20 }, (_, i) => ({
        id: Date.now() + i,
        x: Math.random() * 100,
        y: Math.random() * 100,
        delay: Math.random() * 2,
      }));
      setParticles(newParticles);
    };

    generateParticles();
    const interval = setInterval(generateParticles, 3000);

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[200] flex items-center justify-center bg-black/80 backdrop-blur-xl"
      >
        {/* Animated Background Particles */}
        {particles.map((particle) => (
          <motion.div
            key={particle.id}
            className="absolute w-2 h-2 bg-primary/30 rounded-full"
            initial={{ 
              x: `${particle.x}vw`, 
              y: `${particle.y}vh`,
              scale: 0,
              opacity: 0
            }}
            animate={{ 
              y: [`${particle.y}vh`, `${particle.y - 50}vh`],
              scale: [0, 1, 0],
              opacity: [0, 0.6, 0]
            }}
            transition={{ 
              duration: 3, 
              delay: particle.delay,
              repeat: Infinity 
            }}
          />
        ))}

        {/* Main Content */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          transition={{ type: "spring", damping: 20 }}
          className="relative w-full max-w-2xl mx-4"
        >
          {/* Glassmorphic Card */}
          <div className="glass-strong rounded-3xl p-8 md:p-12 border border-white/20 shadow-2xl overflow-hidden">
            
            {/* Animated Background Gradient */}
            <div className="absolute inset-0 opacity-20">
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-primary via-secondary to-accent"
                animate={{
                  rotate: [0, 360],
                  scale: [1, 1.2, 1],
                }}
                transition={{
                  duration: 10,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
            </div>

            {/* Content */}
            <div className="relative z-10">
              
              {/* Header with Animated Icon */}
              <div className="flex flex-col items-center mb-8">
                <motion.div
                  className="relative mb-6"
                  animate={{
                    rotate: [0, 360],
                  }}
                  transition={{
                    duration: 3,
                    repeat: Infinity,
                    ease: "linear"
                  }}
                >
                  <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                    <Music className="w-12 h-12 text-white" />
                  </div>
                  
                  {/* Orbiting Icons */}
                  {[0, 120, 240].map((angle, i) => (
                    <motion.div
                      key={i}
                      className="absolute top-1/2 left-1/2"
                      animate={{
                        rotate: [angle, angle + 360],
                      }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        ease: "linear",
                        delay: i * 0.2
                      }}
                      style={{
                        transformOrigin: '0 0',
                      }}
                    >
                      <div className="w-8 h-8 -ml-4 -mt-4 rounded-full bg-accent/80 flex items-center justify-center" style={{ transform: 'translateX(60px)' }}>
                        {i === 0 && <Headphones className="w-4 h-4 text-white" />}
                        {i === 1 && <Radio className="w-4 h-4 text-white" />}
                        {i === 2 && <Zap className="w-4 h-4 text-white" />}
                      </div>
                    </motion.div>
                  ))}
                </motion.div>

                <h2 className="text-2xl md:text-3xl font-bold text-center mb-2 font-orbitron">
                  Creating Your 3D Audio Experience
                </h2>
                <p className="text-muted-foreground text-center font-electrolize text-sm md:text-base">
                  {songTitle}
                </p>
              </div>

              {/* Circular Progress */}
              <div className="flex justify-center mb-8">
                <div className="relative w-48 h-48">
                  {/* Background Circle */}
                  <svg className="w-full h-full transform -rotate-90">
                    <circle
                      cx="96"
                      cy="96"
                      r="88"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      className="text-white/10"
                    />
                    {/* Progress Circle */}
                    <motion.circle
                      cx="96"
                      cy="96"
                      r="88"
                      stroke="url(#gradient)"
                      strokeWidth="8"
                      fill="none"
                      strokeLinecap="round"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: progress / 100 }}
                      transition={{ duration: 0.5, ease: "easeInOut" }}
                      style={{
                        strokeDasharray: "552.92",
                        strokeDashoffset: 552.92 * (1 - progress / 100),
                      }}
                    />
                    <defs>
                      <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#8B5CF6" />
                        <stop offset="50%" stopColor="#EC4899" />
                        <stop offset="100%" stopColor="#F59E0B" />
                      </linearGradient>
                    </defs>
                  </svg>
                  
                  {/* Center Content */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <motion.div
                      key={currentStep}
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      className="text-5xl font-bold text-gradient"
                    >
                      {Math.round(progress)}%
                    </motion.div>
                    <div className="text-sm text-muted-foreground mt-1">
                      Step {currentStep}/{totalSteps}
                    </div>
                  </div>
                </div>
              </div>

              {/* Current Step Description */}
              <motion.div
                key={stepDescription}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center mb-6"
              >
                <div className="flex items-center justify-center gap-2 text-foreground font-medium">
                  <Loader2 className="w-5 h-5 animate-spin text-primary" />
                  <span className="font-electrolize">{stepDescription}</span>
                </div>
              </motion.div>

              {/* Waveform Animation */}
              <div className="flex items-center justify-center gap-1 mb-8 h-16">
                {Array.from({ length: 40 }).map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-1 bg-gradient-to-t from-primary to-secondary rounded-full"
                    animate={{
                      height: [
                        Math.random() * 30 + 10,
                        Math.random() * 50 + 10,
                        Math.random() * 30 + 10,
                      ],
                    }}
                    transition={{
                      duration: 0.8,
                      repeat: Infinity,
                      delay: i * 0.05,
                      ease: "easeInOut",
                    }}
                  />
                ))}
              </div>

              {/* Fun Fact */}
              <motion.div
                key={currentFact}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white/5 rounded-2xl p-4 mb-6 border border-white/10"
              >
                <div className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-accent flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-accent mb-1">Did You Know?</p>
                    <p className="text-sm text-muted-foreground font-electrolize">
                      {funFacts[currentFact]}
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Progress Steps */}
              <div className="flex justify-between items-center mb-6">
                {Array.from({ length: totalSteps }).map((_, i) => (
                  <div key={i} className="flex items-center flex-1">
                    <motion.div
                      className={`w-10 h-10 rounded-full flex items-center justify-center border-2 ${
                        i < currentStep
                          ? 'bg-primary border-primary text-white'
                          : i === currentStep - 1
                          ? 'bg-gradient-to-br from-primary to-secondary border-secondary text-white animate-pulse'
                          : 'bg-white/5 border-white/20 text-muted-foreground'
                      }`}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: i * 0.1 }}
                    >
                      {i < currentStep ? '✓' : i + 1}
                    </motion.div>
                    {i < totalSteps - 1 && (
                      <div className={`flex-1 h-1 mx-2 rounded-full ${
                        i < currentStep - 1 ? 'bg-primary' : 'bg-white/10'
                      }`} />
                    )}
                  </div>
                ))}
              </div>

              {/* Cancel Button */}
              {onCancel && (
                <div className="text-center">
                  <button
                    onClick={onCancel}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors underline"
                  >
                    Cancel Processing
                  </button>
                </div>
              )}

              {/* Estimated Time */}
              <div className="text-center mt-4">
                <p className="text-xs text-muted-foreground font-electrolize">
                  ⏱️ Estimated time: {Math.max(0, (totalSteps - currentStep + 1) * 15)}-{Math.max(0, (totalSteps - currentStep + 1) * 20)} seconds
                </p>
              </div>

            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ProcessingModal;
