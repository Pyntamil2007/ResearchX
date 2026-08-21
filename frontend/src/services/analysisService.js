import api from './api';

export const analysisService = {
  analyzePaper: async (paperId) => {
    const response = await api.post(`/analysis/paper/${paperId}`);
    return response.data;
  },

  getAnalysis: async (analysisId) => {
    const response = await api.get(`/analysis/${analysisId}`);
    return response.data;
  },

  deleteAnalysis: async (analysisId) => {
    const response = await api.delete(`/analysis/${analysisId}`);
    return response.data;
  },

  getResults: async (analysisId) => {
    const response = await api.get(`/results/${analysisId}`);
    return response.data;
  },

  getHistory: async (params = {}) => {
    const response = await api.get('/history', { params });
    return response.data;
  },

  getAdminHistory: async (params = {}) => {
    const response = await api.get('/history/admin', { params });
    return response.data;
  },

  deleteHistoryItem: async (id) => {
    const response = await api.delete(`/history/${id}`);
    return response.data;
  },

  getUserDashboard: async () => {
    const response = await api.get('/dashboard/user');
    return response.data;
  },

  getAdminDashboard: async () => {
    const response = await api.get('/dashboard/admin');
    return response.data;
  },

  getDomainsTaxonomy: async () => {
    const response = await api.get('/analysis/domains/taxonomy');
    return response.data;
  },

  updateAnalysisDomain: async (analysisId, domain) => {
    const response = await api.patch(`/analysis/${analysisId}/domain`, { domain });
    return response.data;
  }
};
