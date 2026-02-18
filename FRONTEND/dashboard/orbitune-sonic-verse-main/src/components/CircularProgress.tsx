interface CircularProgressProps {
  progress: number; // 0 to 1
  size?: number;
  strokeWidth?: number;
  children?: React.ReactNode;
}

const CircularProgress = ({ 
  progress, 
  size = 120, 
  strokeWidth = 4,
  children 
}: CircularProgressProps) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - progress * circumference;

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="absolute inset-0 -rotate-90"
        style={{ filter: 'drop-shadow(0 0 8px rgba(139, 92, 246, 0.5))' }}
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255, 255, 255, 0.1)"
          strokeWidth={strokeWidth}
        />
        {/* Progress circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#progressGradient)"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-300 ease-out"
        />
        <defs>
          <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgb(139, 92, 246)" />
            <stop offset="50%" stopColor="rgb(236, 72, 153)" />
            <stop offset="100%" stopColor="rgb(251, 146, 60)" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        {children}
      </div>
    </div>
  );
};

export default CircularProgress;
