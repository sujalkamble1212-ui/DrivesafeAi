import api from './api';

export const monitoringService = {
  async startSession(frameBase64 = null) {
    const response = await api.post('/monitor/session/start', frameBase64 ? { frame_data: frameBase64 } : {});
    return response.data;
  },

  async endSession(sessionId) {
    const response = await api.post('/monitor/session/end', { session_id: sessionId });
    return response.data;
  },

  async processFrame(frameBase64, sessionId) {
    const response = await api.post('/monitor/frame', {
      frame_data: frameBase64,
      session_id: sessionId,
    });
    return response.data;
  },

  async previewFrame(frameBase64) {
    const response = await api.post('/monitor/preview', {
      frame_data: frameBase64,
    });
    return response.data;
  },

  async saveAlert(sessionId, alertType, message, severity = 'warning') {
    const response = await api.post('/monitor/alert', {
      session_id: sessionId,
      alert_type: alertType,
      message,
      severity,
    });
    return response.data;
  },
};
