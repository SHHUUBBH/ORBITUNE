# ORBITUNE - Authentication Flow Documentation

**Date**: January 2025  
**Project**: ORBITUNE - 3D Spatial Audio Music Platform  
**Scope**: Login/Signup Authentication System

---

## 📋 Overview

This document details the authentication flow implementation for ORBITUNE, including the login/signup page, user session management, and profile display across both Homepage and Dashboard applications.

---

## 🔐 Authentication Flow

Following the provided flowchart, the authentication system implements these steps:

```
1. User loads any page
   ↓
2. Check for valid session token (localStorage)
   ↓
3a. If NO TOKEN → Show Login/Sign Up buttons
   ↓
   User clicks Login/Sign Up → Redirect to /auth page
   ↓
   User submits credentials → Validate form
   ↓
   If SUCCESS → Store session token & user data → Redirect to dashboard
   ↓
3b. If VALID TOKEN → Retrieve user profile data
   ↓
   Display user profile with photo & name
   ↓
   User can access Dashboard or Logout
```

---

## 📁 Files Created/Modified

### **New Files**:
1. `orbitune-homepage/app/auth/page.jsx` - Authentication page with login/signup forms

### **Modified Files**:
1. `orbitune-homepage/app/page.jsx` - Added auth state and profile display to homepage
2. `dashboard/orbitune-sonic-verse-main/src/components/Header.tsx` - Added profile display to dashboard

---

## 🎨 Authentication Page Features

### **Location**: `http://localhost:3000/auth`

### **Visual Design**:
- ✨ Animated background with floating gradient orbs
- 🎵 Floating Headphones and Sparkles icons
- 💎 Glassmorphism card design
- 🌈 ORBITUNE brand gradient colors

### **Form Features**:

#### **Login Mode**:
- Email input with validation
- Password input with show/hide toggle
- "Forgot Password?" link
- Form validation with error messages

#### **Sign Up Mode**:
- Full Name input
- Email input with validation
- Password input (minimum 6 characters)
- Confirm Password input with matching validation
- Form validation with error messages

### **Animations** (Framer Motion):
- Page entry with stagger effect
- Smooth transition between Login/Sign Up modes
- Individual field animations
- Animated error messages
- Background orb animations
- Hover effects on buttons and logo

### **Additional Features**:
- Social login buttons (Google & GitHub) - ready for OAuth integration
- Back to Home button
- Terms & Privacy Policy links
- Fully responsive (mobile to desktop)

---

## 💾 Session Management

### **Storage** (localStorage):

#### **Session Token**:
```javascript
localStorage.setItem('orbitune-session-token', 'mock-token-' + Date.now())
```

#### **User Data**:
```javascript
localStorage.setItem('orbitune-user', JSON.stringify({
  name: "User Name",
  email: "user@example.com",
  photo: "https://ui-avatars.com/api/?name=..."
}))
```

### **Session Checking**:
- Checked on page load
- Polled every 1 second for same-tab updates
- Listens to `storage` events for cross-tab sync
- Validates both token and user data exist

---

## 🏠 Homepage Integration

### **File**: `orbitune-homepage/app/page.jsx`

### **Changes**:

#### **State Management**:
```javascript
const [user, setUser] = useState(null)
const [showUserMenu, setShowUserMenu] = useState(false)
```

#### **Desktop Navigation**:

**When NOT logged in**:
- **LOGIN** button (ghost variant)
- **SIGN UP** button (gradient background)
- Both redirect to `/auth` page

**When logged in**:
- **GO TO APP** button → redirects to dashboard
- **User Profile Dropdown**:
  - User avatar (rounded, bordered)
  - User name (truncated)
  - Dropdown chevron
  - Menu items:
    - Dashboard (redirects to dashboard)
    - Logout (clears session, redirects to homepage)

#### **Mobile Menu**:

**When NOT logged in**:
- Navigation links (Home, About, Features, Credits)
- Theme toggle
- **LOGIN** button
- **SIGN UP** button

**When logged in**:
- User profile card at top with avatar, name, email
- Navigation links
- Theme toggle
- **GO TO DASHBOARD** button
- **LOGOUT** button (red, danger styling)

---

## 📊 Dashboard Integration

