
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { login as apiLogin, register as apiRegister } from '../services/api';
import Loader from '../components/Loader';

const ERROR_TRANSLATIONS = {
  'Invalid credentials': 'Credenciales inválidas',
  'User not found': 'Usuario no encontrado',
  'Incorrect username or password': 'Credenciales inválidas',
  'El usuario ya existe': 'El nombre de usuario ya está en uso',
};

function translateError(message) {
  if (ERROR_TRANSLATIONS[message]) return ERROR_TRANSLATIONS[message];
  if (!message || message.length > 120) return 'Ocurrió un error, intenta nuevamente.';
  return message;
}

export default function LoginPage() {
  const { login } = useAuth();
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [userId, setUserId] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const resetForm = (nextMode) => {
    setUserId('');
    setPassword('');
    setConfirmPassword('');
    setError('');
    setSuccess('');
    setMode(nextMode);
  };

  const handleLogin = async e => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const data = await apiLogin(userId, password);
      login({ sub: userId, role: data.role }, data.access_token);
    } catch (err) {
      if (err.message === 'Failed to fetch') {
        setError('No se pudo conectar con el servidor. Verifica que el backend esté en funcionamiento.');
      } else {
        setError(translateError(err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async e => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    if (password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres.');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await apiRegister(userId, password);
      setSuccess(`Usuario "${userId}" creado exitosamente. Ya puedes iniciar sesión.`);
      setMode('login');
      setPassword('');
      setConfirmPassword('');
    } catch (err) {
      if (err.message === 'Failed to fetch') {
        setError('No se pudo conectar con el servidor.');
      } else {
        setError(translateError(err.message));
      }
    } finally {
      setLoading(false);
    }
  };

  const isLogin = mode === 'login';

  return (
    <main className="container-fluid" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #cbe6fa 0%, #a3cbe6 100%)' }}>
      <div className="p-4 bg-white rounded" style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.15)', minWidth: 340 }}>
        <h1 className="mb-3">Sistema de gestión de reportes</h1>

        {/* Toggle tabs */}
        <ul className="nav nav-tabs mb-4">
          <li className="nav-item">
            <button className={`nav-link${isLogin ? ' active' : ''}`} onClick={() => resetForm('login')}>
              Iniciar sesión
            </button>
          </li>
          <li className="nav-item">
            <button className={`nav-link${!isLogin ? ' active' : ''}`} onClick={() => resetForm('register')}>
              Registrarse
            </button>
          </li>
        </ul>

        {isLogin ? (
          <form onSubmit={handleLogin} aria-label="Formulario de login">
            <div className="mb-3">
              <label htmlFor="userId" className="form-label">Usuario</label>
              <input id="userId" type="text" value={userId} onChange={e => setUserId(e.target.value)}
                required autoFocus className="form-control" />
            </div>
            <div className="mb-3">
              <label htmlFor="password" className="form-label">Contraseña</label>
              <input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)}
                required className="form-control" />
            </div>
            <button type="submit" disabled={loading} className="btn btn-success w-100">
              {loading ? 'Ingresando...' : 'Ingresar'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} aria-label="Formulario de registro">
            <div className="mb-3">
              <label htmlFor="regUserId" className="form-label">Usuario</label>
              <input id="regUserId" type="text" value={userId} onChange={e => setUserId(e.target.value)}
                required autoFocus minLength={3} maxLength={50} className="form-control"
                placeholder="Mínimo 3 caracteres" />
            </div>
            <div className="mb-3">
              <label htmlFor="regPassword" className="form-label">Contraseña</label>
              <input id="regPassword" type="password" value={password} onChange={e => setPassword(e.target.value)}
                required minLength={6} className="form-control" placeholder="Mínimo 6 caracteres" />
            </div>
            <div className="mb-3">
              <label htmlFor="confirmPassword" className="form-label">Confirmar contraseña</label>
              <input id="confirmPassword" type="password" value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required className="form-control" />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary w-100">
              {loading ? 'Registrando...' : 'Crear cuenta'}
            </button>
          </form>
        )}

        {error && <div role="alert" className="alert alert-danger mt-3">{error}</div>}
        {success && <div role="alert" className="alert alert-success mt-3">{success}</div>}
        {loading && <Loader label={isLogin ? 'Verificando credenciales...' : 'Creando cuenta...'} />}
      </div>
    </main>
  );
}
