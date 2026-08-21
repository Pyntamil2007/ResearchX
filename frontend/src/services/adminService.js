import api from './api';

export const adminService = {
  getUsers: async (params = {}) => {
    const response = await api.get('/users', { params });
    return response.data;
  },

  createUser: async (userData) => {
    const response = await api.post('/users', userData);
    return response.data;
  },

  updateUser: async (id, userData) => {
    const response = await api.put(`/users/${id}`, userData);
    return response.data;
  },

  resetUserPassword: async (id, password) => {
    const response = await api.post(`/users/${id}/reset-password`, { password });
    return response.data;
  },

  updateUserStatus: async (id, status) => {
    const response = await api.patch(`/users/${id}/status`, { status });
    return response.data;
  },

  updateUserRole: async (id, role) => {
    const response = await api.patch(`/users/${id}/role`, { role });
    return response.data;
  },

  deleteUser: async (id) => {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  },

  getAllPapers: async (params = {}) => {
    const response = await api.get('/admin/papers', { params });
    return response.data;
  },

  deletePaper: async (id) => {
    const response = await api.delete(`/admin/papers/${id}`);
    return response.data;
  },

  getAdminDashboard: async () => {
    const response = await api.get('/dashboard/admin');
    return response.data;
  },

  getSystemStatistics: async () => {
    const response = await api.get('/admin/statistics');
    return response.data;
  }
};
