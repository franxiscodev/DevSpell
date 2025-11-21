'use client';

import { useState } from 'react';
import { aiApi } from '@/lib/api/ai';

interface SuggestionsPanelProps {
  code: string;
  analysis: {
    complexity: number;
    num_functions: number;
    code_lines: number;
  };
}

export default function SuggestionsPanel({ code, analysis }: SuggestionsPanelProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGetSuggestions = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await aiApi.getSuggestions({ code, analysis });
      setSuggestions(response.suggestions);
    } catch (err: any) {
      console.error('Error getting suggestions:', err);
      setError(err.message || 'Error al obtener sugerencias de IA');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <svg className="w-6 h-6 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          Sugerencias de IA
        </h2>
        <button
          onClick={handleGetSuggestions}
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Analizando...
            </>
          ) : (
            'Obtener sugerencias'
          )}
        </button>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg mb-4 flex items-start">
          <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="font-semibold">Error al obtener sugerencias</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Suggestions list */}
      {suggestions.length > 0 && (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-blue-800">
              <span className="font-semibold">💡 {suggestions.length} sugerencias</span> generadas por IA para mejorar tu código
            </p>
          </div>
          <ol className="space-y-4">
            {suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                <span className="flex-shrink-0 flex items-center justify-center w-7 h-7 rounded-full bg-blue-600 text-white text-sm font-bold mr-4 mt-0.5">
                  {index + 1}
                </span>
                <div className="flex-1">
                  <p className="text-gray-800 leading-relaxed whitespace-pre-line text-[15px]">
                    {suggestion}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Empty state */}
      {!loading && suggestions.length === 0 && !error && (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <p className="mt-4 text-gray-500 text-sm">
            Haz clic en <span className="font-semibold">"Obtener sugerencias"</span> para analizar el código con IA
          </p>
          <p className="mt-2 text-gray-400 text-xs">
            Powered by DeepSeek-Coder 1.3B (local)
          </p>
        </div>
      )}
    </div>
  );
}
