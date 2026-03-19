import React from 'react';
import JobItem from './JobItem';

export default function JobList({ jobs }) {
  if (!Array.isArray(jobs) || jobs.length === 0) {
    return <p>No hay trabajos aún.</p>;
  }
  return (
    <ul aria-label="Lista de trabajos">
      {jobs.map(job => (
        <JobItem key={job.job_id} job={job} />
      ))}
    </ul>
  );
}
