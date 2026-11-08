import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { ProgressProvider } from '../progress';
import { C } from '../theme';

export default function Layout() {
  return (
    <ProgressProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: C.bg },
          headerTintColor: C.accent,
          headerTitleStyle: { color: C.ink },
          contentStyle: { backgroundColor: C.bg },
        }}
      >
        <Stack.Screen name="index" options={{ title: 'NT Greek' }} />
        <Stack.Screen name="path" options={{ title: 'The path' }} />
        <Stack.Screen name="unit/[id]" options={{ title: 'Lesson' }} />
        <Stack.Screen name="review" options={{ title: 'Review' }} />
        <Stack.Screen name="search" options={{ title: 'Lexicon' }} />
        <Stack.Screen name="word/[form]" options={{ title: 'Entry' }} />
        <Stack.Screen name="settings" options={{ title: 'Settings and sources' }} />
      </Stack>
    </ProgressProvider>
  );
}
