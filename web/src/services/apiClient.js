import { API_URL } from '../config/appConfig';
import { getToken } from '../util/tokenStorage';

async function request(path, { method = 'GET', body, auth = true, formData } = {}) {
  const headers = {};

  if (auth) {
    const token = getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  if (body) headers['Content-Type'] = 'application/json';

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: formData ?? (body ? JSON.stringify(body) : undefined),
  });

  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const error = await response.json();
      if (typeof error.detail === 'string') message = error.detail;
      else if (Array.isArray(error.detail)) {
        message = error.detail.map((e) => e.msg).join('. ');
      }
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(message);
  }

  return response.status === 204 ? null : response.json();
}

export const apiClient = {
  get: (path, options) => request(path, { ...options, method: 'GET' }),
  post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
  postForm: (path, formData, options) =>
    request(path, { ...options, method: 'POST', formData }),
  patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body }),
  put: (path, body, options) => request(path, { ...options, method: 'PUT', body }),
  delete: (path, options) => request(path, { ...options, method: 'DELETE' }),
};
