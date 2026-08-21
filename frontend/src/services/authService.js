import api from './api';

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.success && response.data.data) {
      localStorage.setItem('researchx_token', response.data.data.access_token);
      localStorage.setItem('researchx_user', JSON.stringify(response.data.data.user));
    }
    return response.data;
  },

  register: async (name, email, password) => {
    const response = await api.post('/auth/register', { name, email, password });
    if (response.data.success && response.data.data) {
      localStorage.setItem('researchx_token', response.data.data.access_token);
      localStorage.setItem('researchx_user', JSON.stringify(response.data.data.user));
    }
    return response.data;
  },

  getMe: async () => {
    const response = await api.get('/auth/me');
    if (response.data.success && response.data.data) {
      localStorage.setItem('researchx_user', JSON.stringify(response.data.data));
    }
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('researchx_token');
    localStorage.removeItem('researchx_user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('researchx_user');
    try {
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  },

  getToken: () => {
    return localStorage.getItem('researchx_token');
  },

  // Password Recovery
  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  verifyResetToken: async (token) => {
    const response = await api.post('/auth/verify-reset-token', { token });
    return response.data;
  },

  resetPassword: async (token, newPassword) => {
    const response = await api.post('/auth/reset-password', {
      token,
      new_password: newPassword
    });
    return response.data;
  }
};
