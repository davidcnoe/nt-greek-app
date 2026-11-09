import { Link, Stack, useLocalSearchParams } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { State } from 'ts-fsrs';
import { Chip } from '../../components/ui';
import { WORDS } from '../../data';
import { useProgress } from '../../progress';
import { notesFor, READING_BY_SLUG, Reading } from '../../readings';
import { C, GREEK, S } from '../../theme';

type Sel = { kind: 'word'; surface: string; key: string } | { kind: 'note'; id: string } | null;

// One reading: tap a word for its gloss, or a raised number for Nunn's note.
export default function ReadingScreen() {
  const { slug } = useLocalSearchParams<{ slug: string }>();
  const r = slug ? READING_BY_SLUG[slug] : undefined;
  const p = useProgress();
  const [sel, setSel] = useState<Sel>(null);
  const noteNo = useMemo(() => Object.fromEntries(Object.keys(r?.notes ?? {}).map((id, i) => [id, i + 1])), [r]);
  if (!r) return <Text style={[S.body, { padding: 20 }]}>No reading “{slug}”.</Text>;

  const known = (k: string) => {
    const c = p.cards[k];
    return !!c && c.state !== State.New;
  };

  return (
    <View style={S.screen}>
      <Stack.Screen options={{ title: r.title }} />
      <ScrollView contentContainerStyle={[S.wrap, { paddingBottom: sel ? 260 : 40 }]}>
        <View style={{ gap: 6 }}>
          <Text style={S.small}>{`${r.author}${r.date ? ` · ${r.date}` : ''} · Nunn, pp. ${r.pages[0]}–${r.pages[1]}`}</Text>
          <Text style={[S.h2, { fontSize: 21 }]}>{r.title}</Text>
          {r.intro.map((t, i) => <Text key={i} style={S.small}>{t}</Text>)}
          <View style={[S.row, { flexWrap: 'wrap' }]}>
            <Legend color={C.ink} label="you know it" />
            <Legend color={C.accent} label="in the app, not yet learned" />
            <Legend color={C.muted} label="not in the app" />
          </View>
        </View>
        {r.paras.map((para, i) =>
          'h' in para ? (
            <Text key={i} style={[S.h2, { marginTop: 6 }]}>{para.h}</Text>
          ) : (
            <Text key={i} style={{ fontFamily: GREEK, fontSize: 21, lineHeight: 34, color: C.ink }}>
              {para.p.map((x, j) => {
                if (typeof x === 'string') return x;
                if (!Array.isArray(x)) {
                  return (
                    <Text key={j} onPress={() => setSel({ kind: 'note', id: x.n })}
                      style={{ fontSize: 12, color: C.accent, fontWeight: '700', fontFamily: undefined }}>
                      {` ${noteNo[x.n]} `}
                    </Text>
                  );
                }
                const [surface, raw] = x;
                const key = raw.replace(/^\?/, '');
                const inApp = !!WORDS[key];
                const isSel = sel?.kind === 'word' && sel.surface === surface && sel.key === raw;
                return (
                  <Text key={j} onPress={() => setSel({ kind: 'word', surface, key: raw })}
                    style={[
                      inApp && !known(key) ? { color: C.accent } : null,
                      !inApp ? { color: C.muted } : null,
                      isSel ? { backgroundColor: C.accentSoft } : null,
                    ]}>
                    {surface}
                  </Text>
                );
              })}
            </Text>
          ),
        )}
        <Text style={S.small}>Text and notes: H. P. V. Nunn, A Short Syntax of New Testament Greek (1920). Numbers refer to sections of his Syntax.</Text>
      </ScrollView>
      {sel ? <Panel r={r} sel={sel} noteNo={noteNo} onClose={() => setSel(null)} onNote={(id) => setSel({ kind: 'note', id })} /> : null}
    </View>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return <Text style={[S.small, { color, fontWeight: '600' }]}>{label}</Text>;
}

function Panel({ r, sel, noteNo, onClose, onNote }: {
  r: Reading; sel: NonNullable<Sel>; noteNo: Record<string, number>; onClose: () => void; onNote: (id: string) => void;
}) {
  let body: React.ReactNode;
  if (sel.kind === 'note') {
    body = (
      <>
        <Text style={S.small}>{`Nunn's note ${noteNo[sel.id]}`}</Text>
        <Text style={[S.body, { fontFamily: GREEK, fontSize: 18, lineHeight: 26 }]}>{r.notes[sel.id]}</Text>
      </>
    );
  } else {
    const guessed = sel.key.startsWith('?');
    const key = sel.key.replace(/^\?/, '');
    const w = WORDS[key];
    const related = notesFor(r, sel.surface);
    body = (
      <>
        <Text style={[S.greek, { fontSize: 26 }]}>
          {sel.surface}
          {w ? <Text style={[S.greek, { fontSize: 18, color: C.muted }]}>{`  ${guessed ? 'probably ' : ''}from ${key}`}</Text> : null}
        </Text>
        {w ? (
          <>
            <Text style={[S.body, { fontSize: 18 }]}>{w.g}</Text>
            <View style={[S.row, { flexWrap: 'wrap' }]}>
              <Chip text={`${w.c.toLocaleString()}× in NT`} />
              {w.m ? <Chip tone="moss" text="In Moss" /> : null}
            </View>
            <Link href={{ pathname: '/word/[form]', params: { form: key } }} style={[S.small, { color: C.accent, fontWeight: '700' }]}>
              Full entry, with Souter →
            </Link>
          </>
        ) : key.startsWith('~') ? (
          <Text style={S.body}>
            {guessed ? 'Probably from ' : 'From '}
            <Text style={S.greek}>{key.slice(1)}</Text>
            {', which is not in Metzger\'s list.'}
          </Text>
        ) : (
          <Text style={S.body}>A rare word: not in Metzger's list.</Text>
        )}
        {related.slice(0, 2).map((id) => (
          <Text key={id} onPress={() => onNote(id)} style={[S.small, { color: C.ink }]}>
            <Text style={{ color: C.accent, fontWeight: '700' }}>{`Nunn ${noteNo[id]}: `}</Text>
            {r.notes[id]}
          </Text>
        ))}
      </>
    );
  }
  return (
    <View style={{
      position: 'absolute', left: 0, right: 0, bottom: 0, backgroundColor: C.card, borderTopWidth: 1, borderColor: C.line,
      shadowColor: '#000', shadowOpacity: 0.12, shadowRadius: 12, elevation: 8,
    }}>
      <View style={{ width: '100%', maxWidth: 640, alignSelf: 'center', padding: 18, gap: 8 }}>
        {body}
        <Pressable onPress={onClose} accessibilityRole="button" style={[S.btnGhost, { marginTop: 4 }]}>
          <Text style={S.btnGhostText}>Close</Text>
        </Pressable>
      </View>
    </View>
  );
}
