// Cliente HTTP base para el backend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    // Obtener token del localStorage
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  // Manejo centralizado de sesión expirada
  private handleUnauthorized(): void {
    if (typeof window !== 'undefined') {
      // Limpiar sesión
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      // Redirigir a login (fuerza reload completo)
      window.location.href = '/login';
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.handleUnauthorized();
        throw new Error('401 Unauthorized');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async post<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.handleUnauthorized();
        throw new Error('401 Unauthorized');
      }
      const error = await response.json();
      // Log full error for debugging
      console.error('API Error:', error);
      // Handle validation errors (array) vs single errors (string)
      const message = Array.isArray(error.detail)
        ? error.detail.map((e: any) => `${e.loc.join('.')}: ${e.msg}`).join(', ')
        : error.detail || `HTTP error! status: ${response.status}`;
      throw new Error(message);
    }

    return response.json();
  }

  async put<T>(endpoint: string, data: any): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.handleUnauthorized();
        throw new Error('401 Unauthorized');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async delete(endpoint: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.handleUnauthorized();
        throw new Error('401 Unauthorized');
      }
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }
}

export const apiClient = new ApiClient();