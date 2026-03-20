
import React, { useState } from 'react';

export default function JobForm({ onSubmit, loading }) {
  const [showModal, setShowModal] = useState(false);
  const [reportType, setReportType] = useState('ventas');
  const [format, setFormat] = useState('pdf');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [error, setError] = useState('');

  const handleOpenModal = () => {
    setShowModal(true);
    setError('');
  };
  
  const handleCloseModal = () => {
    setShowModal(false);
    setStartDate('');
    setEndDate('');
    setError('');
  };

  const handleSubmit = e => {
    e.preventDefault();
    setError('');
    
    if (!startDate || !endDate) {
      setError('Ambas fechas son obligatorias');
      return;
    }
    
    if (new Date(startDate) > new Date(endDate)) {
      setError('La fecha de inicio no puede ser mayor que la fecha fin');
      return;
    }
    
    const dateRange = `${startDate} to ${endDate}`;
    onSubmit({ reportType, dateRange, format });
    setShowModal(false);
    setStartDate('');
    setEndDate('');
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
              <div style={{ marginBottom: '1em' }}>
                <label htmlFor="reportType">Tipo de reporte:</label>
                <select
                  id="reportType"
                  value={reportType}
                  onChange={e => setReportType(e.target.value)}
                  style={{ margin: '0 1em', width: '100%', marginTop: '0.5em' }}
                  aria-required="true"
                  className="form-control"
                >
                  <option value="ventas">Ventas</option>
                  <option value="inventario">Inventario</option>
                  <option value="clientes">Clientes</option>
                </select>
              </div>

              <div style={{ marginBottom: '1em' }}>
                <label htmlFor="startDate">Fecha de inicio: *</label>
                <input
                  type="date"
                  id="startDate"
                  value={startDate}
                  onChange={e => setStartDate(e.target.value)}
                  required
                  className="form-control"
                  style={{ marginTop: '0.5em' }}
                  aria-required="true"
                />
              </div>

              <div style={{ marginBottom: '1em' }}>
                <label htmlFor="endDate">Fecha fin: *</label>
                <input
                  type="date"
                  id="endDate"
                  value={endDate}
                  onChange={e => setEndDate(e.target.value)}
                  required
                  className="form-control"
                  style={{ marginTop: '0.5em' }}
                  aria-required="true"
                />
              </div>

              <div style={{ marginBottom: '1em' }}>
                <label htmlFor="format">Formato:</label>
                <select
                  id="format"
                  value={format}
                  onChange={e => setFormat(e.target.value)}
                  style={{ marginTop: '0.5em', width: '100%' }}
                  aria-required="true"
                  className="form-control"
                >
                  <option value="pdf">PDF</option>
                  <option value="xlsx">Excel (XLSX)</option>
                  <option value="csv">CSV</option>
                </select>
              </div>

              {error && <div className="alert alert-danger" role="alert">{error}</div>}

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
