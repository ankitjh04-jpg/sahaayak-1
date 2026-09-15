import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';
import { demoLogin, Session } from '../api/auth';
import { User, Language } from '../types';

interface Context { user: User | null; loading: boolean; error: string; language: Language; setLanguage: (l: Language) => void; accept: (session: Session) => void; switchRole: (role: 'farmer' | 'expert') => Promise<void>; logout: () => Promise<void>; t: (en: string, hi?: string, pa?: string) => string }
const AppContext = createContext<Context>(null!);
export const useApp = () => useContext(AppContext);
export const AppProvider = ({ children }: { children: React.ReactNode }) => {
 const [user, setUser] = useState<User | null>(null), [loading, setLoading] = useState(true), [error, setError] = useState('');
 const [language, updateLanguage] = useState<Language>((localStorage.getItem('sahaayak-language') as Language) || 'en');
 const accept = (s: Session) => { localStorage.setItem('sahaayak-token', s.access_token); localStorage.setItem('sahaayak-user', JSON.stringify(s.user)); sessionStorage.removeItem('sahaayak-signed-out'); setUser(s.user); setError(''); };
 const setLanguage = (l: Language) => { updateLanguage(l); localStorage.setItem('sahaayak-language', l); document.documentElement.lang = l; };
 useEffect(() => { (async () => { try {
   if (localStorage.getItem('sahaayak-token')) { const me = await api<User>('/me'); setUser(me); localStorage.setItem('sahaayak-user', JSON.stringify(me)); }
   else if (!sessionStorage.getItem('sahaayak-signed-out') && window.location.pathname === '/') {const config=await api('/config');if(config.demo_mode)accept(await demoLogin('farmer'));}
 } catch (e: any) {
   if (!navigator.onLine && localStorage.getItem('sahaayak-user')) setUser(JSON.parse(localStorage.getItem('sahaayak-user')!));
   else { localStorage.removeItem('sahaayak-token'); setError(e.message); }
 } finally { setLoading(false); } })(); }, []);
 const switchRole = async (role: 'farmer' | 'expert') => {if(role==='expert')throw new Error('Expert access requires email and password');accept(await demoLogin('farmer'));};
 const logout = async () => { try { await api('/auth/logout', {method: 'POST'}); } finally { localStorage.removeItem('sahaayak-token'); localStorage.removeItem('sahaayak-user'); sessionStorage.setItem('sahaayak-signed-out', 'true'); setUser(null); } };
 return <AppContext.Provider value={{ user, loading, error, language, setLanguage, accept, switchRole, logout, t: (en, hi, pa) => language === 'hi' ? hi || en : language === 'pa' ? pa || en : en }}>{children}</AppContext.Provider>;
};