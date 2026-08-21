import api from './api';

export const paperService = {
  uploadPaper: async (formData, onUploadProgress) => {
    const response = await api.post('/papers/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  loadDemoPaper: async (demoFileName) => {
    const response = await api.post(`/papers/demo/${encodeURIComponent(demoFileName)}`);
    return response.data;
  },

  getPapers: async (params = {}) => {
    const response = await api.get('/papers', { params });
    return response.data;
  },

  getPaperById: async (id) => {
    const response = await api.get(`/papers/${id}`);
    return response.data;
  },

  downloadPaperUrl: (id) => {
    const token = localStorage.getItem('researchx_token');
    return `http://127.0.0.1:8000/api/papers/${id}/download?token=${token}`;
  },

  deletePaper: async (id) => {
    const response = await api.delete(`/papers/${id}`);
    return response.data;
  }
};
