import { render, screen } from '@testing-library/react';
import JobList from './JobList';

const jobs = [
  { job_id: '1', report_type: 'ventas', status: 'COMPLETED', created_at: new Date().toISOString() },
  { job_id: '2', report_type: 'inventario', status: 'FAILED', created_at: new Date().toISOString() },
];

describe('JobList', () => {
  it('muestra la lista de trabajos', () => {
    render(<JobList jobs={jobs} />);
    expect(screen.getByText(/ventas/i)).toBeInTheDocument();
    expect(screen.getByText(/inventario/i)).toBeInTheDocument();
  });
  it('muestra mensaje si no hay trabajos', () => {
    render(<JobList jobs={[]} />);
    expect(screen.getByText(/No hay trabajos/i)).toBeInTheDocument();
  });
});
