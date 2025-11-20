import { ApiClient } from './client';
import type { Project, ProjectCreate, ProjectUpdate } from '@/types';

const client = new ApiClient();

/**
 * API de proyectos
 */
export const projectsApi = {
  /**
   * Obtener todos los proyectos del usuario autenticado
   */
  async getAll(): Promise<Project[]> {
    return client.get<Project[]>('/projects');
  },

  /**
   * Obtener un proyecto por ID
   */
  async getById(id: string): Promise<Project> {
    return client.get<Project>(`/projects/${id}`);
  },

  /**
   * Crear un nuevo proyecto
   */
  async create(data: ProjectCreate): Promise<Project> {
    return client.post<Project>('/projects', data);
  },

  /**
   * Actualizar un proyecto existente
   */
  async update(id: string, data: ProjectUpdate): Promise<Project> {
    return client.put<Project>(`/projects/${id}`, data);
  },

  /**
   * Eliminar un proyecto
   */
  async delete(id: string): Promise<void> {
    return client.delete(`/projects/${id}`);
  },
};
