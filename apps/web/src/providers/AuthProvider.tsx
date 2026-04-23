'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { UserManager, WebStorageStateStore, User as OIDCUser } from 'oidc-client-ts';
import { useRouter, usePathname } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  tenant_id: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  accessToken: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// OIDC Configuration - In production, these would be in environment variables
const oidcConfig = {
  authority: process.env.NEXT_PUBLIC_OIDC_AUTHORITY || "https://example-issuer.com",
  client_id: process.env.NEXT_PUBLIC_OIDC_CLIENT_ID || "seed-oi-client-id",
  redirect_uri: typeof window !== 'undefined' ? `${window.location.origin}/login/callback` : "",
  post_logout_redirect_uri: typeof window !== 'undefined' ? window.location.origin : "",
  response_type: "code",
  scope: "openid profile email",
  userStore: typeof window !== 'undefined' ? new WebStorageStateStore({ store: window.localStorage }) : undefined,
  monitorSession: false,
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const [userManager] = useState(() => typeof window !== 'undefined' ? new UserManager(oidcConfig) : null);

  const resolveInternalUser = useCallback(async (token: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const internalUser = await response.json();
        setUser(internalUser);
      } else {
        console.error("Failed to resolve internal user profile");
      }
    } catch (err) {
      console.error("Error resolving internal user", err);
    }
  }, []);

  useEffect(() => {
    if (!userManager) return;

    const initAuth = async () => {
      try {
        // Check if we are in a callback
        if (pathname === '/login/callback') {
          const oidcUser = await userManager.signinCallback();
          setAccessToken(oidcUser.access_token);
          await resolveInternalUser(oidcUser.access_token);
          router.push('/overview');
          return;
        }

        // Check for existing session
        const oidcUser = await userManager.getUser();
        if (oidcUser && !oidcUser.expired) {
          setAccessToken(oidcUser.access_token);
          await resolveInternalUser(oidcUser.access_token);
        }
      } catch (err) {
        console.error("Auth initialization error", err);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, [userManager, pathname, resolveInternalUser, router]);

  const login = async () => {
    if (userManager) {
      await userManager.signinRedirect();
    }
  };

  const logout = async () => {
    if (userManager) {
      await userManager.signoutRedirect();
      setUser(null);
      setAccessToken(null);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      isLoading, 
      isAuthenticated: !!accessToken, 
      login, 
      logout,
      accessToken 
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
