import { apiClient } from './client';
import type { LoginRequest, RegisterRequest, AuthResponse, User } from '@/types';

export const authApi = {
  // Login
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    // FastAPI OAuth2 espera form data
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    
    // Guardar token en localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    return data;
  },

  // Register
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const data = await apiClient.post<AuthResponse>('/auth/register', userData);
    
    // Guardar token en localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    return data;
  },

  // Get current user
  async getMe(): Promise<User> {
    return apiClient.get<User>('/auth/me');
  },

  // Logout
  logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
    }
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    if (typeof window !== 'undefined') {
      return !!localStorage.getItem('access_token');
    }
    return false;
  },

  // Get stored user
  getStoredUser(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    }
    return null;
  },
};
