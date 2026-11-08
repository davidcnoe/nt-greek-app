import { Link } from 'expo-router';
import React from 'react';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { FAMILIES, Word, WORDS } from '../data';
import { C, S } from '../theme';

export function Screen({ children }: { children: React.ReactNode }) {
  return (
    <ScrollView style={S.screen} contentContainerStyle={S.wrap} keyboardShouldPersistTaps="handled">
      {children}
    </ScrollView>
  );
}

export function Button({ title, onPress, ghost, disabled }: {
  title: string; onPress: () => void; ghost?: boolean; disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [ghost ? S.btnGhost : S.btn, { opacity: disabled ? 0.4 : pressed ? 0.8 : 1 }]}
    >
      <Text style={ghost ? S.btnGhostText : S.btnText}>{title}</Text>
    </Pressable>
  );
}

export function Chip({ text, tone = 'accent' }: { text: string; tone?: 'accent' | 'moss' }) {
  return (
    <View style={[S.chip, tone === 'moss' && { backgroundColor: C.mossSoft }]}>
      <Text style={[S.chipText, tone === 'moss' && { color: C.moss }]}>{text}</Text>
    </View>
  );
}

/** Coverage bar: share of NT running words learned, plus words familiar from Moss. */
export function Meter({ known, familiar }: { known: number; familiar: number }) {
  return (
    <View style={{ gap: 6 }}>
      <View style={{ height: 14, borderRadius: 7, backgroundColor: C.line, overflow: 'hidden', flexDirection: 'row' }}>
        <View style={{ width: `${known * 100}%`, backgroundColor: C.accent }} />
        <View style={{ width: `${familiar * 100}%`, backgroundColor: C.moss, opacity: 0.45 }} />
      </View>
      <Text style={S.small}>
        You have learned words that make up {Math.round(known * 100)}% of the Greek New Testament
        {familiar > 0 ? `; another ${Math.round(familiar * 100)}% are familiar from Moss` : ''}.
      </Text>
    </View>
  );
}

/** Greek headword with its grammatical info. */
export function Headword({ form, size = 30 }: { form: string; size?: number }) {
  const w = WORDS[form];
  return (
    <Text style={[S.greek, { fontSize: size }]}>
      {form}
      {w?.gr ? <Text style={[S.greek, { fontSize: size * 0.6, color: C.muted }]}>{`, ${w.gr}`}</Text> : null}
    </Text>
  );
}

/** The answer side of a card: gloss, derivative, Moss, family. */
export function Answer({ form, w, moss }: { form: string; w: Word; moss?: boolean }) {
  const fam = w.f != null ? FAMILIES[w.f] : null;
  return (
    <View style={{ gap: 8 }}>
      <Text style={[S.body, { fontSize: 20 }]}>{w.g}</Text>
      {w.d ? <Text style={S.small}>Cf. {w.d}</Text> : null}
      {moss && w.m && w.mg && w.mg !== w.g ? <Text style={[S.small, { color: C.moss }]}>Moss: {w.mg}</Text> : null}
      {fam ? (
        <Text style={S.small}>
          {fam.root ? `root ${fam.root}${fam.gloss ? `, ${fam.gloss}` : ''}: ` : 'Family: '}
          <Text style={S.greek}>{fam.members.filter((m) => m !== form).slice(0, 8).join(', ')}</Text>
        </Text>
      ) : null}
      <Link href={{ pathname: '/word/[form]', params: { form } }} style={[S.small, { color: C.accent, fontWeight: '700' }]}>
        Full entry, with Souter →
      </Link>
    </View>
  );
}
