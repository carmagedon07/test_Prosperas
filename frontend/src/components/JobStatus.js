import React from 'react';
import styles from '../styles/JobStatus.module.css';

const statusMap = {
  PENDING: { colorClass: styles['status-pending'], icon: '⏳', label: 'Pendiente' },
  PROCESSING: { colorClass: styles['status-processing'], icon: '🔄', label: 'Procesando' },
  COMPLETED: { colorClass: styles['status-completed'], icon: '✅', label: 'Completado' },
  FAILED: { colorClass: styles['status-failed'], icon: '❌', label: 'Fallido' },
};

export default function JobStatus({ status }) {
  const { colorClass, icon, label } = statusMap[status] || {};
  return (
    <span className={`${styles.status} ${colorClass}`} aria-label={label} role="status">
      <span className={styles.icon} aria-hidden="true">{icon}</span>
      {label}
    </span>
  );
}
