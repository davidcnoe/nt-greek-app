// Learner progress: one FSRS card per word, completed units, and settings.
// Saved with AsyncStorage (localStorage on the web).
import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Card, createEmptyCard, fsrs, generatorParameters, Grade, Rating, State } from 'ts-fsrs';
import { TOTAL_LEMMA_TOKENS, UNITS, WORDS } from './data';

const KEY = 'nt-greek-app/progress/v1';
const scheduler = fsrs(generatorParameters({ enable_fuzz: true, request_retention: 0.9 }));

type Settings = { mossGraduate: boolean };
type Saved = { cards: Record<string, Card>; done: string[]; settings: Settings };

const EMPTY: Saved = { cards: {}, done: [], settings: { mossGraduate: false } };

function revive(c: Card): Card {
  return { ...c, due: new Date(c.due), last_review: c.last_review ? new Date(c.last_review) : undefined };
}

type Ctx = {
  ready: boolean;
  cards: Record<string, Card>;
  done: Set<string>;
  settings: Settings;
  grade: (form: string, rating: Grade) => void;
  finishUnit: (unitId: string) => void;
  setMossGraduate: (on: boolean) => void;
  due: (now?: Date) => string[];
  preview: (form: string) => Record<Grade, Date>;
  coverage: () => { known: number; familiar: number };
  nextUnit: () => number;
  reset: () => void;
};

const ProgressContext = createContext<Ctx | null>(null);

export function ProgressProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<Saved>(EMPTY);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const s = await AsyncStorage.getItem(KEY);
        if (s) {
          const p = JSON.parse(s) as Saved;
          const cards: Record<string, Card> = {};
          for (const [k, v] of Object.entries(p.cards ?? {})) cards[k] = revive(v);
          setState({ cards, done: p.done ?? [], settings: { ...EMPTY.settings, ...p.settings } });
        }
      } catch {
        // Storage unavailable: start fresh; progress lives in memory for this session.
      }
      setReady(true);
    })();
  }, []);

  useEffect(() => {
    if (!ready) return;
    AsyncStorage.setItem(KEY, JSON.stringify(state)).catch(() => {});
  }, [state, ready]);

  const grade = useCallback((form: string, rating: Grade) => {
    setState((s) => {
      const now = new Date();
      const card = s.cards[form] ?? createEmptyCard(now);
      const next = scheduler.next(card, now, rating).card;
      return { ...s, cards: { ...s.cards, [form]: next } };
    });
  }, []);

  const finishUnit = useCallback((unitId: string) => {
    setState((s) => (s.done.includes(unitId) ? s : { ...s, done: [...s.done, unitId] }));
  }, []);

  const setMossGraduate = useCallback((on: boolean) => {
    setState((s) => ({ ...s, settings: { ...s.settings, mossGraduate: on } }));
  }, []);

  const due = useCallback(
    (now = new Date()) =>
      Object.entries(state.cards)
        .filter(([, c]) => c.state !== State.New && c.due <= now)
        .sort((a, b) => a[1].due.getTime() - b[1].due.getTime())
        .map(([k]) => k),
    [state.cards],
  );

  const preview = useCallback(
    (form: string) => {
      const now = new Date();
      const card = state.cards[form] ?? createEmptyCard(now);
      const p = scheduler.repeat(card, now);
      return {
        [Rating.Again]: p[Rating.Again].card.due,
        [Rating.Hard]: p[Rating.Hard].card.due,
        [Rating.Good]: p[Rating.Good].card.due,
        [Rating.Easy]: p[Rating.Easy].card.due,
      } as Record<Grade, Date>;
    },
    [state.cards],
  );

  // Share of NT running words covered: each SBLGNT lemma counted once.
  const coverage = useCallback(() => {
    const known = new Set<string>();
    const familiar = new Set<string>();
    for (const [form, c] of Object.entries(state.cards)) {
      // Any word studied in a lesson counts (learning or review stage).
      if (c.state !== State.New && WORDS[form]) known.add(WORDS[form].l);
    }
    if (state.settings.mossGraduate) {
      for (const w of Object.values(WORDS)) if (w.m && !known.has(w.l)) familiar.add(w.l);
    }
    const count = (set: Set<string>) => {
      const seen = new Map<string, number>();
      for (const w of Object.values(WORDS)) if (set.has(w.l)) seen.set(w.l, w.c);
      let n = 0;
      seen.forEach((v) => (n += v));
      return n / TOTAL_LEMMA_TOKENS;
    };
    return { known: count(known), familiar: count(familiar) };
  }, [state.cards, state.settings.mossGraduate]);

  const nextUnit = useCallback(() => {
    const i = UNITS.findIndex((u) => !state.done.includes(u.id));
    return i === -1 ? UNITS.length - 1 : i;
  }, [state.done]);

  const reset = useCallback(() => setState(EMPTY), []);

  const value = useMemo<Ctx>(
    () => ({
      ready, cards: state.cards, done: new Set(state.done), settings: state.settings,
      grade, finishUnit, setMossGraduate, due, preview, coverage, nextUnit, reset,
    }),
    [ready, state, grade, finishUnit, setMossGraduate, due, preview, coverage, nextUnit, reset],
  );
  return <ProgressContext.Provider value={value}>{children}</ProgressContext.Provider>;
}

export function useProgress(): Ctx {
  const c = useContext(ProgressContext);
  if (!c) throw new Error('useProgress outside ProgressProvider');
  return c;
}

export function untilText(d: Date): string {
  const mins = Math.max(1, Math.round((d.getTime() - Date.now()) / 60000));
  if (mins < 60) return `${mins} min`;
  const hours = Math.round(mins / 60);
  if (hours < 24) return `${hours} h`;
  const days = Math.round(hours / 24);
  if (days < 31) return `${days} d`;
  return `${Math.round(days / 30)} mo`;
}
