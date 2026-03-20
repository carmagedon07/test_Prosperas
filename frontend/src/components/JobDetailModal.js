import React, { useState } from 'react';
import { getJobById } from '../services/api';
import JobStatus from './JobStatus';

export default function JobDetailModal({ show, onClose, token }) {
  const [jobId, setJobId] = useState('');
  const [job, setJob] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!jobId.trim()) return;
    setLoading(true);
    setJob(null);
    setError('');
    try {
      const data = await getJobById(token, jobId.trim());
      setJob(data);
    } catch (err) {
      setError(err.status === 404 ? 'Job no encontrado.' : 'Error al buscar el job.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setJobId('');
    setJob(null);
    setError('');
    onClose();
  };

  if (!show) return null;

  return (
    <div
      className="modal d-block"
      style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
      role="dialog"
      aria-modal="true"
    >
      <div className="modal-dialog modal-dialog-centered">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">🔍 Buscar Job por ID</h5>
            <button type="button" className="btn-close" onClick={handleClose} aria-label="Cerrar" />
          </div>
          <div className="modal-body">
            <form onSubmit={handleSearch} className="d-flex gap-2 mb-3">
              <input
                type="text"
                className="form-control"
                placeholder="Ingresa el Job ID (UUID)..."
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? '...' : 'Buscar'}
              </button>
            </form>

            {error && (
              <div className="alert alert-danger" role="alert">{error}</div>
            )}

            {job && (
              <table className="table table-bordered table-sm">
                <tbody>
                  <tr><th>Job ID</th><td style={{ fontFamily: 'monospace', fontSize: '0.8em' }}>{job.job_id}</td></tr>
                  <tr><th>Tipo</th><td>{job.report_type}</td></tr>
                  <tr><th>Formato</th><td>{job.format}</td></tr>
                  <tr><th>Rango de fechas</th><td>{job.date_range}</td></tr>
                  <tr><th>Estado</th><td><JobStatus status={job.status} /></td></tr>
                  <tr><th>Creado</th><td>{new Date(job.created_at).toLocaleString('es-ES')}</td></tr>
                  <tr><th>Actualizado</th><td>{new Date(job.updated_at).toLocaleString('es-ES')}</td></tr>
                  {job.result_url && (
                    <tr>
                      <th>Resultado</th>
                      <td><a href={job.result_url} target="_blank" rel="noreferrer">{job.result_url}</a></td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={handleClose}>Cerrar</button>
          </div>
        </div>
      </div>
    </div>
  );
}
