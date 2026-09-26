import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface User {
    id: string;
    name: string;
    email: string;
    profilePhoto?: string;
    createdAt: Date;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
}

interface AuthContextType {
    user: User | null;
    isAuthenticated: boolean;
    login: (email: string, password: string) => Promise<boolean>;
    signup: (name: string, email: string, password: string) => Promise<boolean>;
    logout: () => void;
    updateProfile: (name: string, profilePhoto?: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY = 'orbitune-auth';
const USERS_KEY = 'orbitune-users';

export function AuthProvider({ children }: { children: ReactNode }) {
    const [authState, setAuthState] = useState<AuthState>({
        user: null,
        isAuthenticated: false,
    });

    // Load auth state from localStorage on mount
    useEffect(() => {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                setAuthState({
                    user: {
                        ...parsed.user,
                        createdAt: new Date(parsed.user.createdAt),
                    },
                    isAuthenticated: true,
                });
            }
        } catch (error) {
            console.error('Failed to load auth state:', error);
        }
    }, []);

    // Save auth state to localStorage
    const saveAuthState = (state: AuthState) => {
        setAuthState(state);
        if (state.isAuthenticated && state.user) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } else {
            localStorage.removeItem(STORAGE_KEY);
        }
    };

    // Get all users from localStorage
    const getUsers = (): User[] => {
        try {
            const stored = localStorage.getItem(USERS_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch {
            return [];
        }
    };

    // Save users to localStorage
    const saveUsers = (users: User[]) => {
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
    };

    const signup = async (name: string, email: string, password: string): Promise<boolean> => {
        try {
            const users = getUsers();

            // Check if user already exists
            if (users.some(u => u.email === email)) {
                return false;
            }

            // Create new user
            const newUser: User = {
                id: Date.now().toString(),
                name,
                email,
                createdAt: new Date(),
            };

            // Store user credentials (in real app, this would be done server-side with proper hashing)
            users.push(newUser);
            saveUsers(users);

            // Store password separately (simplified for demo)
            localStorage.setItem(`pwd_${email}`, password);

            // Auto-login after signup
            saveAuthState({
                user: newUser,
                isAuthenticated: true,
            });

            return true;
        } catch (error) {
            console.error('Signup error:', error);
            return false;
        }
    };

    const login = async (email: string, password: string): Promise<boolean> => {
        try {
            const users = getUsers();
            const user = users.find(u => u.email === email);

            if (!user) {
                return false;
            }

            // Verify password (simplified for demo)
            const storedPassword = localStorage.getItem(`pwd_${email}`);
            if (storedPassword !== password) {
                return false;
            }

            saveAuthState({
                user,
                isAuthenticated: true,
            });

            return true;
        } catch (error) {
            console.error('Login error:', error);
            return false;
        }
    };

    const logout = () => {
        saveAuthState({
            user: null,
            isAuthenticated: false,
        });
    };

    const updateProfile = (name: string, profilePhoto?: string) => {
        if (!authState.user) return;

        const updatedUser = {
            ...authState.user,
            name,
            profilePhoto: profilePhoto || authState.user.profilePhoto,
        };

        // Update in users list
        const users = getUsers();
        const userIndex = users.findIndex(u => u.id === authState.user!.id);
        if (userIndex !== -1) {
            users[userIndex] = updatedUser;
            saveUsers(users);
        }

        // Update current auth state
        saveAuthState({
            user: updatedUser,
            isAuthenticated: true,
        });
    };

    return (
        <AuthContext.Provider
            value={{
                user: authState.user,
                isAuthenticated: authState.isAuthenticated,
                login,
                signup,
                logout,
                updateProfile,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
}
