import {useCallback,useEffect,useRef,useState} from 'react';
import {toast} from 'sonner';
import {api,post} from '../api/client';
import {useApp} from '../app/context';
export interface FarmerNotification {id:string;advisory_id:string;title:string;message:string;question:string;crop:string;input_type:string;created_at:string;read_at:string|null;status:string}
export function useNotifications(){
 const {user}=useApp();const [items,setItems]=useState<FarmerNotification[]>([]),[unread,setUnread]=useState(0),[error,setError]=useState('');const known=useRef<Set<string>|null>(null);
 const refresh=useCallback(async()=>{
  if(!user||!navigator.onLine)return;
  try{const response=await api<{items:FarmerNotification[];unread_count:number}>('/notifications');
   if(known.current){const additions=response.items.filter(n=>!known.current!.has(n.id)&&!n.read_at);if(additions.length)toast.success(additions.length===1?additions[0].message:`${additions.length} new expert updates`);}
   known.current=new Set(response.items.map(n=>n.id));setItems(response.items);setUnread(response.unread_count);setError('');
  }catch(e:any){setError(e.message);}
 },[user?.id]);
 useEffect(()=>{known.current=null;setItems([]);setUnread(0);refresh();const timer=setInterval(()=>{if(document.visibilityState==='visible')refresh();},15000);window.addEventListener('online',refresh);window.addEventListener('notifications-updated',refresh);const visible=()=>{if(document.visibilityState==='visible')refresh();};document.addEventListener('visibilitychange',visible);return()=>{clearInterval(timer);window.removeEventListener('online',refresh);window.removeEventListener('notifications-updated',refresh);document.removeEventListener('visibilitychange',visible);};},[refresh]);
 const markRead=async(id:string)=>{await post(`/notifications/${id}/read`);await refresh();window.dispatchEvent(new Event('notifications-updated'));};
 const markAll=async()=>{await post('/notifications/read-all');await refresh();window.dispatchEvent(new Event('notifications-updated'));};
 return {items,unread,error,refresh,markRead,markAll};
}