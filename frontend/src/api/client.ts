const configuredOrigin = process.env.REACT_APP_BACKEND_URL;
const origin = process.env.NODE_ENV === 'development' ? '' : configuredOrigin;
if (process.env.NODE_ENV !== 'development' && !origin) throw new Error('REACT_APP_BACKEND_URL must be configured');
export const API = `${origin}/api/v1`;
export class ApiError extends Error { constructor(message: string, public status: number) { super(message); } }
export async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const token = localStorage.getItem('sahaayak-token');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !(options.body instanceof FormData)) headers.set('Content-Type', 'application/json');
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 25000);
  try {
    const response = await fetch(`${API}${path}`, { ...options, headers, signal: controller.signal });
    const body = await response.text();
    let data: any;
    try {
      data = body ? JSON.parse(body) : null;
    } catch {
      if (response.status === 502 || response.status === 503 || response.status === 504) {
        throw new ApiError('The backend service is unavailable. Start the local API server and try again.', response.status);
      }
      throw new ApiError(`The server returned an invalid response (${response.status}). Please refresh and try again.`, response.status);
    }
    if (!response.ok) {
      const message = Array.isArray(data.detail) ? data.detail.map((x: any) => x.msg).join('. ') : data.detail;
      throw new ApiError(message || 'Something went wrong. Please try again.', response.status);
    }
    return data;
  } finally { clearTimeout(timeout); }
}
export const post = <T = any>(path: string, body: unknown = {}) => api<T>(path, { method: 'POST', body: JSON.stringify(body) });
export async function downloadAttachment(id: string) {
 const response = await fetch(`${API}/uploads/${id}/content`, {headers: {Authorization: `Bearer ${localStorage.getItem('sahaayak-token')}`}});
 if (!response.ok) throw new Error('Attachment unavailable');
 const blob = await response.blob(); const url = URL.createObjectURL(blob); const a = document.createElement('a');
 a.href = url; a.download = `sahaayak-${id}.${blob.type.includes('pdf') ? 'pdf' : blob.type.split('/')[1] || 'bin'}`; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}