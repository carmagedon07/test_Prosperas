import React, { useEffect, useState, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { createJob, getJobs } from '../services/api';
import JobList from '../components/JobList';
import JobForm from '../components/JobForm';
import Loader from '../components/Loader';
import usePolling from '../hooks/usePolling';
import Navbar from '../components/Navbar';

function allJobsFinished(jobs) {
  return jobs.length > 0 && jobs.every(j => j.status === 'COMPLETED' || j.status === 'FAILED');
}

export default function Dashboard() {
  const { token } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState('');

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
      <main style={{ maxWidth: 600, margin: '2em auto', padding: '1em' }}>
        <h1>Mis trabajos</h1>
        <JobForm onSubmit={handleCreateJob} loading={creating} />
        {loading ? <Loader /> : <JobList jobs={jobs} />}
        {error && <div role="alert" style={{ color: 'red', marginTop: '1em' }}>{error}</div>}
      </main>
    </>
  );
}
