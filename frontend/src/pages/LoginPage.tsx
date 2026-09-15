import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, ShieldCheck, Phone, Loader2, UserRound } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Brand, ErrorNotice } from '../components/shared';
import { useApp } from '../app/context';
import { demoLogin, localDemoLogin, requestOtp, verifyOtp } from '../api/auth';
import { Language } from '../types';
import {api} from '../api/client';
import {AadhaarDemo} from '../components/AadhaarDemo';

export default function LoginPage() {
 const {t,language,setLanguage,accept,switchRole} = useApp();
 const navigate=useNavigate();
 const [name,setName]=useState(''),[phone,setPhone]=useState(''),[code,setCode]=useState('');
 const [demoCode,setDemoCode]=useState(''),[sent,setSent]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const [config,setConfig]=useState<{otp_mode:string;demo_mode:boolean}|null>(null);
 const [resendUntil,setResendUntil]=useState(0),[remaining,setRemaining]=useState(0);
 const demoOtpFallback=!config||Boolean(config.demo_mode&&config.otp_mode!=='live');
 useEffect(()=>{api('/config').then(setConfig).catch(()=>setConfig({otp_mode:'unconfigured',demo_mode:true}));},[]);
 useEffect(()=>{const update=()=>setRemaining(Math.max(0,Math.ceil((resendUntil-Date.now())/1000)));update();const timer=setInterval(update,1000);return()=>clearInterval(timer);},[resendUntil]);
 const submit=async(e:React.FormEvent)=>{
  e.preventDefault();setError('');
  const normalizedName=name.normalize('NFC').trim().replace(/ +/g,' ');
  if(normalizedName.length<2||!/[\p{L}]/u.test(normalizedName)||!/^[\p{L}\p{M} .’'\-\u200c\u200d]+$/u.test(normalizedName)){
   setError(t('Enter your name using letters, spaces, apostrophes, hyphens or periods.','अपना नाम अक्षरों, स्पेस, एपॉस्ट्रॉफ़, हाइफ़न या बिंदु से लिखें।','ਆਪਣਾ ਨਾਮ ਅੱਖਰਾਂ, ਖਾਲੀ ਥਾਂ, ਅਪੋਸਟ੍ਰੋਫੀ, ਹਾਈਫਨ ਜਾਂ ਬਿੰਦੀ ਨਾਲ ਲਿਖੋ।'));return;
  }
  setBusy(true);
  try{
   const normalizedPhone=`+91${phone}`;
    if(sent){
     if(demoOtpFallback&&code!=='123456')throw new Error('Incorrect OTP. Please enter 123456.');
    let session;
    if(demoOtpFallback){try{session=await demoLogin('farmer');}catch{session=localDemoLogin(normalizedName);}}
    else session=await verifyOtp(normalizedPhone,code,language);
    const personalizedSession=demoOtpFallback?{...session,user:{...session.user,profile:{...session.user.profile,name:normalizedName}}}:session;
    accept(personalizedSession);navigate(personalizedSession.user.role==='expert'?'/expert':'/');
    }
    else if(demoOtpFallback){setName(normalizedName);setDemoCode('123456');setResendUntil(Date.now()+30*1000);setSent(true);}
    else{const response=await requestOtp(normalizedPhone,language,normalizedName);setName(normalizedName);setDemoCode(response.demo_code||'');setResendUntil(Date.now()+(response.resend_after||30)*1000);setSent(true);}
  }catch(e:any){setError(e.message);}finally{setBusy(false);}
 };
 const explore=async(role:'farmer'|'expert')=>{if(role==='expert'){navigate('/expert/login');return;}setBusy(true);setError('');try{await switchRole('farmer');navigate('/');}catch(e:any){setError(e.message);}finally{setBusy(false);}};
 return <div className="login-page">
  <img className="login-background" src="/images/wheat-hero.jpg" alt="Green wheat growing in sunlight"/><div className="login-scrim"/>
  <header className="login-header"><Brand light/><select data-testid="login-language" aria-label="Language" value={language} disabled={busy||sent} onChange={e=>setLanguage(e.target.value as Language)}><option value="en" label="English"/><option value="hi" label="हिन्दी"/><option value="pa" label="ਪੰਜਾਬੀ"/></select></header>
  <div className="login-content">
   <p className="eyebrow" data-testid="login-eyebrow">{t('ROOTED IN YOUR WELL-BEING','आपकी खुशहाली से जुड़ा','ਤੁਹਾਡੀ ਖੁਸ਼ਹਾਲੀ ਨਾਲ ਜੁੜਿਆ')}</p>
   <h1 data-testid="login-title">{t('Good farming starts','अच्छी खेती की शुरुआत','ਚੰਗੀ ਖੇਤੀ ਦੀ ਸ਼ੁਰੂਆਤ')}<br/><em>{t('with good company.','एक अच्छे साथी से।','ਚੰਗੇ ਸਾਥੀ ਨਾਲ।')}</em></h1>
   <div className="login-form-box">
    <h2 data-testid="login-form-heading">{sent?t('Verify your phone number','अपना फ़ोन नंबर सत्यापित करें','ਆਪਣਾ ਫ਼ੋਨ ਨੰਬਰ ਤਸਦੀਕ ਕਰੋ'):t('Welcome to Sahaayak','सहायक में आपका स्वागत है','ਸਹਾਇਕ ਵਿੱਚ ਤੁਹਾਡਾ ਸਵਾਗਤ ਹੈ')}</h2>
    <p data-testid="login-subtitle">{t('Your farm. Your language. Your companion.','आपका खेत। आपकी भाषा। आपका साथी।','ਤੁਹਾਡਾ ਖੇਤ। ਤੁਹਾਡੀ ਭਾਸ਼ਾ। ਤੁਹਾਡਾ ਸਾਥੀ।')}</p>
    <ErrorNotice message={error}/>
    <form onSubmit={submit}>
     <div className="login-identity-field"><label htmlFor="farmer-name">{t('Farmer’s full name','किसान का पूरा नाम','ਕਿਸਾਨ ਦਾ ਪੂਰਾ ਨਾਮ')}</label><div className="phone-input"><UserRound size={17}/><input id="farmer-name" data-testid="login-farmer-name" name="name" type="text" autoComplete="name" autoCapitalize="words" required minLength={2} maxLength={80} disabled={sent||busy} value={name} onChange={e=>setName(e.target.value)} placeholder={t('Your full name','आपका पूरा नाम','ਤੁਹਾਡਾ ਪੂਰਾ ਨਾਮ')}/></div></div>
     <label htmlFor="phone">{t('Mobile number','मोबाइल नंबर','ਮੋਬਾਈਲ ਨੰਬਰ')}</label>
     <div className="phone-input"><Phone size={17}/><span>+91</span><input id="phone" data-testid="login-phone" type="tel" name="tel-national" autoComplete="tel-national" inputMode="numeric" required disabled={sent||busy} placeholder={t('Your 10-digit number','आपका 10 अंकों का नंबर','ਤੁਹਾਡਾ 10 ਅੰਕਾਂ ਦਾ ਨੰਬਰ')} value={phone} onChange={e=>setPhone(e.target.value)} pattern="[0-9]{10}" maxLength={10}/></div>
    {!sent&&<p className="login-service-status" data-testid="login-service-status">{config?.otp_mode==='live'?t('SMS verification powered by Twilio.','Twilio द्वारा SMS सत्यापन।','Twilio ਰਾਹੀਂ SMS ਤਸਦੀਕ।'):config?.otp_mode==='demo'||demoOtpFallback?t('Demo phone verification · No SMS is sent.','डेमो फ़ोन सत्यापन · SMS नहीं भेजा जाता।','ਡੈਮੋ ਫ਼ੋਨ ਤਸਦੀਕ · SMS ਨਹੀਂ ਭੇਜਿਆ ਜਾਂਦਾ।'):t('SMS login needs Twilio configuration. No SMS can be sent yet.','SMS लॉगिन के लिए Twilio कॉन्फ़िगरेशन चाहिए। अभी SMS नहीं भेजा जा सकता।','SMS ਲਾਗਇਨ ਲਈ Twilio ਸੈਟਅੱਪ ਚਾਹੀਦਾ ਹੈ। ਅਜੇ SMS ਨਹੀਂ ਭੇਜਿਆ ਜਾ ਸਕਦਾ।')}</p>}
     {sent&&<><div className="notice" data-testid={demoCode?'demo-otp-notice':'live-otp-notice'}><div>{demoCode?<>{t('SIMULATED OTP — no SMS sent. Demo code:','सिम्युलेटेड OTP — SMS नहीं भेजा गया। कोड:','ਸਿਮੂਲੇਟਡ OTP — SMS ਨਹੀਂ ਭੇਜਿਆ। ਕੋਡ:')} <strong>{demoCode}</strong></>:t(`Verification SMS requested for +91${phone}.`,`+91${phone} पर सत्यापन SMS का अनुरोध किया गया।`,`+91${phone} ਤੇ ਤਸਦੀਕ SMS ਦੀ ਬੇਨਤੀ ਕੀਤੀ ਗਈ।`)}</div></div><label htmlFor="otp">{t('6-digit verification code','6 अंकों का कोड','6 ਅੰਕਾਂ ਦਾ ਕੋਡ')}</label><input id="otp" data-testid="login-otp" className="form-input otp-input" autoComplete="one-time-code" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} required disabled={busy} value={code} onChange={e=>setCode(e.target.value)}/><small data-testid="otp-expiry-info">{t('Expires in 5 minutes · 5 attempts','5 मिनट में समाप्त · 5 प्रयास','5 ਮਿੰਟ ਵਿੱਚ ਮਿਆਦ ਖ਼ਤਮ · 5 ਕੋਸ਼ਿਸ਼ਾਂ')}</small></>}
    <Button data-testid="login-submit" className="btn primary full" type="submit" disabled={busy||!config||(config.otp_mode==='unconfigured'&&!config.demo_mode)}>{busy?<Loader2 className="spin" size={17}/>:<>{sent?t('Verify & continue','सत्यापित करें','ਤਸਦੀਕ ਕਰੋ'):t('Get verification code','सत्यापन कोड प्राप्त करें','ਤਸਦੀਕ ਕੋड ਪ੍ਰਾਪ्त ਕਰੋ')}<ArrowRight size={17}/></>}</Button>
     {sent&&<button className="text-button" type="button" data-testid="change-phone" disabled={busy||remaining>0} onClick={()=>{setSent(false);setCode('');setDemoCode('');setError('');}}>{remaining>0?`${remaining}s · ${t('before a new code','नए कोड से पहले','ਨਵੇਂ ਕੋਡ ਤੋਂ ਪਹਿਲਾਂ')}`:t('Edit details / request a new code','विवरण बदलें / नया कोड प्राप्त करें','ਵੇਰਵੇ ਬਦਲੋ / ਨਵਾਂ ਕੋਡ ਲਵੋ')}</button>}
    </form>
    {config?.demo_mode&&<AadhaarDemo/>}
    <div className="login-demo-divider"><span>{t('OTHER WORKSPACES','अन्य कार्यक्षेत्र','ਹੋਰ ਵਰਕਸਪੇਸ')}</span></div>
    <div className="demo-login-buttons">{config?.demo_mode&&<button data-testid="demo-login-farmer" disabled={busy} onClick={()=>explore('farmer')}>{t('Farmer demo','किसान डेमो','ਕਿਸਾਨ ਡੈਮੋ')}<ArrowRight size={14}/></button>}<button data-testid="demo-login-expert" disabled={busy} onClick={()=>explore('expert')}>{t('Expert sign-in','विशेषज्ञ साइन-इन','ਮਾਹਰ ਸਾਈਨ-ਇਨ')}<ArrowRight size={14}/></button></div>
    <div className="login-trust" data-testid="login-privacy-note"><ShieldCheck size={15}/>{t('Your information stays yours.','आपकी जानकारी सुरक्षित है।','ਤੁਹਾਡੀ ਜਾਣਕਾਰੀ ਸੁਰੱਖਿਅਤ ਹੈ।')}</div>
   </div>
  </div><div className="login-footer" data-testid="login-footer">SIH26131 · Detect → Predict → Advise → Validate → Monitor</div>
 </div>;
}