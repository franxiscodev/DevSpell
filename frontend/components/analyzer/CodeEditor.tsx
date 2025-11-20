'use client';

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function CodeEditor({ value, onChange, placeholder, disabled }: CodeEditorProps) {
  return (
    <div className="w-full">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
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
