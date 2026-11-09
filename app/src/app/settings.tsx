import React, { useState } from 'react';
import { Switch, Text, View } from 'react-native';
import { Button, Screen } from '../components/ui';
import { WORDS } from '../data';
import { useProgress } from '../progress';
import { C, S } from '../theme';

export default function Settings() {
  const p = useProgress();
  const [confirm, setConfirm] = useState(false);
  const moss = Object.values(WORDS).filter((w) => w.m).length;
  return (
    <Screen>
      <View style={S.card}>
        <View style={[S.row, { justifyContent: 'space-between' }]}>
          <Text style={[S.h2, { flex: 1 }]}>I have studied MossMethod</Text>
          <Switch
            value={p.settings.mossGraduate}
            onValueChange={p.setMossGraduate}
            trackColor={{ true: C.moss, false: C.line }}
          />
        </View>
        <Text style={S.small}>
          {moss} of the words here are in the vocabulary of Moss's First Greek Reader. When this is on, they are
          marked in every lesson and counted as familiar on your progress bar.
        </Text>
      </View>


      <Button
        ghost
        title={confirm ? 'Tap again to erase all progress (cannot be undone)' : 'Erase my progress'}
        onPress={() => {
          if (confirm) {
            p.reset();
            setConfirm(false);
          } else setConfirm(true);
        }}
      />
    </Screen>
  );
}
