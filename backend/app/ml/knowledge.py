"""Curated agronomy knowledge for the 35 model classes.

Keys mirror CLASS_LABELS in labels.py exactly. Severity is a general class
estimate (how damaging the condition typically is); per-request severity also
factors in model confidence and top-2 competition.
"""
CROP_INFO = {
    'Cauliflower': 'Cool-season brassica grown for its white curd. Thrives at 15–20 °C with steady moisture; heading is sensitive to heat and water stress.',
    'Cotton': 'Deep-rooted fibre crop with a 150–180 day season. Needs warm weather, well-drained soil and careful pest surveillance through squaring and boll formation.',
    'Maize': 'Fast-growing cereal needing full sun and warm temperatures (21–30 °C). Critical stages are knee-high growth, tasselling and grain fill, all of which demand steady moisture.',
    'Onion': 'Shallow-rooted allium grown for bulbs. Prefers cool early growth and dry, warm ripening; uniform irrigation and good drainage prevent most bulb rots.',
    'Potato': 'Cool-season tuber crop (15–25 °C). Hilled rows and even moisture produce uniform tubers; foliage health through the tuber-bulking stage decides yield.',
    'Rice': 'Semi-aquatic cereal grown in paddies or wet fields. Warm temperatures, clean seed and balanced fertiliser keep the crop vigorous through panicle initiation.',
    'Wheat': 'Temperate cereal sown in cool weather and harvested dry. Yield is set at tillering and grain fill; rusts and smuts are the main threats to watch from flag leaf onward.',
}

MAINTAIN = {
    'Cauliflower': ['Irrigate evenly (2.5 cm/week); never let heads dry out', 'Blanch curds by tying leaves when heads are golf-ball size', 'Rotate with non-brassicas for 2–3 years', 'Scout weekly for caterpillars and aphids on the underside of leaves'],
    'Cotton': ['Deep-plough and remove stubbles after picking to break pest cycles', 'Avoid excess nitrogen late in the season — it invites sucking pests', 'Monitor pheromone traps for bollworms twice a week in squaring/boll stages', 'Keep field edges and channels weed-free'],
    'Maize': ['Maintain uniform plant spacing and thin crowded seedlings early', 'Side-dress nitrogen at knee-high and again at tasselling', 'Weed the first 4–6 weeks — later competition costs most yield', 'Do not let water stand after heavy rain; drain low spots'],
    'Onion': ['Water lightly and often; stop irrigation 2 weeks before harvest', 'Avoid overhead watering in the evening — wet foliage overnight invites disease', 'Cure bulbs in shade with good airflow before storage', 'Remove and destroy any plants with diseased leaves immediately'],
    'Potato': ['Hill soil around plants when they are 15–20 cm tall', 'Irrigate evenly; fluctuating moisture causes misshapen tubers', 'Use certified disease-free seed tubers each season', 'Cut vines and harvest promptly once the crop matures to protect tubers'],
    'Rice': ['Keep a shallow, steady water level; drain only for weeding or top-dressing', 'Split nitrogen doses to avoid lush, disease-prone growth', 'Remove weed hosts and volunteer rice from bunds', 'Transplant at correct spacing for air movement through the canopy'],
    'Wheat': ['Sow certified seed at the recommended date and depth', 'Apply balanced NPK; excessive nitrogen prolongs susceptibility', 'Irrigate at crown-root, tillering, jointing and grain-fill stages', 'Scout from flag-leaf stage for rust pustules and smut symptoms'],
}

