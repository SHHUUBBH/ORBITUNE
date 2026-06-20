"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card } from "@/components/ui/card"
import { Eye, EyeOff, Mail, Lock, User, ArrowLeft, Headphones, Sparkles, Music, Radio, Disc3, Waves } from "lucide-react"

export default function AuthPage() {
  // Always start with false (signup) to avoid hydration mismatch
  const [isLogin, setIsLogin] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: ""
  })
  const [errors, setErrors] = useState({})
  const [isMounted, setIsMounted] = useState(false)

  // Sync theme with homepage and dashboard
  useEffect(() => {
    setIsMounted(true) // Mark as mounted for client-side rendering
    
    // Check if user has logged in before and update mode (only on client)
    const params = new URLSearchParams(window.location.search)
    const mode = params.get('mode')
    if (mode === 'login') {
      setIsLogin(true)
    } else if (mode === 'signup') {
      setIsLogin(false)
    } else {
      const hasLoggedInBefore = localStorage.getItem('orbitune-has-logged-in')
      if (hasLoggedInBefore === 'true') {
        setIsLogin(true)
      }
    }
    
    const updateTheme = () => {
      const savedTheme = localStorage.getItem('orbitune-ui-theme')
      const isThemeDark = !savedTheme || savedTheme === 'dark'

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
    updateTheme()

    // Listen for theme changes from other tabs
    const handleStorageChange = (e) => {
      if (e.key === 'orbitune-ui-theme') {
        updateTheme()
      }
    }

    window.addEventListener('storage', handleStorageChange)

    // Poll for changes in same tab
    const themeInterval = setInterval(updateTheme, 500)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      clearInterval(themeInterval)
    }
  }, [])

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: "" }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!formData.email) {
      newErrors.email = "Email is required"
    } else if (!emailRegex.test(formData.email)) {
      newErrors.email = "Invalid email format"
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = "Password is required"
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters"
    }

    // Sign up specific validations
    if (!isLogin) {
      if (!formData.name) {
        newErrors.name = "Name is required"
      }
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = "Please confirm your password"
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = "Passwords do not match"
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (validateForm()) {
      // Simulate authentication (no backend for now)
      console.log(isLogin ? "Logging in..." : "Signing up...", formData)
      
      // Store mock session token
      const userData = {
        name: formData.name || formData.email.split('@')[0],
        email: formData.email,
        photo: `https://ui-avatars.com/api/?name=${encodeURIComponent(formData.name || formData.email)}&background=8B5CF6&color=fff`
      };
      
      localStorage.setItem('orbitune-session-token', 'mock-token-' + Date.now());
      localStorage.setItem('orbitune-user', JSON.stringify(userData));
      localStorage.setItem('orbitune-has-logged-in', 'true'); // Remember user has logged in
      
      console.log('✅ Session saved:', userData);
      
      // Redirect to dashboard immediately
      window.location.href = 'http://localhost:5173/dashboard'
    }
  }

  const toggleMode = () => {
    const newMode = !isLogin
    console.log('Toggling mode from', isLogin ? 'Login' : 'Signup', 'to', newMode ? 'Login' : 'Signup')
    setIsLogin(newMode)
    setErrors({})
    setFormData({
      name: "",
      email: "",
      password: "",
      confirmPassword: ""
    })
  }

  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
        staggerChildren: 0.1
      }
    },
    exit: {
      opacity: 0,
      y: -20,
      transition: { duration: 0.3 }
    }
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: { duration: 0.4, ease: "easeOut" }
    }
  }

  const floatingVariants = {
    animate: {
      y: [0, -20, 0],
      rotate: [0, 5, -5, 0],
      transition: {
        duration: 6,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  }

  const orbVariants = {
    animate: {
      scale: [1, 1.2, 1],
      rotate: [0, 360],
      opacity: [0.3, 0.6, 0.3],
      transition: {
        duration: 15,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  }

  const particleVariants = {
    animate: (i) => ({
      y: [0, -100, 0],
      x: [0, Math.sin(i) * 50, 0],
      opacity: [0, 1, 0],
      transition: {
        duration: 3 + i,
        repeat: Infinity,
        delay: i * 0.5,
        ease: "easeInOut"
      }
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden p-4">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#8b5cf610_1px,transparent_1px),linear-gradient(to_bottom,#8b5cf610_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_80%_80%_at_50%_50%,#000_70%,transparent_100%)]" />
      
      {/* Massive Animated Orbs */}
      <div className="absolute inset-0 z-0">
        <motion.div
          className="absolute -top-40 -left-40 w-[500px] h-[500px] bg-gradient-to-br from-primary/30 via-secondary/20 to-transparent rounded-full blur-3xl"
          animate={{
            scale: [1, 1.4, 1],
            rotate: [0, 180, 360],
            opacity: [0.3, 0.6, 0.3]
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute -bottom-40 -right-40 w-[600px] h-[600px] bg-gradient-to-tl from-accent/30 via-secondary/20 to-transparent rounded-full blur-3xl"
          animate={{
            scale: [1, 1.5, 1],
            rotate: [360, 180, 0],
            opacity: [0.2, 0.5, 0.2]
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-primary/10 via-transparent to-transparent rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.2, 0.4, 0.2]
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
      </div>

      {/* Rotating Ring Animation */}
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border-2 border-primary/10 rounded-full"
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
      />
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] border-2 border-secondary/10 rounded-full"
        animate={{ rotate: -360 }}
        transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
      />

      {/* Floating Particles */}
      {isMounted && [...Array(8)].map((_, i) => (
        <motion.div
          key={i}
          custom={i}
          variants={particleVariants}
          animate="animate"
          className="absolute"
          style={{
            left: `${10 + i * 10}%`,
            top: `${20 + (i * 8)}%`, // Fixed positions instead of random
          }}
        >
          <div className="w-2 h-2 bg-primary/30 rounded-full blur-sm" />
        </motion.div>
      ))}

      {/* Floating Music Icons */}
      <motion.div
        className="absolute top-[15%] left-[10%] text-primary/20 pointer-events-none"
        variants={floatingVariants}
        animate="animate"
      >
        <Headphones className="w-16 h-16" />
      </motion.div>
      <motion.div
        className="absolute top-[25%] right-[15%] text-secondary/20 pointer-events-none"
        variants={floatingVariants}
        animate="animate"
        transition={{ delay: 0.5 }}
      >
        <Music className="w-12 h-12" />
      </motion.div>
      <motion.div
        className="absolute bottom-[20%] left-[15%] text-accent/20 pointer-events-none"
        variants={floatingVariants}
        animate="animate"
        transition={{ delay: 1 }}
      >
        <Radio className="w-14 h-14" />
      </motion.div>
      <motion.div
        className="absolute bottom-[30%] right-[10%] text-primary/20 pointer-events-none"
        variants={floatingVariants}
        animate="animate"
        transition={{ delay: 1.5 }}
      >
        <Disc3 className="w-20 h-20" />
      </motion.div>
      <motion.div
        className="absolute top-[60%] left-[5%] text-secondary/20 pointer-events-none"
        variants={floatingVariants}
        animate="animate"
        transition={{ delay: 2 }}
      >
        <Waves className="w-10 h-10" />
      </motion.div>
      <motion.div
        className="absolute top-[40%] right-[8%] text-accent/20 pointer-events-none"
        variants={floatingVariants}
        animate="animate"
        transition={{ delay: 2.5 }}
      >
        <Sparkles className="w-18 h-18" />
      </motion.div>

      {/* Back to Home Button */}
      <motion.div
        className="absolute top-4 left-4 sm:top-8 sm:left-8 z-50"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Button
          variant="ghost"
          onClick={() => window.location.href = 'http://localhost:3000'}
          className="group gap-2 glassmorphism-nav hover:glass-strong font-electrolize"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Back to Home
        </Button>
      </motion.div>

      {/* Main Auth Card */}
      <motion.div
        className="relative z-20 w-full max-w-md"
        initial={{ opacity: 0, scale: 0.8, y: 50 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ 
          duration: 0.8, 
          type: "spring", 
          stiffness: 100,
          delay: 0.2
        }}
      >
        {/* Glow Effect Behind Card */}
        <motion.div
          className="absolute inset-0 bg-gradient-to-br from-primary/30 via-secondary/20 to-accent/30 rounded-3xl blur-3xl"
          animate={{
            scale: [1, 1.1, 1],
            opacity: [0.3, 0.5, 0.3]
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        />
        
        <Card className="relative glassmorphism-card p-6 sm:p-8 shadow-2xl border-gradient backdrop-blur-2xl">
          {/* Logo */}
          <motion.div
            className="flex flex-col items-center mb-8"
            variants={itemVariants}
          >
            <motion.div
              className="relative mb-4"
              animate={{
                scale: [1, 1.05, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              whileHover={{ scale: 1.15, rotate: 15 }}
            >
              <motion.div 
                className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-br from-primary via-secondary to-accent flex items-center justify-center"
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              >
                <Headphones className="w-10 h-10 sm:w-12 sm:h-12 text-white" style={{ animation: 'none' }} />
              </motion.div>
              <motion.div 
                className="absolute inset-0 rounded-full bg-gradient-to-br from-primary via-secondary to-accent blur-2xl opacity-60"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.6, 0.8, 0.6]
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
              {/* Orbiting dots */}
              <motion.div
                className="absolute top-0 left-1/2 w-3 h-3 bg-primary rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                style={{ originX: 0.5, originY: 2.5 }}
              />
              <motion.div
                className="absolute top-0 left-1/2 w-2 h-2 bg-secondary rounded-full"
                animate={{ rotate: -360 }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                style={{ originX: 0.5, originY: 3 }}
              />
            </motion.div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gradient font-orbitron tracking-wider">
              ORBITUNE
            </h1>
            <p className="text-xs sm:text-sm text-muted-foreground font-electrolize mt-2 text-center">
              {isLogin ? "Welcome back to the future of audio" : "Join the 3D audio revolution"}
            </p>
          </motion.div>

          {/* Form */}
          <AnimatePresence mode="wait">
            <motion.form
              key={isLogin ? "login" : "signup"}
              onSubmit={handleSubmit}
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              className="space-y-4 sm:space-y-5"
            >
              {/* Name Field (Sign Up Only) */}
              <AnimatePresence>
                {!isLogin && (
                  <motion.div
                    variants={itemVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="space-y-2"
                  >
                    <Label htmlFor="name" className="text-sm font-medium font-electrolize">
                      Full Name
                    </Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="name"
                        name="name"
                        type="text"
                        placeholder="Enter your full name"
                        value={formData.name}
                        onChange={handleInputChange}
                        className={`pl-10 glass border-white/10 focus:border-primary/50 transition-all font-electrolize ${
                          errors.name ? "border-red-500/50" : ""
                        }`}
                      />
                    </div>
                    {errors.name && (
                      <motion.p
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-xs text-red-500 font-electrolize"
                      >
                        {errors.name}
                      </motion.p>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Email Field */}
              <motion.div variants={itemVariants} className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium font-electrolize">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="Enter your email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className={`pl-10 glass border-white/10 focus:border-primary/50 transition-all font-electrolize ${
                      errors.email ? "border-red-500/50" : ""
                    }`}
                  />
                </div>
                {errors.email && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-red-500 font-electrolize"
                  >
                    {errors.email}
                  </motion.p>
                )}
              </motion.div>

              {/* Password Field */}
              <motion.div variants={itemVariants} className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium font-electrolize">
                  Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    id="password"
                    name="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    value={formData.password}
                    onChange={handleInputChange}
                    className={`pl-10 pr-10 glass border-white/10 focus:border-primary/50 transition-all font-electrolize ${
                      errors.password ? "border-red-500/50" : ""
                    }`}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {errors.password && (
                  <motion.p
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-xs text-red-500 font-electrolize"
                  >
                    {errors.password}
                  </motion.p>
                )}
              </motion.div>

              {/* Confirm Password Field (Sign Up Only) */}
              <AnimatePresence>
                {!isLogin && (
                  <motion.div
                    variants={itemVariants}
                    initial="hidden"
                    animate="visible"
                    exit="exit"
                    className="space-y-2"
                  >
                    <Label htmlFor="confirmPassword" className="text-sm font-medium font-electrolize">
                      Confirm Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="confirmPassword"
                        name="confirmPassword"
                        type={showPassword ? "text" : "password"}
                        placeholder="Confirm your password"
                        value={formData.confirmPassword}
                        onChange={handleInputChange}
                        className={`pl-10 glass border-white/10 focus:border-primary/50 transition-all font-electrolize ${
                          errors.confirmPassword ? "border-red-500/50" : ""
                        }`}
                      />
                    </div>
                    {errors.confirmPassword && (
                      <motion.p
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-xs text-red-500 font-electrolize"
                      >
                        {errors.confirmPassword}
                      </motion.p>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Forgot Password (Login Only) */}
              {isLogin && (
                <motion.div variants={itemVariants} className="flex justify-end">
                  <button
                    type="button"
                    className="text-xs sm:text-sm text-primary hover:text-primary/80 transition-colors font-electrolize"
                  >
                    Forgot Password?
                  </button>
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.div variants={itemVariants}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button
                    type="submit"
                    className="relative w-full gradient-bg text-white font-electrolize font-bold tracking-wider overflow-hidden uppercase h-11 sm:h-12 group"
                  >
                    <motion.div
                      className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                      animate={{ x: [-200, 200] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    />
                    <span className="relative z-10 flex items-center justify-center gap-2">
                      {isLogin ? "Sign In" : "Create Account"}
                      <motion.span
                        animate={{ x: [0, 5, 0] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                      >
                        →
                      </motion.span>
                    </span>
                  </Button>
                </motion.div>
              </motion.div>

              {/* Toggle Mode */}
              <motion.div variants={itemVariants} className="text-center pt-4">
                <p className="text-xs sm:text-sm text-muted-foreground font-electrolize">
                  {isLogin ? "Don't have an account?" : "Already have an account?"}
                  <button
                    type="button"
                    onClick={toggleMode}
                    className="ml-2 text-primary hover:text-primary/80 transition-colors font-semibold"
                  >
                    {isLogin ? "Sign Up" : "Sign In"}
                  </button>
                </p>
              </motion.div>
            </motion.form>
          </AnimatePresence>
        </Card>

        {/* Footer Note */}
        <motion.p
          variants={itemVariants}
          className="text-center text-xs text-muted-foreground mt-6 font-electrolize"
        >
          By continuing, you agree to ORBITUNE's{" "}
          <span className="text-primary hover:underline cursor-pointer">Terms of Service</span> and{" "}
          <span className="text-primary hover:underline cursor-pointer">Privacy Policy</span>
        </motion.p>
      </motion.div>
    </div>
  )
}
