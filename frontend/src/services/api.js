const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function login(user_id, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id, password })
  });
  if (!res.ok) {
    let message = 'Error de autenticación';
    try {
      const data = await res.json();
      if (data && data.detail) message = data.detail;
    } catch {}
    throw new Error(message);
  }
  return res.json();
}

export async function createJob(token, report_type, date_range, format) {
  const res = await fetch(`${API_URL}/jobs`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ report_type, date_range, format })
  });
  if (!res.ok) throw new Error('Error al crear el job');
  return res.json();
}

export async function getJobs(token, limit = 20, offset = 0) {
  const res = await fetch(`${API_URL}/jobs?limit=${limit}&offset=${offset}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) {
    const error = new Error('Error al obtener los jobs');
    error.status = res.status;
    throw error;
  }
  return res.json();
}

export async function getJobById(token, job_id) {
  const res = await fetch(`${API_URL}/jobs/${job_id}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) {
    const error = new Error(res.status === 404 ? 'Job not found' : 'Error al obtener el job');
    error.status = res.status;
    throw error;
  }
  return res.json();
}

export async function deleteAllJobs(token) {
  const res = await fetch(`${API_URL}/jobs`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  if (!res.ok) {
    const error = new Error('Error al eliminar los jobs');
    error.status = res.status;
    throw error;
  }
  return res.json();
}
