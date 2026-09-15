import React from 'react';
import { BrowserRouter,Routes,Route,Navigate,Outlet,Link } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AppProvider,useApp } from './app/context';
import { Layout } from './components/Layout';
import { Loading } from './components/shared';
import LoginPage from './pages/LoginPage';
import FarmerDashboard from './pages/FarmerDashboard';
import FieldsPage from './pages/FieldsPage';
import NewAdvisoryPage from './pages/NewAdvisoryPage';
import AdvisoryResultPage from './pages/AdvisoryResultPage';
import HistoryPage from './pages/HistoryPage';
import ExpertDashboard from './pages/ExpertDashboard';
import CaseReviewPage from './pages/CaseReviewPage';
import KnowledgePage from './pages/KnowledgePage';
import ExpertLoginPage from './pages/ExpertLoginPage';
import NotificationsPage from './pages/NotificationsPage';
import LocationPage from './pages/LocationPage';
import './styles/tokens.css';
import './styles/global.css';
import './styles/identity-camera.css';
import './styles/connected-features.css';
import { registerOfflineShell } from './app/offlineRegistration';
window.addEventListener('load', registerOfflineShell, {once:true});
document.title = 'Sahaayak — Your farming companion';
const Guard=({role}:{role?:string})=>{const {user,loading}=useApp();if(loading)return <div className="app-boot"><Loading/></div>;if(!user)return <Navigate to={role==='expert'?'/expert/login':'/login'} replace/>;if(role&&user.role!==role)return <Navigate to={role==='expert'?'/expert/login':'/'} replace/>;return <Outlet/>;};
class ErrorBoundary extends React.Component<{children:React.ReactNode},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true};}render(){return this.state.failed?<div className="empty-state" data-testid="app-error"><h1>Let’s try that again.</h1><p>Your saved information is safe.</p><button className="btn primary" data-testid="app-reload" onClick={()=>window.location.reload()}>Reload workspace</button></div>:this.props.children;}}
export default function App(){return <ErrorBoundary><AppProvider><BrowserRouter><Routes>
 <Route path="/login" element={<LoginPage/>}/><Route path="/expert/login" element={<ExpertLoginPage/>}/>
 <Route element={<Guard/>}><Route element={<Layout/>}>
  <Route element={<Guard role="farmer"/>}><Route index element={<FarmerDashboard/>}/><Route path="fields" element={<FieldsPage/>}/><Route path="fields/:id" element={<FieldsPage/>}/><Route path="advisories/new" element={<NewAdvisoryPage/>}/><Route path="advisories/:id" element={<AdvisoryResultPage/>}/><Route path="history" element={<HistoryPage/>}/><Route path="location" element={<LocationPage/>}/><Route path="notifications" element={<NotificationsPage/>}/></Route>
  <Route element={<Guard role="expert"/>}><Route path="expert" element={<ExpertDashboard/>}/><Route path="expert/cases/:id" element={<CaseReviewPage/>}/></Route><Route path="knowledge" element={<KnowledgePage/>}/><Route path="*" element={<div className="empty-state" data-testid="not-found"><h1>A little off the path.</h1><Link className="btn primary" to="/" data-testid="not-found-home">Back to your farm →</Link></div>}/>
 </Route></Route></Routes><Toaster position="bottom-right" richColors closeButton/></BrowserRouter></AppProvider></ErrorBoundary>;}