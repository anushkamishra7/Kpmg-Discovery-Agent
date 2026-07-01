export type WallStyleKey = 'royale-play' | 'living-room' | 'moonlit-silk';

export interface WallPreset {
  key: WallStyleKey;
  label: string;
  color: string;
  roughness: number;
  metalness: number;
  bumpScale: number;
}

export const WALL_PRESETS: Record<WallStyleKey, WallPreset> = {
  'royale-play': {
    key: 'royale-play',
    label: 'Royale Play Textures',
    color: '#c2986b',
    roughness: 0.7,
    metalness: 0.04,
    bumpScale: 0.065,
  },
  'living-room': {
    key: 'living-room',
    label: 'Living Room Concepts',
    color: '#8d9a85',
    roughness: 0.6,
    metalness: 0.03,
    bumpScale: 0.045,
  },
  'moonlit-silk': {
    key: 'moonlit-silk',
    label: 'Moonlit Silk 2026',
    color: '#3d3c54',
    roughness: 0.42,
    metalness: 0.12,
    bumpScale: 0.02,
  },
};

export const DEFAULT_WALL_STYLE: WallStyleKey = 'royale-play';
