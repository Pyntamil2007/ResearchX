import api from './api';

export const userService = {
  getProfile: async (id) => {
    const response = await api.get(`/users/${id}`);
    return response.data;
  },

  updateProfile: async (id, userData) => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  },

  changePassword: async (id, newPassword) => {
    const response = await api.put(`/users/${id}`, { password: newPassword });
    return response.data;
  },

  deleteMyAccount: async (password) => {
    const response = await api.post('/users/me/delete', { password });
    return response.data;
  }
};
