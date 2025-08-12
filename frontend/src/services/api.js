import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An error occurred';
    return Promise.reject(new Error(message));
  }
);

export const fileAPI = {
  getFiles: () => api.get('/files'),
  
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

export const chatAPI = {
  createSession: () => api.post('/create-session'),
  
  sendMessage: (data) => api.post('/chat', data),
  
  deleteSession: (sessionId) => api.delete(`/session/${sessionId}`),
  
  getSessionInfo: (sessionId) => api.get(`/session/${sessionId}/info`),
};
