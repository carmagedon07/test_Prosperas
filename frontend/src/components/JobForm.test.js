import { render, screen, fireEvent } from '@testing-library/react';
import JobForm from './JobForm';

describe('JobForm', () => {
  it('permite seleccionar tipo de reporte y enviar', () => {
    const onSubmit = jest.fn();
    render(<JobForm onSubmit={onSubmit} loading={false} />);
    fireEvent.change(screen.getByLabelText(/Tipo de reporte/i), { target: { value: 'inventario' } });
    fireEvent.click(screen.getByRole('button', { name: /Crear reporte/i }));
    expect(onSubmit).toHaveBeenCalledWith('inventario');
  });
});
