import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <nav style={{ background: '#222', color: '#fff', padding: '1em', display: 'flex', justifyContent: 'space-between' }}>
      <span style={{ fontWeight: 'bold' }}>Procesamiento de Reportes</span>
      {user && (
        <span>
          Usuario: <strong>{user.sub}</strong> <button onClick={logout} style={{ marginLeft: '1em' }}>Cerrar sesión</button>
        </span>
      )}
    </nav>
  );
}
