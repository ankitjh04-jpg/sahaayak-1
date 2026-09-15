import { useEffect,useState } from 'react';
import { useLocation } from 'react-router-dom';
import { CheckCircle2,X } from 'lucide-react';
import { useApp } from '../app/context';
export const OfflineSyncStatus=()=>{
 const {user,t}=useApp();const location=useLocation();
 const key=`sahaayak-last-sync:${user?.id}`;
 const [synced,setSynced]=useState<{owner:string;count:number;time:string}|null>(null);
 useEffect(()=>{const load=()=>{try{setSynced(JSON.parse(localStorage.getItem(key)||'null'));}catch{setSynced(null);}};load();window.addEventListener('queue-synced',load);return()=>window.removeEventListener('queue-synced',load);},[key]);
 if(location.pathname!=='/history'||!synced||synced.owner!==user?.id)return null;
 return <div className="notice sync-confirmation" data-testid="offline-sync-success"><CheckCircle2 size={18}/><div><strong>{synced.count} {t('saved submission(s) synced','सहेजे गए अनुरोध सिंक हुए','ਸੰਭਾਲੇ ਬੇਨਤੀ ਸਿੰਕ ਹੋਏ')}</strong><p>{t('Your offline observations are now in your advisory history.','आपके ऑफलाइन निरीक्षण अब सलाह इतिहास में हैं।','ਤੁਹਾਡੇ ਆਫਲਾਈਨ ਨਿਰੀਖਣ ਹੁਣ ਸਲਾਹ ਇਤਿਹਾਸ ਵਿੱਚ ਹਨ।')} · {new Date(synced.time).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})}</p></div><button className="icon-button" aria-label="Dismiss sync confirmation" data-testid="dismiss-sync-confirmation" onClick={()=>{localStorage.removeItem(key);setSynced(null);}}><X size={15}/></button></div>;
};