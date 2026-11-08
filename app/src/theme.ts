import { Platform, StyleSheet } from 'react-native';

export const C = {
  bg: '#f7f3ea',
  card: '#fffdf8',
  ink: '#2b2621',
  muted: '#6f665c',
  line: '#e3dccd',
  accent: '#7a2e1f',
  accentSoft: '#f1e2dc',
  good: '#2f6b3f',
  moss: '#4f6b2f',
  mossSoft: '#e7eedb',
};

export const GREEK = Platform.select({
  web: '"Gentium Plus", "GFS Didot", "Palatino Linotype", Palatino, Georgia, serif',
  ios: 'Georgia',
  default: 'serif',
});

export const S = StyleSheet.create({
  screen: { flex: 1, backgroundColor: C.bg },
  wrap: { width: '100%', maxWidth: 640, alignSelf: 'center', padding: 20, gap: 16 },
  card: { backgroundColor: C.card, borderRadius: 14, borderWidth: 1, borderColor: C.line, padding: 18, gap: 8 },
  h1: { fontSize: 26, fontWeight: '700', color: C.ink, fontFamily: GREEK },
  h2: { fontSize: 18, fontWeight: '700', color: C.ink },
  body: { fontSize: 16, color: C.ink, lineHeight: 23 },
  small: { fontSize: 13, color: C.muted, lineHeight: 18 },
  greek: { fontFamily: GREEK, color: C.ink },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  btn: { backgroundColor: C.accent, borderRadius: 10, paddingVertical: 13, paddingHorizontal: 18, alignItems: 'center' },
  btnText: { color: '#fff', fontSize: 16, fontWeight: '700' },
  btnGhost: { borderRadius: 10, paddingVertical: 11, paddingHorizontal: 14, alignItems: 'center', borderWidth: 1, borderColor: C.line, backgroundColor: C.card },
  btnGhostText: { color: C.ink, fontSize: 15, fontWeight: '600' },
  chip: { borderRadius: 999, paddingHorizontal: 9, paddingVertical: 3, backgroundColor: C.accentSoft },
  chipText: { fontSize: 12, color: C.accent, fontWeight: '700' },
});
