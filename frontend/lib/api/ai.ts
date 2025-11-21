import { apiClient } from './client';

// =============================================================================
// Types
// =============================================================================

export interface SuggestionsRequest {
  code: string;
  analysis: {
    complexity: number;
    num_functions: number;
    code_lines: number;
  };
}

export interface SuggestionsResponse {
  suggestions: string[];
}

export interface ExplainRequest {
  function_name: string;
  function_code: string;
}

export interface ExplainResponse {
  explanation: string;
}

export interface OptimizeRequest {
  code: string;
}

export interface OptimizeResponse {
  optimized_code: string;
}

// =============================================================================
// AI API Client
// =============================================================================

export const aiApi = {
  /**
   * Obtener sugerencias de mejora para código analizado
   */
  async getSuggestions(request: SuggestionsRequest): Promise<SuggestionsResponse> {
    return apiClient.post<SuggestionsResponse>('/ai/suggestions', request);
  },

  /**
   * Explicar qué hace una función específica
   */
  async explainFunction(request: ExplainRequest): Promise<ExplainResponse> {
    return apiClient.post<ExplainResponse>('/ai/explain', request);
  },

  /**
   * Optimizar código reduciendo complejidad
   */
  async optimizeCode(request: OptimizeRequest): Promise<OptimizeResponse> {
    return apiClient.post<OptimizeResponse>('/ai/optimize', request);
  },
};
