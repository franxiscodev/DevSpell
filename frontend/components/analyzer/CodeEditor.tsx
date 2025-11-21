'use client';

import { KeyboardEvent } from 'react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function CodeEditor({ value, onChange, placeholder, disabled }: CodeEditorProps) {
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault();

      const target = e.currentTarget;
      const start = target.selectionStart;
      const end = target.selectionEnd;

      // Insertar 4 espacios (o tab) en la posición del cursor
      const newValue = value.substring(0, start) + '    ' + value.substring(end);
      onChange(newValue);

      // Colocar el cursor después de los espacios insertados
      setTimeout(() => {
        target.selectionStart = target.selectionEnd = start + 4;
      }, 0);
    }
  };

  return (
    <div className="w-full">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder || 'Pega tu código Python aquí...'}
        disabled={disabled}
        className="w-full h-96 p-4 font-mono text-sm bg-gray-900 text-gray-100 rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50 disabled:cursor-not-allowed"
        spellCheck={false}
      />
      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
        <span>{value.split('\n').length} líneas</span>
        <span>{value.length} caracteres</span>
      </div>
    </div>
  );
}
