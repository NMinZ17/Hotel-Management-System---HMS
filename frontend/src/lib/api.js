import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tự động gắn token nếu có (dùng cho các tuần sau)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Các hàm gọi API cơ bản

export const roomApi = {
  getAll: () => apiClient.get('/api/rooms'),
  getById: (id) => apiClient.get(`/api/rooms/${id}`),
};

export default apiClient;