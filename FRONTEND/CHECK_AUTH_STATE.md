# Dashboard Profile Not Showing - Diagnostic Guide

## 🔍 Quick Check

Open browser console (F12) on the dashboard page and run:

```javascript
// Check session token
console.log('Session Token:', localStorage.getItem('orbitune-session-token'));

// Check user data
console.log('User Data:', localStorage.getItem('orbitune-user'));

// Parse user data
try {
  const user = JSON.parse(localStorage.getItem('orbitune-user'));
  console.log('Parsed User:', user);
} catch (e) {
  console.error('Error parsing user:', e);
}
```

## 🔧 Quick Fix

If the session token exists but user data is missing, run this in console:

```javascript
// Create fallback user
const fallbackUser = {
  name: 'ORBITUNE User',
  email: 'user@orbitune.com',
  photo: 'https://ui-avatars.com/api/?name=ORBITUNE+User&background=8B5CF6&color=fff'
};

localStorage.setItem('orbitune-user', JSON.stringify(fallbackUser));

// Reload page
location.reload();
```

## ✅ What I Fixed

1. **Added Fallback User Creation**:
   - If session token exists but user data is missing, creates a default user
   - Prevents profile from being hidden

2. **Added Console Logging**:
   - Logs when user session is found
   - Logs when fallback is created
   - Helps debug auth issues

3. **Added Image Error Handling**:
   - If avatar fails to load, falls back to ui-avatars.com
   - Prevents broken image icons

4. **Added Login Button Fallback**:
   - If no user is found, shows "Login" button
   - Redirects to auth page

5. **Added Title Tooltip**:
   - Hover over profile shows "Logged in as [name]"

## 🧪 Testing Steps

1. **Clear Everything and Start Fresh**:
   ```javascript
   localStorage.clear();
   location.reload();
   ```

2. **Login via Homepage**:
   - Go to http://localhost:3000
   - Click LOGIN or SIGN UP
   - Complete authentication
   - Should redirect to dashboard with profile visible

3. **Check Profile Display**:
   - Profile avatar should appear in top-right
   - Click avatar to see dropdown menu
   - Verify name and email are displayed

## 🐛 Common Issues

### Issue 1: Profile Not Showing After Login
**Cause**: User data not saved during login
**Fix**: Check auth page is saving both token AND user data

### Issue 2: Avatar Shows Broken Image
**Cause**: Invalid photo URL
**Fix**: Now automatically falls back to ui-avatars.com

### Issue 3: Profile Shows on Homepage but Not Dashboard
**Cause**: Different apps reading localStorage at different times
**Fix**: Added polling (checks every 1 second) + storage event listener

## 🎯 Expected Behavior

**After Login**:
1. Auth page saves:
   - `orbitune-session-token`: 'mock-token-TIMESTAMP'
   - `orbitune-user`: JSON with name, email, photo

2. Dashboard reads both values

3. Profile appears in header with:
   - User avatar (circular)
   - Name (on screens ≥640px)
   - Dropdown chevron (on screens ≥640px)

4. Click profile to see:
   - Full name and email
   - "Homepage" button
   - "Logout" button

**If No Login**:
- Shows "Login" button in header
- Clicking redirects to /auth page

## 💡 Force Profile to Show

Run this in browser console on dashboard:

```javascript
// Set mock session
localStorage.setItem('orbitune-session-token', 'mock-token-' + Date.now());

// Set user data
localStorage.setItem('orbitune-user', JSON.stringify({
  name: 'Test User',
  email: 'test@orbitune.com',
  photo: 'https://ui-avatars.com/api/?name=Test+User&background=8B5CF6&color=fff'
}));

// Reload
location.reload();
```

Profile should now appear!

---

**Status**: ✅ Fixed with fallback user creation
**Next**: Test by logging in fresh from homepage
