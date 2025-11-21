'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api/auth';
import { projectsApi } from '@/lib/api/projects';
import type { User, Project, ProjectCreate } from '@/types';
import ProjectCard from '@/components/projects/ProjectCard';
import ProjectModal from '@/components/projects/ProjectModal';
import Navbar from '@/components/layout/Navbar';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);

  useEffect(() => {
    // Verificar autenticación
    if (!authApi.isAuthenticated()) {
      router.push('/login');
      return;
    }

    // Cargar usuario
    const storedUser = authApi.getStoredUser();
    if (storedUser) {
      setUser(storedUser);
    }
    setLoading(false);

    // Cargar proyectos
    loadProjects();
  }, [router]);

  const loadProjects = async () => {
    setLoadingProjects(true);
    try {
      const data = await projectsApi.getAll();
      setProjects(data);
    } catch (error: any) {
      console.error('Error al cargar proyectos:', error);
      // El ApiClient ya maneja automáticamente los errores 401
    } finally {
      setLoadingProjects(false);
    }
  };

  const handleCreateProject = async (data: ProjectCreate) => {
    await projectsApi.create(data);
    await loadProjects();
  };

  const handleUpdateProject = async (data: ProjectCreate) => {
    if (!editingProject) return;
    await projectsApi.update(editingProject.id, data);
    await loadProjects();
    setEditingProject(null);
  };

  const handleDeleteProject = async (projectId: string) => {
    await projectsApi.delete(projectId);
    await loadProjects();
  };

  const openCreateModal = () => {
    setEditingProject(null);
    setIsModalOpen(true);
  };

  const openEditModal = (project: Project) => {
    setEditingProject(project);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingProject(null);
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Cargando...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar title="DevSpell" />

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Bienvenido al Dashboard
          </h2>
          <p className="text-gray-600">
            Gestiona tus proyectos y análisis de código
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Proyectos
            </h3>
            <p className="text-3xl font-bold text-blue-600 mb-2">
              {loadingProjects ? '...' : projects.length}
            </p>
            <p className="text-sm text-gray-600">Total de proyectos</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Análisis
            </h3>
            <p className="text-3xl font-bold text-green-600 mb-2">0</p>
            <p className="text-sm text-gray-600">Próximamente</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Reportes
            </h3>
            <p className="text-3xl font-bold text-purple-600 mb-2">0</p>
            <p className="text-sm text-gray-600">Próximamente</p>
          </div>
        </div>

        {/* Projects Section */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-2xl font-bold text-gray-900">Mis Proyectos</h3>
            <button
              onClick={openCreateModal}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              + Nuevo Proyecto
            </button>
          </div>

          {loadingProjects ? (
            <div className="text-center py-12">
              <p className="text-gray-600">Cargando proyectos...</p>
            </div>
          ) : projects.length === 0 ? (
            <div className="bg-white p-12 rounded-lg shadow-sm border border-gray-200 text-center">
              <p className="text-gray-600 mb-4">No tienes proyectos aún</p>
              <button
                onClick={openCreateModal}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                Crear tu primer proyecto →
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
                <ProjectCard
                  key={project.id}
                  project={project}
                  onEdit={openEditModal}
                  onDelete={handleDeleteProject}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {/* Modal */}
      <ProjectModal
        isOpen={isModalOpen}
        onClose={closeModal}
        onSubmit={editingProject ? handleUpdateProject : handleCreateProject}
        project={editingProject}
      />
    </div>
  );
}
