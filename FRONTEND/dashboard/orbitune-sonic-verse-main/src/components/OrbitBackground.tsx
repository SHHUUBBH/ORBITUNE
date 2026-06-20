const OrbitBackground = () => {
  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
      {/* Orbital rings */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
        <div className="absolute w-[300px] h-[300px] rounded-full border border-primary/20 orbit-slow" />
        <div className="absolute w-[500px] h-[500px] rounded-full border border-secondary/20 orbit-medium" />
        <div className="absolute w-[700px] h-[700px] rounded-full border border-accent/20 orbit-fast" />
      </div>

      {/* Floating orbs */}
      <div className="absolute top-20 left-20 w-32 h-32 rounded-full bg-primary/20 blur-3xl float" />
      <div className="absolute bottom-20 right-20 w-40 h-40 rounded-full bg-secondary/20 blur-3xl float" style={{ animationDelay: '2s' }} />
      <div className="absolute top-1/2 right-40 w-24 h-24 rounded-full bg-accent/20 blur-3xl float" style={{ animationDelay: '4s' }} />
    </div>
  );
};

export default OrbitBackground;
