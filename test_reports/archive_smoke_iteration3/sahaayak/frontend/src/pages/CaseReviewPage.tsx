import { useEffect,useState } from 'react';
import { Link,useParams } from 'react-router-dom';
import { ArrowLeft,ShieldCheck,Loader2,CheckCircle2 } from 'lucide-react';
import { toast } from 'sonner';
import { useApp } from '../app/context';
import { useData } from '../hooks/useData';
import { Advisory,Source } from '../types';
import { post } from '../api/client';
import { PageHeading,StatusBadge,Loading,ErrorNotice } from '../components/shared';
import { AdvisoryContent } from '../components/AdvisoryContent';
import { Button } from '../components/ui/button';

export default function CaseReviewPage(){
 const {id}=useParams();const {t}=useApp();
 const {data:item,loading,error,refresh}=useData<Advisory|null>(`/advisories/${id}`,null);
 const {data:sources}=useData<Source[]>('/knowledge-sources',[]);
 const [decision,setDecision]=useState('validated'),[recommendation,setRecommendation]=useState(''),[rationale,setRationale]=useState(''),[source,setSource]=useState(''),[busy,setBusy]=useState(false),[reviewError,setReviewError]=useState('');
 useEffect(()=>{if(item)setRecommendation(item.expert_recommendation||item.recommendation?.steps.join('\n\n')||'');},[item]);
 const submit=async(e:React.FormEvent)=>{e.preventDefault();setBusy(true);setReviewError('');try{await post(`/expert/cases/${id}/review`,{decision,recommendation,rationale,source_id:source||sources[0]?.id});toast.success('Review saved with an audit trail.');refresh();}catch(e:any){setReviewError(e.message);}finally{setBusy(false);}};
 if(loading&&!item)return <Loading/>;
 if(!item)return <ErrorNotice message={error||'Case not found'}/>;
 return <>
  <Link className="back-link" data-testid="review-back" to="/expert"><ArrowLeft size={15}/>{t('Back to review queue','समीक्षा कतार पर वापस जाएँ','ਸਮੀਖਿਆ ਕਤਾਰ ਤੇ ਵਾਪਸ ਜਾਓ')}</Link>
  <PageHeading eyebrow={`${item.crop.toUpperCase()} · ${item.location.toUpperCase()}`} title={t('A careful second look.','एक सावधान दूसरी नज़र।','ਇੱਕ ਧਿਆਨ ਨਾਲ ਦੂਜੀ ਨਜ਼ਰ।')} description={`${item.farmer_name} · ${item.field_name}`} action={<StatusBadge status={item.status} id="review"/>}/>
  <ErrorNotice message={error}/>
  <div className="case-review-grid"><div><AdvisoryContent item={item}/></div><aside className="review-form-panel">
   {item.status==='verified'?<div className="review-complete" data-testid="review-complete"><CheckCircle2 size={35}/><h2>{t('Care, verified.','देखभाल, सत्यापित।','ਦੇਖਭਾਲ, ਤਸਦੀਕ।')}</h2><p>{t('This decision has been saved to the audit trail.','यह निर्णय ऑडिट रिकॉर्ड में सहेजा गया है।','ਇਹ ਫੈਸਲਾ ਆਡਿਟ ਰਿਕਾਰਡ ਵਿੱਚ ਸੰਭਾਲਿਆ ਗਿਆ ਹੈ।')}</p><Link className="btn primary" data-testid="review-return-queue" to="/expert">Return to queue →</Link></div>:<form onSubmit={submit}>
    <h2><ShieldCheck size={21}/>{t('Your expert review','आपकी विशेषज्ञ समीक्षा','ਤੁਹਾਡੀ ਮਾਹਰ ਸਮੀਖਿਆ')}</h2><p className="muted small">Validate the guidance, not an unconfirmed diagnosis.</p><ErrorNotice message={reviewError}/>
    <label>{t('Decision','निर्णय','ਫੈਸਲਾ')}<select data-testid="review-decision" value={decision} onChange={e=>setDecision(e.target.value)}><option value="validated" label="Validate general guidance"/><option value="edited" label="Edit & validate guidance"/><option value="needs_information" label="Request more information"/></select></label>
    <label>{t('Recommendation','सिफारिश','ਸਿਫਾਰਸ਼')}<textarea data-testid="review-recommendation" required minLength={20} maxLength={5000} rows={8} value={recommendation} onChange={e=>{setRecommendation(e.target.value);if(decision==='validated')setDecision('edited');}}/></label>
    <label>{t('Cited source','उद्धृत स्रोत','ਹਵਾਲਾ ਸਰੋਤ')}<select data-testid="review-source" required value={source||sources[0]?.id||''} onChange={e=>setSource(e.target.value)}>
     {!sources.length&&<option value="" label="No verified source available"/>}
     {sources.map(s=><option data-testid={`review-source-option-${s.id}`} key={s.id} value={s.id} label={`${s.publisher} · ${s.title}`}/>)}
    </select></label>
    <label>{t('Rationale & changes','कारण और बदलाव','ਕਾਰਨ ਅਤੇ ਬਦਲਾਅ')}<textarea data-testid="review-rationale" required minLength={10} maxLength={2000} rows={4} placeholder="Explain the evidence, changes, and remaining uncertainty…" value={rationale} onChange={e=>setRationale(e.target.value)}/></label>
    <div className="notice" data-testid="review-safety">General source library only. Pesticide or fertilizer dosage is not supported.</div>
    <Button className="btn primary full" data-testid="submit-expert-review" type="submit" disabled={busy||!sources.length}>{busy?<Loader2 className="spin" size={17}/>:<ShieldCheck size={17}/>} {t('Save expert decision','विशेषज्ञ निर्णय सहेजें','ਮਾਹਰ ਫੈਸਲਾ ਸੰਭਾਲੋ')}</Button>
   </form>}
   {!!item.reviews?.length&&<div className="review-audit"><h2>{t('Decision trail','निर्णय का रिकॉर्ड','ਫੈਸਲੇ ਦਾ ਰਿਕਾਰਡ')}</h2>{item.reviews.map(r=><div key={r.id} data-testid={`audit-${r.id}`}><strong>{r.expert_name}</strong><span>{r.decision} · {new Date(r.created_at).toLocaleDateString()}</span><p>{r.rationale}</p><small>{r.source?.publisher} · {r.source?.title}</small></div>)}</div>}
  </aside></div>
 </>;
}