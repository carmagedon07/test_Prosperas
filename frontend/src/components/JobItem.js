import React from 'react';
import JobStatus from './JobStatus';

export default function JobItem({ job }) {
  return (
    <li style={{ borderBottom: '1px solid #eee', padding: '1em 0', listStyle: 'none' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <strong>Tipo de reporte:</strong> {job.report_type}<br />
          <strong>Rango de fechas:</strong> {job.date_range}<br />
          <strong>Formato:</strong> {job.format}<br />
          <span style={{ fontSize: '0.9em', color: '#666' }}>Creado: {new Date(job.created_at).toLocaleString('es-ES')}</span>
        </div>
        <JobStatus status={job.status} />
      </div>
      {job.result_url && (
        <div style={{ marginTop: '0.5em' }}>
          <a href={job.result_url} target="_blank" rel="noopener noreferrer" aria-label="Descargar reporte">
            Descargar reporte
          </a>
        </div>
      )}
    </li>
  );
}
