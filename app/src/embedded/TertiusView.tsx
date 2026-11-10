// iOS and Android: the prototype's page in a web view, full screen and offline (David, 2026-11-09: the
// store app wraps the prototype, so every change to prototype/ carries over after
// `node scripts/build-embed.mjs`).
//
// - Progress: the page saves to its own storage and also hands each save to the app, which keeps it in
//   AsyncStorage; at start the app puts its copy back into the page first, so progress survives even if
//   the system clears the web view's storage.
// - Outside links (latinperdiem.com, sources) open in the phone's browser.
// - Safe areas: the page runs under the status bar and home indicator and pads its own header and bottom
//   bar by the device's insets, so their colours reach the screen's edges in either theme; it tells the
//   app its theme so the status bar's clock and icons stay legible.
import AsyncStorage from '@react-native-async-storage/async-storage';
import { StatusBar } from 'expo-status-bar';
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Linking, useColorScheme, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { WebView as RNWebView, type WebViewMessageEvent, type WebViewProps } from 'react-native-webview';
import page from './page';

// The package's typings default the class's extra props to `undefined`, which leaves no valid props
// under TypeScript 6; this gives the component its real props and the two methods used here.
type WebViewHandle = { reload: () => void; injectJavaScript: (js: string) => void };
const WebView = RNWebView as unknown as React.ComponentType<WebViewProps & React.RefAttributes<WebViewHandle>>;

// The page's storage keys begin with this (prototype/app.js, STORE).
const KEY_PREFIX = 'ntgreek:';
// Gives the page an address of its own, for its storage; nothing is ever loaded from it.
const BASE_URL = 'https://tertius.latinperdiem.com/';
const BG = { light: '#fbf9f5', dark: '#10151f' };

type Message = { t: 'save'; k: string; v: string | null } | { t: 'open'; u: string } | { t: 'theme'; v: 'light' | 'dark' };

export default function TertiusView() {
  const system = useColorScheme() === 'dark' ? 'dark' : 'light';
  const [theme, setTheme] = useState<'light' | 'dark'>(system);
  const [saved, setSaved] = useState<Record<string, string> | null>(null);
  const insets = useSafeAreaInsets();
  const web = useRef<WebViewHandle>(null);

  useEffect(() => {
    (async () => {
      const keys = (await AsyncStorage.getAllKeys()).filter((k) => k.startsWith(KEY_PREFIX));
      const pairs = await AsyncStorage.multiGet(keys);
      setSaved(Object.fromEntries(pairs.filter((p): p is [string, string] => p[1] != null)));
    })().catch(() => setSaved({}));
  }, []);

  // Set once, when the saved progress has been read, so the page is not rebuilt as insets settle.
  const html = useMemo(() => {
    if (!saved) return null;
    const boot = `<script>(function(){
var s=${JSON.stringify(saved).replace(/</g, '\\u003c')};
try{for(var k in s)localStorage.setItem(k,s[k]);}catch(e){}
function send(m){window.ReactNativeWebView&&window.ReactNativeWebView.postMessage(JSON.stringify(m));}
window.__TERTIUS={
  save:function(k,v){send({t:'save',k:k,v:v});},
  openUrl:function(u){send({t:'open',u:u});},
  theme:function(v){send({t:'theme',v:v});}
};
document.documentElement.style.setProperty('--safe-top','${Math.round(insets.top)}px');
document.documentElement.style.setProperty('--safe-bottom','${Math.round(insets.bottom)}px');
})();</script>`;
    return page.replace('<head>', `<head>${boot}`);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [saved]);

  // Insets can settle after the first render (rotation is off, but a split screen can change them).
  useEffect(() => {
    web.current?.injectJavaScript(`document.documentElement.style.setProperty('--safe-top','${Math.round(insets.top)}px');
document.documentElement.style.setProperty('--safe-bottom','${Math.round(insets.bottom)}px');
window.dispatchEvent(new Event('resize'));true;`);
  }, [insets.top, insets.bottom]);

  const onMessage = (e: WebViewMessageEvent) => {
    let m: Message;
    try { m = JSON.parse(e.nativeEvent.data); } catch { return; }
    if (m.t === 'save' && m.k.startsWith(KEY_PREFIX)) {
      (m.v == null ? AsyncStorage.removeItem(m.k) : AsyncStorage.setItem(m.k, m.v)).catch(() => {});
    } else if (m.t === 'open' && /^https?:\/\//.test(m.u)) {
      Linking.openURL(m.u).catch(() => {});
    } else if (m.t === 'theme') {
      setTheme(m.v);
    }
  };

  return (
    <View style={{ flex: 1, backgroundColor: BG[theme] }}>
      <StatusBar style={theme === 'dark' ? 'light' : 'dark'} />
      {html && (
        <WebView
          ref={web}
          source={{ html, baseUrl: BASE_URL }}
          originWhitelist={['*']}
          onMessage={onMessage}
          // Anything but the page itself (a link that slipped past the page's own handler) goes to the browser.
          onShouldStartLoadWithRequest={(r: { url: string }) => {
            if (r.url === BASE_URL || r.url.startsWith('about:') || r.url.startsWith('data:')) return true;
            if (/^https?:\/\//.test(r.url)) Linking.openURL(r.url).catch(() => {});
            return false;
          }}
          setSupportMultipleWindows={false}
          style={{ flex: 1, backgroundColor: BG[theme] }}
          containerStyle={{ backgroundColor: BG[theme] }}
          contentInsetAdjustmentBehavior="never"
          automaticallyAdjustContentInsets={false}
          bounces={false}
          overScrollMode="never"
          textZoom={100}
          hideKeyboardAccessoryView
          allowsBackForwardNavigationGestures={false}
          webviewDebuggingEnabled={__DEV__}
          onContentProcessDidTerminate={() => web.current?.reload()}
          onRenderProcessGone={() => web.current?.reload()}
        />
      )}
    </View>
  );
}
