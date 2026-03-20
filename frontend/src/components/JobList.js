import React from 'react';
import JobStatus from './JobStatus';

export default function JobList({ jobs, page, totalPages, totalJobs, pageSize, onPageChange }) {
  if (!Array.isArray(jobs) || (jobs.length === 0 && page === 1)) {
    return <p>No hay trabajos aún.</p>;
  }

  const goToPage = (p) => {
    if (p >= 1 && p <= totalPages) onPageChange(p);
  };

  // Build a compact range of page buttons
  const pageNumbers = [];
  const delta = 2;
  for (let i = Math.max(1, page - delta); i <= Math.min(totalPages, page + delta); i++) {
    pageNumbers.push(i);
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-2">
        <small className="text-muted">
          Mostrando {jobs.length === 0 ? 0 : (page - 1) * pageSize + 1}–{(page - 1) * pageSize + jobs.length} de {totalJobs} solicitudes
        </small>
        <small className="text-muted">Página {page} de {totalPages}</small>
      </div>
      <div className="table-responsive">
        <table className="table table-striped align-middle">
          <thead>
            <tr>
              <th>#</th>
              <th>Job ID</th>
              <th>Tipo de reporte</th>
              <th>Formato</th>
              <th>Fecha de solicitud</th>
              <th>Estatus</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job, index) => (
              <tr key={job.job_id}>
                <td><strong>{(page - 1) * pageSize + index + 1}</strong></td>
                <td>
                  <span
                    style={{
                      fontFamily: 'monospace',
                      fontSize: '0.75em',
                      wordBreak: 'break-all',
                      cursor: 'help'
                    }}
                    title={`Job ID: ${job.job_id}`}
                  >
                    {job.job_id}
                  </span>
                </td>
                <td>{job.report_type}</td>
                <td>{job.format}</td>
                <td>{new Date(job.created_at).toLocaleString('es-ES')}</td>
                <td><JobStatus status={job.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {totalPages > 1 && (
        <nav aria-label="Paginación de trabajos">
          <ul className="pagination justify-content-center">
            <li className={`page-item${page === 1 ? ' disabled' : ''}`}>
              <button className="page-link" onClick={() => goToPage(1)} disabled={page === 1}>&laquo;</button>
            </li>
            <li className={`page-item${page === 1 ? ' disabled' : ''}`}>
              <button className="page-link" onClick={() => goToPage(page - 1)} disabled={page === 1}>Anterior</button>
            </li>
            {pageNumbers[0] > 1 && <li className="page-item disabled"><span className="page-link">…</span></li>}
            {pageNumbers.map(n => (
              <li key={n} className={`page-item${page === n ? ' active' : ''}`}>
                <button className="page-link" onClick={() => goToPage(n)}>{n}</button>
              </li>
            ))}
            {pageNumbers[pageNumbers.length - 1] < totalPages && <li className="page-item disabled"><span className="page-link">…</span></li>}
            <li className={`page-item${page === totalPages ? ' disabled' : ''}`}>
              <button className="page-link" onClick={() => goToPage(page + 1)} disabled={page === totalPages}>Siguiente</button>
            </li>
            <li className={`page-item${page === totalPages ? ' disabled' : ''}`}>
              <button className="page-link" onClick={() => goToPage(totalPages)} disabled={page === totalPages}>&raquo;</button>
            </li>
          </ul>
        </nav>
      )}
      <footer className="text-center mt-4 mb-2 text-muted" style={{fontSize: '0.9rem'}}>
        &copy; {new Date().getFullYear()} | Desarrollado por Pedro Nel Caro Diaz
      </footer>
    </>
  );
}
