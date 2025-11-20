'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { projectsApi } from '@/lib/api/projects';
import { analyzerApi } from '@/lib/api/analyzer';
import type { Project, AnalysisResponse } from '@/types';
import CodeEditor from '@/components/analyzer/CodeEditor';
import AnalysisResults from '@/components/analyzer/AnalysisResults';

export default function AnalyzePage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [code, setCode] = useState('');
  const [results, setResults] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Verificar autenticación
    if (!authApi.isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Cargar proyecto
    loadProject();
  }, [projectId, router]);

  const loadProject = async () => {
    try {
      const data = await projectsApi.getById(projectId);
      setProject(data);
    } catch (err: any) {
      setError('Error al cargar el proyecto');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Por favor, ingresa código para analizar');
      return;
    }

    setAnalyzing(true);
    setError('');
    setResults(null);

    try {
      const data = await analyzerApi.analyzeCode(code);
      setResults(data);
    } catch (err: any) {
      setError(err.message || 'Error al analizar el código');
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleClear = () => {
    setCode('');
    setResults(null);
    setError('');
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Cargando...</div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-red-600 mb-4">Proyecto no encontrado</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-blue-600 hover:text-blue-800"
          >
            Volver al dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-blue-600 hover:text-blue-800 text-sm mb-2"
          >
            ← Volver al dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
          <p className="text-gray-600 mt-1">Analizar Código Python</p>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Code Editor Section */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Editor de Código</h2>
              <div className="flex gap-2">
                <button
                  onClick={handleClear}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  disabled={analyzing || !code}
                >
                  Limpiar
                </button>
                <button
                  onClick={handleAnalyze}
                  className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:bg-blue-400"
                  disabled={analyzing || !code.trim()}
                >
                  {analyzing ? 'Analizando...' : 'Analizar Código'}
                </button>
              </div>
            </div>

            <CodeEditor
              value={code}
              onChange={setCode}
              disabled={analyzing}
              placeholder="# Pega tu código Python aquí
# Ejemplo:
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
"
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* Results Section */}
          {results && (
            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Resultados del Análisis
              </h2>
              <AnalysisResults results={results} />
            </div>
          )}

          {/* Empty State */}
          {!results && !error && !analyzing && (
            <div className="bg-white p-12 rounded-lg shadow-sm border border-gray-200 text-center">
              <p className="text-gray-600 mb-2">
                Ingresa código Python arriba y haz clic en "Analizar Código"
              </p>
              <p className="text-sm text-gray-500">
                El analizador calculará métricas de complejidad, número de funciones y más
              </p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
