'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { analysisHistoryApi } from '@/lib/api/analysisHistory';
import type { SavedAnalysisDetail } from '@/types';
import AnalysisResults from '@/components/analyzer/AnalysisResults';
import CodeEditor from '@/components/analyzer/CodeEditor';
import Navbar from '@/components/layout/Navbar';

export default function AnalysisDetailPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;
  const analysisId = params.analysisId as string;

  const [analysis, setAnalysis] = useState<SavedAnalysisDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalysis();
  }, [analysisId]);

  const loadAnalysis = async () => {
    setLoading(true);
    setError(null);

    try {
      const data = await analysisHistoryApi.getAnalysisDetail(analysisId);
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || 'Error al cargar el análisis');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Cargando análisis...</div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || 'Análisis no encontrado'}</p>
          <button
            onClick={() => router.push(`/projects/${projectId}/history`)}
            className="text-blue-600 hover:text-blue-800"
          >
            ← Volver al historial
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar title="Dashboard" showBackButton={true} />

      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            {analysis.name || `Análisis del ${formatDate(analysis.created_at)}`}
          </h1>
          <p className="text-gray-600 mt-1">
            Guardado el {formatDate(analysis.created_at)}
          </p>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Métricas */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Resultados del Análisis
            </h2>
            <AnalysisResults
              results={{
                total_lines: analysis.total_lines,
                code_lines: analysis.code_lines,
                complexity: analysis.complexity,
                num_functions: analysis.num_functions,
                num_classes: analysis.num_classes,
                num_imports: analysis.num_imports,
                functions: analysis.functions,
              }}
            />
          </div>

          {/* Código */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Código Analizado
            </h2>
            <CodeEditor value={analysis.code} onChange={() => {}} disabled />
          </div>
        </div>
      </main>
    </div>
  );
}
