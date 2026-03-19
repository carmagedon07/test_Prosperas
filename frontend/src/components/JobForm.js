
import React, { useState } from 'react';

export default function JobForm({ onSubmit, loading }) {
  const [showModal, setShowModal] = useState(false);
  const [reportType, setReportType] = useState('ventas');
  const [format, setFormat] = useState('pdf');

  const handleOpenModal = () => setShowModal(true);
  const handleCloseModal = () => setShowModal(false);

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit({ reportType, format });
    setShowModal(false);
  };

  return (
    <>
      <button type="button" onClick={handleOpenModal} disabled={loading} aria-busy={loading} className="btn btn-success">
        Solicitud de reporte
      </button>
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: '2em', borderRadius: '8px', minWidth: '300px', boxShadow: '0 2px 8px rgba(0,0,0,0.2)' }}>
            <h2>Solicitar reporte</h2>
            <form onSubmit={handleSubmit} aria-label="Formulario de solicitud de reporte">
              <label htmlFor="reportType">Tipo de reporte:</label>
              <select
                id="reportType"
                value={reportType}
                onChange={e => setReportType(e.target.value)}
                style={{ margin: '0 1em' }}
                aria-required="true"
              >
                <option value="ventas">Ventas</option>
                <option value="inventario">Inventario</option>
                <option value="clientes">Clientes</option>
              </select>

              <label htmlFor="format" style={{ marginLeft: '1em' }}>Formato:</label>
              <select
                id="format"
                value={format}
                onChange={e => setFormat(e.target.value)}
                style={{ margin: '0 1em' }}
                aria-required="true"
              >
                <option value="pdf">PDF</option>
                <option value="xlsx">Excel (XLSX)</option>
                <option value="csv">CSV</option>
              </select>

              <div style={{ marginTop: '1.5em', display: 'flex', justifyContent: 'flex-end', gap: '1em' }}>
                <button type="button" onClick={handleCloseModal} className="btn btn-danger">Cancelar</button>
                <button type="submit" disabled={loading} aria-busy={loading} className="btn btn-success">
                  {loading ? 'Solicitando...' : 'Solicitar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
