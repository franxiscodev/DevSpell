'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { projectsApi } from '@/lib/api/projects';
import { analyzerApi } from '@/lib/api/analyzer';
import { analysisHistoryApi } from '@/lib/api/analysisHistory';
import type { Project, AnalysisResponse, AnalysisCreate } from '@/types';
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
  const [saving, setSaving] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [analysisName, setAnalysisName] = useState('');
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

  const handleSaveAnalysis = async () => {
    if (!results || !code.trim()) {
      setError('No hay resultados para guardar');
      return;
    }

    setSaving(true);
    setError('');

    try {
      const analysisData: AnalysisCreate = {
        name: analysisName.trim() || undefined,
        code: code,
        total_lines: results.total_lines,
        code_lines: results.code_lines,
        complexity: results.complexity,
        num_functions: results.num_functions,
        num_classes: results.num_classes,
        num_imports: results.num_imports,
        functions_data: results.functions,
        project_id: projectId,
      };

      await analysisHistoryApi.saveAnalysis(analysisData);
      setShowSaveModal(false);
      setAnalysisName('');
      alert('Análisis guardado exitosamente');
    } catch (err: any) {
      setError(err.message || 'Error al guardar el análisis');
      console.error(err);
    } finally {
      setSaving(false);
    }
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
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Resultados del Análisis
                </h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => router.push(`/projects/${projectId}/history`)}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                  >
                    Ver historial
                  </button>
                  <button
                    onClick={() => setShowSaveModal(true)}
                    className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
                    disabled={saving}
                  >
                    💾 Guardar Análisis
                  </button>
                </div>
              </div>
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

      {/* Modal para guardar análisis */}
      {showSaveModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Guardar Análisis
            </h3>
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Nombre (opcional)
              </label>
              <input
                type="text"
                value={analysisName}
                onChange={(e) => setAnalysisName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ej: Análisis inicial, Versión optimizada..."
                disabled={saving}
              />
              <p className="text-xs text-gray-500 mt-1">
                Si no ingresas un nombre, se usará la fecha actual
              </p>
            </div>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowSaveModal(false);
                  setAnalysisName('');
                }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                disabled={saving}
              >
                Cancelar
              </button>
              <button
                onClick={handleSaveAnalysis}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors disabled:bg-green-400"
                disabled={saving}
              >
                {saving ? 'Guardando...' : 'Guardar'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
