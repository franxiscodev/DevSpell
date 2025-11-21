'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { analysisHistoryApi } from '@/lib/api/analysisHistory';
import { projectsApi } from '@/lib/api/projects';
import type { SavedAnalysis, Project } from '@/types';
import ConfirmDialog from '@/components/ui/ConfirmDialog';
import Toast from '@/components/ui/Toast';
import Navbar from '@/components/layout/Navbar';

export default function AnalysisHistoryPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [analyses, setAnalyses] = useState<SavedAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    loadData();
  }, [projectId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Cargar proyecto y análisis en paralelo
      const [projectData, analysesData] = await Promise.all([
        projectsApi.getById(projectId),
        analysisHistoryApi.getProjectAnalyses(projectId),
      ]);

      setProject(projectData);
      setAnalyses(analysesData);
    } catch (err: any) {
      setError(err.message || 'Error al cargar el historial');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (analysisId: string) => {
    try {
      await analysisHistoryApi.deleteAnalysis(analysisId);
      setDeleteConfirm(null);
      setToast({ message: 'Análisis eliminado exitosamente', type: 'success' });
      await loadData(); // Recargar lista
    } catch (err: any) {
      setDeleteConfirm(null);
      setToast({ message: 'Error al eliminar análisis: ' + err.message, type: 'error' });
    }
  };

  const handleViewDetail = (analysisId: string) => {
    router.push(`/projects/${projectId}/history/${analysisId}`);
  };

  const getComplexityColor = (complexity: number) => {
    if (complexity <= 5) return 'text-green-600 bg-green-50';
    if (complexity <= 10) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Cargando historial...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar title={project?.name || 'Historial'} showBackButton={true} />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Historial de Análisis
          </h1>
          {project && (
            <p className="text-gray-600 mt-2">Proyecto: {project.name}</p>
          )}
        </div>

        {/* Lista de análisis */}
        {analyses.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <p className="text-gray-500 mb-4">
              No hay análisis guardados para este proyecto
            </p>
            <button
              onClick={() => router.push(`/projects/${projectId}/analyze`)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Analizar código
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {analyses.map((analysis) => (
              <div
                key={analysis.id}
                className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {analysis.name || `Análisis del ${formatDate(analysis.created_at)}`}
                    </h3>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div>
                        <p className="text-sm text-gray-500">Líneas de código</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {analysis.code_lines}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Complejidad</p>
                        <p
                          className={`text-lg font-semibold px-3 py-1 rounded-full inline-block ${getComplexityColor(analysis.complexity)}`}
                        >
                          {analysis.complexity}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Funciones</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {analysis.num_functions}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Clases</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {analysis.num_classes}
                        </p>
                      </div>
                    </div>

                    <p className="text-xs text-gray-500">
                      Creado: {formatDate(analysis.created_at)}
                    </p>
                  </div>

                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => handleViewDetail(analysis.id)}
                      className="text-blue-600 hover:text-blue-800 text-sm font-medium px-4 py-2 border border-blue-600 rounded-lg hover:bg-blue-50"
                    >
                      Ver detalle
                    </button>
                    <button
                      onClick={() => setDeleteConfirm(analysis.id)}
                      className="text-red-600 hover:text-red-800 text-sm font-medium"
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confirm dialog */}
      {deleteConfirm && (
        <ConfirmDialog
          title="Eliminar Análisis"
          message="¿Estás seguro de que deseas eliminar este análisis? Esta acción no se puede deshacer."
          confirmText="Eliminar"
          cancelText="Cancelar"
          type="danger"
          onConfirm={() => handleDelete(deleteConfirm)}
          onCancel={() => setDeleteConfirm(null)}
        />
      )}

      {/* Toast notifications */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
