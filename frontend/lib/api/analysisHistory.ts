import { apiClient } from './client';
import type {
  SavedAnalysis,
  SavedAnalysisDetail,
  AnalysisCreate,
  AnalysisCompare,
} from '@/types';

/**
 * API client para historial de análisis.
 */
export const analysisHistoryApi = {
  /**
   * Guarda un análisis en la base de datos.
   */
  async saveAnalysis(data: AnalysisCreate): Promise<SavedAnalysis> {
    return apiClient.post<SavedAnalysis>('/analyses', data);
  },

  /**
   * Lista todos los análisis de un proyecto.
   */
  async getProjectAnalyses(projectId: string): Promise<SavedAnalysis[]> {
    return apiClient.get<SavedAnalysis[]>(`/analyses/project/${projectId}`);
  },

  /**
   * Obtiene el detalle completo de un análisis (incluyendo código).
   */
  async getAnalysisDetail(analysisId: string): Promise<SavedAnalysisDetail> {
    return apiClient.get<SavedAnalysisDetail>(`/analyses/${analysisId}`);
  },

  /**
   * Elimina un análisis.
   */
  async deleteAnalysis(analysisId: string): Promise<void> {
    return apiClient.delete(`/analyses/${analysisId}`);
  },

  /**
   * Compara dos análisis.
   */
  async compareAnalyses(id1: string, id2: string): Promise<AnalysisCompare> {
    return apiClient.get<AnalysisCompare>(`/analyses/${id1}/compare/${id2}`);
  },
};
