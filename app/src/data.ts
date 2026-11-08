// App data: built by scripts/build_app_data.py from Metzger (1946), Souter (1916), Moss (1893),
// and MorphGNT frequencies. Cards are keyed by Metzger's own form of the word.
import raw from '../assets/data/lexicon.json';

export type Word = {
  l: string;   // SBLGNT lemma the form is counted under
  c: number;   // NT occurrences of that lemma
  r: number;   // frequency rank of the lemma
  g: string;   // card gloss (Metzger 1946)
  gs: string;  // gloss source
  gr: string;  // grammatical info (genitive, article, adjective endings)
  d: string;   // Metzger's English derivative / memory aid
  t: string;   // Metzger's frequency heading
  f: number | null; // root family id
  m: boolean;  // in Moss's First Greek Reader vocabulary
  mg: string;  // Moss's meaning
  s: string;   // Souter's entry (OCR text, being proofread)
};

export type Family = { id: number; root: string | null; gloss: string | null; members: string[] };

export type Unit = {
  id: string;
  kind: 'family' | 'frequency';
  title: string;
  subtitle: string;
  family?: number;
  words: string[];
};

type Data = {
  meta: { nt_tokens: number; built: string; sources: string[] };
  words: Record<string, Word>;
  families: Family[];
  units: Unit[];
};

const data = raw as unknown as Data;

export const META = data.meta;
export const WORDS = data.words;
export const FAMILIES: Record<number, Family> = Object.fromEntries(data.families.map((f) => [f.id, f]));
export const UNITS = data.units;
export const UNIT_INDEX: Record<string, number> = Object.fromEntries(UNITS.map((u, i) => [u.id, i]));

/** Lower-case Greek without accents, breathings, or iota subscripts; final sigma as σ. */
export function plain(s: string): string {
  return s
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/ς/g, 'σ');
}

const TRANSLIT: Record<string, string> = {
  a: 'α', b: 'β', g: 'γ', d: 'δ', e: 'ε', z: 'ζ', h: 'η', q: 'θ', i: 'ι', k: 'κ', l: 'λ', m: 'μ',
  n: 'ν', x: 'ξ', o: 'ο', p: 'π', r: 'ρ', s: 'σ', t: 'τ', u: 'υ', f: 'φ', c: 'χ', y: 'ψ', w: 'ω',
};

/** Latin-letter input to Greek (Beta Code style letters), for typing without a Greek keyboard. */
export function latinToGreek(s: string): string {
  return s
    .toLowerCase()
    .replace(/th/g, 'θ').replace(/ph/g, 'φ').replace(/ch/g, 'χ').replace(/ps/g, 'ψ')
    .split('')
    .map((ch) => TRANSLIT[ch] ?? ch)
    .join('');
}

export type Hit = { form: string; why: 'greek' | 'english' | 'souter' };

/** Search by Greek (accents optional), Latin transliteration, or English. */
export function search(query: string, limit = 60): Hit[] {
  const q = query.trim();
  if (!q) return [];
  const isGreek = /[Ͱ-Ͽἀ-῿]/.test(q);
  const g = plain(isGreek ? q : latinToGreek(q));
  const e = q.toLowerCase();
  const out: Hit[] = [];
  const seen = new Set<string>();
  const forms = Object.keys(WORDS).sort((a, b) => WORDS[a].r - WORDS[b].r);
  const push = (form: string, why: Hit['why']) => {
    if (!seen.has(form)) {
      seen.add(form);
      out.push({ form, why });
    }
  };
  for (const f of forms) if (plain(f).startsWith(g)) push(f, 'greek');
  if (!isGreek) {
    const re = new RegExp(`\\b${e.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i');
    for (const f of forms) if (re.test(WORDS[f].g) || re.test(WORDS[f].mg)) push(f, 'english');
    for (const f of forms) if (re.test(WORDS[f].s)) push(f, 'souter');
  }
  return out.slice(0, limit);
}

export const TOTAL_LEMMA_TOKENS = META.nt_tokens;
