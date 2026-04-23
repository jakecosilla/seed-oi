'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { Auth0Provider as Auth0SDKProvider, useAuth0 } from '@auth0/auth0-react';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  tenant_id: string;
}

interface AuthContextType {
  user: User | null; // This is the internal Seed OI user record
  auth0User: any; // This is the raw Auth0 profile
  isLoading: boolean;
  isAuthenticated: boolean;
  login: () => Promise<void>;
  signup: () => Promise<void>;
  logout: () => Promise<void>;
  accessToken: string | null;
  error: Error | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const InternalAuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const {
    user: auth0User,
    isAuthenticated,
    getAccessTokenSilently,
    loginWithRedirect,
    logout: auth0Logout,
    isLoading: isAuth0Loading,
    error: auth0Error
  } = useAuth0();

  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isInternalLoading, setIsInternalLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const resolveInternalUser = useCallback(async (token: string) => {
    setIsInternalLoading(true);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const internalUser = await response.json();
        setUser(internalUser);
      } else {
        const errData = await response.json();
        console.error("Failed to resolve internal user profile", errData);
      }
    } catch (err: any) {
      console.error("Error resolving internal user", err);
    } finally {
      setIsInternalLoading(false);
    }
  }, []);

  useEffect(() => {
    const fetchToken = async () => {
      if (isAuthenticated) {
        try {
          const token = await getAccessTokenSilently();
          setAccessToken(token);
          await resolveInternalUser(token);
        } catch (e: any) {
          console.error("Error getting access token", e);
          setError(e);
        }
      } else {
        setUser(null);
        setAccessToken(null);
      }
    };
    fetchToken();
  }, [isAuthenticated, getAccessTokenSilently, resolveInternalUser]);

  const login = async () => {
    await loginWithRedirect();
  };

  const signup = async () => {
    await loginWithRedirect({
      authorizationParams: {
        screen_hint: 'signup',
      },
    });
  };

  const logout = async () => {
    await auth0Logout({
      logoutParams: {
        returnTo: typeof window !== 'undefined' ? window.location.origin : ""
      }
    });
  };

  return (
    <AuthContext.Provider value={{
      user,
      auth0User,
      isLoading: isAuth0Loading || isInternalLoading,
      isAuthenticated,
      login,
      signup,
      logout,
      accessToken,
      error: auth0Error || error
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN || "";
  const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID || "";
  const audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE || "";

  return (
    <Auth0SDKProvider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: typeof window !== 'undefined' ? `${window.location.origin}/login/callback` : "",
        audience: audience,
        scope: "openid profile email"
      }}
      cacheLocation="localstorage"
    >
      <InternalAuthProvider>
        {children}
      </InternalAuthProvider>
    </Auth0SDKProvider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
