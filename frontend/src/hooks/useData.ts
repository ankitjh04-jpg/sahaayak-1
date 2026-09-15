import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import { useApp } from '../app/context';
export function useData<T>(path: string, initial: T) {
 const { user } = useApp(); const key = `sahaayak-cache:${user?.id}:${path}`;
 const [data, setData] = useState<T>(() => { try {return JSON.parse(localStorage.getItem(key) || 'null') || initial;} catch {return initial;} });
 const [loading, setLoading] = useState(true), [error, setError] = useState('');
 const refresh = useCallback(async () => { setLoading(true); setError(''); try { const result = await api<T>(path); setData(result); localStorage.setItem(key, JSON.stringify(result)); } catch (e: any) { setError(navigator.onLine ? e.message : 'Offline · showing saved information'); } finally { setLoading(false); } }, [path, key]);
 useEffect(() => {refresh();}, [refresh]);
 return { data, loading, error, refresh, setData };
}