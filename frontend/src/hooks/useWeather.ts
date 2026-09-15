import {useCallback,useEffect,useRef,useState} from 'react';
import {api} from '../api/client';
export interface Weather {status:string;provider:string;location:string;temperature:number|null;humidity:number|null;precipitation:number|null;precipitation_interval_seconds?:number;wind_speed:number|null;condition?:string;observed_at:string|null;fetched_at?:string;stale:boolean;reason?:string;source_kind?:string;attribution?:string}
export function useWeather(query=''){
 const [data,setData]=useState<Weather|null>(null),[loading,setLoading]=useState(true),[error,setError]=useState('');const sequence=useRef(0);
 const refresh=useCallback(async()=>{const request=++sequence.current;setLoading(true);try{const result=await api<Weather>(`/weather${query?'?'+query:''}`);if(request===sequence.current){setData(result);setError('');}}catch(e:any){if(request===sequence.current)setError(navigator.onLine?e.message:'Offline · weather cannot be refreshed.');}finally{if(request===sequence.current)setLoading(false);}},[query]);
 useEffect(()=>{setData(null);refresh();const interval=setInterval(()=>navigator.onLine&&document.visibilityState==='visible'&&refresh(),600000);window.addEventListener('online',refresh);return()=>{sequence.current++;clearInterval(interval);window.removeEventListener('online',refresh);};},[refresh]);
 return {data,loading,error,refresh};
}