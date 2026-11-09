// Nunn's Appendix II readings, built by scripts/build_app_readings.py.
import raw from '../assets/data/readings.json';
import { plain } from './data';

/** A paragraph piece: plain text, a Greek word [surface, key], or a footnote marker {n}. */
export type Piece = string | [string, string] | { n: string };
export type Para = { h: string } | { p: Piece[]; pg: number };
export type Reading = {
  slug: string; title: string; author: string; date: string; heading: string;
  intro: string[]; pages: [number, number]; words: number; taught: number;
  paras: Para[]; notes: Record<string, string>;
};

export const READINGS = raw as unknown as Reading[];
export const READING_BY_SLUG: Record<string, Reading> = Object.fromEntries(READINGS.map((r) => [r.slug, r]));

/** Keys (app cards) of every word in a reading, one per token. */
export function tokenKeys(r: Reading): string[] {
  const out: string[] = [];
  for (const para of r.paras) {
    if ('p' in para) for (const x of para.p) if (Array.isArray(x)) out.push(x[1].replace(/^\?/, ''));
  }
  return out;
}

/** Nunn's notes in this reading that mention the word (accents ignored). */
export function notesFor(r: Reading, surface: string): string[] {
  const w = plain(surface).replace(/['’᾽]/g, '');
  if (w.length < 3) return [];
  return Object.entries(r.notes)
    .filter(([, t]) => plain(t).split(/[^α-ω]+/).includes(w))
    .map(([id]) => id);
}
