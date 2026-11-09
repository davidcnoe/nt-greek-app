import { router, Stack, usePathname } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { Pressable, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { ProgressProvider } from '../progress';
import { C } from '../theme';

// Four-button bottom bar, as in Telamon: always visible, on every screen, and no Back buttons.
// The buttons are numbered 1–4 until David names them.
const BUTTONS = [
  { label: '1', href: '/', match: (p: string) => p === '/' },
  { label: '2', href: '/tools', match: (p: string) => p === '/tools' },
  { label: '3', href: '/settings', match: (p: string) => p === '/settings' },
  { label: '4', href: '/about', match: (p: string) => p === '/about' },
] as const;

function BottomBar() {
  const path = usePathname();
  const insets = useSafeAreaInsets();
  return (
    <View style={{
      flexDirection: 'row', backgroundColor: C.card, borderTopWidth: 1, borderTopColor: C.line,
      paddingBottom: insets.bottom,
    }}>
      {BUTTONS.map((b) => {
        const on = b.match(path);
        return (
          <Pressable key={b.label} accessibilityRole="button" accessibilityLabel={`Button ${b.label}`}
            onPress={() => router.navigate(b.href)}
            style={({ pressed }) => ({ flex: 1, alignItems: 'center', paddingVertical: 14, opacity: pressed ? 0.6 : 1 })}>
            <Text style={{ fontSize: 17, fontWeight: '700', color: on ? C.accent : C.muted }}>{b.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

export default function Layout() {
  return (
    <ProgressProvider>
      <StatusBar style="dark" />
      <View style={{ flex: 1, backgroundColor: C.bg }}>
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: C.bg },
            headerTitle: 'Tertius',
            headerTitleStyle: { color: C.ink },
            headerBackVisible: false,
            headerLeft: () => null,
            contentStyle: { backgroundColor: C.bg },
            animation: 'none',
          }}
        />
        <BottomBar />
      </View>
    </ProgressProvider>
  );
}
