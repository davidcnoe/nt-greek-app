import React from 'react';
import { Text, View } from 'react-native';
import { Screen } from '../components/ui';
import { META } from '../data';
import { S } from '../theme';

// Button 4: what the app is and where its words come from.
export default function About() {
  return (
    <Screen>
      <View style={S.card}>
        <Text style={S.h2}>About</Text>
        <Text style={S.body}>
          A vocabulary trainer for reading the Greek New Testament. Words come in the order of Bruce Metzger's
          Lexical Aids (1946): first by how often they occur, then by root families, so that each new word is learned
          with its relatives. Each lesson is studied, then recalled; spaced repetition brings every word back just
          before you would forget it.
        </Text>
      </View>
      <View style={S.card}>
        <Text style={S.h2}>Sources</Text>
        {META.sources.map((s) => (
          <Text key={s} style={S.small}>• {s}</Text>
        ))}
        <Text style={S.small}>• Nunn, A Short Syntax of New Testament Greek (1920), Appendix II, for the readings</Text>
        <Text style={S.small}>Glosses and English derivatives are Metzger's (1946). Data built {META.built}.</Text>
      </View>
    </Screen>
  );
}
