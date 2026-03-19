import { render, screen } from '@testing-library/react';
import Loader from './Loader';

describe('Loader', () => {
  it('muestra el mensaje por defecto', () => {
    render(<Loader />);
    expect(screen.getByText(/Cargando/i)).toBeInTheDocument();
  });
  it('muestra un mensaje personalizado', () => {
    render(<Loader label="Procesando..." />);
    expect(screen.getByText(/Procesando/i)).toBeInTheDocument();
  });
});
