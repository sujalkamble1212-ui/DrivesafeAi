import api from './api';

export const reportService = {
  async downloadReport(sessionId) {
    const response = await api.get(`/reports/${sessionId}`, {
      responseType: 'blob',
    });

    // Create a download link for the blob
    const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `DriveSafeAI_Report_Session_${sessionId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  },

  async getReportStatus(sessionId) {
    const response = await api.get(`/reports/${sessionId}/status`);
    return response.data;
  },
};