DISEASES = {
    'Cauliflower_Bacterial_Spot_Rot': {
        'name': 'Bacterial spot / rot', 'severity': 'moderate',
        'early': ['Small, angular, water-soaked spots on leaves that turn yellow-edged', 'Spots merge into large dead patches; heads develop sunken brown flecks'],
        'actions': ['Remove and destroy infected leaves — do not compost', 'Spray copper-based bactericide at 5–7 day intervals', 'Avoid overhead irrigation; water at the base', 'Improve spacing for airflow and rotate out of brassicas next season'],
    },
    'Cauliflower_Black_Rot': {
        'name': 'Black rot (Xanthomonas)', 'severity': 'high',
        'early': ['Yellow V-shaped lesions at leaf margins with blackened veins', 'Stunting and premature leaf drop starting from lower leaves'],
        'actions': ['Use certified, hot-water-treated seed only', 'Remove and destroy symptomatic plants immediately', 'Copper sprays slow spread but cannot cure it', 'Adopt a 2–3 year rotation away from brassicas'],
    },
    'Cauliflower_Downy_Mildew': {
        'name': 'Downy mildew', 'severity': 'moderate',
        'early': ['Yellow angular patches on upper leaf surface', 'Grey-purple fuzzy growth on the underside in humid mornings'],
        'actions': ['Spray a recommended fungicide (e.g. metalaxyl) at first sign', 'Water in the morning so leaves dry quickly', 'Increase plant spacing and weed control to cut humidity', 'Remove crop debris after harvest'],
    },
    'Cauliflower_Healthy': {
        'name': 'Healthy plant', 'severity': 'none',
        'early': [], 'actions': ['No treatment needed — keep up the current care routine'],
    },
    'Cauliflower_Insect_Hole': {
        'name': 'Insect feeding damage', 'severity': 'mild',
        'early': ['Irregular holes in leaves', 'Dark green frass (droppings) on leaves and in the head'],
        'actions': ['Hand-pick caterpillars in small plots; encourage birds', 'Spray Bt (Bacillus thuringiensis) or neem on young larvae', 'Use row covers to keep moths off young plants', 'Scout twice weekly — holes appear before damage becomes serious'],
    },
    'Cotton_Aphids': {
        'name': 'Aphid infestation', 'severity': 'moderate',
        'early': ['Clusters of small soft insects on leaf undersides and shoots', 'Sticky honeydew, sooty mould and curled leaves'],
        'actions': ['Place yellow sticky traps and spray neem oil early', 'Conserve natural enemies (ladybirds, chrysopids) — avoid broad-spectrum sprays', 'If populations explode, use a selective insecticide rotated by mode of action', 'Avoid excess nitrogen which makes lush, attractive growth'],
    },
    'Cotton_Bacterial_Blight': {
        'name': 'Bacterial blight', 'severity': 'high',
        'early': ['Angular, water-soaked leaf spots with yellow halos', 'Black lesions on stems ("black arm") and boll rot'],
        'actions': ['Use acid-delinted, disease-free seed', 'Remove and burn infected plants', 'Copper sprays reduce spread in young crops', 'Rotate with non-hosts and plough in debris after harvest'],
    },
    'Cotton_Curl_Virus': {
        'name': 'Leaf curl virus', 'severity': 'high',
        'early': ['Upward curling and thickening of young leaves with vein swelling', 'Yellow mottling and stunted new growth'],
        'actions': ['Remove and destroy infected plants — there is no cure', 'Control the whitefly vector with sticky traps and judicious insecticide rotation', 'Plant resistant varieties next season', 'Keep field and bunds free of volunteer cotton and weed hosts'],
    },
    'Cotton_Fussarium_Wilt': {
        'name': 'Fusarium wilt', 'severity': 'high',
        'early': ['Yellowing and wilting starting on one side of the plant', 'Brown streaking inside the stem visible when split'],
        'actions': ['There is no chemical cure — pull and destroy affected plants', 'Improve drainage; the fungus favours wet soils', 'Rotate with non-hosts (e.g. cereals) for 2–3 years', 'Grow resistant varieties in known wilt soils'],
    },
    'Cotton_Healthy': {
        'name': 'Healthy plant', 'severity': 'none',
        'early': [], 'actions': ['No treatment needed — continue monitoring and balanced feeding'],
    },
    'Cotton_Powdery_Mildew': {
        'name': 'Powdery mildew', 'severity': 'mild',
        'early': ['White, talc-like powdery patches on the upper leaf surface', 'Leaves yellow and drop prematurely in heavy infections'],
        'actions': ['Spray sulphur or a triazole fungicide at first appearance', 'Improve airflow by spacing and weeding', 'Avoid late nitrogen that keeps leaves soft', 'Remove heavily infected lower leaves'],
    },
    'Cotton_Target_Spot': {
        'name': 'Target spot (Areolar leaf spot)', 'severity': 'moderate',
        'early': ['Round brown spots with concentric rings like a target', 'Spots drop out, giving a shot-holed look; older leaves affected first'],
        'actions': ['Remove lower infected leaves and destroy them', 'Spray a protectant fungicide if the disease is climbing the plant', 'Avoid dense canopies — thin or manage nitrogen', 'Do not work in the field when foliage is wet'],
    },
    'Maize_Healthy': {
        'name': 'Healthy plant', 'severity': 'none',
        'early': [], 'actions': ['No treatment needed — maintain the fertility and weed plan'],
    },
    'Maize_Leaf_Blight': {
        'name': 'Southern corn leaf blight', 'severity': 'moderate',
        'early': ['Small tan, rectangular lesions between leaf veins', 'Lesions lengthen rapidly in warm humid weather, drying whole leaves'],
        'actions': ['Spray a recommended fungicide (e.g. mancozeb) at early lesions', 'Rotate with non-cereals and bury previous crop residue', 'Choose resistant hybrids next season', 'Improve drainage and avoid very dense stands'],
    },
    'Maize_Leaf_Spot': {
        'name': 'Leaf spot (Cercospora type)', 'severity': 'moderate',
        'early': ['Small round to oval brown spots with yellow halos', 'Spots darken with age and may join into streaks'],
        'actions': ['Apply a labelled fungicide when 5–10% of leaves show spots', 'Plough under stubble to reduce carry-over inoculum', 'Rotate away from maize for a season', 'Keep nutrition balanced — stressed crops spot worst'],
    },
    'Maize_Maize_Rust': {
        'name': 'Common rust', 'severity': 'moderate',
        'early': ['Tiny round, cinnamon-brown pustules scattered on both leaf surfaces', 'Powdery rust spores rub off on your hand when wiped'],
        'actions': ['Spray a systemic fungicide (triazole/strobilurin) before pustules cover the flag leaf', 'Plant resistant hybrids for the next cycle', 'Avoid late sowing, which peaks rust pressure', 'Do not irrigate from infected to clean blocks; wash hands/tools between'],
    },
    'Maize_Northern_Leaf_Blight': {
        'name': 'Northern corn leaf blight', 'severity': 'high',
        'early': ['Long, cigar-shaped grey-green lesions up to 15 cm along the leaf', 'Lesions turn tan-brown and leaves wither from the tip'],
        'actions': ['Apply fungicide at first lesions, before silking if possible', 'Grow resistant hybrids — genetics is the cheapest control', 'Rotate and plough in infected residue', 'Ensure good airflow and drainage'],
    },
    'Maize_Streak_Virus': {
        'name': 'Maize streak virus', 'severity': 'high',
        'early': ['Chlorotic, broken stripes running parallel along young leaves', 'Plants stunted with narrow, yellow leaves'],
        'actions': ['Rogue out infected plants immediately — no cure exists', 'Control leafhopper vectors with early plantings and, if needed, seed treatment/insecticide', 'Avoid planting next to old maize fields', 'Use certified streak-resistant seed next season'],
    },
    'Onion_Busuk_Daun': {
        'name': 'Purple blotch / leaf blight (Busuk daun)', 'severity': 'moderate',
        'early': ['Small white sunken spots that enlarge into purple-centred lesions', 'Yellow halo around lesions; leaf tips die back'],
        'actions': ['Spray a systemic fungicide (e.g. tebuconazole/mancozeb) on a 7-day cycle in wet weather', 'Avoid overhead watering and crowded beds', 'Remove infected leaves from the field', 'Rotate with non-alliums and practise clean seed'],
    },
    'Onion_Healthy': {
        'name': 'Healthy plant', 'severity': 'none',
        'early': [], 'actions': ['No treatment needed — keep irrigation steady and beds weed-free'],
    },
    'Onion_Moler': {
        'name': 'Onion molder / white rot complex (Moler)', 'severity': 'high',
        'early': ['Yellowing and wilting of leaf tips in patches', 'White fungal growth with small black sclerotia at the bulb base'],
        'actions': ['Lift and destroy (do not compost) infected bulbs with surrounding soil', 'Avoid infested fields for 5+ years — sclerotia persist', 'Improve drainage; the disease thrives in wet, cool soil', 'Treat seed/sets with a registered fungicide before planting'],
    },
    'Onion_Trotol': {
        'name': 'Onion thrips damage (Trotol)', 'severity': 'moderate',
        'early': ['Silvery-white streaks and speckles along leaves', 'Tiny dark insects at leaf bases when unfolded; black frass spots'],
        'actions': ['Spray neem or a registered insecticide at 5–10 thrips per leaf', 'Blue/yellow sticky traps to monitor and reduce adults', 'Avoid overlapping onion plantings nearby', 'Keep plants well watered — drought-stressed crops suffer more'],
    },
    'Potato_Early_Blight': {
        'name': 'Early blight (Alternaria)', 'severity': 'moderate',
        'early': ['Brown spots with concentric rings ("target spots") on older leaves', 'Yellow halo around lesions; leaves drop from the bottom up'],
        'actions': ['Start a protectant fungicide programme (chlorothalonil/mancozeb) and keep it on schedule', 'Remove and destroy infected lower leaves', 'Maintain even watering and balanced fertility — stressed plants blight first', 'Rotate potatoes with cereals/legumes for 2 years'],
    },
    'Potato_Healthy': {
        'name': 'Healthy plant', 'severity': 'none',
        'early': [], 'actions': ['No treatment needed — keep hilling, watering and scouting on schedule'],
    },
    'Potato_Late_Blight': {
        'name': 'Late blight (Phytophthora infestans)', 'severity': 'severe',
        'early': ['Water-soaked, pale-green to brown blotches with pale yellow margins', 'White fuzzy spore growth on leaf undersides in humid mornings; spread within days'],
        'actions': ['EMERGENCY — spray a systemic oomycete fungicide (e.g. cymoxanil+mancozeb, metalaxyl) immediately and repeat every 5–7 days', 'Rogue out and destroy (burn/bury) badly infected plants', 'Do not irrigate overhead during infection periods', 'Harvest only after vines are fully dead and 2+ weeks of dry weather; inspect tubers for rot'],
    },
    'Rice_Bacterial_Blight': {
        'name': 'Bacterial leaf blight', 'severity': 'high',
        'early': ['Wavy-edged yellow-to-grey lesions starting at leaf tips', 'Milky droplets that dry into small amber beads along leaf edges'],
        'actions': ['No curative chemical — drain briefly and cut excess nitrogen', 'Spray copper compounds to limit spread on young infections', 'Use resistant varieties and clean seed next season', 'Remove infected stubble and volunteer rice'],
    },
    'Rice_Blast': {
        'name': 'Rice blast (Pyricularia)', 'severity': 'severe',
        'early': ['Diamond-shaped lesions with grey centres and brown margins on leaves', 'Neck nodes blacken at panicle emergence — panicles break or turn white ("whiteheads")'],
        'actions': ['Spray tricyclazole or azoxystrobin at first leaf lesions and again at heading', 'Cut nitrogen and keep water steady — dry/flood cycles worsen blast', 'Remove collapsed panicles and stubble after harvest', 'Plant resistant varieties in blast-prone fields'],
    },
    'Rice_Brown_Spot': {
        'name': 'Brown spot', 'severity': 'moderate',
        'early': ['Small round brown spots with grey or yellow centres on leaves', 'Many spots per leaf signal poor soil nutrition rather than pure disease'],
        'actions': ['Correct soil fertility first — brown spot is a hunger disease; apply balanced NPK with potash', 'Spray a protectant fungicide if lesions exceed 5% of leaf area', 'Use clean, well-filled seed; discard discoloured grain', 'Rotate and remove infected straw'],
    },
    'Rice_Tungro': {
        'name': 'Tungro virus', 'severity': 'severe',
        'early': ['Yellow-orange discolouration starting from leaf tips with dark brown dots', 'Plants stunted with poor, late panicle production'],
        'actions': ['Rogue infected plants — no chemical cure exists', 'Control the green leafhopper vector: early border spraying and neem/registered insecticide', 'Plant resistant varieties and synchronise planting dates across the area', 'Remove stubble and volunteer rice between seasons'],
    },
    'Wheat_Brown_Rust': {
        'name': 'Brown/leaf rust', 'severity': 'moderate',
        'early': ['Small round orange-brown pustules scattered irregularly on leaves', 'Rust dust rubs off easily; pustules cluster on lower leaves first'],
        'actions': ['Spray a triazole fungicide before pustules reach the flag leaf', 'Scout weekly and re-treat in 3 weeks if new pustules appear', 'Choose resistant varieties for the next sowing', 'Avoid excessive nitrogen and late sowing'],
    },
    'Wheat_Crown_Root_Rot': {
        'name': 'Crown/root rot', 'severity': 'moderate',
        'early': ['Chocolate-brown lesions on the stem base just above the soil line', 'Whiteheads with empty or shrivelled grain and rotted roots'],
        'actions': ['No in-season cure — support the crop with balanced nutrition (zinc and potash help)', 'Avoid alternating water stress and waterlogging', 'Rotate out of cereals 1–2 seasons; treat seed with a registered fungicide', 'Remove stubble and manage grass weeds that host the fungus'],
    },
    'Wheat_Healthy': {
        'name': 'Healthy plant', 'severity': 'none',
        'early': [], 'actions': ['No treatment needed — continue the irrigation and nutrition schedule'],
    },
    'Wheat_Loose_Smut': {
        'name': 'Loose smut', 'severity': 'high',
        'early': ['Black sooty powder replacing grain in the ear, emerging slightly early', 'Spores blow away leaving a bare spike'],
        'actions': ['No field control — the infection is inside the seed', 'Collect and burn smutted ears before spores spread', 'Next season use certified seed or hot-water/seed treatment to kill embryo-borne smut', 'Do not save seed from smutted plots'],
    },
    'Wheat_Septoria': {
        'name': 'Septoria leaf blotch', 'severity': 'moderate',
        'early': ['Grey-brown irregular blotches speckled with tiny black dots (pycnidia)', 'Blotch creeps up the plant from the lowest leaves in wet weather'],
        'actions': ['Spray a triazole/SDHI fungicide when the blotch threatens the flag leaf', 'Bury stubble and rotate away from wheat', 'Improve airflow; avoid very thick stands', 'Scout after each wet spell — rain spreads spores upward'],
    },
    'Wheat_Yellow_Rust': {
        'name': 'Yellow/stripe rust', 'severity': 'high',
        'early': ['Narrow yellow stripes of small pustules running along leaf veins', 'Yellow powder on fingers after wiping a leaf; stripes merge into yellow patches'],
        'actions': ['Spray a triazole fungicide promptly — yellow rust explodes in cool, humid spells', 'Re-inspect 10–14 days after spraying and re-treat if fresh pustules appear', 'Plant resistant varieties for the next season', 'Scout the whole field and nearby plots; rust moves in waves'],
    },
}

