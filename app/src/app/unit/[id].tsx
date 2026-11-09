import { router, Stack, useLocalSearchParams } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { Rating } from 'ts-fsrs';
import { Answer, Button, Chip, Headword, Screen } from '../../components/ui';
import { FAMILIES, UNIT_INDEX, UNITS, WORDS } from '../../data';
import { useProgress } from '../../progress';
import { C, S } from '../../theme';

// A lesson: first study the words together (a family is learned as a family), then recall each
// one. Words missed go to the back of the queue until recalled once; every answer is recorded
// in the spaced-repetition schedule.
export default function UnitScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const unit = UNITS[UNIT_INDEX[id ?? ''] ?? 0];
  const p = useProgress();
  const [phase, setPhase] = useState<'study' | 'recall' | 'done'>('study');
  const [queue, setQueue] = useState<string[]>([]);
  const [shown, setShown] = useState(false);
  const [missed, setMissed] = useState<Set<string>>(new Set());
  const fam = unit.family != null ? FAMILIES[unit.family] : null;
  const words = useMemo(() => unit.words.filter((w) => WORDS[w]), [unit]);

  const start = () => {
    setQueue([...words].sort(() => Math.random() - 0.5));
    setShown(false);
    setPhase('recall');
  };

  const answer = (knew: boolean) => {
    const [cur, ...rest] = queue;
    p.grade(cur, knew ? Rating.Good : Rating.Again);
    if (!knew) setMissed((m) => new Set(m).add(cur));
    const next = knew ? rest : [...rest, cur];
    setShown(false);
    if (next.length === 0) {
      p.finishUnit(unit.id);
      setPhase('done');
    } else setQueue(next);
  };

  if (phase === 'study') {
    return (
      <Screen>
        
        <View style={S.card}>
          <Text style={S.h1}>{unit.title}</Text>
          {fam?.root ? (
            <Text style={S.body}>
              The words below share the root {fam.root}{fam.gloss ? `, “${fam.gloss}”` : ''}. Learn them together:
              each one is the root plus a prefix or a suffix.
            </Text>
          ) : (
            <Text style={S.body}>
              {unit.kind === 'frequency'
                ? `Common words from Metzger's list (${unit.subtitle}). Read each one aloud and connect it to its English cousin.`
                : unit.subtitle}
            </Text>
          )}
        </View>
        {words.map((form) => {
          const w = WORDS[form];
          return (
            <View key={form} style={S.card}>
              <View style={[S.row, { justifyContent: 'space-between' }]}>
                <Headword form={form} size={24} />
                {p.settings.mossGraduate && w.m ? <Chip tone="moss" text="Moss" /> : null}
              </View>
              <Text style={S.body}>{w.g}</Text>
              {w.d ? <Text style={S.small}>Cf. {w.d}</Text> : null}
              <Text style={S.small}>{w.c.toLocaleString()} times in the New Testament</Text>
            </View>
          );
        })}
        <Button title="I've studied these. Test me" onPress={start} />
      </Screen>
    );
  }

  if (phase === 'done') {
    const i = UNIT_INDEX[unit.id];
    const next = UNITS[i + 1];
    return (
      <Screen>
        <View style={S.card}>
          <Text style={S.h1}>Lesson complete</Text>
          <Text style={S.body}>
            {words.length - missed.size} of {words.length} recalled on the first try. These words now come back for
            review just before you would forget them.
          </Text>
        </View>
        {next ? <Button title={`Next: ${next.title}`} onPress={() => router.replace({ pathname: '/unit/[id]', params: { id: next.id } })} /> : null}
        <Button ghost title="Home" onPress={() => router.dismissAll()} />
      </Screen>
    );
  }

  const cur = queue[0];
  const w = WORDS[cur];
  return (
    <Screen>
      <Text style={S.small}>{queue.length} to go</Text>
      <Pressable onPress={() => setShown(true)} style={[S.card, { minHeight: 220, justifyContent: 'center', gap: 16 }]}>
        <Headword form={cur} size={36} />
        {shown ? <Answer form={cur} w={w} moss={p.settings.mossGraduate} /> : <Text style={S.small}>Say the meaning, then tap to check.</Text>}
      </Pressable>
      {shown ? (
        <View style={S.row}>
          <View style={{ flex: 1 }}><Button ghost title="Missed it" onPress={() => answer(false)} /></View>
          <View style={{ flex: 1 }}><Button title="Knew it" onPress={() => answer(true)} /></View>
        </View>
      ) : (
        <Button title="Show meaning" onPress={() => setShown(true)} />
      )}
      {fam?.root ? <Text style={[S.small, { color: C.muted }]}>Root {fam.root}: the family's shared meaning is “{fam.gloss}”.</Text> : null}
    </Screen>
  );
}
