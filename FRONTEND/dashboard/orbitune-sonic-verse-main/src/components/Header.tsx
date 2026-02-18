import { useState, useEffect } from 'react';
import { Headphones, Menu, Moon, Sun, Home, User, LogOut, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/components/theme-provider';
import { motion, AnimatePresence } from 'framer-motion';

const Header = () => {
  const { theme, setTheme } = useTheme();
  const [user, setUser] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize a cosmetic user profile (no real auth)
  useEffect(() => {
    const ensureUserProfile = () => {
      const userData = localStorage.getItem('orbitune-user');

      if (userData) {
        try {
          setUser(JSON.parse(userData));
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      } else {
        const fallbackUser = {
          name: 'ORBITUNE User',
          email: 'user@orbitune.com',
          photo:
            'https://ui-avatars.com/api/?name=ORBITUNE+User&background=8B5CF6&color=fff',
        };
        setUser(fallbackUser);
        localStorage.setItem('orbitune-user', JSON.stringify(fallbackUser));
      }

      setIsLoading(false);
    };

    // Initial load
    ensureUserProfile();

    // Listen for profile changes from other tabs
    const handleStorageChange = (e) => {
      if (e.key === 'orbitune-user') {
        ensureUserProfile();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // No explicit logout needed; header just shows a cosmetic profile.

  return (
    <header className="fixed top-0 left-0 right-0 z-40 glass-strong border-b border-white/10 backdrop-blur-xl">
      <div className="container mx-auto px-3 sm:px-4 lg:px-6 h-14 sm:h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="relative">
            <div className="w-8 h-8 sm:w-9 sm:h-9 lg:w-10 lg:h-10 rounded-full bg-gradient-to-br from-primary via-secondary to-accent flex items-center justify-center animate-spin-slow">
              <Headphones className="w-4 h-4 sm:w-4.5 sm:h-4.5 lg:w-5 lg:h-5 text-white" style={{ animation: 'none' }} />
            </div>
            <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary via-secondary to-accent blur-lg opacity-50" />
          </div>
          <h1 className="text-base sm:text-lg md:text-xl lg:text-2xl font-bold text-gradient font-orbitron tracking-wider">ORBITUNE</h1>
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          {/* Homepage Button */}
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full h-8 w-8 sm:h-9 sm:w-9 lg:h-10 lg:w-10"
            onClick={() => window.location.href = 'http://localhost:3000'}
            title="Go to Homepage"
          >
            <Home className="w-4 h-4 sm:w-4.5 sm:h-4.5 lg:w-5 lg:h-5" />
          </Button>

          {/* Theme Toggle */}
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full h-8 w-8 sm:h-9 sm:w-9 lg:h-10 lg:w-10"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            title="Toggle theme"
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4 sm:w-4.5 sm:h-4.5 lg:w-5 lg:h-5" />
            ) : (
              <Moon className="w-4 h-4 sm:w-4.5 sm:h-4.5 lg:w-5 lg:h-5" />
            )}
          </Button>

          {/* User Profile - All Screens */}
          {user ? (
            <div className="relative">
              <motion.button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center gap-1.5 sm:gap-2 glass hover:glass-strong px-2 sm:px-2.5 py-1.5 rounded-full transition-all border border-white/10 hover:border-primary/50"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title={`Logged in as ${user.name}`}
              >
                <img
                  src={user.photo}
                  alt={user.name}
                  className="w-6 h-6 sm:w-7 sm:h-7 rounded-full border-2 border-primary/50"
                  onError={(e) => {
                    e.target.src = 'https://ui-avatars.com/api/?name=' + encodeURIComponent(user.name) + '&background=8B5CF6&color=fff'
                  }}
                />
                <span className="hidden sm:inline text-xs font-medium font-electrolize max-w-[80px] lg:max-w-[100px] truncate">
                  {user.name}
                </span>
                <ChevronDown className="hidden sm:inline w-3 h-3" />
              </motion.button>

              {/* Dropdown Menu */}
              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, y: -10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -10, scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                    className="absolute right-0 mt-2 w-48 sm:w-56 bg-background/95 backdrop-blur-xl rounded-xl border border-white/10 shadow-2xl overflow-hidden z-50"
                    style={{
                      boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 30px rgba(139, 92, 246, 0.3)'
                    }}
                  >
                    <div className="p-2.5 sm:p-3 border-b border-white/10">
                      <p className="text-sm font-semibold font-orbitron truncate">{user.name}</p>
                      <p className="text-xs text-muted-foreground font-electrolize truncate">{user.email}</p>
                    </div>
                    <div className="p-2">
                      <button
                        onClick={() => { window.location.href = 'http://localhost:3000'; }}
                        className="w-full flex items-center gap-2 px-3 py-2 text-sm font-electrolize hover:bg-primary/10 rounded-lg transition-colors"
                      >
                        <Home className="w-4 h-4" />
                        Homepage
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ) : isLoading ? (
            // Loading state
            <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-primary/20 animate-pulse" />
          ) : null}
        </div>
      </div>
    </header>
  );
};

export default Header;
