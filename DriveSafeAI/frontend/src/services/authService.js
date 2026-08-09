import api from './api';

export const authService = {
  async register(username, email, password, fullName) {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
      full_name: fullName,
    });
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async login(usernameOrEmail, password) {
    const response = await api.post('/auth/login', {
      username_or_email: usernameOrEmail,
      password,
    });
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async logout() {
    try {
      await api.post('/auth/logout');
    } catch {
      // Ignore network failure on logout
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  },

  async getProfile() {
    const response = await api.get('/auth/profile');
    return response.data.user;
  },

  async updateProfile(profileData) {
    const response = await api.put('/auth/profile', profileData);
    if (response.data.user) {
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
};
