import { Stack } from 'expo-router';
import React from 'react';

// One screen: the whole app is the prototype's page, shown full screen (src/embedded/TertiusView).
// The page draws its own header and bottom bar, so the navigator shows none.
export default function Layout() {
  return <Stack screenOptions={{ headerShown: false, animation: 'none' }} />;
}
