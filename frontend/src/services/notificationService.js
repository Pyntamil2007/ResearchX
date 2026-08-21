import api from './api';

export const notificationService = {
  getNotifications: async (unreadOnly = false, limit = 50) => {
    const response = await api.get('/notifications', {
      params: {
        unread_only: unreadOnly,
        limit: limit
      }
    });
    return response.data;
  },

  markAsRead: async (id) => {
    const response = await api.patch(`/notifications/${id}/read`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.patch('/notifications/read-all');
    return response.data;
  },

  deleteNotification: async (id) => {
    const response = await api.delete(`/notifications/${id}`);
    return response.data;
  },

  clearAll: async () => {
    const response = await api.delete('/notifications');
    return response.data;
  }
};
