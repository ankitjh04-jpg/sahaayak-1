import { BookOpen, ShieldCheck, AlertTriangle, Info, Download, ExternalLink, ScanSearch, Sprout, Wrench, Eye, Activity } from 'lucide-react';
import { toast } from 'sonner';
import { Advisory, Detection, Guidance } from '../types';
import { useApp } from '../app/context';
import { downloadAttachment } from '../api/client';

const URGENCY = {
  immediate: { color: '#b91c1c', en: 'Urgent action needed', hi: 'तत्काल कार्रवाई आवश्यक', pa: 'ਤੁਰੰਤ ਕਾਰਵਾਈ ਲੋੜੀਂਦੀ' },
  soon: { color: '#b45309', en: 'Act soon', hi: 'जल्द कार्रवाई करें', pa: 'ਜਲਦੀ ਕਾਰਵਾਈ ਕਰੋ' },
  routine: { color: '#15803d', en: 'Routine care', hi: 'नियमित देखभाल', pa: 'ਨਿਯਮਤ ਦੇਖਭਾਲ' },
  none: { color: '#15803d', en: 'No disease pressure', hi: 'कोई रोग दबाव नहीं', pa: 'ਕੋਈ ਰੋਗ ਦਬਾਅ ਨਹੀਂ' },
};

const DiagnosisBanner = ({ item }: { item: Advisory }) => {
  const { t } = useApp();
  const d = item.detections;
  if (d?.status === 'predicted' && d.confidence != null) {
    const pct = (d.confidence * 100).toFixed(1);
    return (
      <div className="notice ok" data-testid="diagnosis-label">
        <ScanSearch size={19} />
        <div>
          <strong>{t('Diagnosis', 'निदान', 'ਤਸ਼ਖ਼ੀਸ')}</strong>
          <p data-testid="diagnosis-statement">
            {t(
              `Based on your uploaded image, this crop shows ${d.disease} with ${pct}% model confidence. Follow the action plan below and consult a local expert before spraying pesticide.`,
              `आपकी अपलोड की गई तस्वीर के आधार पर, इस फसल में ${d.disease} के लक्षण दिखते हैं (${pct}% मॉडल विश्वास)। नीचे दी गई कार्रवाई अपनाएँ और छिड़काव से पहले स्थानीय विशेषज्ञ से सलाह लें।`,
              `ਤੁਹਾਡੀ ਅੱਪਲੋਡ ਕੀਤੀ ਤਸਵੀਰ ਦੇ ਆਧਾਰ 'ਤੇ, ਇਸ ਫ਼ਸਲ ਵਿੱਚ ${d.disease} ਦੇ ਲੱਛਣ ਦਿਖਦੇ ਹਨ (${pct}% ਮਾਡਲ ਭਰੋਸਾ)। ਹੇਠਾਂ ਦਿੱਤੀ ਕਾਰਵਾਈ ਅਪਣਾਓ ਅਤੇ ਛਿੜਕਾਅ ਤੋਂ ਪਹਿਲਾਂ ਸਥਾਨਕ ਮਾਹਰ ਤੋਂ ਸਲਾਹ ਲਵੋ।`
            )}
          </p>
        </div>
      </div>
    );
  }
  return (
    <div className="notice warning" data-testid="general-advisory-label">
      <Info size={19} />
      <div>
        <strong>{t('General guidance · Not a diagnosis', 'सामान्य मार्गदर्शन · निदान नहीं', 'ਆਮ ਮਾਰਗਦਰਸ਼ਨ · ਤਸ਼ਖ਼ੀਸ ਨਹੀਂ')}</strong>
        <p>{t('This case needs more verified information before field-specific advice can be given.', 'खेत-विशिष्ट सलाह से पहले अधिक सत्यापित जानकारी चाहिए।', 'ਖੇਤ-ਵਿਸ਼ੇਸ਼ ਸਲਾਹ ਤੋਂ ਪਹਿਲਾਂ ਹੋਰ ਤਸਦੀਕਸ਼ੁਦਾ ਜਾਣਕਾਰੀ ਚਾਹੀਦੀ ਹੈ।')}</p>
      </div>
    </div>
  );
};
const CropPrediction = ({ d }: { d: Detection }) => {
  const { t } = useApp();
  const count = d.images_analyzed || 1;
  return (
    <section className="expert-note" data-testid="crop-prediction">
      <div className="section-title"><h2><ScanSearch size={19} />{t('Crop prediction', 'फसल भविष्यवाणी', 'ਫ਼ਸਲ ਭਵਿੱਖਬਾਣੀ')}</h2></div>
      <p data-testid="prediction-class">{d.disease}</p>
      <div className="confidence-bar" data-testid="prediction-confidence">
        <span className="confidence-fill" style={{ width: `${Math.round((d.confidence || 0) * 100)}%` }} />
        {((d.confidence || 0) * 100).toFixed(1)}% {t('model match', 'मॉडल मेल', 'ਮਾਡਲ ਮੇਲ')}
      </div>
      <p className="prediction-meta">
        {t(`Analyzed ${count} image${count > 1 ? 's' : ''} with ${d.model} · ${d.preprocessing || ''}`, `${d.model} से ${count} छवि का विश्लेषण`, `${d.model} ਤੋਂ ${count} ਤਸਵੀਰ ਦਾ ਵਿਸ਼ਲੇਸ਼ਣ`)}
      </p>
      {d.top_predictions && d.top_predictions.length > 1 && (
        <ol className="prediction-alternatives">
          {d.top_predictions.slice(1).map(p => (
            <li key={p.class_id}>
              {(p.probability * 100).toFixed(1)}% · {p.class_label || t(`Class #${p.class_id}`, `वर्ग #${p.class_id}`, `ਵਰਗ #${p.class_id}`)}
            </li>
          ))}
        </ol>
      )}
      {!d.labels_configured && (
        <p className="prediction-meta" data-testid="labels-pending">
          {t(
            'Class-label mapping is not configured yet; results show the raw class id from the model. Paste the 35 training class names into backend/app/ml/labels.py to display human-readable names.',
            'वर्ग-नाम मैपिंग अभी कॉन्फ़िगर नहीं है; परिणाम मॉडल का कच्चा वर्ग क्रमांक दिखाते हैं। 35 वर्ग नाम backend/app/ml/labels.py में जोड़ें।',
            'ਵਰਗ-ਨਾਮ ਮੈਪਿੰਗ ਹਾਲੇ ਕੌਨਫ਼ਿਗਰ ਨਹੀਂ ਹੈ; ਨਤੀਜੇ ਮਾਡਲ ਦਾ ਕੱਚਾ ਵਰਗ ਨੰਬਰ ਦਿਖਾਉਂਦੇ ਹਨ। 35 ਵਰਗ ਨਾਮ backend/app/ml/labels.py ਵਿੱਚ ਜੋੜੋ।'
          )}
        </p>
      )}
    </section>
  );
};

