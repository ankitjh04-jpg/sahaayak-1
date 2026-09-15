import { useEffect,useRef,useState } from 'react';
import { Camera,Upload,Mic,Square,FileText,X,Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { compressImage } from '../hooks/offline';
import { useApp } from '../app/context';

interface Props {mode:string;files:File[];setFiles:(files:File[])=>void;onBusyChange?:(busy:boolean)=>void}
export const AttachmentInput=({mode,files,setFiles,onBusyChange}:Props)=>{
 const {t}=useApp();
 const input=useRef<HTMLInputElement>(null),cameraInput=useRef<HTMLInputElement>(null);
 const recorder=useRef<MediaRecorder|null>(null),stream=useRef<MediaStream|null>(null),timer=useRef<ReturnType<typeof setTimeout>|null>(null);
 const mounted=useRef(true),locked=useRef(false),currentFiles=useRef(files);currentFiles.current=files;
 const busyCallback=useRef(onBusyChange);busyCallback.current=onBusyChange;
 const [recording,setRecording]=useState(false),[processing,setProcessing]=useState(false),[preview,setPreview]=useState(''),[captured,setCaptured]=useState(false);
 useEffect(()=>{const file=files.find(f=>f.type.startsWith('image/'));if(!file){setPreview('');setCaptured(false);return;}const url=URL.createObjectURL(file);setPreview(url);return()=>URL.revokeObjectURL(url);},[files]);
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;if(timer.current)clearTimeout(timer.current);if(recorder.current?.state==='recording')recorder.current.stop();stream.current?.getTracks().forEach(track=>track.stop());busyCallback.current?.(false);};},[]);
 const add=async(selected:File[],fromCamera=false)=>{
  // Native cancellation supplies no file; do not alter the existing attachments.
  if(!selected.length||locked.current)return;
  if(currentFiles.current.length+selected.length>5){toast.error(t('Maximum 5 files per advisory','एक सलाह में अधिकतम 5 फाइलें','ਇੱਕ ਸਲਾਹ ਵਿੱਚ ਵੱਧ ਤੋਂ ਵੱਧ 5 ਫਾਈਲਾਂ'));return;}
  locked.current=true;setProcessing(true);busyCallback.current?.(true);
  try{
   const result:File[]=[];
   for(const file of selected){
    if(file.size===0)throw new Error(t('This file is empty. Please take another photo or choose a different file.','यह फाइल खाली है। दूसरी फोटो लें या फाइल चुनें।','ਇਹ ਫਾਈਲ ਖਾਲੀ ਹੈ। ਹੋਰ ਫੋਟੋ ਲਓ ਜਾਂ ਫਾਈਲ ਚੁਣੋ।'));
    if(file.size>10*1024*1024)throw new Error(t('Each file must be 10 MB or smaller','हर फाइल 10 MB या उससे छोटी होनी चाहिए','ਹਰ ਫਾਈਲ 10 MB ਜਾਂ ਇਸ ਤੋਂ ਛੋਟੀ ਹੋਣੀ ਚਾਹੀਦੀ ਹੈ'));
    const type=file.type.split(';')[0];
    if(fromCamera&&!type.startsWith('image/'))throw new Error(t('Please take or choose a photo.','कृपया फोटो लें या चुनें।','ਕਿਰਪਾ ਕਰਕੇ ਫੋਟੋ ਲਓ ਜਾਂ ਚੁਣੋ।'));
    if(!['image/jpeg','image/png','image/webp','application/pdf','audio/wav','audio/mpeg','audio/mp4','audio/ogg','audio/webm'].includes(type))throw new Error(t('Unsupported file type. For photos, use JPG, PNG or WebP.','फाइल का प्रकार समर्थित नहीं है। फोटो के लिए JPG, PNG या WebP चुनें।','ਫਾਈਲ ਦੀ ਕਿਸਮ ਸਮਰਥਿਤ ਨਹੀਂ ਹੈ। ਫੋਟੋ ਲਈ JPG, PNG ਜਾਂ WebP ਚੁਣੋ।'));
    result.push(await compressImage(file));
   }
   if(mounted.current){setFiles([...currentFiles.current,...result]);setCaptured(fromCamera);}
  }catch(e:any){if(mounted.current)toast.error(e.message||t('This photo could not be opened. Please try another.','यह फोटो नहीं खुल सकी। दूसरी फोटो चुनें।','ਇਹ ਫੋਟੋ ਨਹੀਂ ਖੁੱਲ੍ਹ ਸਕੀ। ਹੋਰ ਫੋਟੋ ਚੁਣੋ।'));}
  finally{locked.current=false;if(mounted.current){setProcessing(false);busyCallback.current?.(false);}if(input.current)input.current.value='';if(cameraInput.current)cameraInput.current.value='';}
 };
 const toggleRecording=async()=>{
  if(recording){recorder.current?.stop();return;}
  if(locked.current)return;
  busyCallback.current?.(true);
  try{
   if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder)throw new Error('Audio recording is not supported. Upload an audio file instead.');
   stream.current=await navigator.mediaDevices.getUserMedia({audio:true});
   if(!mounted.current){stream.current.getTracks().forEach(track=>track.stop());return;}
   const mime=['audio/webm','audio/mp4','audio/ogg'].find(type=>MediaRecorder.isTypeSupported(type));
   const rec=new MediaRecorder(stream.current,mime?{mimeType:mime}:{});recorder.current=rec;const chunks:BlobPart[]=[];
   rec.ondataavailable=e=>chunks.push(e.data);
   rec.onstop=()=>{if(timer.current)clearTimeout(timer.current);stream.current?.getTracks().forEach(track=>track.stop());if(!mounted.current)return;setRecording(false);const type=rec.mimeType.split(';')[0];add([new File(chunks,`voice-note.${type.split('/')[1]}`,{type})]);};
   rec.start();setRecording(true);timer.current=setTimeout(()=>rec.state==='recording'&&rec.stop(),60000);
  }catch(e:any){stream.current?.getTracks().forEach(track=>track.stop());busyCallback.current?.(false);if(mounted.current)toast.error(e.message||'Microphone permission unavailable');}
 };
 const blocked=processing||recording||files.length>=5;
 const Icon=mode==='image'?Camera:mode==='voice'?Mic:FileText;
 return <div className="attachment-section">
  <input ref={input} type="file" className="sr-only" data-testid="attachment-file-input" aria-label="Choose attachment" multiple disabled={blocked} accept={mode==='voice'?'audio/webm,audio/mp4,audio/wav,audio/mpeg,audio/ogg':mode==='soil'?'image/jpeg,image/png,image/webp,application/pdf':'image/jpeg,image/png,image/webp'} onChange={e=>add(Array.from(e.target.files||[]))}/>
  {mode!=='voice'&&<input ref={cameraInput} type="file" className="sr-only" data-testid="camera-file-input" aria-label="Take a photo with your camera" accept="image/*" capture="environment" disabled={blocked} onChange={e=>add(Array.from(e.target.files||[]),true)}/>}
  <div className="upload-zone" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();if(!recording)add(Array.from(e.dataTransfer.files));}}>
   {preview?<img className="attachment-preview" data-testid="attachment-preview" src={preview} alt="Your crop attachment"/>:<span className="upload-icon"><Icon size={28} strokeWidth={1.5}/></span>}
   <h3 data-testid="upload-title">{mode==='voice'?t('Your words, in your language','आपकी बात, आपकी भाषा में','ਤੁਹਾਡੀ ਗੱਲ, ਤੁਹਾਡੀ ਭਾਸ਼ਾ ਵਿੱਚ'):mode==='soil'?t('Share your Soil Health Card','अपना मृदा स्वास्थ्य कार्ड साझा करें','ਆਪਣਾ ਮਿੱਟੀ ਸਿਹਤ ਕਾਰਡ ਸਾਂਝਾ ਕਰੋ'):t('Let’s take a closer look','आइए करीब से देखें','ਆਓ ਨੇੜਿਓਂ ਵੇਖੀਏ')}</h3>
   <p data-testid="upload-help">{mode==='voice'?'WAV, MP3, M4A, OGG or WebM · up to 10 MB':mode==='soil'?'PDF, JPG, PNG or WebP · up to 10 MB':'JPG, PNG or WebP · up to 10 MB · compressed before upload'}</p>
   <div className="upload-actions">
    {mode==='voice'?<button type="button" data-testid="record-voice" disabled={processing||files.length>=5} className={`btn ${recording?'recording':'primary'}`} onClick={toggleRecording}>{recording?<Square size={15}/>:<Mic size={16}/>} {recording?t('Stop recording','रिकॉर्डिंग रोकें','ਰਿਕਾਰਡਿੰਗ ਰੋਕੋ'):t('Record voice note','वॉइस नोट रिकॉर्ड करें','ਵੌਇਸ ਨੋਟ ਰਿਕਾਰਡ ਕਰੋ')}</button>:<button type="button" data-testid="take-photo" className="btn primary" disabled={blocked} onClick={()=>cameraInput.current?.click()}><Camera size={17}/>{t('Take photo','फोटो लें','ਫੋਟੋ ਲਓ')}</button>}
    <button data-testid="choose-attachment" className="btn outline" type="button" disabled={blocked} onClick={()=>input.current?.click()}>{processing?<Loader2 size={16} className="spin"/>:<Upload size={16}/>} {mode==='image'?t('Choose from gallery','गैलरी से चुनें','ਗੈਲਰੀ ਤੋਂ ਚੁਣੋ'):t('Choose file','फाइल चुनें','ਫਾਈਲ ਚੁਣੋ')}</button>
   </div>
   {mode!=='voice'&&<p className="camera-support-note" data-testid="camera-support-note">{t('Your phone controls camera access. On computers, a file picker may open instead.','कैमरे की अनुमति आपका फ़ोन नियंत्रित करता है। कंप्यूटर पर फाइल चयन खुल सकता है।','ਕੈਮਰੇ ਦੀ ਇਜਾਜ਼ਤ ਤੁਹਾਡਾ ਫ਼ੋਨ ਕੰਟਰੋਲ ਕਰਦਾ ਹੈ। ਕੰਪਿਊਟਰ ਤੇ ਫਾਈਲ ਚੋਣ ਖੁੱਲ੍ਹ ਸਕਦੀ ਹੈ।')}</p>}
   {captured&&<div className="capture-status" role="status" data-testid="camera-photo-ready">{t('Photo added. Ready to submit with your observations.','फोटो जुड़ गई। अपने विवरण के साथ भेजने के लिए तैयार है।','ਫੋਟੋ ਜੁੜ ਗਈ। ਆਪਣੇ ਵੇਰਵਿਆਂ ਨਾਲ ਭੇਜਣ ਲਈ ਤਿਆਰ ਹੈ।')}</div>}
   {recording&&<span className="recording-label" data-testid="recording-status">● Recording · stops automatically after 60 seconds</span>}
  </div>
  {files.map((file,index)=><div className="attachment-file" key={`${file.name}-${index}`} data-testid={`attached-file-${index}`}><FileText size={17}/><span>{file.name}<small>{Math.round(file.size/1024)} KB</small></span><button type="button" data-testid={`remove-file-${index}`} disabled={processing||recording} aria-label={`Remove ${file.name}`} onClick={()=>{setCaptured(false);setFiles(files.filter((_,i)=>i!==index));}}><X size={16}/></button></div>)}
  <p className="adapter-notice" data-testid="attachment-demo-notice">{mode==='voice'?t('Demo: audio is saved, but not transcribed. Add a typed description below.','डेमो: ऑडियो सहेजा जाता है, लिखा नहीं जाता। नीचे विवरण लिखें।','ਡੈਮੋ: ਆਡੀਓ ਸੰਭਾਲਿਆ ਜਾਂਦਾ ਹੈ, ਲਿਖਿਆ ਨਹੀਂ ਜਾਂਦਾ। ਹੇਠਾਂ ਵੇਰਵਾ ਲਿਖੋ।'):mode==='soil'?t('Demo: soil values are not extracted automatically. Add known values to your field profile.','डेमो: मिट्टी के मान स्वचालित रूप से नहीं निकाले जाते।','ਡੈਮੋ: ਮਿੱਟੀ ਦੇ ਮੁੱਲ ਆਪਣੇ ਆਪ ਨਹੀਂ ਕੱਢੇ ਜਾਂਦੇ।'):t('Demo: images are saved for expert review. No automated disease diagnosis is performed.','डेमो: तस्वीरें विशेषज्ञ समीक्षा के लिए सहेजी जाती हैं। रोग निदान नहीं होता।','ਡੈਮੋ: ਤਸਵੀਰਾਂ ਮਾਹਰ ਸਮੀਖਿਆ ਲਈ ਸੰਭਾਲੀਆਂ ਜਾਂਦੀਆਂ ਹਨ। ਬਿਮਾਰੀ ਦੀ ਤਸ਼ਖ਼ੀਸ ਨਹੀਂ ਹੁੰਦੀ।')}</p>
 </div>;
};