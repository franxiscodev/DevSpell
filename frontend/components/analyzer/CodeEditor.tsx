'use client';

import { KeyboardEvent, useRef, useEffect } from 'react';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function CodeEditor({ value, onChange, placeholder, disabled }: CodeEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lineNumbersRef = useRef<HTMLDivElement>(null);

  // Calcular número de líneas
  const lines = value.split('\n');
  const lineCount = lines.length;

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

  // Sincronizar scroll de números con textarea
  const handleScroll = () => {
    if (lineNumbersRef.current && textareaRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
    }
  };

  return (
    <div className="w-full">
      {/* Editor con números de línea */}
      <div className="flex border border-gray-700 rounded-lg overflow-hidden bg-gray-900">
        {/* Números de línea */}
        <div
          ref={lineNumbersRef}
          className="flex-shrink-0 w-12 bg-gray-800 text-gray-500 text-right text-sm font-mono py-4 pr-3 select-none overflow-hidden"
          style={{
            height: '384px', // h-96 = 384px
            overflowY: 'hidden',
            lineHeight: '1.5rem' // Debe coincidir con el textarea
          }}
        >
          {Array.from({ length: Math.max(lineCount, 20) }, (_, i) => (
            <div key={i + 1} className="leading-6">
              {i + 1}
            </div>
          ))}
        </div>

        {/* Textarea de código */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onScroll={handleScroll}
          placeholder={placeholder || 'Pega tu código Python aquí...'}
          disabled={disabled}
          className="flex-1 h-96 p-4 pl-3 font-mono text-sm bg-gray-900 text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none disabled:opacity-50 disabled:cursor-not-allowed leading-6"
          spellCheck={false}
          style={{ lineHeight: '1.5rem' }} // 24px = leading-6
        />
      </div>

      {/* Estadísticas */}
      <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
        <span>{lineCount} líneas</span>
        <span>{value.length} caracteres</span>
      </div>
    </div>
  );
}
