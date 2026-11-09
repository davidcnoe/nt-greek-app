import { Link, Stack, useLocalSearchParams } from 'expo-router';
import React from 'react';
import { Text, View } from 'react-native';
import { State } from 'ts-fsrs';
import { Chip, Headword, Screen } from '../../components/ui';
import { FAMILIES, WORDS } from '../../data';
import { useProgress } from '../../progress';
import { C, S } from '../../theme';

// Full entry: Metzger's gloss and derivative, the root family, Moss, and Souter's lexicon entry.
export default function WordScreen() {
  const { form } = useLocalSearchParams<{ form: string }>();
  const w = form ? WORDS[form] : undefined;
  const p = useProgress();
  if (!form || !w) {
    return (
      <Screen>
        <Text style={S.body}>No entry for “{form}”.</Text>
      </Screen>
    );
  }
  const fam = w.f != null ? FAMILIES[w.f] : null;
  const card = p.cards[form];
  return (
    <Screen>
      
      <View style={S.card}>
        <Headword form={form} size={34} />
        <Text style={[S.body, { fontSize: 20 }]}>{w.g}</Text>
        {w.d ? <Text style={S.small}>Cf. {w.d}</Text> : null}
        <View style={[S.row, { flexWrap: 'wrap' }]}>
          <Chip text={`${w.c.toLocaleString()}× in NT${w.l !== form ? ` (as ${w.l})` : ''}`} />
          {w.t ? <Chip text={w.t.replace('Words Occurring ', '').toLowerCase()} /> : null}
          {w.m ? <Chip tone="moss" text="In Moss" /> : null}
          {card ? <Chip text={card.state === State.Review ? 'Learned' : 'Learning'} /> : null}
        </View>
      </View>

      {fam ? (
        <View style={S.card}>
          <Text style={S.h2}>{fam.root ? `Root ${fam.root}` : 'Word family'}</Text>
          {fam.gloss ? <Text style={S.small}>{fam.gloss}</Text> : null}
          {fam.members.map((m) => (
            <Link key={m} href={{ pathname: '/word/[form]', params: { form: m } }} style={{ paddingVertical: 3 }}>
              <Text style={[S.greek, { fontSize: 17, fontWeight: m === form ? '700' : '400' }]}>{m}</Text>
              <Text style={S.small}>{`  ${WORDS[m]?.g ?? ''}`}</Text>
            </Link>
          ))}
        </View>
      ) : null}

      {w.m && w.mg ? (
        <View style={[S.card, { backgroundColor: C.mossSoft, borderColor: C.mossSoft }]}>
          <Text style={[S.h2, { color: C.moss }]}>In Moss's First Greek Reader</Text>
          <Text style={S.body}>{w.mg}</Text>
        </View>
      ) : null}

      {w.s ? (
        <View style={S.card}>
          <Text style={S.h2}>Souter, Pocket Lexicon (1916)</Text>
          <Text style={[S.body, { fontFamily: undefined }]}>{w.s}</Text>
          <Text style={[S.small, { fontStyle: 'italic' }]}>
            Souter's text is machine-read from the 1917 printing and is still being proofread.
          </Text>
        </View>
      ) : null}
    </Screen>
  );
}