const CropGuidance = ({ g }: { g: Guidance }) => {
  const { t } = useApp();
  const u = URGENCY[(g.urgency as keyof typeof URGENCY) || 'routine'];
  return (
    <section className="expert-note" data-testid="crop-guidance">
      <div className="section-title"><h2><Sprout size={19} />{t('Full crop guidance', 'पूरी फसल मार्गदर्शिका', 'ਪੂਰੀ ਫ਼ਸਲ ਮਾਰਗਦਰਸ਼ਨ')}</h2></div>
      <p data-testid="guidance-crop"><strong>{g.crop}</strong> — {g.crop_info}</p>
      <div className="confidence-bar" data-testid="severity-estimate" style={{ borderColor: u.color }}>
        <span className="confidence-fill" style={{ width: `${g.severity_pct}%`, background: u.color }} />
        {g.severity === 'none'
          ? t(u.en, u.hi, u.pa)
          : `${t('Estimated impact', 'अनुमानित प्रभाव', 'ਅਨੁਮਾਨਿਤ ਪ੍ਰਭਾਵ')}: ${g.severity_pct}% · ${t(u.en, u.hi, u.pa)}`}
      </div>
      <div className="section-title"><h3><Wrench size={16} />{t('Maintaining crop health', 'फसल स्वास्थ्य बनाए रखना', 'ਫ਼ਸਲ ਸਿਹਤ ਕਾਇਮ ਰੱਖਣਾ')}</h3></div>
      <ul>{g.maintain.map((m, i) => <li key={i}>{m}</li>)}</ul>
      {g.early_signs.length > 0 && (
        <>
          <div className="section-title"><h3><Eye size={16} />{t('Early symptoms & signs to watch', 'देखने योग्य शुरुआती लक्षण', 'ਦੇਖਣ ਯੋਗ ਸ਼ੁਰੂਆਤੀ ਲੱਛਣ')}</h3></div>
          <ul data-testid="early-signs">{g.early_signs.map((s, i) => <li key={i}>{s}</li>)}</ul>
        </>
      )}
      {g.actions.length > 0 && (
        <>
          <div className="section-title"><h3><Activity size={16} />{t('What to do now', 'अब क्या करें', 'ਹੁਣ ਕੀ ਕਰਨਾ ਹੈ')}</h3></div>
          <ul data-testid="action-items">{g.actions.map((a, i) => <li key={i}>{a}</li>)}</ul>
        </>
      )}
      <p className="prediction-meta">
        {t(
          'General agronomic guidance for the predicted condition. Always follow the pesticide label and local expert advice before spraying.',
          'अनुमानित स्थिति के लिए सामान्य कृषि मार्गदर्शन। छिड़काव से पहले दवा का लेबल और स्थानीय विशेषज्ञ सलाह अवश्य देखें।',
          'ਅਨੁਮਾਨਿਤ ਸਥਿਤੀ ਲਈ ਆਮ ਖੇਤੀ ਮਾਰਗਦਰਸ਼ਨ। ਛਿੜਕਾਅ ਤੋਂ ਪਹਿਲਾਂ ਦਵਾਈ ਦਾ ਲੇਬਲ ਅਤੇ ਸਥਾਨਕ ਮਾਹਰ ਸਲਾਹ ਜ਼ਰੂਰ ਵੇਖੋ।'
        )}
      </p>
    </section>
  );
};
export const AdvisoryContent = ({ item }: { item: Advisory }) => {
  const { t } = useApp();
  const d = item.detections;
  const predicted = d?.status === 'predicted' && d.confidence != null;
  return (
    <>
      <div className="result-context">
        <div>
          <span className="eyebrow">{t('YOUR OBSERVATION', 'आपका निरीक्षण', 'ਤੁਹਾਡਾ ਨਿਰੀਖਣ')}</span>
          <p data-testid="result-query">{item.inputs.query || t('Attachment submitted without a typed description', 'बिना विवरण के फाइल भेजी गई', 'ਬਿਨਾਂ ਵੇਰਵੇ ਫਾਈਲ ਭੇਜੀ ਗਈ')}</p>
        </div>
        {item.inputs.upload_ids?.length > 0 && (
          <div className="result-attachments">
            {item.inputs.upload_ids.map((id, i) => (
              <button data-testid={`download-attachment-${i}`} key={id} className="btn outline" onClick={() => downloadAttachment(id).catch(e => toast.error(e.message))}>
                <Download size={15} />Attachment {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>
      <DiagnosisBanner item={item} />
      {predicted && d && <CropPrediction d={d} />}
      {predicted && d?.guidance && <CropGuidance g={d.guidance} />}
      {item.expert_recommendation && (
        <section className="expert-note">
          <div className="section-title"><h2><ShieldCheck size={19} />{t('A note from your expert', 'आपके विशेषज्ञ की सलाह', 'ਤੁਹਾਡੇ ਮਾਹਰ ਦੀ ਸਲਾਹ')}</h2></div>
          <p data-testid="expert-recommendation">{item.expert_recommendation}</p>
          <span data-testid="expert-name">{item.expert_name} · {t('Demo expert review', 'डेमो विशेषज्ञ समीक्षा', 'ਡੈਮੋ ਮਾਹਰ ਸਮੀਖਿਆ')}</span>
        </section>
      )}
      {item.recommendation && (
        <section className="recommendation-section">
          <span className="eyebrow">{t('YOUR NEXT STEPS', 'आपके अगले कदम', 'ਤੁਹਾਡੇ ਅਗਲੇ ਕਦਮ')}</span>
          <h2 className="result-serif" data-testid="recommendation-title">{item.recommendation.title}</h2>
          <p className="recommendation-summary" data-testid="recommendation-summary">{item.recommendation.summary}</p>
          <ol className="recommendation-steps">
            {item.recommendation.steps.map((s, i) => <li key={i}><span>0{i + 1}</span><p data-testid={`recommendation-step-${i}`}>{s}</p></li>)}
          </ol>
          <div className="safety-boundary" data-testid="safety-boundary"><ShieldCheck size={19} /><p>{item.recommendation.safety}</p></div>
        </section>
      )}
      <div className="result-evidence">
        <section>
          <h2><AlertTriangle size={18} />{t('What’s still missing', 'अभी क्या अधूरा है', 'ਅਜੇ ਕੀ ਅਧੂਰਾ ਹੈ')}</h2>
          <ul>{item.missing_inputs?.map((s, i) => <li key={i} data-testid={`missing-input-${i}`}>{s}</li>)}</ul>
        </section>
        <section>
          <h2><Info size={18} />{t('What we’re assuming', 'हमारी धारणाएँ', 'ਸਾਡੀਆਂ ਧਾਰਨਾਵਾਂ')}</h2>
          <ul>{item.assumptions?.map((s, i) => <li key={i} data-testid={`assumption-${i}`}>{s}</li>)}</ul>
        </section>
      </div>
      <section className="citation-section">
        <h2><BookOpen size={18} />{t('Rooted in reliable knowledge', 'विश्वसनीय ज्ञान पर आधारित', 'ਭਰੋਸੇਯੋਗ ਗਿਆਨ ਤੇ ਆਧਾਰਿਤ')}</h2>
        {item.citations?.map(s => (
          <a href={s.url} target="_blank" rel="noreferrer" className="citation" key={s.id} data-testid={`citation-${s.id}`}>
            <span className="source-monogram">{s.publisher}</span>
            <div>
              <h3>{s.title}<ExternalLink size={14} /></h3>
              <p>{s.scope}</p>
              <small>{s.document_version}</small>
            </div>
          </a>
        ))}
      </section>
    </>
  );
};