### **File**: `dashboard/orbitune-sonic-verse-main/src/components/Header.tsx`

### **Changes**:

#### **State Management**:
```javascript
const [user, setUser] = useState(null)
const [showUserMenu, setShowUserMenu] = useState(false)
```

#### **Desktop Header**:

**When logged in** (user profile shown):
- Home button → redirects to homepage
- Theme toggle
- **User Profile Dropdown**:
  - User avatar
  - User name
  - Dropdown menu:
    - Homepage (redirects to homepage)
    - Logout (clears session, redirects to homepage)
- Mobile menu button (on smaller screens)

---

## 🔄 Cross-Tab Synchronization

Both Homepage and Dashboard listen for `localStorage` changes:

```javascript
window.addEventListener('storage', (e) => {
  if (e.key === 'orbitune-user' || e.key === 'orbitune-session-token') {
    checkUserSession()
  }
})
```

**Behavior**:
- Login in one tab → Profile appears in all open tabs
- Logout in one tab → Profile disappears in all open tabs
- Theme changes sync across tabs
- Works across Homepage ↔ Dashboard

---

## 🎯 User Actions

### **Login/Signup Flow**:
1. User clicks **LOGIN** or **SIGN UP** button
2. Redirected to `/auth` page
3. User fills form and submits
4. Form validates (email format, password length, matching passwords)
5. If valid → Session stored → Redirect to dashboard
6. Profile appears in navbar

### **Logout Flow**:
1. User clicks profile dropdown
2. User clicks **Logout**
3. Session cleared from localStorage
4. User redirected to homepage
5. Profile disappears, LOGIN/SIGN UP buttons appear

---

## 🛠️ Backend Integration (Future)

Currently using **mock authentication** (no backend). To integrate with real backend:

### **1. Update `auth/page.jsx` handleSubmit**:

```javascript
const handleSubmit = async (e) => {
  e.preventDefault()
  
  if (validateForm()) {
    try {
      const endpoint = isLogin ? '/api/login' : '/api/signup'
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          name: formData.name // for signup only
        })
      })
      
      const data = await response.json()
      
      if (response.ok) {
        // Store real token and user data
        localStorage.setItem('orbitune-session-token', data.token)
        localStorage.setItem('orbitune-user', JSON.stringify(data.user))
        
        // Redirect to dashboard
        window.location.href = 'http://localhost:5173/dashboard'
      } else {
        // Handle error
        setErrors({ form: data.message })
      }
    } catch (error) {
      setErrors({ form: 'Network error. Please try again.' })
    }
  }
}
```

### **2. Add Token Validation**:

Update session checking to validate token with backend:

```javascript
const checkUserSession = async () => {
  const token = localStorage.getItem('orbitune-session-token')
  
  if (token) {
    try {
      const response = await fetch('/api/validate-token', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        // Invalid token - clear session
        localStorage.removeItem('orbitune-session-token')
        localStorage.removeItem('orbitune-user')
        setUser(null)
      }
    } catch (error) {
      console.error('Token validation error:', error)
    }
  }
}
```

### **3. Backend API Endpoints Needed**:

- `POST /api/signup` - Create new user account
- `POST /api/login` - Authenticate user
- `GET /api/validate-token` - Validate session token
- `POST /api/logout` - Invalidate token (optional)
- `GET /api/user/profile` - Get user profile data

---

## 📱 Responsive Behavior

### **Desktop (≥1280px)**:
- Full navbar with all buttons visible
- User dropdown in navbar
- Smooth animations

### **Tablet (768px - 1279px)**:
- LOGIN button visible on medium screens
- SIGN UP and profile hidden until large screens
- Mobile menu available

### **Mobile (< 768px)**:
- Only theme toggle and menu button visible
- Full mobile menu with profile card
- Optimized touch targets
- Vertical layout for all options

---

## 🎨 Styling Classes Used

### **Glassmorphism**:
- `glass` - Semi-transparent background with backdrop blur
- `glass-strong` - More opaque glass effect
- `glassmorphism-nav` - Navbar-specific glass styling
- `glassmorphism-card` - Card-specific glass styling

