import { router } from 'expo-router';
import React, { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { Grade, Rating } from 'ts-fsrs';
import { Answer, Button, Headword, Screen } from '../components/ui';
import { WORDS } from '../data';
import { untilText, useProgress } from '../progress';
import { C, S } from '../theme';

const GRADES: { r: Grade; label: string }[] = [
  { r: Rating.Again, label: 'Again' },
  { r: Rating.Hard, label: 'Hard' },
  { r: Rating.Good, label: 'Good' },
  { r: Rating.Easy, label: 'Easy' },
];

// Spaced-repetition review (FSRS): each grade shows when the word will come back.
export default function Review() {
  const p = useProgress();
  const [queue] = useState(() => p.due().filter((f) => WORDS[f]));
  const [i, setI] = useState(0);
  const [shown, setShown] = useState(false);

  if (i >= queue.length) {
    return (
      <Screen>
        <View style={S.card}>
          <Text style={S.h1}>{queue.length ? 'Review finished' : 'Nothing to review'}</Text>
          <Text style={S.body}>{queue.length ? `${queue.length} words reviewed.` : 'Come back later, or start the next lesson.'}</Text>
        </View>
        <Button title="Home" onPress={() => router.back()} />
      </Screen>
    );
  }

  const form = queue[i];
  const w = WORDS[form];
  const when = shown ? p.preview(form) : null;
  return (
    <Screen>
      <Text style={S.small}>{queue.length - i} left</Text>
      <Pressable onPress={() => setShown(true)} style={[S.card, { minHeight: 220, justifyContent: 'center', gap: 16 }]}>
        <Headword form={form} size={36} />
        {shown ? <Answer form={form} w={w} moss={p.settings.mossGraduate} /> : <Text style={S.small}>Say the meaning, then tap to check.</Text>}
      </Pressable>
      {shown && when ? (
        <View style={[S.row, { flexWrap: 'wrap' }]}>
          {GRADES.map(({ r, label }) => (
            <View key={label} style={{ flex: 1, minWidth: 70 }}>
              <Button
                ghost={r !== Rating.Good}
                title={`${label}\n${untilText(when[r])}`}
                onPress={() => {
                  p.grade(form, r);
                  setShown(false);
                  setI(i + 1);
                }}
              />
            </View>
          ))}
        </View>
      ) : (
        <Button title="Show meaning" onPress={() => setShown(true)} />
      )}
      <Text style={[S.small, { color: C.muted }]}>Each word returns just before you are likely to forget it.</Text>
    </Screen>
  );
}
