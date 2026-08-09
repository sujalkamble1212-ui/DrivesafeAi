import api from './api';

export const settingService = {
  async getSettings() {
    const response = await api.get('/settings');
    return response.data.settings;
  },

  async updateSettings(settingsData) {
    const response = await api.put('/settings', settingsData);
    return response.data.settings;
  },
};
