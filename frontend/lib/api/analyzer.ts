import { ApiClient } from './client';
import type { AnalyzeRequest, AnalysisResponse } from '@/types';

const client = new ApiClient();

/**
 * API de análisis de código
 */
export const analyzerApi = {
  /**
   * Analizar código Python
   */
  async analyzeCode(code: string): Promise<AnalysisResponse> {
    const request: AnalyzeRequest = { code };
    return client.post<AnalysisResponse>('/analyze', request);
  },
};
