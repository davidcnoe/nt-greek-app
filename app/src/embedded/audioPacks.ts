// The headword audio, bundled with the app: 13 packs of up to 100 clips ({clip key: base64 mp3} as JSON text),
// written by scripts/audio_bundle.py into prototype/audio/ and read from there (see metro.config.js).
// Pack N holds clips T(N*100) to T(N*100+99).
/* eslint-disable @typescript-eslint/no-require-imports */
const packs: Record<number, number> = {
  0: require('../../../prototype/audio/pack_00.bin'),
  1: require('../../../prototype/audio/pack_01.bin'),
  2: require('../../../prototype/audio/pack_02.bin'),
  3: require('../../../prototype/audio/pack_03.bin'),
  4: require('../../../prototype/audio/pack_04.bin'),
  5: require('../../../prototype/audio/pack_05.bin'),
  6: require('../../../prototype/audio/pack_06.bin'),
  7: require('../../../prototype/audio/pack_07.bin'),
  8: require('../../../prototype/audio/pack_08.bin'),
  9: require('../../../prototype/audio/pack_09.bin'),
  10: require('../../../prototype/audio/pack_10.bin'),
  11: require('../../../prototype/audio/pack_11.bin'),
  12: require('../../../prototype/audio/pack_12.bin'),
};
export default packs;
