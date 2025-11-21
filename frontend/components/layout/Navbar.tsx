'use client';

import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { authApi } from '@/lib/api/auth';

interface NavbarProps {
  title?: string;
  showBackButton?: boolean;
}

export default function Navbar({ title = 'DevSpell', showBackButton = false }: NavbarProps) {
  const router = useRouter();
  const [username, setUsername] = useState<string>('');

  useEffect(() => {
    // Obtener usuario del localStorage
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          const user = JSON.parse(userStr);
          setUsername(user.username || user.email);
        } catch (e) {
          console.error('Error parsing user:', e);
        }
      }
    }
  }, []);

  const handleLogout = () => {
    authApi.logout();
    router.push('/login');
  };

  const handleBack = () => {
    router.back();
  };

  const handleGoToDashboard = () => {
    router.push('/dashboard');
  };

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left side */}
          <div className="flex items-center space-x-4">
            {showBackButton && (
              <button
                onClick={handleBack}
                className="text-gray-600 hover:text-gray-900 flex items-center space-x-1"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                <span>Atrás</span>
              </button>
            )}
            <button
              onClick={handleGoToDashboard}
              className="text-xl font-bold text-blue-600 hover:text-blue-700"
            >
              {title}
            </button>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {username && (
              <span className="text-gray-700">
                <span className="text-gray-500">Hola,</span> <span className="font-medium">{username}</span>
              </span>
            )}
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
            >
              Cerrar sesión
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