### **Gradients**:
- `gradient-bg` - Primary gradient background
- `gradient-text` - Gradient text effect
- `text-gradient` - Alternative gradient text
- `border-gradient` - Gradient border

### **Effects**:
- `glow-effect` - Subtle glow animation
- `hover-scale` - Scale on hover
- `hover-glow` - Glow on hover
- `hover-pulse` - Pulse animation on hover

---

## ✅ Validation Rules

### **Email**:
- Required field
- Must match email regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
- Error: "Email is required" or "Invalid email format"

### **Password**:
- Required field
- Minimum 6 characters
- Error: "Password is required" or "Password must be at least 6 characters"

### **Name** (Sign Up only):
- Required field
- Error: "Name is required"

### **Confirm Password** (Sign Up only):
- Required field
- Must match password field
- Error: "Please confirm your password" or "Passwords do not match"

---

## 🚀 Testing Checklist

- [x] Login form validation works
- [x] Sign up form validation works
- [x] Password show/hide toggle works
- [x] Form switches between Login/Sign Up modes
- [x] Session token stored on successful login/signup
- [x] User data stored in localStorage
- [x] Profile displays correctly in homepage navbar
- [x] Profile displays correctly in dashboard header
- [x] Dropdown menu shows/hides on click
- [x] Logout clears session and redirects
- [x] Cross-tab synchronization works
- [x] Mobile menu shows profile when logged in
- [x] Mobile menu shows auth buttons when logged out
- [x] Responsive design works on all breakpoints
- [x] Animations smooth and performant
- [x] Back to home button works on auth page

---

## 🐛 Known Limitations (Mock Auth)

1. **No actual credential validation** - All logins succeed
2. **No user persistence** - Session cleared on logout
3. **No password recovery** - "Forgot Password" link is placeholder
4. **No OAuth integration** - Social login buttons are placeholders
5. **Token doesn't expire** - No automatic session timeout
6. **No server-side validation** - All validation is client-side only

These will be resolved when backend integration is complete.

---

## 📚 Dependencies

### **Homepage**:
- `framer-motion` - Animations
- `lucide-react` - Icons
- `@/components/ui/button` - Button component
- `@/components/ui/input` - Input component
- `@/components/ui/label` - Label component
- `@/components/ui/card` - Card component

### **Dashboard**:
- `framer-motion` - Animations
- `lucide-react` - Icons
- `react` - useState, useEffect hooks
- `@/components/ui/button` - Button component
- `@/components/theme-provider` - Theme context

---

## 🔗 URL Structure

- Homepage: `http://localhost:3000`
- Auth Page: `http://localhost:3000/auth`
- Dashboard: `http://localhost:5173/dashboard`

---

## 👥 User Experience Flow

### **First-Time User**:
1. Lands on homepage
2. Sees LOGIN/SIGN UP buttons
3. Clicks SIGN UP
4. Fills registration form
5. Submits → Redirected to dashboard
6. Profile appears in header
7. Can navigate back to homepage (profile persists)

### **Returning User**:
1. Lands on homepage
2. Session token valid → Profile appears automatically
3. Can access dashboard directly
4. Can logout from either page

### **Mobile User**:
1. Opens mobile menu
2. If logged in → Sees profile card at top
3. Can access dashboard or logout
4. If not logged in → Sees LOGIN/SIGN UP buttons

---

## 🎯 Future Enhancements

- [ ] Add password strength indicator
- [ ] Add email verification flow
- [ ] Add password reset functionality
- [ ] Implement OAuth (Google, GitHub, etc.)
- [ ] Add "Remember Me" checkbox
- [ ] Add session timeout warning
- [ ] Add user profile edit page
- [ ] Add user avatar upload
- [ ] Add two-factor authentication
- [ ] Add login history/activity log
- [ ] Add "Stay signed in on this device" option
- [ ] Add loading states during authentication

---

## 📝 Notes

- All animations are optimized for performance
- Session polling is lightweight (checks localStorage only)
- Profile images use ui-avatars.com for mock data
- Theme synchronization works independently of auth state
- Mobile menu automatically closes after navigation
- Dropdown menus close on outside click (handled by AnimatePresence)

---

**Last Updated**: January 2025  
**Version**: 1.0.0  
**Status**: ✅ Ready for Backend Integration
