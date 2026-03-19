
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { login as apiLogin } from '../services/api';
import Loader from '../components/Loader';

// Mapa centralizado de traducciones de errores
const LOGIN_ERROR_TRANSLATIONS = {
  'Invalid credentials': 'Credenciales inválidas',
  'User not found': 'Usuario no encontrado',
  'Incorrect username or password': 'Credenciales inválidas',
  // Agrega aquí más traducciones según sea necesario
};

function translateLoginError(message) {
  if (LOGIN_ERROR_TRANSLATIONS[message]) return LOGIN_ERROR_TRANSLATIONS[message];
  // Si el mensaje es muy genérico o técnico, muestra un mensaje amigable
  if (!message || message.length > 100) return 'Ocurrió un error, intenta nuevamente.';
  return message;
}

export default function LoginPage() {
  const { login } = useAuth();
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await apiLogin(userId, password);
      login({ sub: userId, role: data.role }, data.access_token);
      setSuccess(true);
    } catch (err) {
      if (err.message === 'Failed to fetch') {
        setError('No se pudo conectar con el servidor. Verifica tu conexión o que el backend esté en funcionamiento.');
      } else {
        setError(translateLoginError(err.message));
      }
      setSuccess(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="container-fluid" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #cbe6fa 0%, #a3cbe6 100%)' }}>
      <div className="p-4 bg-white rounded" style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.15)' }}>
        <h1 className="mb-4">Sistema de gestión de reportes</h1>
        <div className="alert alert-info mb-4" role="alert">
          <b>Diligencie usuario y contraseña para ingresar al sistema.</b>
        </div>
        <form onSubmit={handleSubmit} aria-label="Formulario de login">
          <div className="mb-3">
            <label htmlFor="userId" className="form-label">Usuario</label>
            <input
              id="userId"
              type="text"
              value={userId}
              onChange={e => setUserId(e.target.value)}
              required
              autoFocus
              aria-required="true"
              className="form-control"
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">Contraseña</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              aria-required="true"
              className="form-control"
            />
          </div>
          <button type="submit" disabled={loading} aria-busy={loading} className="btn btn-success w-100">
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
          {error && <div role="alert" className="alert alert-danger mt-3">{error}</div>}
          {success && <div role="alert" className="alert alert-success mt-3">Se ingresó de manera exitosa</div>}
        </form>
        {loading && <Loader label="Verificando credenciales..." />}
      </div>
    </main>
  );
}
