"use client"

import { createContext, useContext, useState, useEffect, ReactNode, useRef } from 'react';
import { jwtDecode } from 'jwt-decode';
import { apiFetch, getUserProfile } from '@/lib/api';
import { toast } from "@/components/ui/use-toast"
import { useLanguage } from "@/context/LanguageContext";

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
}

interface UserProfile {
  id: number;
  username: string;
  nickname: string;
  profile_image_key: string;
  achievements: Achievement[];
  // ... other fields if needed
}

interface AuthContextType {
  token: string | null;
  user: { username: string } | null;
  userProfile: UserProfile | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { t } = useLanguage();

  // Use ref to track achievement count without triggering re-renders for logic
  const prevAchievementsRef = useRef<Achievement[]>([]);

  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    if (storedToken) {
      try {
        const decodedUser: { sub: string, exp: number } = jwtDecode(storedToken);
        if (decodedUser.exp * 1000 > Date.now()) {
          setToken(storedToken);
          setUser({ username: decodedUser.sub });
        } else {
          localStorage.removeItem('authToken');
        }
      } catch (error) {
        console.error("Failed to decode token on initial load", error);
        localStorage.removeItem('authToken');
      }
    }
    setIsLoading(false);
  }, []);

  // Fetch profile whenever 'user' is set (login or initial load)
  useEffect(() => {
    if (user?.username) {
      refreshProfile(true); // Initial fetch, quiet mode
    } else {
      setUserProfile(null);
      prevAchievementsRef.current = [];
    }
  }, [user]);

  const refreshProfile = async (silent: boolean = false) => {
    if (!user?.username) return;

    try {
      const result = await getUserProfile(user.username, token);

      if (result.success && result.data) {
        const profileData = result.data;

        if (!silent && userProfile) {
          // 업적 달성 여부 확인
          const newAchievements = profileData.achievements || [];
          const oldAchievements = prevAchievementsRef.current;

          if (newAchievements.length > oldAchievements.length) {
            // 신규 달성 업적 확인
            const oldIds = new Set(oldAchievements.map((a: Achievement) => a.id));
            const added = newAchievements.filter((a: Achievement) => !oldIds.has(a.id));

            added.forEach((ach: Achievement) => {
              const translatedName = (t.achievements as any)[ach.id]?.name || ach.name;
              const translatedDesc = (t.achievements as any)[ach.id]?.desc || ach.description;

              toast({
                title: `Achievement Unlocked: ${translatedName} ${ach.icon}`,
                description: translatedDesc,
              });
            });
          }
        }

        setUserProfile(profileData);
        prevAchievementsRef.current = profileData.achievements || [];
      } else {
        console.error("Failed to fetch user profile:", result.error);
      }
    } catch (error) {
      console.error("Error in refreshProfile:", error);
    }
  };

  const login = (newToken: string) => {
    try {
      const decodedUser: { sub: string } = jwtDecode(newToken);
      localStorage.setItem('authToken', newToken);
      setToken(newToken);
      setUser({ username: decodedUser.sub });
    } catch (error) {
      console.error("Failed to decode token on login", error);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setToken(null);
    setUser(null);
    setUserProfile(null);
    prevAchievementsRef.current = [];
  };

  return (
    <AuthContext.Provider value={{ token, user, userProfile, isLoading, login, logout, refreshProfile }}>
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
