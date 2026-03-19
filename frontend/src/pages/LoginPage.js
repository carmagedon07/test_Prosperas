
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

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const data = await apiLogin(userId, password);
      login({ sub: userId, role: data.role }, data.access_token);
    } catch (err) {
      if (err.message === 'Failed to fetch') {
        setError('No se pudo conectar con el servidor. Verifica tu conexión o que el backend esté en funcionamiento.');
      } else {
        setError(translateLoginError(err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ maxWidth: 400, margin: '4em auto', padding: '2em', border: '1px solid #eee', borderRadius: 8 }}>
      <h1>Iniciar sesión</h1>
      <form onSubmit={handleSubmit} aria-label="Formulario de login">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1em' }}>
          <div>
            <label htmlFor="userId">Usuario</label><br />
            <input
              id="userId"
              type="text"
              value={userId}
              onChange={e => setUserId(e.target.value)}
              required
              autoFocus
              aria-required="true"
              style={{ width: '100%' }}
            />
          </div>
          <div>
            <label htmlFor="password">Contraseña</label><br />
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              aria-required="true"
              style={{ width: '100%' }}
            />
          </div>
          <button type="submit" disabled={loading} aria-busy={loading} style={{ marginTop: '1em' }}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
          {error && <div role="alert" style={{ color: 'red', marginTop: '1em' }}>{error}</div>}
        </div>
      </form>
      {loading && <Loader label="Verificando credenciales..." />}
    </main>
  );
}
