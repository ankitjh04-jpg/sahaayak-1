"""Localised farmer-facing copy produced by the backend.

Every entry exists for each supported language, so a farmer reading a case in
their own language never sees a mixed-language advisory.
"""
LANGUAGES = ('en', 'hi', 'pa', 'or')

COPY = {
    'missing_inputs': {
        'en': {'diagnosis': 'Expert-confirmed diagnosis', 'weather': 'Current weather data', 'soil': 'Soil test values', 'description': 'Typed description of symptoms'},
        'hi': {'diagnosis': 'विशेषज्ञ-पुष्ट निदान', 'weather': 'वर्तमान मौसम डेटा', 'soil': 'मृदा परीक्षण मान', 'description': 'लक्षणों का लिखित विवरण'},
        'pa': {'diagnosis': 'ਮਾਹਰ-ਪੁਸ਼ਟ ਤਸ਼ਖ਼ੀਸ', 'weather': 'ਮੌਜੂਦਾ ਮੌਸਮ ਡੇਟਾ', 'soil': 'ਮਿੱਟੀ ਟੈਸਟ ਮੁੱਲ', 'description': 'ਲੱਛਣਾਂ ਦਾ ਲਿਖਤੀ ਵੇਰਵਾ'},
        'or': {'diagnosis': 'ବିଶେଷଜ୍ଞ-ନିଶ୍ଚିତ ନିଦାନ', 'weather': 'ବର୍ତ୍ତମାନର ପାଣିପାଗ ତଥ୍ୟ', 'soil': 'ମାଟି ପରୀକ୍ଷା ମୂଲ୍ୟ', 'description': 'ଲକ୍ଷଣର ଲିଖିତ ବର୍ଣ୍ଣନା'},
    },
    'assumptions_vision': {
        'en': ['Vision prediction comes from the bundled CNN model (Crop_pred_model.h5) on the uploaded image(s); it is not expert-verified.'],
        'hi': ['दृश्य भविष्यवाणी आपकी अपलोड की गई तस्वीर पर बंडल किए गए CNN मॉडल (Crop_pred_model.h5) से आती है; यह विशेषज्ञ-सत्यापित नहीं है।'],
        'pa': ['ਦ੍ਰਿਸ਼ ਭਵਿੱਖਬਾਣੀ ਤੁਹਾਡੇ ਅੱਪਲੋਡ ਕੀਤੇ ਫ਼ੋਟੋ ਤੇ ਬੰਡਲ ਕੀਤੇ CNN ਮਾਡਲ (Crop_pred_model.h5) ਤੋਂ ਆਉਂਦੀ ਹੈ; ਇਹ ਮਾਹਰ-ਤਸਦੀਕਸ਼ੁਦਾ ਨਹੀਂ ਹੈ।'],
        'or': ['ଦୃଶ୍ୟ ପୂର୍ବାନୁମାନ ଆପଣ ଅପଲୋଡ୍ କରିଥିବା ଛବି ଉପରେ ବଣ୍ଡଲ ହୋଇଥିବା CNN ମଡେଲ (Crop_pred_model.h5) ରୁ ଆସେ; ଏହା ବିଶେଷଜ୍ଞ-ଯାଞ୍ଚିତ ନୁହେଁ।'],
    },
    'assumptions_general': {
        'en': ['Crop, location and symptoms are farmer-reported, not independently verified.', 'No live vision, weather, soil OCR, or language-model inference was performed.'],
        'hi': ['फसल, स्थान और लक्षण किसान द्वारा बताए गए हैं, स्वतंत्र रूप से सत्यापित नहीं।', 'कोई लाइव दृश्य, मौसम, मृदा OCR या भाषा-मॉडल अनुमान नहीं किया गया।'],
        'pa': ['ਫ਼ਸਲ, ਸਥਾਨ ਅਤੇ ਲੱਛਣ ਕਿਸਾਨ ਵਲੋਂ ਦੱਸੇ ਗਏ ਹਨ, ਸਵਤੰਤਰ ਤੌਰ ਤੇ ਤਸਦੀਕ ਨਹੀਂ ਕੀਤੇ ਗਏ।', 'ਕੋਈ ਲਾਈਵ ਦ੍ਰਿਸ਼, ਮੌਸਮ, ਮਿੱਟੀ OCR ਜਾਂ ਭਾਸ਼ਾ-ਮਾਡਲ ਅਨੁਮਾਨ ਨਹੀਂ ਕੀਤਾ ਗਿਆ।'],
        'or': ['ଫସଲ, ସ୍ଥାନ ଓ ଲକ୍ଷଣ ଚାଷୀ ଦ୍ୱାରା ଜଣାଯାଇଛି, ସ୍ୱତନ୍ତ୍ର ଭାବେ ଯାଞ୍ଚ ହୋଇନାହିଁ।', 'କୌଣସି ଜୀବନ୍ତ ଦୃଶ୍ୟ, ପାଣିପାଗ, ମାଟି OCR କିମ୍ବା ଭାଷା-ମଡେଲ ଅନୁମାନ କରାଯାଇନାହିଁ।'],
    },
    'not_assessed': {
        'en': 'Not assessed',
        'hi': 'आकलन नहीं हुआ',
        'pa': 'ਮੁਲਾਂਕਣ ਨਹੀਂ ਹੋਇਆ',
        'or': 'ମୂଲ୍ୟାଙ୍କନ ହୋଇନାହିଁ',
    },
    'model_match': {
        'en': '% model match',
        'hi': '% मॉडल मेल',
        'pa': '% ਮਾਡਲ ਮੇਲ',
        'or': '% ମଡେଲ ମେଳ',
    },
    'expert_responded_title': {
        'en': 'Your expert has responded',
        'hi': 'आपके विशेषज्ञ ने जवाब दिया है',
        'pa': 'ਤੁਹਾਡੇ ਮਾਹਰ ਨੇ ਜਵਾਬ ਦਿੱਤਾ ਹੈ',
        'or': 'ଆପଣଙ୍କ ବିଶେଷଜ୍ଞ ଉତ୍ତର ଦେଇଛନ୍ତି',
    },
    'expert_responded_message': {
        'en': '{expert} reviewed your {crop} advisory.',
        'hi': '{expert} ने आपकी {crop} सलाह की समीक्षा की।',
        'pa': '{expert} ਨੇ ਤੁਹਾਡੀ {crop} ਸਲਾਹ ਦੀ ਸਮੀਖਿਆ ਕੀਤੀ।',
        'or': '{expert} ଆପଣଙ୍କ {crop} ପରାମର୍ଶ ସମୀକ୍ଷା କରିଛନ୍ତି।',
    },
    'reason_general': {
        'en': 'Unverified inputs; general guidance only',
        'hi': 'असत्यापित इनपुट; केवल सामान्य मार्गदर्शन',
        'pa': 'ਅਤਸਦੀਕਸ਼ੁਦਾ ਇਨਪੁਟ; ਸਿਰਫ਼ ਆਮ ਮਾਰਗਦਰਸ਼ਨ',
        'or': 'ଅଯାଞ୍ଚିତ ଇନପୁଟ୍; କେବଳ ସାଧାରଣ ମାର୍ଗଦର୍ଶନ',
    },
    'risk_reason': {
        'en': 'Insufficient verified inputs for a field-specific risk estimate.',
        'hi': 'खेत-विशिष्ट जोखिम अनुमान के लिए सत्यापित जानकारी अपर्याप्त है।',
        'pa': 'ਖੇਤ-ਵਿਸ਼ੇਸ਼ ਜੋਖਮ ਅੰਦਾਜ਼ੇ ਲਈ ਤਸਦੀਕਸ਼ੁਦਾ ਜਾਣਕਾਰੀ ਘੱਟ ਹੈ।',
        'or': 'ଜମି ଅନୁସାରେ ଜୋଖିମ ଅନୁମାନ ପାଇଁ ଯାଞ୍ଚିତ ସୂଚନା ଯଥେଷ୍ଟ ନାହିଁ।',
    },
    'general_advisory': {
        'or': {
            'title': 'ପହିଲେ ନିରୀକ୍ଷଣ କରନ୍ତୁ, ପରେ ଚିକିତ୍ସା ବାଛନ୍ତୁ',
            'summary': 'ଏହା ସାଧାରଣ କୃଷି ମାର୍ଗଦର୍ଶନ, ନିଦାନ ନୁହେଁ। ଉପଲବ୍ଧ ସୂଚନା ରୋଗ, ପୋଷକ ତତ୍ତ୍ୱର ଅଭାବ କିମ୍ବା ଫସଲ ଜୋଖିମକୁ ନିଶ୍ଚିତ କରିପାରିବ ନାହିଁ।',
            'steps': [
                'ପ୍ରଭାବିତ ଓ ସୁସ୍ଥ ଗଛଗୁଡ଼ିକୁ ଦେଖନ୍ତୁ। ଲକ୍ଷଣ କେବେ ଆରମ୍ଭ ହେଲା ଓ ସେଗୁଡ଼ି ବ୍ୟାପୁଛି କି, ଲେଖନ୍ତୁ।',
                'ପ୍ରାକୃତିକ ଆଲୋକରେ ପୂର୍ଣ୍ଣ ଗଛ ଏବଂ ପତ୍ରର ଦୁଇ ପାସି ଛବି ନିଅନ୍ତୁ। ସିଞ୍ଚାଇ ଓ ନିକଟତନ କୃଷି ଇନପୁଟ ସୂଚନା ବିଶେଷଜ୍ଞଙ୍କୁ ଦିଅନ୍ତୁ।',
                'ପ୍ରତିରୋଧ ଓ ପରିବେଶ କୀଟ ପ୍ରବନ୍ଧନକୁ ପ୍ରାଧାନ୍ୟତା ଦିଅନ୍ତୁ। କେବଳ ଲକ୍ଷଣ ଦେଖି କୀଟନାଶକ କିମ୍ବା ମାତ୍ରା ବାଛନ୍ତୁ ନାହିଁ।',
            ],
            'safety': 'କୀଟନାଶକ କିମ୍ବା ସାରର ମାତ୍ରା, ଅମଳ ପୂର୍ବାନୁମାନ କିମ୍ବା ଗ୍ୟାରେଣ୍ଟି ଦିଆଯାଏ ନାହିଁ। ଚିକିତ୍ସା ପୂର୍ବରୁ ସ୍ଥାନୀୟ କୃଷି ବିଶେଷଜ୍ଞଙ୍କୁ ସମ୍ପର୍କ କରନ୍ତୁ।',
        },
    },
}


def pick(language, key):
    """Localised entry for a key, falling back to English."""
    values = COPY[key]
    return values.get(language) or values['en']


def missing_labels(language):
    """Labels for the inputs a case is still missing."""
    return pick(language, 'missing_inputs')


GENERAL_ADVISORY = COPY['general_advisory']['or']
