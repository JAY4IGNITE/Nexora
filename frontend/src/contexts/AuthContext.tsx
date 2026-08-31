import React, { createContext, useContext, useEffect, useState } from 'react';
import { User as FirebaseUser, signOut as firebaseSignOut } from 'firebase/auth';
import { auth, onAuthStateChanged } from '@/lib/firebase';

export type UserRole = 'ADMIN' | 'GOVERNMENT' | 'INSTITUTION' | 'TRAINER' | 'EMPLOYER' | 'STUDENT';

export interface UserProfile {
  id: string;
  firebase_uid: string;
  email: string;
  display_name: string | null;
  role: UserRole;
  is_active: boolean;
}

interface AuthContextType {
  firebaseUser: FirebaseUser | null;
  profile: UserProfile | null;
  loading: boolean;
  isAuthenticated: boolean;
  role: UserRole | null;
  logout: () => Promise<void>;
  syncProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchProfile = async (token: string) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setProfile(data);
      } else {
        setProfile(null);
      }
    } catch (error) {
      console.error("Failed to fetch profile:", error);
      setProfile(null);
    }
  };

  const syncProfile = async () => {
    if (auth.currentUser) {
      const token = await auth.currentUser.getIdToken(true); // force refresh
      await fetchProfile(token);
    }
  };

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);
      if (user) {
        const token = await user.getIdToken();
        await fetchProfile(token);
      } else {
        setProfile(null);
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const logout = async () => {
    await firebaseSignOut(auth);
  };

  return (
    <AuthContext.Provider
      value={{
        firebaseUser,
        profile,
        loading,
        isAuthenticated: !!profile,
        role: profile?.role || null,
        logout,
        syncProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
