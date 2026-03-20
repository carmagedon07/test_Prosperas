import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { createJob, getJobs, deleteAllJobs } from '../services/api';
import JobList from '../components/JobList';
import JobForm from '../components/JobForm';
import Loader from '../components/Loader';
import usePolling from '../hooks/usePolling';
import Navbar from '../components/Navbar';
import JobDetailModal from '../components/JobDetailModal';

function allJobsFinished(jobs) {
  return jobs.length > 0 && jobs.every(j => j.status === 'COMPLETED' || j.status === 'FAILED');
}

export default function Dashboard() {
  const { token } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');
  const [showSearchModal, setShowSearchModal] = useState(false);

  const fetchJobs = useCallback(async () => {
    try {
      const data = await getJobs(token);
      setJobs(data.jobs || []);
      setError('');
    } catch (err) {
      // Manejo robusto de error 403
      const msg = (err && err.message) ? err.message : '';
      const isForbidden = (err && err.status === 403) ||
        msg.includes('403') ||
        msg.toLowerCase().includes('admin privileges required') ||
        (err && err.detail && typeof err.detail === 'string' && err.detail.toLowerCase().includes('admin privileges required'));
      if (isForbidden) {
        setError('NO_AUTH');
      } else {
        setError('Error al obtener los trabajos');
      }
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  usePolling(fetchJobs, 2000, allJobsFinished(jobs));

  const handleCreateJob = async ({ reportType, dateRange, format }) => {
    setCreating(true);
    try {
      await createJob(token, reportType, dateRange, format);
      await fetchJobs();
    } catch {
      setError('Error al crear el trabajo');
    } finally {
      setCreating(false);
    }
  };

  const handleDeleteAll = async () => {
    const confirmed = window.confirm('¿Está seguro que desea eliminar TODOS los trabajos? Esta acción no se puede deshacer.');
    if (!confirmed) return;

    try {
      const result = await deleteAllJobs(token);
      alert(`Se eliminaron ${result.count} trabajos exitosamente`);
      await fetchJobs();
    } catch (err) {
      const isForbidden = (err && err.status === 403);
      if (isForbidden) {
        alert('No tienes permisos de administrador para eliminar todos los trabajos');
      } else {
        alert('Error al eliminar los trabajos');
      }
    }
  };

  if (error === 'NO_AUTH') {
    return (
      <>
        <Navbar />
        <main style={{ maxWidth: 600, margin: '2em auto', padding: '1em', textAlign: 'center' }}>
          <h1>Acceso no autorizado</h1>
          <p>No tienes permisos para ver esta sección.</p>
        </main>
      </>
    );
  }
  return (
    <>
      <Navbar />
      <div style={{ minHeight: '100vh', background: '#15b6ef', padding: '2em 0' }}>
        <div className="container" style={{ maxWidth: 900 }}>
          <div className="card shadow-sm mb-4">
            <div className="card-body">
              <h2 className="card-title mb-3" style={{ fontWeight: 'bold' }}>Bienvenido al módulo de procesamiento de reportes</h2>
              <p className="card-text text-muted mb-0">Aquí puede gestionar y solicitar reportes.</p>
            </div>
          </div>
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <JobForm onSubmit={handleCreateJob} loading={creating} />
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button 
                    className="btn btn-info btn-sm"
                    onClick={() => setShowSearchModal(true)}
                    style={{ height: 'fit-content' }}
                  >
                    🔍 Buscar por ID
                  </button>
                  <button 
                    className="btn btn-danger btn-sm"
                    onClick={handleDeleteAll}
                    style={{ height: 'fit-content' }}
                  >
                    🗑️ Limpiar Tabla
                  </button>
                </div>
              </div>
              <h3 className="mb-3">Listado de solicitudes de reportes</h3>
              {loading ? <Loader /> : <JobList jobs={jobs} />}
              {error && <div role="alert" className="alert alert-danger mt-3">{error}</div>}
            </div>
          </div>
        </div>
      </div>
      <JobDetailModal 
        show={showSearchModal} 
        onClose={() => setShowSearchModal(false)} 
        token={token} 
      />
    </>
  );
}
