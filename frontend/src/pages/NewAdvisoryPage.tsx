import { useRef,useState } from 'react';
import { Link,useNavigate,useSearchParams } from 'react-router-dom';
import { MessageSquareText,Camera,Mic,FileText,ArrowRight,ShieldCheck,BookOpen,Check,Loader2,Leaf,WifiOff } from 'lucide-react';
import { Button } from '../components/ui/button';
import { PageHeading,ErrorNotice,Loading } from '../components/shared';
import { AttachmentInput } from '../components/AttachmentInput';
import { useApp } from '../app/context';
import { useData } from '../hooks/useData';
import { FarmField } from '../types';
import { createAdvisory,uploadFile } from '../api/advisories';
import { queueSubmission } from '../hooks/offline';
import { toast } from 'sonner';

export default function NewAdvisoryPage(){
 const {t,user,language}=useApp();
 const navigate=useNavigate();
 const [params]=useSearchParams();
 const {data:fields,loading,error:loadError}=useData<FarmField[]>('/fields',[]);
 const initial=params.get('mode')||'text';
 const [mode,setMode]=useState(['text','image','voice','soil'].includes(initial)?initial:'text');
 const [field,setField]=useState(params.get('field')||'');
 const [query,setQuery]=useState(''),[files,setFiles]=useState<File[]>([]),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const [attachmentsBusy,setAttachmentsBusy]=useState(false);
 const key=useRef(crypto.randomUUID());
 const submit=async(e:React.FormEvent)=>{
  e.preventDefault();setError('');if(attachmentsBusy||busy)return;
  if(!files.length&&query.trim().length<8){setError(t('Please describe your concern in at least 8 characters.','कृपया कम से कम 8 अक्षरों में लिखें।','ਕਿਰਪਾ ਕਰਕੇ ਘੱਟੋ-ਘੱਟ 8 ਅੱਖਰਾਂ ਵਿੱਚ ਲਿਖੋ।'));return;}
  setBusy(true);
  const payload={field_id:field||fields[0]?.id,query:query.trim(),input_type:mode,language,upload_ids:[] as string[],idempotency_key:key.current};
  try{
   if(!navigator.onLine){await queueSubmission({id:key.current,owner:user!.id,payload,files,created_at:new Date().toISOString()});toast.success('Saved on this device. We’ll sync when you’re back online.');navigate('/history');return;}
   const uploads=await Promise.all(files.map(uploadFile));
   const result=await createAdvisory({...payload,upload_ids:uploads.map(u=>u.id)});
   navigate(`/advisories/${result.advisory_id}`);
  }catch(e:any){setError(e.message||'Unable to submit. Your information is still here.');}finally{setBusy(false);}
 };
 const modes=[{id:'text',icon:MessageSquareText,label:t('Write','लिखें','ਲਿਖੋ')},{id:'image',icon:Camera,label:t('Crop photo','फसल फोटो','ਫ਼ਸਲ ਫੋਟੋ')},{id:'voice',icon:Mic,label:t('Voice note','वॉइस नोट','ਵੌਇਸ ਨੋਟ')},{id:'soil',icon:FileText,label:t('Soil card','मृदा कार्ड','ਮਿੱਟੀ ਕਾਰਡ')}];
 return <>
  <PageHeading eyebrow={t('LET’S GROW THROUGH IT','आइए साथ आगे बढ़ें','ਆਓ ਇਕੱਠੇ ਅੱਗੇ ਵਧੀਏ')} title={t('What’s on your mind?','आप क्या जानना चाहते हैं?','ਤੁਸੀਂ ਕੀ ਜਾਣਨਾ ਚਾਹੁੰਦੇ ਹੋ?')} description={t('A small concern or a big question. We’re here for your farm.','एक छोटी चिंता या बड़ा सवाल। हम आपके खेत के लिए यहाँ हैं।','ਛੋਟੀ ਚਿੰਤਾ ਜਾਂ ਵੱਡਾ ਸਵਾਲ। ਅਸੀਂ ਤੁਹਾਡੇ ਖੇਤ ਲਈ ਇੱਥੇ ਹਾਂ।')}/>
  <div className="advisory-compose-grid">
   <form className="advisory-compose" onSubmit={submit}>
    <ErrorNotice message={error||loadError}/>
    <div className="form-section">
     <label htmlFor="advisory-field" className="section-form-label"><span className="step-number">01</span>{t('Which field needs a little care?','किस खेत को देखभाल चाहिए?','ਕਿਹੜੇ ਖੇਤ ਨੂੰ ਦੇਖਭਾਲ ਚਾਹੀਦੀ ਹੈ?')}</label>
     {loading&&!fields.length?<Loading/>:fields.length?<select id="advisory-field" data-testid="advisory-field-select" value={field||fields[0]?.id} onChange={e=>{setField(e.target.value);key.current=crypto.randomUUID();}}>
      {fields.map(f=><option data-testid={`advisory-field-option-${f.id}`} key={f.id} value={f.id} label={`${f.name} · ${f.crop} · ${f.acreage} acres`}/>)}
     </select>:<div className="notice" data-testid="no-fields-notice">{t('Add a field before requesting advice.','सलाह से पहले खेत जोड़ें।','ਸਲਾਹ ਤੋਂ ਪਹਿਲਾਂ ਖੇਤ ਜੋੜੋ।')}<Link to="/fields?add=true" data-testid="new-advisory-add-field">{t('Add a field','खेत जोड़ें','ਖੇਤ ਜੋੜੋ')} →</Link></div>}
    </div>
    <div className="form-section">
     <div className="section-form-label"><span className="step-number">02</span>{t('Tell us what you’re noticing','हमें बताएं कि आप क्या देख रहे हैं','ਦੱਸੋ ਕਿ ਤੁਸੀਂ ਕੀ ਵੇਖ ਰਹੇ ਹੋ')}</div>
     <div className="input-mode-tabs" role="tablist">{modes.map(m=><button type="button" role="tab" aria-selected={mode===m.id} data-testid={`input-mode-${m.id}`} className={mode===m.id?'active':''} key={m.id} onClick={()=>{setMode(m.id);key.current=crypto.randomUUID();}}><m.icon size={18}/><span>{m.label}</span></button>)}</div>
     {mode!=='text'&&<AttachmentInput mode={mode} files={files} onBusyChange={setAttachmentsBusy} setFiles={f=>{setFiles(f);key.current=crypto.randomUUID();}}/>}
     <label className="query-label" htmlFor="advisory-query">{t('Your question or observations','आपका सवाल या निरीक्षण','ਤੁਹਾਡਾ ਸਵਾਲ ਜਾਂ ਨਿਰੀਖਣ')}</label>
     <textarea id="advisory-query" data-testid="advisory-query" maxLength={4000} rows={6} value={query} onChange={e=>{setQuery(e.target.value);key.current=crypto.randomUUID();}} placeholder={t('For example, the lower leaves of my wheat crop have started turning yellow over the past three days…','उदाहरण: पिछले तीन दिनों से मेरी गेहूँ की फसल के निचले पत्ते पीले हो रहे हैं…','ਉਦਾਹਰਨ: ਪਿਛਲੇ ਤਿੰਨ ਦਿਨਾਂ ਤੋਂ ਮੇਰੀ ਕਣਕ ਦੀ ਫ਼ਸਲ ਦੇ ਹੇਠਲੇ ਪੱਤੇ ਪੀਲੇ ਹੋ ਰਹੇ ਹਨ…')}/>
     <div className="textarea-footer"><span>{t('A few details can make a big difference.','कुछ विवरण बहुत मदद कर सकते हैं।','ਕੁਝ ਵੇਰਵੇ ਬਹੁਤ ਮਦਦ ਕਰ ਸਕਦੇ ਹਨ।')}</span><span data-testid="query-character-count">{query.length}/4000</span></div>
    </div>
    <div className="compose-submit"><span><ShieldCheck size={16}/>{t('Your information is private & secure','आपकी जानकारी निजी और सुरक्षित है','ਤੁਹਾਡੀ ਜਾਣਕਾਰੀ ਨਿੱਜੀ ਅਤੇ ਸੁਰੱਖਿਅਤ ਹੈ')}</span>
     <Button data-testid="submit-advisory" type="submit" className="btn primary" disabled={busy||attachmentsBusy||!fields.length}>{busy?<><Loader2 className="spin" size={16}/>{t('Submitting…','भेज रहे हैं…','ਭੇਜ ਰਹੇ ਹਾਂ…')}</>:<>{navigator.onLine?t('Get guidance','मार्गदर्शन पाएं','ਮਾਰਗਦਰਸ਼ਨ ਲਵੋ'):t('Save offline','ऑफलाइन सहेजें','ਆਫਲਾਈਨ ਸੰਭਾਲੋ')}{navigator.onLine?<ArrowRight size={17}/>:<WifiOff size={17}/>}</>}</Button>
    </div>
   </form>
   <aside className="compose-aside">
    <div className="aside-plant"><Leaf size={35} strokeWidth={1.2}/></div>
    <h2>{t('Good advice starts with','अच्छी सलाह की शुरुआत','ਚੰਗੀ ਸਲਾਹ ਦੀ ਸ਼ੁਰੂਆਤ')}<br/><em>{t('a little understanding.','थोड़ी समझ से।','ਥੋੜ੍ਹੀ ਸਮਝ ਨਾਲ।')}</em></h2>
    <div className="aside-tip"><Check size={16}/><div><strong>{t('The little details matter','छोटे विवरण महत्वपूर्ण हैं','ਛੋਟੇ ਵੇਰਵੇ ਮਹੱਤਵਪੂਰਨ ਹਨ')}</strong><p>{t('When did it start? Is it spreading? What has changed recently?','कब शुरू हुआ? क्या फैल रहा है? हाल में क्या बदला?','ਕਦੋਂ ਸ਼ੁਰੂ ਹੋਇਆ? ਕੀ ਫੈਲ ਰਿਹਾ ਹੈ? ਹਾਲ ਵਿੱਚ ਕੀ ਬਦਲਿਆ?')}</p></div></div>
    <div className="aside-tip"><BookOpen size={16}/><div><strong>{t('Knowledge, with its roots','ज्ञान, अपने स्रोत के साथ','ਗਿਆਨ, ਆਪਣੇ ਸਰੋਤ ਨਾਲ')}</strong><p>{t('General guidance is backed by a cited agricultural source.','सामान्य मार्गदर्शन कृषि स्रोत पर आधारित है।','ਆਮ ਮਾਰਗਦਰਸ਼ਨ ਖੇਤੀ ਸਰੋਤ ਤੇ ਆਧਾਰਿਤ ਹੈ।')}</p></div></div>
    <div className="aside-tip"><ShieldCheck size={16}/><div><strong>{t('An expert when it matters','ज़रूरत पर विशेषज्ञ','ਲੋੜ ਵੇਲੇ ਮਾਹਰ')}</strong><p>{t('Uncertain cases go to an agricultural expert, not a guess.','अनिश्चित मामलों में विशेषज्ञ, अनुमान नहीं।','ਅਨਿਸ਼ਚਿਤ ਕੇਸ ਮਾਹਰ ਕੋਲ ਜਾਂਦੇ ਹਨ, ਅੰਦਾਜ਼ੇ ਨਹੀਂ।')}</p></div></div>
    <div className="demo-safety-note" data-testid="advisory-demo-safety"><strong>SIH DEMO</strong><p>{t('No automated diagnosis or live forecast. Missing inputs are always shown.','स्वचालित निदान या लाइव पूर्वानुमान नहीं। अधूरी जानकारी हमेशा दिखाई जाती है।','ਆਟੋਮੈਟਿਕ ਤਸ਼ਖ਼ੀਸ ਜਾਂ ਲਾਈਵ ਪੂਰਵ ਅਨੁਮਾਨ ਨਹੀਂ। ਅਧੂਰੀ ਜਾਣਕਾਰੀ ਹਮੇਸ਼ਾ ਦਿਖਾਈ ਜਾਂਦੀ ਹੈ।')}</p></div>
   </aside>
  </div>
 </>;
}