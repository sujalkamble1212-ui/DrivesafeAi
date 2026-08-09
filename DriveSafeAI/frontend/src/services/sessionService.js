import api from './api';

export const sessionService = {
  async getSessions(page = 1, perPage = 10) {
    const response = await api.get('/sessions', {
      params: { page, per_page: perPage },
    });
    return response.data;
  },

  async getSessionById(sessionId) {
    const response = await api.get(`/sessions/${sessionId}`);
    return response.data;
  },

  async deleteSession(sessionId) {
    const response = await api.delete(`/sessions/${sessionId}`);
    return response.data;
  },

  async getAlerts(page = 1, perPage = 20, sessionId = null, alertType = null) {
    const params = { page, per_page: perPage };
    if (sessionId) params.session_id = sessionId;
    if (alertType) params.alert_type = alertType;

    const response = await api.get('/alerts', { params });
    return response.data;
  },

  async deleteAlert(alertId) {
    const response = await api.delete(`/alerts/${alertId}`);
    return response.data;
  },
};
