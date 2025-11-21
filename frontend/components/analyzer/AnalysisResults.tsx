'use client';

import type { AnalysisResponse } from '@/types';

interface AnalysisResultsProps {
  results: AnalysisResponse;
}

export default function AnalysisResults({ results }: AnalysisResultsProps) {
  const getComplexityColor = (complexity: number) => {
    if (complexity <= 5) return 'text-green-600 bg-green-50';
    if (complexity <= 10) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getComplexityLabel = (complexity: number) => {
    if (complexity <= 5) return 'Baja';
    if (complexity <= 10) return 'Media';
    return 'Alta';
  };

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">Líneas Totales</p>
          <p className="text-2xl font-bold text-gray-900">{results.total_lines}</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">Líneas de Código</p>
          <p className="text-2xl font-bold text-blue-600">{results.code_lines}</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">Complejidad</p>
          <p className={`text-2xl font-bold ${getComplexityColor(results.complexity).split(' ')[0]}`}>
            {results.complexity}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {getComplexityLabel(results.complexity)}
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">Funciones</p>
          <p className="text-2xl font-bold text-purple-600">{results.num_functions}</p>
        </div>
      </div>

      {/* More Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">Clases</p>
          <p className="text-xl font-bold text-gray-900">{results.num_classes}</p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <p className="text-sm text-gray-600 mb-1">Imports</p>
          <p className="text-xl font-bold text-gray-900">{results.num_imports}</p>
        </div>
      </div>

      {/* Functions Table */}
      {results.functions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              Funciones Detectadas ({results.functions.length})
            </h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Función
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Líneas
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Complejidad
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {results.functions.map((func, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">
                      {func.name}()
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {func.line_start} - {func.line_end}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getComplexityColor(
                          func.complexity
                        )}`}
                      >
                        {func.complexity} ({getComplexityLabel(func.complexity)})
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
