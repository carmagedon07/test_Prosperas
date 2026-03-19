import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from './LoginPage';
import { AuthProvider } from '../context/AuthContext';

describe('LoginPage', () => {
  it('renderiza el formulario de login', () => {
    render(
      <AuthProvider>
        <LoginPage />
      </AuthProvider>
    );
    expect(screen.getByLabelText(/Usuario/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Entrar/i })).toBeInTheDocument();
  });
});
