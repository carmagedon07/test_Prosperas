import React from 'react';

export default function Loader({ label = 'Cargando...' }) {
  return (
    <div role="status" aria-live="polite" style={{ textAlign: 'center', padding: '2em' }}>
      <span aria-hidden="true" style={{ fontSize: '2em' }}>⏳</span>
      <div>{label}</div>
    </div>
  );
}
