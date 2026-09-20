/**
 * Read-aloud helper for the advisory result page.
 *
 * The spoken script is taken from the rendered diagnosis, crop prediction and
 * crop guidance sections, so the assistant always reads exactly what the page
 * shows (and in the language the farmer is already reading).
 */
export const SPOKEN_SECTION_TESTIDS = ['diagnosis-label', 'general-advisory-label', 'crop-prediction', 'crop-guidance'];
const CHUNK_LIMIT = 180;
const LANG_CODES: Record<string, string> = { en: 'en-IN', hi: 'hi-IN', pa: 'pa-IN', or: 'or-IN' };
export const speechLang = (language: string) => LANG_CODES[language] || 'en-IN';
const textOf = (element: Element) => {
  const parts: string[] = [];
  const walk = (node: Node) => {
    if (node.nodeType === 3) {
      const text = (node.nodeValue || '').replace(/\s+/g, ' ').trim();
      if (text) parts.push(text);
      return;
    }
    if (node.nodeType !== 1) return;
    node.childNodes.forEach(walk);
  };
  walk(element);
  return parts.join(' ');
};
/** Visible text of the diagnosis, crop prediction and crop guidance sections, in that order. */
export const collectSpokenText = (root: ParentNode = document) => SPOKEN_SECTION_TESTIDS
  .map(testid => root.querySelector(`[data-testid="${testid}"]`))
  .filter((element): element is Element => !!element)
  .map(textOf)
  .filter(Boolean)
  .join(' ')
  .replace(/\s+/g, ' ')
  .trim();
const splitLong = (text: string, limit: number): string[] => {
  const pieces: string[] = [];
  let rest = text;
  while (rest.length > limit) {
    const near = rest.lastIndexOf(' ', limit);
    const next = rest.indexOf(' ', limit);
    const cut = near > limit * 0.6 ? near : next;
    if (cut === -1) break;
    pieces.push(rest.slice(0, cut).trim());
    rest = rest.slice(cut).trim();
  }
  if (rest) pieces.push(rest);
  return pieces;
};
/** Sentences end with . ! ? or a danda (।), the full stop used by Hindi and Punjabi. */
const sentences = (text: string): string[] => {
  const parts = text.split(/([.!?\u0964])\s+/);
  const found: string[] = [];
  for (let i = 0; i < parts.length; i += 2) {
    const sentence = `${parts[i]}${parts[i + 1] || ''}`.trim();
    if (sentence) found.push(sentence);
  }
  return found;
};
/** Short utterances keep the browser from cutting a long script off part-way through. */
export const chunkText = (text: string, limit = CHUNK_LIMIT): string[] => {
  const chunks: string[] = [];
  for (const sentence of sentences(text)) {
    if (sentence.length > limit) {
      for (const piece of splitLong(sentence, limit)) {
        const last = chunks[chunks.length - 1];
        if (last && `${last} ${piece}`.length <= limit) chunks[chunks.length - 1] = `${last} ${piece}`;
        else chunks.push(piece);
      }
      continue;
    }
    const last = chunks[chunks.length - 1];
    if (last && `${last} ${sentence}`.length <= limit) chunks[chunks.length - 1] = `${last} ${sentence}`;
    else chunks.push(sentence);
  }
  return chunks;
};
/** Prefers the advisory-language voice, then the closest Indian English voice, then anything installed. */
export const pickVoice = (voices: SpeechSynthesisVoice[], lang: string): SpeechSynthesisVoice | undefined => {
  const base = lang.slice(0, 2).toLowerCase();
  const match = (code: string) => voices.find(v => v.lang.toLowerCase().replace('_', '-') === code);
  return match(lang.toLowerCase())
    || voices.find(v => v.lang.toLowerCase().startsWith(`${base}-`))
    || voices.find(v => v.lang.toLowerCase().startsWith(base))
    || (base === 'en' ? undefined : match('en-in') || voices.find(v => v.lang.toLowerCase().startsWith('en')))
    || voices[0];
};