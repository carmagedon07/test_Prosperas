import { render, screen } from '@testing-library/react';
import JobStatus from './JobStatus';

describe('JobStatus', () => {
  it('muestra el estado Pendiente', () => {
    render(<JobStatus status="PENDING" />);
    expect(screen.getByLabelText(/Pendiente/i)).toBeInTheDocument();
  });
  it('muestra el estado Procesando', () => {
    render(<JobStatus status="PROCESSING" />);
    expect(screen.getByLabelText(/Procesando/i)).toBeInTheDocument();
  });
  it('muestra el estado Completado', () => {
    render(<JobStatus status="COMPLETED" />);
    expect(screen.getByLabelText(/Completado/i)).toBeInTheDocument();
  });
  it('muestra el estado Fallido', () => {
    render(<JobStatus status="FAILED" />);
    expect(screen.getByLabelText(/Fallido/i)).toBeInTheDocument();
  });
});
