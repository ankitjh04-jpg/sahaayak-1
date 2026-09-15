import {useState} from 'react';
import {BadgeCheck,Loader2} from 'lucide-react';
import {post} from '../api/client';
import {useApp} from '../app/context';
export const AadhaarDemo=()=>{
 const {t}=useApp();const [done,setDone]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const check=async()=>{
  setBusy(true);setError('');
  try{const result=await post('/auth/aadhaar/demo',{});if(result.mode==='demo'&&result.verified===false)setDone(true);else setError('Unexpected verification response.');}
  catch(e:any){setError(e.message);}
  finally{setBusy(false);}
 };
 return <div className="aadhaar-demo"><div><strong>{t('Aadhaar · Demo only','आधार · केवल डेमो','ਆਧਾਰ · ਸਿਰਫ਼ ਡੈਮੋ')}</strong><p data-testid="aadhaar-demo-disclosure">{t('No Aadhaar number is collected. This is not identity verification.','आधार नंबर नहीं लिया जाता। यह पहचान सत्यापन नहीं है।','ਆਧਾਰ ਨੰਬਰ ਨਹੀਂ ਲਿਆ ਜਾਂਦਾ। ਇਹ ਪਛਾਣ ਤਸਦੀਕ ਨਹੀਂ ਹੈ।')}</p></div>
  <button type="button" data-testid="aadhaar-demo-verify" disabled={busy||done} className="btn outline" onClick={check}>{busy?<Loader2 className="spin" size={14}/>:<BadgeCheck size={15}/>} {done?t('Demo complete','डेमो पूर्ण','ਡੈਮੋ ਪੂਰਾ'):t('Run demo check','डेमो जाँच करें','ਡੈਮੋ ਜਾਂਚ ਕਰੋ')}</button>
  {done&&<p className="aadhaar-demo-status" role="status" data-testid="aadhaar-demo-success">{t('Demo check complete. Aadhaar has NOT been verified.','डेमो जाँच पूर्ण। आधार का सत्यापन नहीं हुआ है।','ਡੈਮੋ ਜਾਂਚ ਪੂਰੀ। ਆਧਾਰ ਦੀ ਤਸਦੀਕ ਨਹੀਂ ਹੋਈ ਹੈ।')}</p>}
  {error&&<p role="alert" data-testid="aadhaar-demo-error">{error}</p>}
 </div>;
};