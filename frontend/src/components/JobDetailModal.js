import React, { useState } from 'react';
import { getJobById } from '../services/api';
import JobStatus from './JobStatus';

export default function JobDetailModal({ show, onClose, token }) {
  const [jobId, setJobId] = useState('');
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!jobId.trim()) {
      setError('Por favor ingrese un Job ID');
      return;
    }

    setLoading(true);
    setError('');
    setJob(null);

    try {
      const data = await getJobById(token, jobId.trim());
      setJob(data);
    } catch (err) {
      const msg = err.message || 'Error al buscar el reporte';
      if (msg.includes('404') || msg.includes('not found')) {
        setError('Reporte no encontrado o no tienes acceso a él');
      } else {
        setError(msg);
      }
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

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleString('es-ES');
    } catch {
      return dateString;
    }
  };

  if (!show) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '2rem',
        maxWidth: '600px',
        width: '90%',
        maxHeight: '80vh',
        overflowY: 'auto',
        position: 'relative'
      }}>
        <button
          onClick={handleClose}
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            border: 'none',
            background: 'transparent',
            fontSize: '1.5rem',
            cursor: 'pointer',
            color: '#666'
          }}
        >
          ×
        </button>

        <h3 style={{ marginBottom: '1.5rem', color: '#333' }}>
          🔍 Buscar Reporte por ID
        </h3>

        <div style={{ marginBottom: '1.5rem' }}>
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Ingrese el Job ID (ej: abc123...)"
              value={jobId}
              onChange={(e) => setJobId(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <button
              className="btn btn-primary"
              onClick={handleSearch}
              disabled={loading}
            >
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </div>
        </div>

        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {job && (
          <div style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '1.5rem',
            backgroundColor: '#f8f9fa'
          }}>
            <h5 style={{ marginBottom: '1rem', color: '#495057' }}>
              Detalles del Reporte
            </h5>

            <table className="table table-sm table-borderless" style={{ marginBottom: 0 }}>
              <tbody>
                <tr>
                  <td style={{ fontWeight: 'bold', width: '40%' }}>Job ID:</td>
                  <td style={{ wordBreak: 'break-all', fontSize: '0.9em', fontFamily: 'monospace' }}>
                    {job.job_id}
                  </td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 'bold' }}>Estado:</td>
                  <td><JobStatus status={job.status} /></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 'bold' }}>Tipo de Reporte:</td>
                  <td>{job.report_type}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 'bold' }}>Rango de Fechas:</td>
                  <td>{job.date_range || 'N/A'}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 'bold' }}>Formato:</td>
                  <td>{job.format?.toUpperCase() || 'N/A'}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 'bold' }}>Fecha Creación:</td>
                  <td>{formatDate(job.created_at)}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 'bold' }}>Última Actualización:</td>
                  <td>{formatDate(job.updated_at)}</td>
                </tr>
                {job.result_url && (
                  <tr>
                    <td style={{ fontWeight: 'bold' }}>URL del Resultado:</td>
                    <td>
                      <a href={job.result_url} target="_blank" rel="noopener noreferrer">
                        {job.result_url}
                      </a>
                    </td>
                  </tr>
                )}
                {job.result && (
                  <tr>
                    <td style={{ fontWeight: 'bold', verticalAlign: 'top' }}>Resultado:</td>
                    <td>
                      <pre style={{
                        backgroundColor: '#fff',
                        padding: '0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.85em',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        border: '1px solid #ddd'
                      }}>
                        {typeof job.result === 'string' 
                          ? job.result 
                          : JSON.stringify(job.result, null, 2)
                        }
                      </pre>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
          <button
            className="btn btn-secondary"
            onClick={handleClose}
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}
