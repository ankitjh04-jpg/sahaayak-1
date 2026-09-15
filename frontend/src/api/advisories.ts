import { api, post } from './client';
import { Advisory, Submission } from '../types';
export const getAdvisories = () => api<Advisory[]>('/advisories');
export const getAdvisory = (id: string) => api<Advisory>(`/advisories/${id}`);
export const createAdvisory = (body: Submission) => post<{ advisory_id: string; job_id: string; status: string }>('/advisories', body);
export async function uploadFile(file: File) { const form = new FormData(); form.append('file', file); return api<{ id: string; duplicate?: boolean }>('/uploads', { method: 'POST', body: form }); }