// The audio packs live in ../prototype/audio (one copy, shared with the web prototype); Metro must be
// allowed to read outside app/ and to treat the .bin packs as assets (.bin is added to Metro's asset extensions).
const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const config = getDefaultConfig(__dirname);
config.watchFolders = [...(config.watchFolders ?? []), path.resolve(__dirname, '..', 'prototype', 'audio')];
config.resolver.assetExts = [...config.resolver.assetExts, 'bin'];
// Assets outside app/ must still find react-native's asset registry in app/node_modules.
config.resolver.nodeModulesPaths = [...(config.resolver.nodeModulesPaths ?? []), path.resolve(__dirname, 'node_modules')];
module.exports = config;
