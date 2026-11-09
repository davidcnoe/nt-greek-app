import { router } from 'expo-router';
import React from 'react';
import { ActivityIndicator, Text, View } from 'react-native';
import { Button, Chip, Meter, Screen } from '../components/ui';
import { UNITS, WORDS } from '../data';
import { useProgress } from '../progress';
import { C, S } from '../theme';

export default function Home() {
  const p = useProgress();
  if (!p.ready) {
    return (
      <View style={[S.screen, { justifyContent: 'center' }]}>
        <ActivityIndicator color={C.accent} />
      </View>
    );
  }
  const due = p.due().length;
  const cov = p.coverage();
  const i = p.nextUnit();
  const unit = UNITS[i];
  const allDone = p.done.size >= UNITS.length;
  const mossInUnit = unit.words.filter((w) => WORDS[w]?.m).length;

  return (
    <Screen>
      <View style={S.card}>
        <Text style={S.h2}>Your New Testament</Text>
        <Meter known={cov.known} familiar={cov.familiar} />
      </View>

      <View style={S.card}>
        <Text style={S.small}>{allDone ? 'Path complete' : `Next lesson · ${i + 1} of ${UNITS.length}`}</Text>
        <Text style={S.h1}>{unit.title}</Text>
        <Text style={S.body}>{unit.subtitle}</Text>
        <Text style={[S.greek, { fontSize: 18, color: C.muted }]}>{unit.words.join(', ')}</Text>
        <View style={[S.row, { flexWrap: 'wrap' }]}>
          <Chip text={unit.kind === 'family' ? 'Root family' : 'Frequency list'} />
          <Chip text={`${unit.words.length} words`} />
          {p.settings.mossGraduate && mossInUnit > 0 ? <Chip tone="moss" text={`${mossInUnit} from Moss`} /> : null}
        </View>
        <Button title={allDone ? 'Review the last lesson' : 'Start lesson'} onPress={() => router.push({ pathname: '/unit/[id]', params: { id: unit.id } })} />
      </View>

      <View style={S.card}>
        <Text style={S.h2}>Review</Text>
        <Text style={S.body}>{due === 0 ? 'Nothing due. Well done.' : `${due} word${due === 1 ? '' : 's'} due now.`}</Text>
        <Button title="Review now" onPress={() => router.push('/review')} disabled={due === 0} />
      </View>

      <View style={[S.row, { flexWrap: 'wrap' }]}>
        <View style={{ flex: 1, minWidth: 140 }}><Button ghost title="The path" onPress={() => router.push('/path')} /></View>
        <View style={{ flex: 1, minWidth: 140 }}><Button ghost title="Readings" onPress={() => router.push('/readings')} /></View>
        <View style={{ flex: 1, minWidth: 140 }}><Button ghost title="Lexicon" onPress={() => router.push('/search')} /></View>
        <View style={{ flex: 1, minWidth: 140 }}><Button ghost title="Settings" onPress={() => router.push('/settings')} /></View>
      </View>
    </Screen>
  );
}
