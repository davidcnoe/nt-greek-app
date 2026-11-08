import { router } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { Pressable, Text, TextInput, View } from 'react-native';
import { Screen } from '../components/ui';
import { search, WORDS } from '../data';
import { C, GREEK, S } from '../theme';

// Lexicon: type Greek (accents optional), Latin letters (logos, agape, theos), or English.
export default function Search() {
  const [q, setQ] = useState('');
  const hits = useMemo(() => search(q), [q]);
  return (
    <Screen>
      <TextInput
        value={q}
        onChangeText={setQ}
        placeholder="Greek, Latin letters, or English"
        placeholderTextColor={C.muted}
        autoCapitalize="none"
        autoCorrect={false}
        style={[S.card, { fontSize: 18, fontFamily: GREEK, paddingVertical: 12 }]}
      />
      {q && hits.length === 0 ? <Text style={S.small}>No matches.</Text> : null}
      {hits.map(({ form, why }) => (
        <Pressable
          key={form}
          onPress={() => router.push({ pathname: '/word/[form]', params: { form } })}
          style={[S.card, { paddingVertical: 10 }]}
        >
          <View style={[S.row, { justifyContent: 'space-between' }]}>
            <Text style={[S.greek, { fontSize: 20 }]}>{form}</Text>
            <Text style={S.small}>{WORDS[form].c.toLocaleString()}×</Text>
          </View>
          <Text style={S.body} numberOfLines={2}>{WORDS[form].g}</Text>
          {why === 'souter' ? <Text style={S.small}>Found in Souter's entry</Text> : null}
        </Pressable>
      ))}
    </Screen>
  );
}
