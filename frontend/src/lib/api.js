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

// Chuẩn hóa thông báo lỗi trả về từ API / Mạng (theo Mục 6 UI Conventions)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      return Promise.reject({
        type: 'NETWORK_ERROR',
        message: 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra đường truyền mạng.',
      });
    }

    const { status, data } = error.response;
    const serverMessage = data?.detail || data?.message;

    if (status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      return Promise.reject({
        type: 'AUTH_ERROR',
        status,
        message: serverMessage || 'Phiên đăng nhập hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.',
      });
    }
    if (status === 403) {
      return Promise.reject({
        type: 'FORBIDDEN_ERROR',
        status,
        message: serverMessage || 'Bạn không có quyền truy cập dữ liệu này.',
      });
    }

    if (status === 409) {
      return Promise.reject({
        type: 'CONFLICT_ERROR',
        status,
        message: serverMessage || 'Phòng đã hết hoặc bị trùng lịch trong khoảng thời gian đã chọn.',
      });
    }

    return Promise.reject({
      type: 'API_ERROR',
      status,
      message: serverMessage || 'Đã xảy ra lỗi trong quá trình xử lý yêu cầu.',
    });
  }
);


// 1. API Xác thực
export const authApi = {
  login: (credentials) => apiClient.post('/api/auth/login', credentials),
  register: (payload) => apiClient.post('/api/auth/register', payload),
  getMe: () => apiClient.get('/api/auth/me'),
};

// Các hàm gọi API cơ bản

export const roomApi = {
  getAll: (params) => apiClient.get('/api/rooms', { params }),
  getById: (id) => apiClient.get(`/api/rooms/${id}`),
  searchAvailable: (params) => apiClient.get('/api/rooms/available', { params }),
};

export const reservationApi = {
  create: (payload) => apiClient.post('/api/reservations', payload),
  getMyReservations: () => apiClient.get('/api/reservations/my'),
  getById: (id) => apiClient.get(`/api/reservations/${id}`),
  cancel: (id, reason) => apiClient.post(`/api/reservations/${id}/cancel`, { reason }),
};

export default apiClient;