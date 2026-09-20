import {useEffect,useState} from 'react';
import {NavLink,Link,Outlet,useLocation,useNavigate} from 'react-router-dom';
import {LayoutDashboard,Sprout,MessageSquarePlus,History,BookOpen,ArrowLeftRight,ChevronDown,Globe2,LogOut,WifiOff,ArrowUpRight,MapPin} from 'lucide-react';
import {toast} from 'sonner';
import {useApp} from '../app/context';
import {Brand} from './shared';
import {readQueue,syncQueue} from '../hooks/offline';
import {Language} from '../types';
import {OfflineSyncStatus} from './OfflineSyncStatus';
import {NotificationBell} from './NotificationBell';

export const Layout=()=>{
 const {user,language,setLanguage,t,logout}=useApp();const location=useLocation(),navigate=useNavigate();
 const [online,setOnline]=useState(navigator.onLine),[queued,setQueued]=useState(0),[profile,setProfile]=useState(false);
 const isExpert=user?.role==='expert';
 useEffect(()=>{
  const update=async()=>{setOnline(navigator.onLine);setQueued((await readQueue()).filter(q=>q.owner===user?.id).length);};
  const sync=async()=>{await update();if(navigator.onLine&&user){const n=await syncQueue(user.id);if(n)toast.success(`${n} saved submission${n>1?'s':''} synced`);}};
  sync();window.addEventListener('online',sync);window.addEventListener('offline',update);window.addEventListener('queue-change',update);
  return()=>{window.removeEventListener('online',sync);window.removeEventListener('offline',update);window.removeEventListener('queue-change',update);};
 },[user]);
 useEffect(()=>{window.scrollTo(0,0);setProfile(false);},[location.pathname]);
 const nav=isExpert?[{to:'/expert',icon:LayoutDashboard,label:t('Review workspace','समीक्षा कार्यक्षेत्र','ਸਮੀਖਿਆ ਵਰਕਸਪੇਸ')},{to:'/knowledge',icon:BookOpen,label:t('Knowledge library','ज्ञान पुस्तकालय','ਗਿਆਨ ਲਾਇਬ੍ਰੇਰੀ')}]:[{to:'/',icon:LayoutDashboard,label:t('Overview','अवलोकन','ਸੰਖੇਪ')},{to:'/fields',icon:Sprout,label:t('My fields','मेरे खेत','ਮੇਰੇ ਖੇਤ')},{to:'/advisories/new',icon:MessageSquarePlus,label:t('New advisory','नई सलाह','ਨਵੀਂ ਸਲਾਹ')},{to:'/history',icon:History,label:t('Advisory history','सलाह का इतिहास','ਸਲਾਹ ਇਤਿਹਾਸ')}];
 const onSwitch=()=>navigate(isExpert?'/login':'/expert/login');
 return <div className="app-shell"><aside className="sidebar"><Brand light/>
  <div className="workspace-label">{t('YOUR WORKSPACE','आपका कार्यक्षेत्र','ਤੁਹਾਡਾ ਵਰਕਸਪੇਸ')}</div>
  <nav className="side-nav">{nav.map(n=><NavLink key={n.to} to={n.to} end className={({isActive})=>isActive?'active':''} data-testid={`nav-${n.to==='/'?'overview':n.to.replace(/\//g,'-').slice(1)}`}><n.icon size={19}/>{n.label}{n.to==='/advisories/new'&&<span className="nav-plus">+</span>}</NavLink>)}</nav>
  <div className="sidebar-rule"/>{!isExpert&&<><Link to="/location" className="library-link" data-testid="nav-location"><MapPin size={18}/>{t('Map & weather','नक्शा और मौसम','ਨਕਸ਼ਾ ਅਤੇ ਮੌਸਮ')}<ArrowUpRight size={14}/></Link><Link to="/knowledge" className="library-link" data-testid="nav-knowledge"><BookOpen size={18}/>{t('Knowledge library','ज्ञान पुस्तकालय','ਗਿਆਨ ਲਾਇਬ੍ਰੇਰੀ')}<ArrowUpRight size={14}/></Link></>}
  <div className="sidebar-bottom"><div className="sidebar-quote"><Sprout size={30}/><p>{t('Rooted in knowledge.','ज्ञान से जुड़ें।','ਗਿਆਨ ਨਾਲ ਜੁੜੇ।')}<br/><em>{t('Growing with you.','आपके साथ बढ़ें।','ਤੁਹਾਡੇ ਨਾਲ ਵਧਦੇ।')}</em></p></div><button className="switch-role" data-testid="switch-role" onClick={onSwitch}><ArrowLeftRight size={16}/>{isExpert?t('Farmer sign-in','किसान साइन-इन','ਕਿਸਾਨ ਸਾਈਨ-ਇਨ'):t('Expert sign-in','विशेषज्ञ साइन-इन','ਮਾਹਰ ਸਾਈਨ-ਇਨ')}<ArrowUpRight size={14}/></button><div className="demo-marker" data-testid="demo-mode"><span/>SIH WORKSPACE<span className="demo-version">v1.1</span></div></div>
 </aside><div className="main-shell"><header className="topbar">
  <div className="breadcrumb" data-testid="breadcrumb"><span>Sahaayak</span><span>/</span>{nav.find(n=>n.to===location.pathname)?.label||t('Your farming companion','आपका कृषि साथी','ਤੁਹਾਡਾ ਖੇਤੀ ਸਾਥੀ')}</div><Link to="/" className="mobile-brand" data-testid="mobile-brand"><Sprout size={23}/>Sahaayak</Link>
  <div className="topbar-actions"><div className="language-control"><Globe2 size={16}/><select data-testid="language-selector" aria-label="Language" value={language} onChange={e=>setLanguage(e.target.value as Language)}><option value="en" label="English"/><option value="hi" label="हिन्दी"/><option value="pa" label="ਪੰਜਾਬੀ"/><option value="or" label="ଓଡ଼ିଆ"/></select><ChevronDown size={12}/></div><div className="topbar-divider"/>{!isExpert&&<NotificationBell/>}<button className="avatar" data-testid="profile-button" aria-label="Account menu" onClick={()=>setProfile(!profile)}>{user?.profile.name.split(' ').map(x=>x[0]).slice(0,2).join('')}</button></div>
  {profile&&<div className="header-popover" data-testid="profile-menu"><strong data-testid="profile-name">{user?.profile.name}</strong><small data-testid="profile-phone">{(user as any)?.email||user?.phone} · {user?.role}</small>{!isExpert&&<Link to="/location" data-testid="profile-location"><MapPin size={16}/>{t('Map & weather','नक्शा और मौसम','ਨਕਸ਼ਾ ਅਤੇ ਮੌਸਮ')}</Link>}<button data-testid="profile-switch-role" onClick={onSwitch}><ArrowLeftRight size={16}/>{isExpert?'Farmer sign-in':'Expert sign-in'}</button><button data-testid="logout-button" onClick={async()=>{try{await logout();}catch{}navigate(isExpert?'/expert/login':'/login');}}><LogOut size={16}/>{t('Sign out','साइन आउट','ਸਾਈਨ ਆਉਟ')}</button></div>}
 </header>{(!online||queued>0)&&<div className="offline-banner" data-testid="offline-banner"><WifiOff size={16}/>{!online?t('You’re offline. Your submissions will be saved on this device.','आप ऑफलाइन हैं। आपकी जानकारी इस डिवाइस पर सहेजी जाएगी।','ਤੁਸੀਂ ਆਫਲਾਈਨ ਹੋ। ਜਾਣਕਾਰੀ ਇਸ ਡਿਵਾਈਸ ਤੇ ਸੁਰੱਖਿਅਤ ਹੋਵੇਗੀ।'):`${queued} submission(s) waiting to sync`}<Link to="/history" data-testid="offline-queue-link">{queued} queued</Link></div>}
 <main className="main-content"><OfflineSyncStatus/><Outlet/></main><footer className="app-footer"><span><Sprout size={14}/>{t('A little knowledge. A better harvest.','थोड़ा ज्ञान। बेहतर फसल।','ਥੋੜ੍ਹਾ ਗਿਆਨ। ਵਧੀਆ ਫ਼ਸਲ।')}</span><span data-testid="demo-disclosure">SIH26131 <i>·</i>{t('Cited guidance · Human review','उद्धृत मार्गदर्शन · मानवीय समीक्षा','ਹਵਾਲਾ ਮਾਰਗਦਰਸ਼ਨ · ਮਨੁੱਖੀ ਸਮੀਖਿਆ')}</span></footer></div>
 <nav className="mobile-nav">{nav.slice(0,4).map(n=><NavLink key={n.to} to={n.to} end data-testid={`mobile-nav-${n.to.replace(/\//g,'-')}`}><n.icon size={21}/><span>{n.to==='/history'?t('History','इतिहास','ਇਤਿਹਾਸ'):n.to==='/advisories/new'?t('Ask','पूछें','ਪੁੱਛੋ'):n.label}</span></NavLink>)}</nav></div>;
};