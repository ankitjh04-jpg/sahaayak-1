import { post } from './client';
import { User, Language } from '../types';
export interface Session { access_token: string; user: User }
export const demoLogin = (role: 'farmer' | 'expert') => post<Session>('/auth/demo', { role });
export const localDemoLogin = (name: string): Session => ({
 access_token: `demo-local-${Date.now()}`,
 user: {id: 'demo-local-farmer', phone: '+919876543210', role: 'farmer', language: 'en', profile: {name, location: 'Ludhiana, Punjab'}},
});
export const requestOtp = (phone: string, language: Language, name?: string) => post('/auth/otp/request', { phone, language, ...(name === undefined ? {} : {name}) });
export const verifyOtp = (phone: string, code: string, language: Language) => post<Session>('/auth/otp/verify', { phone, code, language });