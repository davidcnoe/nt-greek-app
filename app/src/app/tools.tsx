import { router } from 'expo-router';
import React from 'react';
import { Pressable, Text } from 'react-native';
import { Screen } from '../components/ui';
import { S } from '../theme';

// Button 2: everything besides today's lesson and review.
const ITEMS = [
  { href: '/path', title: 'The path', text: "All lessons in order: Metzger's frequency lists and root families." },
  { href: '/review', title: 'Review', text: 'Words due for review now.' },
  { href: '/search', title: 'Lexicon', text: 'Search Metzger, Moss, and Souter in Greek, Latin letters, or English.' },
  { href: '/readings', title: 'Readings', text: 'Early Christian Greek beyond the New Testament, with Nunn\'s notes.' },
] as const;

export default function Tools() {
  return (
    <Screen>
      {ITEMS.map((it) => (
        <Pressable key={it.href} accessibilityRole="button" onPress={() => router.push(it.href)}
          style={({ pressed }) => [S.card, { opacity: pressed ? 0.85 : 1 }]}>
          <Text style={S.h2}>{it.title}</Text>
          <Text style={S.small}>{it.text}</Text>
        </Pressable>
      ))}
    </Screen>
  );
}
