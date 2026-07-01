import * as THREE from 'three';

interface NoiseOctave {
  count: number;
  minRadius: number;
  maxRadius: number;
  alpha: number;
}

interface NoiseTextureOptions {
  size?: number;
  baseValue?: number;
  octaves?: NoiseOctave[];
  repeat?: [number, number];
}

/** Builds a tileable grayscale noise canvas by stamping randomized light/dark
 * speckles at several radius bands, then wraps it as a repeating CanvasTexture. */
function createNoiseTexture(opts: NoiseTextureOptions = {}): THREE.CanvasTexture {
  const {
    size = 512,
    baseValue = 150,
    octaves = [
      { count: 700, minRadius: 6, maxRadius: 18, alpha: 0.06 },
      { count: 2600, minRadius: 1, maxRadius: 4, alpha: 0.1 },
      { count: 7000, minRadius: 0.4, maxRadius: 1.2, alpha: 0.14 },
    ],
    repeat = [4, 4],
  } = opts;

  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d')!;

  ctx.fillStyle = `rgb(${baseValue},${baseValue},${baseValue})`;
  ctx.fillRect(0, 0, size, size);

  for (const { count, minRadius, maxRadius, alpha } of octaves) {
    for (let i = 0; i < count; i++) {
      const x = Math.random() * size;
      const y = Math.random() * size;
      const r = minRadius + Math.random() * (maxRadius - minRadius);
      const shade = Math.random() > 0.5 ? 255 : 0;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${shade},${shade},${shade},${alpha})`;
      ctx.fill();
    }
  }

  const texture = new THREE.CanvasTexture(canvas);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.repeat.set(repeat[0], repeat[1]);
  texture.needsUpdate = true;
  return texture;
}

/** Procedural plaster/stucco finish maps (bump + roughness) for the accent wall, built
 * purely from canvas noise so no external texture assets are required. */
export function createPlasterMaps() {
  const bumpMap = createNoiseTexture({
    baseValue: 128,
    octaves: [
      { count: 600, minRadius: 7, maxRadius: 20, alpha: 0.1 },
      { count: 2400, minRadius: 1.5, maxRadius: 4, alpha: 0.16 },
      { count: 6500, minRadius: 0.4, maxRadius: 1.3, alpha: 0.22 },
    ],
  });

  const roughnessMap = createNoiseTexture({
    baseValue: 195,
    octaves: [
      { count: 450, minRadius: 10, maxRadius: 26, alpha: 0.05 },
      { count: 1600, minRadius: 2, maxRadius: 6, alpha: 0.06 },
    ],
  });

  return { bumpMap, roughnessMap };
}
