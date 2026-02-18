"use client"

import { useState, useEffect } from "react"
import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Menu, X, Sun, Moon, Github, Linkedin, Music, Headphones, Zap, Sparkles, Code, Brain, User, LogOut, ChevronDown } from "lucide-react"
import GridScan from "@/components/GridScan"
import Squares from "@/components/Squares"
import AnimatedBackground from "@/components/AnimatedBackground"

export default function HomePage() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isDarkMode, setIsDarkMode] = useState(true) // Always start with dark mode for SSR consistency
  const [activeProfile, setActiveProfile] = useState(null)
  const [user, setUser] = useState(null)
  const [showUserMenu, setShowUserMenu] = useState(false)

  const { scrollYProgress } = useScroll()
  const heroOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0])
  const heroScale = useTransform(scrollYProgress, [0, 0.3], [1, 0.8])

  // Check for user-like profile (no real auth) and load theme
  useEffect(() => {
    // Always ensure a default ORBITUNE user exists (no login required)
    const checkUserSession = () => {
      const userData = localStorage.getItem('orbitune-user')

      if (userData) {
        try {
          setUser(JSON.parse(userData))
        } catch (error) {
          console.error('Error parsing user data:', error)
        }
      } else {
        const fallbackUser = {
          name: 'ORBITUNE User',
          email: 'user@orbitune.com',
          photo:
            'https://ui-avatars.com/api/?name=ORBITUNE+User&background=8B5CF6&color=fff',
        }
        localStorage.setItem('orbitune-user', JSON.stringify(fallbackUser))
        setUser(fallbackUser)
      }
    }

    const updateTheme = () => {
      const savedTheme = localStorage.getItem('orbitune-ui-theme')
      const isThemeDark = !savedTheme || savedTheme === 'dark'

      setIsDarkMode(isThemeDark)

      // Apply theme to document
      if (isThemeDark) {
        document.documentElement.classList.add('dark')
        document.documentElement.classList.remove('light')
      } else {
        document.documentElement.classList.add('light')
        document.documentElement.classList.remove('dark')
      }
    }

    // Initial load
    checkUserSession()
    updateTheme()

    // Listen for theme and auth changes from other tabs
    const handleStorageChange = (e) => {
      if (e.key === 'orbitune-ui-theme') {
        updateTheme()
      }
      if (e.key === 'orbitune-user') {
        checkUserSession()
      }
    }

    window.addEventListener('storage', handleStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [])

  const scrollToSection = (sectionId) => {
    document.getElementById(sectionId)?.scrollIntoView({ behavior: "smooth" })
    setIsMenuOpen(false)
  }

  const toggleTheme = () => {
    const newIsDarkMode = !isDarkMode
    setIsDarkMode(newIsDarkMode)

    // Apply theme to document
    if (newIsDarkMode) {
      document.documentElement.classList.add('dark')
      document.documentElement.classList.remove('light')
    } else {
      document.documentElement.classList.add('light')
      document.documentElement.classList.remove('dark')
    }

    // Save theme to localStorage (sync with dashboard)
    const themeValue = newIsDarkMode ? 'dark' : 'light'
    localStorage.setItem('orbitune-ui-theme', themeValue)

    // Trigger storage event manually for same-tab sync
    window.dispatchEvent(new StorageEvent('storage', {
      key: 'orbitune-ui-theme',
      newValue: themeValue,
      oldValue: isDarkMode ? 'dark' : 'light'
    }))
  }

  const openProfile = (profileId) => {
    setActiveProfile(profileId)
  }

  const closeProfile = () => {
    setActiveProfile(null)
  }

  const handleLogout = () => {
    // Clear cosmetic profile for this session
    try {
      localStorage.removeItem('orbitune-user')
    } catch (error) {
      console.error('Failed to clear orbitune-user from localStorage', error)
    }
    setUser(null)
    setShowUserMenu(false)
  }

  const handleGetStarted = () => {
    // Open the app dashboard directly (no auth required)
    window.location.href = 'http://localhost:5173/dashboard'
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  }

  const itemVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.9 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        type: "spring",
        stiffness: 100,
        damping: 12,
      },
    },
  }

  const teamProfiles = [
    {
      id: "subhro",
      name: "Subhro Pal",
      role: "UI & Backend Server Dev",
      description: "Full-stack developer specializing in modern web technologies and server architecture.",
      icon: Code,
      gradient: "from-blue-500 to-purple-600",
      skills: ["React", "Node.js", "UI/UX", "Database Design"],
      photo: "/subhro.jpg",
    },
    {
      id: "yuvraj",
      name: "Yuvraj Singh Kushwah",
      role: "AI Integration & ML Dev",
      description: "AI/ML engineer focused on intelligent music processing and spatial audio algorithms.",
      icon: Brain,
      gradient: "from-green-500 to-teal-600",
      skills: ["Machine Learning", "AI Integration", "Audio Processing", "Python"],
      photo: "/yuvraj.png",
    },
  ]

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">

      <nav className="fixed top-0 w-full z-50 glassmorphism-nav backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 md:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16 lg:h-18">
            <motion.div
              className="flex-shrink-0"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
            >
              <h1 className="text-lg sm:text-xl md:text-2xl font-bold font-orbitron gradient-text tracking-wider interactive hover-glow">
                ORBITUNE
              </h1>
            </motion.div>

            <div className="hidden lg:block">
              <div className="ml-10 flex items-baseline space-x-6 xl:space-x-8">
                {[
                  { name: "HOME", icon: "🏠" },
                  { name: "ABOUT", icon: "ℹ️" },
                  { name: "FEATURES", icon: "⚡" },
                  { name: "CREDITS", icon: "👥" },
                ].map((item) => (
                  <motion.button
                    key={item.name}
                    onClick={() => scrollToSection(item.name.toLowerCase())}
                    className="nav-button-enhanced text-foreground font-electrolize font-medium tracking-wide px-3 lg:px-4 py-2 text-xs lg:text-sm transition-all duration-300 interactive relative group"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <span className="relative z-10">{item.name}</span>
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-primary/20 via-secondary/20 to-accent/20 rounded-lg opacity-0 group-hover:opacity-100"
                      initial={{ scale: 0.8 }}
                      whileHover={{ scale: 1 }}
                      transition={{ duration: 0.2 }}
                    />
                  </motion.button>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-2 sm:space-x-3 lg:space-x-4">
              <Button variant="ghost" size="sm" onClick={toggleTheme} className="glow-effect interactive hover-scale h-8 w-8 sm:h-9 sm:w-9 p-0">
                {isDarkMode ? <Sun className="h-3.5 w-3.5 sm:h-4 sm:w-4" /> : <Moon className="h-3.5 w-3.5 sm:h-4 sm:w-4" />}
              </Button>

              {/* Show different buttons based on auth state */}
              {user ? (
                // User is logged in - Show profile and dashboard button
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { window.location.href = 'http://localhost:5173/dashboard'; }}
                    className="hidden lg:inline-flex glow-effect interactive hover-scale font-electrolize font-medium tracking-wide text-xs lg:text-sm px-3 lg:px-4"
                  >
                    GO TO APP
                  </Button>

                  {/* User Profile Dropdown - Desktop */}
                  <div className="hidden lg:block relative">
                    <motion.button
                      onClick={() => setShowUserMenu(!showUserMenu)}
                      className="flex items-center gap-2 glass hover:glass-strong px-3 py-1.5 rounded-full transition-all border border-white/10 hover:border-primary/50"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <img
                        src={user.photo}
                        alt={user.name}
                        className="w-7 h-7 rounded-full border-2 border-primary/50"
                      />
                      <span className="text-xs font-medium font-electrolize max-w-[100px] truncate">
                        {user.name}
                      </span>
                      <ChevronDown className="w-3 h-3" />
                    </motion.button>

                    {/* Dropdown Menu */}
                    <AnimatePresence>
                      {showUserMenu && (
                        <motion.div
                          initial={{ opacity: 0, y: -10, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, y: -10, scale: 0.95 }}
                          transition={{ duration: 0.2 }}
                          className="absolute right-0 mt-2 w-56 glass-strong rounded-xl border border-white/10 shadow-2xl overflow-hidden z-50"
                        >
                          <div className="p-3 border-b border-white/10">
                            <p className="text-sm font-semibold font-orbitron truncate">{user.name}</p>
                            <p className="text-xs text-muted-foreground font-electrolize truncate">{user.email}</p>
                          </div>
                          <div className="p-2">
                            <button
                              onClick={() => { window.location.href = 'http://localhost:5173/dashboard'; }}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm font-electrolize hover:bg-primary/10 rounded-lg transition-colors"
                            >
                              <User className="w-4 h-4" />
                              Dashboard
                            </button>
                            <button
                              onClick={handleLogout}
                              className="w-full flex items-center gap-2 px-3 py-2 text-sm font-electrolize hover:bg-red-500/10 text-red-500 rounded-lg transition-colors"
                            >
                              <LogOut className="w-4 h-4" />
                              Logout
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                </>
              ) : (
                // User is not logged in - Show login/signup buttons
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => { window.location.href = 'http://localhost:3000/auth?mode=login'; }}
                    className="hidden md:inline-flex glow-effect interactive hover-scale font-electrolize font-medium tracking-wide text-xs lg:text-sm px-3 lg:px-4"
                  >
                    LOGIN
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => { window.location.href = 'http://localhost:3000/auth?mode=signup'; }}
                    className="hidden lg:inline-flex glow-effect interactive hover-scale font-electrolize font-medium tracking-wide text-xs lg:text-sm px-3 lg:px-4 gradient-bg text-white border-0"
                  >
                    SIGN UP
                  </Button>
                </>
              )}

              <div className="lg:hidden">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMenuOpen(!isMenuOpen)}
                  className="interactive hover-scale h-8 w-8 sm:h-9 sm:w-9 p-0"
                >
                  {isMenuOpen ? <X className="h-5 w-5 sm:h-6 sm:w-6" /> : <Menu className="h-5 w-5 sm:h-6 sm:w-6" />}
                </Button>
              </div>
            </div>
          </div>
        </div>

        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="lg:hidden glassmorphism-nav border-t border-white/10"
            >
              <div className="px-3 sm:px-4 pt-3 pb-4 space-y-2">
                {/* User Profile Section - Mobile */}
                {user && (
                  <div className="glass-strong p-3 rounded-xl border border-white/10 mb-3">
                    <div className="flex items-center gap-3">
                      <img
                        src={user.photo}
                        alt={user.name}
                        className="w-10 h-10 rounded-full border-2 border-primary/50"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold font-orbitron truncate">{user.name}</p>
                        <p className="text-xs text-muted-foreground font-electrolize truncate">{user.email}</p>
                      </div>
                    </div>
                  </div>
                )}

                {["HOME", "ABOUT", "FEATURES", "CREDITS"].map((item) => (
                  <button
                    key={item}
                    onClick={() => scrollToSection(item.toLowerCase())}
                    className="nav-button-enhanced text-foreground font-electrolize font-medium tracking-wide block px-4 py-2.5 text-sm sm:text-base w-full text-left interactive rounded-lg hover:bg-primary/10 transition-colors"
                  >
                    {item}
                  </button>
                ))}
                <Button
                  variant="ghost"
                  onClick={toggleTheme}
                  className="w-full justify-start font-electrolize interactive text-sm sm:text-base h-10 sm:h-11"
                >
                  {isDarkMode ? <Sun className="h-4 w-4 mr-2" /> : <Moon className="h-4 w-4 mr-2" />}
                  TOGGLE THEME
                </Button>

                {/* Show different buttons based on auth state */}
                {user ? (
                  <>
                    <Button
                      variant="outline"
                      onClick={() => { window.location.href = 'http://localhost:5173/dashboard'; }}
                      className="w-full justify-start font-electrolize interactive text-sm sm:text-base h-10 sm:h-11"
                    >
                      <User className="h-4 w-4 mr-2" />
                      GO TO DASHBOARD
                    </Button>
                    <Button
                      variant="ghost"
                      onClick={handleLogout}
                      className="w-full justify-start font-electrolize interactive text-sm sm:text-base h-10 sm:h-11 text-red-500 hover:bg-red-500/10"
                    >
                      <LogOut className="h-4 w-4 mr-2" />
                      LOGOUT
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      onClick={() => { window.location.href = 'http://localhost:3000/auth?mode=login'; }}
                      className="w-full justify-start font-electrolize interactive text-sm sm:text-base h-10 sm:h-11"
                    >
                      <User className="h-4 w-4 mr-2" />
                      LOGIN
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => { window.location.href = 'http://localhost:3000/auth?mode=signup'; }}
                      className="w-full justify-start font-electrolize interactive text-sm sm:text-base h-10 sm:h-11 gradient-bg text-white border-0"
                    >
                      SIGN UP
                    </Button>
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>

      <section id="home" className="relative min-h-screen flex items-center justify-center overflow-hidden pt-14 sm:pt-16">
        <div className="absolute inset-0 z-0">
          {!isDarkMode ? (
            <GridScan
              sensitivity={0.55}
              lineThickness={1}
              linesColor="#392e4e"
              gridScale={0.1}
              scanColor="#FF9FFC"
              scanOpacity={0.4}
              enablePost
              bloomIntensity={0.6}
              chromaticAberration={0.002}
              noiseIntensity={0.01}
              style={{ width: '100%', height: '100%', pointerEvents: 'auto' }}
            />
          ) : (
            <Squares
              speed={0.5}
              squareSize={60}
              direction='diagonal'
              borderColor='rgb(23, 46, 53)'
              hoverFillColor='rgb(48, 0, 97)'
            />
          )}
          <div className="absolute bottom-0 left-0 w-32 h-0 bg-background/95 rounded-tr-lg z-50"></div>
          <div className="absolute bottom-0 right-0 w-32 h-0 bg-background/95 rounded-tl-lg z-50"></div>
          <div className="absolute inset-0 bg-gradient-to-b from-black/20 to-black/40 pointer-events-none"></div>
        </div>

        <motion.div
          style={{ opacity: heroOpacity, scale: heroScale }}
          className="relative z-10 text-center px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto pointer-events-none"
        >
          <motion.div variants={containerVariants} initial="hidden" animate="visible" className="mb-6 sm:mb-8 lg:mb-10">
            <motion.h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold font-orbitron mb-4 sm:mb-6 text-balance gradient-text tracking-wide leading-tight">
              {["EXPERIENCE", "MUSIC", "IN", "A", "NEW", "ORBIT"].map((word, wordIndex) => (
                <motion.span key={wordIndex} className="inline-block mr-2 sm:mr-3 lg:mr-4" variants={itemVariants}>
                  {word}
                </motion.span>
              ))}
            </motion.h1>
          </motion.div>

          <motion.p
            variants={itemVariants}
            initial="hidden"
            animate="visible"
            className="text-sm sm:text-base md:text-lg lg:text-xl xl:text-2xl text-white mb-8 sm:mb-10 lg:mb-12 max-w-3xl mx-auto text-pretty font-electrolize tracking-wide uppercase leading-relaxed"
          >
            IMMERSE YOURSELF IN REVOLUTIONARY 3D SPATIAL AUDIO TECHNOLOGY THAT TRANSFORMS HOW YOU EXPERIENCE MUSIC FOREVER.
          </motion.p>

          <motion.div variants={itemVariants} initial="hidden" animate="visible">
            <Button
              size="lg"
              className={`${isDarkMode ? 'bg-black text-white border border-black' : 'gradient-bg text-white'} font-electrolize font-bold tracking-wider px-6 sm:px-8 py-3 sm:py-4 text-sm sm:text-base lg:text-lg transition-all duration-300 transform hover:scale-110 uppercase interactive hover-pulse h-12 sm:h-14 pointer-events-auto`}
              onClick={handleGetStarted}
            >
              GET STARTED
              <Zap className="ml-2 h-4 w-4 sm:h-5 sm:w-5" />
            </Button>
          </motion.div>
        </motion.div>
      </section>

      <section id="about" className="py-12 sm:py-16 lg:py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-background to-background/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-center mb-10 sm:mb-12 lg:mb-16"
          >
            <motion.h2
              variants={itemVariants}
              className={`text-3xl sm:text-4xl lg:text-5xl font-bold font-orbitron mb-4 sm:mb-6 text-balance ${isDarkMode ? 'text-foreground' : 'gradient-text'} tracking-wide uppercase interactive`}
            >
              ABOUT ORBITUNE
            </motion.h2>
            <motion.p
              variants={itemVariants}
              className="text-base sm:text-lg lg:text-xl text-muted-foreground max-w-3xl mx-auto text-pretty font-electrolize tracking-wide uppercase interactive leading-relaxed"
            >
              WE'RE REVOLUTIONIZING THE MUSIC EXPERIENCE WITH CUTTING-EDGE SPATIAL AUDIO TECHNOLOGY AND AI-POWERED MOOD
              TRANSFORMATION.
            </motion.p>
          </motion.div>

          <motion.div variants={itemVariants} initial="hidden" whileInView="visible" viewport={{ once: true }}>
            <Card className={`glassmorphism-card p-6 sm:p-8 lg:p-12 hover:scale-105 transition-all duration-500 interactive ${!isDarkMode ? 'border border-black' : 'border-gradient'}`}>
              <div className="grid md:grid-cols-2 gap-6 sm:gap-8 lg:gap-12 items-center">
                <div>
                  <h3 className={`text-xl sm:text-2xl lg:text-3xl font-bold font-orbitron mb-4 sm:mb-6 ${isDarkMode ? 'text-foreground' : 'gradient-text'} tracking-wide uppercase interactive`}>
                    THE FUTURE OF AUDIO
                  </h3>
                  <p className="text-sm sm:text-base lg:text-lg text-muted-foreground mb-4 sm:mb-6 leading-relaxed font-electrolize tracking-wide uppercase interactive">
                    ORBITUNE COMBINES ADVANCED 3D SPATIAL AUDIO PROCESSING WITH INTELLIGENT AI TO CREATE PERSONALIZED
                    MUSIC EXPERIENCES THAT ADAPT TO YOUR MOOD AND ENVIRONMENT.
                  </p>
                  <p className="text-sm sm:text-base lg:text-lg text-muted-foreground leading-relaxed font-electrolize tracking-wide uppercase interactive">
                    OUR REVOLUTIONARY TECHNOLOGY DOESN'T JUST PLAY MUSIC—IT CREATES IMMERSIVE SOUNDSCAPES THAT TRANSPORT
                    YOU TO NEW DIMENSIONS OF AUDIO EXPERIENCE.
                  </p>
                </div>
                <div className="flex justify-center mt-6 md:mt-0">
                  <div className="relative w-full max-w-md aspect-video rounded-lg overflow-hidden bg-black">
                    <video
                      className="w-full h-full object-cover"
                      autoPlay={true}
                      loop={true}
                      muted={true}
                      playsInline={true}
                      preload="auto"
                    >
                      <source src="/about Orbitune.mp4" type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      <section id="features" className="relative py-12 sm:py-16 lg:py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <AnimatedBackground isDarkMode={isDarkMode} />
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-center mb-10 sm:mb-12 lg:mb-16"
          >
            <motion.h2
              variants={itemVariants}
              className={`text-3xl sm:text-4xl lg:text-5xl font-bold font-orbitron mb-4 sm:mb-6 text-balance ${isDarkMode ? 'text-foreground' : 'gradient-text'} tracking-wide uppercase interactive`}
            >
              FEATURES
            </motion.h2>
            <motion.p
              variants={itemVariants}
              className="text-base sm:text-lg lg:text-xl text-muted-foreground max-w-3xl mx-auto text-pretty font-electrolize tracking-wide uppercase interactive leading-relaxed"
            >
              EXPERIENCE MUSIC LIKE NEVER BEFORE WITH OUR TWO CORE INNOVATIONS.
            </motion.p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid sm:grid-cols-2 gap-4 sm:gap-6 lg:gap-8 max-w-6xl mx-auto"
          >
            {[
              {
                icon: Headphones,
                title: "3D SPATIAL AUDIO",
                description:
                  "IMMERSE YOURSELF IN MULTI-DIMENSIONAL SOUNDSCAPES THAT SURROUND AND ENVELOP YOU FROM EVERY ANGLE.",
                gradient: "from-primary to-secondary",
                video: "/3D spatial audio.mp4",
              },
              {
                icon: Zap,
                title: "AI CHATBOT COMPANION",
                description:
                  "INTELLIGENT MUSIC ASSISTANT THAT LEARNS YOUR PREFERENCES AND SUGGESTS THE PERFECT TRACKS.",
                gradient: "from-accent to-primary",
                video: "/AI CHATBOT.mp4",
              },
            ].map((feature, index) => (
              <motion.div key={index} variants={itemVariants}>
                <Card className={`glassmorphism-card overflow-hidden h-full group hover:scale-105 transition-all duration-500 interactive ${!isDarkMode ? 'border border-black' : 'border-gradient'} feature-card`}>
                  {/* Video Section */}
                  <div className="relative w-full h-64 bg-gradient-to-br from-gray-800 to-gray-900 flex items-center justify-center overflow-hidden">
                    {feature.video ? (
                      <video
                        className="w-full h-full object-cover"
                        autoPlay
                        loop
                        muted
                        playsInline
                      >
                        <source src={feature.video} type="video/mp4" />
                      </video>
                    ) : (
                      <div className="text-center text-gray-400">
                        <feature.icon className="h-16 w-16 mx-auto mb-2 opacity-50" />
                        <p className="text-sm font-electrolize">Video Coming Soon</p>
                      </div>
                    )}
                  </div>

                  {/* Content Section */}
                  <div className="p-5 sm:p-6 lg:p-8 text-center">
                    <h3 className={`text-lg sm:text-xl lg:text-2xl font-bold font-orbitron mb-3 sm:mb-4 ${isDarkMode ? 'text-foreground' : 'gradient-text'} tracking-wide interactive uppercase`}>
                      {feature.title.toUpperCase()}
                    </h3>
                    <p className="text-xs sm:text-sm lg:text-base text-muted-foreground leading-relaxed font-electrolize tracking-wide interactive">
                      {feature.description}
                    </p>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      <section id="credits" className="relative py-12 sm:py-16 lg:py-20 px-4 sm:px-6 lg:px-8 border-t border-gradient overflow-hidden">
        <AnimatedBackground isDarkMode={isDarkMode} />
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-center mb-10 sm:mb-12 lg:mb-16"
          >
            <motion.h2
              variants={itemVariants}
              className={`text-3xl sm:text-4xl lg:text-5xl font-bold font-orbitron mb-4 sm:mb-6 text-balance ${isDarkMode ? 'text-foreground' : 'gradient-text'} tracking-wide uppercase interactive`}
            >
              MEET THE TEAM
            </motion.h2>
            <motion.p
              variants={itemVariants}
              className="text-base sm:text-lg lg:text-xl text-muted-foreground max-w-3xl mx-auto text-pretty font-electrolize tracking-wide uppercase interactive leading-relaxed"
            >
              THE BRILLIANT MINDS BEHIND ORBITUNE'S REVOLUTIONARY TECHNOLOGY.
            </motion.p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid sm:grid-cols-2 gap-6 sm:gap-8 lg:gap-12 mb-10 sm:mb-12 lg:mb-16"
          >
            {teamProfiles.map((profile, index) => (
              <motion.div key={profile.id} variants={itemVariants}>
                <Card className={`glassmorphism-card p-5 sm:p-6 lg:p-8 h-full group hover:scale-105 transition-all duration-500 interactive ${!isDarkMode ? 'border border-black' : 'border-gradient'}`}>
                  <div className="text-center">
                    <div className="mb-4 sm:mb-5 lg:mb-6 flex justify-center">
                      <motion.div
                        className={`p-3 sm:p-3.5 lg:p-4 rounded-full ${isDarkMode ? 'bg-black/20' : `bg-gradient-to-r ${profile.gradient} bg-opacity-20`} group-hover:bg-opacity-40 transition-all duration-500`}
                        whileHover={{ rotate: 360, scale: 1.1 }}
                        transition={{ duration: 0.5 }}
                      >
                        <profile.icon className="h-10 w-10 sm:h-11 sm:w-11 lg:h-12 lg:w-12 text-white group-hover:scale-125 transition-transform duration-500" />
                      </motion.div>
                    </div>
                    <h3 className={`text-xl sm:text-2xl lg:text-2xl font-bold font-orbitron mb-2 ${isDarkMode ? 'text-foreground' : 'gradient-text'} tracking-wide interactive uppercase`}>
                      {profile.name.toUpperCase()}
                    </h3>
                    <p className="text-sm sm:text-base lg:text-lg text-primary font-electrolize tracking-wide uppercase mb-3 sm:mb-4 interactive">
                      {profile.role.toUpperCase()}
                    </p>
                    <p className="text-xs sm:text-sm text-muted-foreground leading-relaxed font-electrolize mb-4 sm:mb-5 lg:mb-6 interactive">
                      {profile.description}
                    </p>
                    <div className="flex flex-wrap justify-center gap-1.5 sm:gap-2 mb-4 sm:mb-5 lg:mb-6">
                      {profile.skills.map((skill, skillIndex) => (
                        <span
                          key={skillIndex}
                          className="px-2.5 sm:px-3 py-0.5 sm:py-1 text-[10px] sm:text-xs bg-primary/20 text-primary rounded-full font-electrolize tracking-wide uppercase"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                    <Button
                      onClick={() => openProfile(profile.id)}
                      className={`${isDarkMode ? 'bg-black text-white border border-black' : 'gradient-bg text-white'} font-electrolize font-bold tracking-wider px-4 sm:px-5 lg:px-6 py-2 text-xs sm:text-sm transition-all duration-300 transform hover:scale-110 uppercase interactive hover-pulse`}
                    >
                      DIGITAL PROFILE CARD
                    </Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="text-center"
          >
            <motion.div variants={itemVariants}>
              <h3 className="text-2xl font-bold font-orbitron gradient-text mb-2 tracking-wider interactive hover-glow uppercase">
                ORBITUNE
              </h3>
              <p className="text-muted-foreground font-electrolize tracking-wide uppercase interactive">
                © 2025 ORBITUNE. ALL RIGHTS RESERVED.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      <AnimatePresence>
        {activeProfile &&
          (() => {
            const profile = teamProfiles.find((p) => p.id === activeProfile)
            return (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[10001] flex items-center justify-center p-4"
                onClick={closeProfile}
              >
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.8, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 300, damping: 25 }}
                  className="relative"
                  onClick={(e) => e.stopPropagation()}
                >
                  <Button
                    onClick={closeProfile}
                    className="absolute -top-4 -right-4 bg-red-500/20 hover:bg-red-500/40 text-white border border-red-500/50 hover:border-red-500 transition-all duration-300 interactive z-[10002]"
                    size="sm"
                  >
                    <X className="h-4 w-4" />
                  </Button>

                  <div className="profile-card">
                    <div className="profile-content">
                      <div className="profile-back">
                        <div className="profile-back-content flex flex-col justify-end h-full pb-8 text-center">
                          <strong className={`${isDarkMode ? 'text-black' : 'text-white'} font-orbitron tracking-wide`}>DIGITAL PROFILE CARD</strong>
                        </div>
                      </div>
                      <div className="profile-front">
                        <div className="profile-img">
                          <img
                            src={profile?.photo}
                            alt={profile?.name}
                            className="w-full h-full object-cover rounded-[10px]"
                          />
                        </div>
                        <div className="profile-front-content">
                          <div className="flex space-x-4 mb-4 justify-center">
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`${isDarkMode ? 'text-black' : 'text-white'} hover:text-primary transition-colors interactive`}
                              onClick={() => {
                                const url = profile?.id === 'yuvraj'
                                  ? 'https://www.linkedin.com'
                                  : 'https://www.linkedin.com';
                                window.open(url, '_blank');
                              }}
                            >
                              <Linkedin className="h-5 w-5" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`${isDarkMode ? 'text-black' : 'text-white'} hover:text-primary transition-colors interactive`}
                              onClick={() => {
                                const url = profile?.id === 'yuvraj'
                                  ? 'https://github.com'
                                  : 'https://github.com';
                                window.open(url, '_blank');
                              }}
                            >
                              <Github className="h-5 w-5" />
                            </Button>
                          </div>
                          <small className="profile-badge font-electrolize mt-38">DEVELOPER</small>
                          <div className="profile-description">
                            <div className="profile-title">
                              <p className="profile-name font-orbitron">
                                <strong>{profile?.name}</strong>
                              </p>
                              <Zap className="h-4 w-4 text-primary" />
                            </div>
                            <p className="profile-footer font-electrolize">{profile?.role}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            )
          })()}
      </AnimatePresence>

    </div>
  )
}