SEVERITY_WEIGHT = {'none': 0.0, 'mild': 0.25, 'moderate': 0.55, 'high': 0.8, 'severe': 0.95}


def guidance_for(label: str, confidence: float, top2: float) -> dict:
    """Build the full advisory payload for one prediction."""
    key = label or ''
    entry = DISEASES.get(key)
    if entry is None:
        stem = key.rsplit('_', 1)[0]
        entry = DISEASES.get(stem + '_Healthy') if stem in CROP_INFO else None
    if entry is None:
        return {}
    crop = key.split('_', 1)[0] if '_' in key else key
    base = SEVERITY_WEIGHT.get(entry['severity'], 0.4)
    margin = max(0.0, min(1.0, 1.0 - top2))
    estimate = round(base * (0.5 + 0.5 * confidence * margin), 2)
    is_healthy = entry['severity'] == 'none'
    return {
        'crop': crop,
        'crop_info': CROP_INFO.get(crop, ''),
        'disease': entry['name'],
        'severity': entry['severity'],
        'severity_estimate': 0.0 if is_healthy else estimate,
        'severity_pct': 0 if is_healthy else int(round(estimate * 100)),
        'maintain': MAINTAIN.get(crop, []),
        'early_signs': entry['early'],
        'actions': entry['actions'],
        'urgency': 'none' if is_healthy else 'immediate' if entry['severity'] == 'severe' else 'soon' if entry['severity'] == 'high' and confidence > 0.6 else 'routine',
    }
