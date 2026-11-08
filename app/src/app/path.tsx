import { router } from 'expo-router';
import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { Screen } from '../components/ui';
import { UNITS } from '../data';
import { useProgress } from '../progress';
import { C, S } from '../theme';

export default function Path() {
  const p = useProgress();
  const next = p.nextUnit();
  return (
    <Screen>
      <Text style={S.small}>
        Root families and Metzger's frequency lists, ordered so the commonest New Testament words come first.
        Any lesson can be opened at any time.
      </Text>
      {UNITS.map((u, i) => {
        const done = p.done.has(u.id);
        return (
          <Pressable
            key={u.id}
            onPress={() => router.push({ pathname: '/unit/[id]', params: { id: u.id } })}
            style={[S.card, { paddingVertical: 12, borderColor: i === next ? C.accent : C.line }]}
          >
            <View style={S.row}>
              <Text style={[S.small, { width: 34 }]}>{done ? '✓' : i + 1}</Text>
              <View style={{ flex: 1 }}>
                <Text style={[S.body, { fontWeight: '700' }]}>{u.title}</Text>
                <Text numberOfLines={1} style={[S.greek, { color: C.muted, fontSize: 15 }]}>{u.words.join(', ')}</Text>
              </View>
            </View>
          </Pressable>
        );
      })}
    </Screen>
  );
}
