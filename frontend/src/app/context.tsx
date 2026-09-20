import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../api/client';
import { demoLogin, Session } from '../api/auth';
import { User, Language } from '../types';
import { DICTIONARY } from '../i18n/dictionary';

interface Context { user: User | null; loading: boolean; error: string; language: Language; setLanguage: (l: Language) => void; accept: (session: Session) => void; switchRole: (role: 'farmer' | 'expert') => Promise<void>; logout: () => Promise<void>; t: (en: string, hi?: string, pa?: string, or?: string) => string }
const AppContext = createContext<Context>(null!);
export const useApp = () => useContext(AppContext);
export const AppProvider = ({ children }: { children: React.ReactNode }) => {
 const [user, setUser] = useState<User | null>(null), [loading, setLoading] = useState(true), [error, setError] = useState('');
 const [language, updateLanguage] = useState<Language>(() => { const stored = localStorage.getItem('sahaayak-language'); return stored === 'hi' || stored === 'pa' || stored === 'or' ? stored : 'en'; });
 const accept = (s: Session) => { localStorage.setItem('sahaayak-token', s.access_token); localStorage.setItem('sahaayak-user', JSON.stringify(s.user)); sessionStorage.removeItem('sahaayak-signed-out'); setUser(s.user); setError(''); };
 const setLanguage = (l: Language) => { updateLanguage(l); localStorage.setItem('sahaayak-language', l); document.documentElement.lang = l; };
 useEffect(() => { document.documentElement.lang = language; }, [language]);
 useEffect(() => { (async () => { try {
  const token=localStorage.getItem('sahaayak-token');
  if (token?.startsWith('demo-local-')) { const saved=localStorage.getItem('sahaayak-user'); if (saved) setUser(JSON.parse(saved)); }
  else if (token) { const me = await api<User>('/me'); setUser(me); localStorage.setItem('sahaayak-user', JSON.stringify(me)); }
 } catch (e: any) {
   if (!navigator.onLine && localStorage.getItem('sahaayak-user')) setUser(JSON.parse(localStorage.getItem('sahaayak-user')!));
   else { localStorage.removeItem('sahaayak-token'); setError(e.message); }
 } finally { setLoading(false); } })(); }, []);
 const switchRole = async (role: 'farmer' | 'expert') => {if(role==='expert')throw new Error('Expert access requires email and password');accept(await demoLogin('farmer'));};
 const logout = async () => { try { await api('/auth/logout', {method: 'POST'}); } finally { localStorage.removeItem('sahaayak-token'); localStorage.removeItem('sahaayak-user'); sessionStorage.setItem('sahaayak-signed-out', 'true'); setUser(null); } };
 return <AppContext.Provider value={{ user, loading, error, language, setLanguage, accept, switchRole, logout, t: (en, hi, pa, or) => { const entry = DICTIONARY[en]; if (language === 'hi') return hi || entry?.hi || en; if (language === 'pa') return pa || entry?.pa || en; if (language === 'or') return or || entry?.or || en; return en; } }}>{children}</AppContext.Provider>;
};