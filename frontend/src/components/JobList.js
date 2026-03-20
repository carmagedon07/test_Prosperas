import React, { useState } from 'react';
import JobStatus from './JobStatus';

const ITEMS_PER_PAGE = 10;

export default function JobList({ jobs }) {
  const [currentPage, setCurrentPage] = useState(1);
  if (!Array.isArray(jobs) || jobs.length === 0) {
    return <p>No hay trabajos aún.</p>;
  }

  const totalPages = Math.ceil(jobs.length / ITEMS_PER_PAGE);
  const startIdx = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIdx = startIdx + ITEMS_PER_PAGE;
  const jobsToShow = jobs.slice(startIdx, endIdx);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) setCurrentPage(page);
  };

  return (
    <>
      <div className="table-responsive">
        <table className="table table-striped align-middle">
          <thead>
            <tr>
              <th>#</th>
              <th>Job ID</th>
              <th>Tipo de reporte</th>
              {/* <th>Rango de fechas</th> */}
              <th>Formato</th>
              <th>Fecha de solicitud</th>
              <th>Estatus</th>
            </tr>
          </thead>
          <tbody>
            {jobsToShow.map((job, index) => (
              <tr key={job.job_id}>
                <td><strong>{startIdx + index + 1}</strong></td>
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
                {/* <td>{job.date_range}</td> */}
                <td>{job.format}</td>
                <td>{new Date(job.created_at).toLocaleString('es-ES')}</td>
                <td><JobStatus status={job.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <nav aria-label="Paginación de trabajos">
        <ul className="pagination justify-content-center">
          <li className={`page-item${currentPage === 1 ? ' disabled' : ''}`}>
            <button className="page-link" onClick={() => goToPage(currentPage - 1)} tabIndex={currentPage === 1 ? -1 : 0}>Anterior</button>
          </li>
          {Array.from({ length: totalPages }, (_, i) => (
            <li key={i + 1} className={`page-item${currentPage === i + 1 ? ' active' : ''}`}>
              <button className="page-link" onClick={() => goToPage(i + 1)}>{i + 1}</button>
            </li>
          ))}
          <li className={`page-item${currentPage === totalPages ? ' disabled' : ''}`}>
            <button className="page-link" onClick={() => goToPage(currentPage + 1)} tabIndex={currentPage === totalPages ? -1 : 0}>Siguiente</button>
          </li>
        </ul>
      </nav>
        <footer className="text-center mt-4 mb-2 text-muted" style={{fontSize: '0.9rem'}}>
          &copy; {new Date().getFullYear()} | Desarrollado por Pedro Nel Caro Diaz
        </footer>
    </>
  );
}
