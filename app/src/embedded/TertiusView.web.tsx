// Web: the same offline page in a full-window iframe. An srcdoc iframe shares the site's address, so
// the page keeps its progress in the browser's own storage; outside links open in a new tab.
import React from 'react';
import page from './page';

const html = page.replace(
  '<head>',
  `<head><script>window.__TERTIUS={openUrl:function(u){window.open(u,'_blank','noopener');}};</script>`,
);

export default function TertiusView() {
  return (
    <iframe
      title="Tertius"
      srcDoc={html}
      style={{ position: 'fixed', inset: 0, width: '100%', height: '100%', border: 0 }}
    />
  );
}
