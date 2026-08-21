import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [token, setToken] = useState(authService.getToken());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = authService.getToken();
      if (savedToken) {
        try {
          const res = await authService.getMe();
          if (res.success && res.data) {
            setUser(res.data);
            setToken(savedToken);
          } else {
            handleLogout();
          }
        } catch {
          handleLogout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const handleLogin = async (email, password) => {
    const res = await authService.login(email, password);
    if (res.success && res.data) {
      setUser(res.data.user);
      setToken(res.data.access_token);
      return res.data;
    }
    throw new Error(res.message || 'Login failed');
  };

  const handleRegister = async (name, email, password) => {
    const res = await authService.register(name, email, password);
    if (res.success && res.data) {
      setUser(res.data.user);
      setToken(res.data.access_token);
      return res.data;
    }
    throw new Error(res.message || 'Registration failed');
  };

  const handleLogout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
  };

  const updateUserProfile = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('researchx_user', JSON.stringify(updatedUser));
  };

  const isAdmin = user?.role === 'ADMIN';

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        isAdmin,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
        updateUserProfile
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
