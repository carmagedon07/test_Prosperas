
import React, { useState } from 'react';

export default function JobForm({ onSubmit, loading }) {
  const [reportType, setReportType] = useState('ventas');
  const [dateRange, setDateRange] = useState('');
  const [format, setFormat] = useState('pdf');

  const handleSubmit = e => {
    e.preventDefault();
    onSubmit({ reportType, dateRange, format });
  };

  return (
    <form onSubmit={handleSubmit} aria-label="Formulario de nuevo reporte" style={{ marginBottom: '2em' }}>
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

      <label htmlFor="dateRange" style={{ marginLeft: '1em' }}>Rango de fechas:</label>
      <input
        id="dateRange"
        type="text"
        placeholder="YYYY-MM-DD a YYYY-MM-DD"
        value={dateRange}
        onChange={e => setDateRange(e.target.value)}
        style={{ margin: '0 1em' }}
        aria-required="true"
      />

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

      <button type="submit" disabled={loading} aria-busy={loading}>
        {loading ? 'Creando...' : 'Crear reporte'}
      </button>
    </form>
  );
}
