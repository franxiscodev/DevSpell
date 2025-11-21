// Tipos para User
export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

// Tipos para Auth
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token: string;
  user: User;
}

// Tipos para Projects
export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
}

export interface ProjectUpdate {
  name?: string;
  description?: string;
}

// Tipos para Analysis
export interface FunctionInfo {
  name: string;
  line_start: number;
  line_end: number;
  complexity: number;
}

export interface AnalyzeRequest {
  code: string;
}

export interface AnalysisResponse {
  total_lines: number;
  code_lines: number;
  complexity: number;
  num_functions: number;
  num_classes: number;
  num_imports: number;
  functions: FunctionInfo[];
}

// Tipos para Analysis guardados (historial)
export interface SavedAnalysis {
  id: string;
  name: string | null;
  total_lines: number;
  code_lines: number;
  complexity: number;
  num_functions: number;
  num_classes: number;
  num_imports: number;
  functions: FunctionInfo[];
  project_id: string;
  user_id: string;
  created_at: string;
}

export interface SavedAnalysisDetail extends SavedAnalysis {
  code: string;
}

export interface AnalysisCreate {
  name?: string;
  code: string;
  total_lines: number;
  code_lines: number;
  complexity: number;
  num_functions: number;
  num_classes: number;
  num_imports: number;
  functions_data?: any;
  project_id: string;
}

export interface AnalysisCompare {
  analysis1: SavedAnalysis;
  analysis2: SavedAnalysis;
  differences: {
    code_lines_diff: number;
    complexity_diff: number;
    num_functions_diff: number;
    num_classes_diff: number;
    num_imports_diff: number;
  };
}
