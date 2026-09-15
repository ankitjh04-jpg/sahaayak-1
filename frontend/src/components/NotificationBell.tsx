import {useEffect,useState} from 'react';
import {Link,useLocation,useNavigate} from 'react-router-dom';
import {Bell,CheckCheck,ArrowUpRight,RefreshCw} from 'lucide-react';
import {toast} from 'sonner';
import {useNotifications} from '../hooks/useNotifications';
import {useApp} from '../app/context';
export const NotificationBell=()=>{
 const {t}=useApp();const {items,unread,error,refresh,markRead,markAll}=useNotifications();const [open,setOpen]=useState(false);const navigate=useNavigate(),location=useLocation();
 useEffect(()=>setOpen(false),[location.pathname]);
 return <div className="notification-anchor"><button className={`icon-button notification-button ${open?'selected':''}`} data-testid="notifications-button" aria-label={t(`Notifications, ${unread} unread`,`सूचनाएँ, ${unread} अपठित`,`ਸੂਚਨਾਵਾਂ, ${unread} ਅਣਪੜ੍ਹੀਆਂ`)} aria-expanded={open} onClick={()=>{setOpen(!open);if(!open)refresh();}}><Bell size={19}/>{unread>0&&<span className="notification-count" data-testid="notification-unread-count">{unread>99?'99+':unread}</span>}</button>
 {open&&<div className="header-popover notification-popover" data-testid="notifications-panel"><div className="notification-heading"><h2>{t('Your updates','आपके अपडेट','ਤੁਹਾਡੇ ਅੱਪਡੇਟ')}</h2><button data-testid="notification-refresh" aria-label="Refresh notifications" className="icon-button" onClick={refresh}><RefreshCw size={15}/></button></div>
 {error&&<p role="alert" data-testid="notification-error">{error}</p>}
 {items.length===0?<p data-testid="notifications-empty">{t('No expert updates yet.','अभी कोई विशेषज्ञ अपडेट नहीं है।','ਅਜੇ ਕੋਈ ਮਾਹਰ ਅੱਪਡੇਟ ਨਹੀਂ ਹੈ।')}</p>:<div className="notification-list">{items.slice(0,5).map(item=><button key={item.id} data-testid={`notification-${item.id}`} className={`notification-item ${item.read_at?'':'unread'}`} onClick={async()=>{try{await markRead(item.id);}catch{toast.error('Could not mark this update as read.');}navigate(`/advisories/${item.advisory_id}`);}}><span><strong>{item.message}</strong><small>{item.question}</small><time>{new Date(item.created_at).toLocaleString()}</time></span><ArrowUpRight size={14}/></button>)}</div>}
 <div className="notification-footer">{unread>0&&<button data-testid="notifications-read-all" onClick={()=>markAll().catch(e=>toast.error(e.message))}><CheckCheck size={15}/>{t('Mark all read','सभी पढ़ा चिह्नित करें','ਸਭ ਪੜ੍ਹੀਆਂ ਕਰੋ')}</button>}<Link to="/notifications" data-testid="notification-history">{t('All updates','सभी अपडेट','ਸਾਰੇ ਅੱਪਡੇਟ')}<ArrowUpRight size={14}/></Link></div></div>}
 </div>;
};