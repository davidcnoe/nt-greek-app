import { router } from 'expo-router';
import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { State } from 'ts-fsrs';
import { Chip, Screen } from '../components/ui';
import { useProgress } from '../progress';
import { READINGS, tokenKeys } from '../readings';
import { C, S } from '../theme';

// Readings beyond the New Testament (Nunn 1920, Appendix II), easiest first.
export default function ReadingsScreen() {
  const p = useProgress();
  const known = (k: string) => {
    const c = p.cards[k];
    return !!c && c.state !== State.New;
  };
  return (
    <Screen>
      <View style={S.card}>
        <Text style={S.h2}>Beyond the New Testament</Text>
        <Text style={S.body}>
          Twelve passages of early Christian Greek chosen by H. P. V. Nunn (1920), with his notes. They are listed
          from easiest to hardest, by how many of their words this app teaches.
        </Text>
      </View>
      {READINGS.map((r, i) => {
        const keys = tokenKeys(r);
        const k = keys.filter(known).length / keys.length;
        return (
          <Pressable
            key={r.slug}
            accessibilityRole="button"
            onPress={() => router.push({ pathname: '/reading/[slug]', params: { slug: r.slug } })}
            style={({ pressed }) => [S.card, { opacity: pressed ? 0.85 : 1 }]}
          >
            <Text style={S.small}>{`${i + 1}. ${r.author}${r.date ? ` · ${r.date}` : ''}`}</Text>
            <Text style={[S.h2, { fontSize: 19 }]}>{r.title}</Text>
            <View style={{ height: 8, borderRadius: 4, backgroundColor: C.line, overflow: 'hidden', flexDirection: 'row' }}>
              <View style={{ width: `${k * 100}%`, backgroundColor: C.accent }} />
              <View style={{ width: `${Math.max(0, r.taught - k) * 100}%`, backgroundColor: C.accent, opacity: 0.25 }} />
            </View>
            <View style={[S.row, { flexWrap: 'wrap' }]}>
              <Chip text={`${r.words.toLocaleString()} words`} />
              <Chip text={`you know ${Math.round(k * 100)}%`} />
              <Chip tone="moss" text={`app teaches ${Math.round(r.taught * 100)}%`} />
            </View>
          </Pressable>
        );
      })}
      <Text style={S.small}>Text: Nunn, A Short Syntax of New Testament Greek (Cambridge, 1920), Appendix II.</Text>
    </Screen>
  );
}
