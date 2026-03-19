import React from 'react';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  return (
    <nav style={{ background: '#222', color: '#fff', padding: '1em', display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end' }}>
      {user && (
        <span style={{ display: 'flex', alignItems: 'center', gap: '1em', fontSize: '1em' }}>
          Usuario: <strong>{user.sub}</strong>
          <button onClick={logout} className="btn btn-outline-light btn-sm" style={{ marginLeft: 0 }}>Cerrar sesión</button>
        </span>
      )}
    </nav>
  );
}
