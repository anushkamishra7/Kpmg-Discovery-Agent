import { Suspense, useEffect, useMemo, useRef } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { BakeShadows, Environment, useGLTF } from '@react-three/drei';
import { createPlasterMaps } from './proceduralTexture';
import { WALL_PRESETS, type WallStyleKey } from './wallPresets';
import { useViewport, type Breakpoint } from './useViewport';

// Recenters the baked "living-room-set.glb" geometry (sofa + side flower, derived
// from the CC-BY-4.0 "Modern Apartment" model — see public/models/CREDIT.txt) so
// its footprint center sits at the local origin with its lowest point at y=0.
const LIVING_ROOM_MODEL_URL = '/models/living-room-set.glb';
const LIVING_ROOM_RECENTER: [number, number, number] = [4.16, -0.228, -1.68];

// Same recentering, for the standalone potted-flower accent piece.
const DECOR_FLOWER_MODEL_URL = '/models/decor-flower.glb';
const DECOR_FLOWER_RECENTER: [number, number, number] = [5.747, -0.406, 0.851];

// Real ceiling height (meters) — the furniture model is already built to real-world
// scale, so the room has to match it rather than the other way around.
const WALL_HEIGHT = 2.8;

const RIG_BY_BREAKPOINT: Record<Breakpoint, { fov: number; camZ: number; camY: number; lateral: number }> = {
  mobile: { fov: 52, camZ: 8.2, camY: 1.4, lateral: 1.6 },
  tablet: { fov: 48, camZ: 7.4, camY: 1.45, lateral: 1.3 },
  desktop: { fov: 45, camZ: 6.8, camY: 1.5, lateral: 1.15 },
};

/** Bakes a small enclosed, warm-lit room into a cube env map purely from
 * primitives so the clearcoat/satin surfaces have something to reflect.
 * A drei `preset="apartment"` HDRI was tried here but its decoded texture
 * blew GPU memory in this sandboxed environment and crashed the WebGL
 * context ("Context Lost") — this stays fully procedural and lightweight. */
function StudioEnvironment() {
  return (
    <Environment background={false} resolution={64} frames={1} environmentIntensity={0.4}>
      <mesh>
        <boxGeometry args={[12, 12, 12]} />
        <meshBasicMaterial color="#3a342c" side={THREE.BackSide} />
      </mesh>
      <pointLight position={[0, 3, 0]} intensity={18} color="#ffead0" />
      <pointLight position={[0, -2, 3]} intensity={6} color="#cfd6e6" />
    </Environment>
  );
}

function StudioLighting({ wallZ }: { wallZ: number }) {
  const targetRef = useRef<THREE.Object3D>(null!);
  const lightRef = useRef<THREE.SpotLight>(null!);

  useEffect(() => {
    if (lightRef.current && targetRef.current) {
      lightRef.current.target = targetRef.current;
    }
  }, []);

  return (
    <>
      <ambientLight intensity={0.7} color="#fff2e2" />
      <directionalLight
        position={[3.2, 4.2, 2.8]}
        intensity={1.4}
        color="#fff8ed"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={16}
        shadow-camera-left={-5}
        shadow-camera-right={5}
        shadow-camera-top={5}
        shadow-camera-bottom={-5}
        shadow-bias={-0.0004}
      />
      <spotLight
        ref={lightRef}
        position={[-1.6, 2.6, wallZ + 2.6]}
        angle={Math.PI / 3}
        penumbra={1}
        intensity={90}
        distance={12}
        decay={2}
        color="#ffe6bd"
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-bias={-0.0003}
      />
      <pointLight position={[1.6, 1.4, wallZ + 4.5]} intensity={3} distance={12} decay={2} color="#fff3df" />
      <object3D ref={targetRef} position={[0, WALL_HEIGHT * 0.5, wallZ]} />
    </>
  );
}

function AccentWall({ presetKey, wallZ }: { presetKey: WallStyleKey; wallZ: number }) {
  const materialRef = useRef<THREE.MeshPhysicalMaterial>(null!);
  const { bumpMap, roughnessMap } = useMemo(() => createPlasterMaps(), []);
  const preset = WALL_PRESETS[presetKey];
  const targetColor = useMemo(() => new THREE.Color(preset.color), [preset.color]);

  useFrame((_, delta) => {
    const mat = materialRef.current;
    if (!mat) return;
    const t = 1 - Math.pow(0.0008, delta);
    mat.color.lerp(targetColor, t);
    mat.roughness = THREE.MathUtils.lerp(mat.roughness, preset.roughness, t);
    mat.metalness = THREE.MathUtils.lerp(mat.metalness, preset.metalness, t);
    mat.bumpScale = THREE.MathUtils.lerp(mat.bumpScale, preset.bumpScale, t);
  });

  return (
    <mesh position={[0, WALL_HEIGHT / 2, wallZ]} receiveShadow>
      <planeGeometry args={[9, WALL_HEIGHT, 64, 64]} />
      <meshPhysicalMaterial
        ref={materialRef}
        color={preset.color}
        roughness={preset.roughness}
        metalness={preset.metalness}
        bumpMap={bumpMap}
        bumpScale={preset.bumpScale}
        roughnessMap={roughnessMap}
        clearcoat={0.15}
        clearcoatRoughness={0.7}
      />
    </mesh>
  );
}

/** Side wall returns + floor-wall baseboard trim — the depth cues a single flat
 * back wall and floor plane can't provide on their own (parallel side surfaces
 * give the eye something to read perspective convergence from). */
function RoomShell({ wallZ }: { wallZ: number }) {
  const depth = 5.5;
  return (
    <>
      <mesh position={[-4.4, WALL_HEIGHT / 2, wallZ + depth / 2]} receiveShadow castShadow>
        <boxGeometry args={[0.18, WALL_HEIGHT, depth]} />
        <meshStandardMaterial color="#e9e1d2" roughness={0.92} />
      </mesh>
      <mesh position={[4.4, WALL_HEIGHT / 2, wallZ + depth / 2]} receiveShadow castShadow>
        <boxGeometry args={[0.18, WALL_HEIGHT, depth]} />
        <meshStandardMaterial color="#e9e1d2" roughness={0.92} />
      </mesh>
      <mesh position={[0, 0.07, wallZ + 0.1]} receiveShadow castShadow>
        <boxGeometry args={[9, 0.14, 0.06]} />
        <meshStandardMaterial color="#f4f0e6" roughness={0.45} />
      </mesh>
    </>
  );
}

/** Area rug grounding the sofa, and a small framed-art accent on the open wall
 * to its left — fills the negative space that read as empty bare wall/floor. */
function LeftAccents({ x, wallZ }: { x: number; wallZ: number }) {
  return (
    <>
      <mesh position={[x + 0.3, 0.005, 1.0]} rotation={[-Math.PI / 2, 0, 0.12]} receiveShadow>
        <circleGeometry args={[1.78, 48]} />
        <meshPhysicalMaterial color="#7c6a52" roughness={0.95} clearcoat={0} />
      </mesh>
      <mesh position={[x + 0.3, 0.007, 1.0]} rotation={[-Math.PI / 2, 0, 0.12]} receiveShadow>
        <circleGeometry args={[1.45, 48]} />
        <meshPhysicalMaterial color="#9c8868" roughness={0.95} clearcoat={0} />
      </mesh>
      <group position={[x + 1.5, 1.62, wallZ + 0.05]}>
        <mesh receiveShadow castShadow>
          <boxGeometry args={[0.9, 1.15, 0.04]} />
          <meshStandardMaterial color="#3a342c" roughness={0.6} />
        </mesh>
        <mesh position={[0, 0, 0.025]}>
          <planeGeometry args={[0.78, 1.0]} />
          <meshStandardMaterial color="#a8765a" roughness={0.85} />
        </mesh>
        <mesh position={[-0.1, -0.15, 0.027]}>
          <planeGeometry args={[0.42, 0.5]} />
          <meshStandardMaterial color="#5c6e57" roughness={0.85} />
        </mesh>
      </group>
    </>
  );
}

/** Console table under the flower, plus a wall-art accent above it — mirrors
 * LeftAccents so the right side reads as a furnished corner, not bare wall/floor. */
function RightAccents({ x, wallZ }: { x: number; wallZ: number }) {
  const legPositions: [number, number][] = [
    [-0.42, -0.22],
    [0.42, -0.22],
    [-0.42, 0.22],
    [0.42, 0.22],
  ];

  return (
    <>
      <group position={[x, 0, -0.55]}>
        <mesh position={[0, 0.46, 0]} castShadow receiveShadow>
          <boxGeometry args={[1.0, 0.04, 0.5]} />
          <meshPhysicalMaterial color="#caa97a" roughness={0.55} clearcoat={0.2} clearcoatRoughness={0.3} />
        </mesh>
        {legPositions.map(([lx, lz]) => (
          <mesh key={`${lx}-${lz}`} position={[lx, 0.23, lz]} castShadow>
            <cylinderGeometry args={[0.022, 0.022, 0.46, 8]} />
            <meshStandardMaterial color="#2c2420" roughness={0.5} metalness={0.2} />
          </mesh>
        ))}
      </group>
      <group position={[x + 0.2, 1.55, wallZ + 0.05]}>
        <mesh receiveShadow castShadow>
          <circleGeometry args={[0.42, 32]} />
          <meshStandardMaterial color="#8b6b4a" roughness={0.6} />
        </mesh>
        <mesh position={[0, 0, 0.012]}>
          <circleGeometry args={[0.34, 32]} />
          <meshStandardMaterial color="#cfa05c" roughness={0.7} />
        </mesh>
      </group>
    </>
  );
}

function Floor() {
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 1]} receiveShadow>
      <planeGeometry args={[16, 16]} />
      <meshPhysicalMaterial
        color="#d9d0c2"
        roughness={0.25}
        metalness={0.02}
        clearcoat={0.5}
        clearcoatRoughness={0.2}
        reflectivity={0.45}
      />
    </mesh>
  );
}

function LivingRoomSet({ x }: { x: number }) {
  const { scene } = useGLTF(LIVING_ROOM_MODEL_URL);
  const cloned = useMemo(() => {
    const clone = scene.clone(true);
    clone.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (mesh.isMesh) {
        mesh.castShadow = true;
        mesh.receiveShadow = true;
      }
    });
    return clone;
  }, [scene]);

  return (
    <group position={[x, 0, 0.1]} scale={0.92} rotation={[0, Math.PI / 2.5, 0]}>
      <primitive object={cloned} position={LIVING_ROOM_RECENTER} />
    </group>
  );
}

useGLTF.preload(LIVING_ROOM_MODEL_URL);

/** Standalone potted-flower accent (the same CC-BY-4.0 "Modern Apartment" source as
 * the sofa, extracted separately via scripts/extract-flower.mjs) replacing the
 * earlier hand-built cone-cluster, which read as an ugly, out-of-place pine tree. */
function DecorPlant({ x }: { x: number }) {
  const { scene } = useGLTF(DECOR_FLOWER_MODEL_URL);
  const cloned = useMemo(() => {
    const clone = scene.clone(true);
    clone.traverse((obj) => {
      const mesh = obj as THREE.Mesh;
      if (mesh.isMesh) {
        mesh.castShadow = true;
        mesh.receiveShadow = true;
      }
    });
    return clone;
  }, [scene]);

  return (
    <group position={[x, 0, -0.6]} scale={1.3} rotation={[0, -Math.PI / 6, 0]}>
      <primitive object={cloned} position={DECOR_FLOWER_RECENTER} />
    </group>
  );
}

useGLTF.preload(DECOR_FLOWER_MODEL_URL);

function SceneContents({ wallStyle, lateral }: { wallStyle: WallStyleKey; lateral: number }) {
  const wallZ = -2.6;
  const sofaX = -2.6 * lateral;
  return (
    <>
      <StudioEnvironment />
      <StudioLighting wallZ={wallZ} />
      <AccentWall presetKey={wallStyle} wallZ={wallZ} />
      <Floor />
      <RoomShell wallZ={wallZ} />
      <LeftAccents x={sofaX} wallZ={wallZ} />
      <RightAccents x={2.5 * lateral} wallZ={wallZ} />
      <Suspense fallback={null}>
        <LivingRoomSet x={sofaX} />
        <DecorPlant x={2.5 * lateral} />
      </Suspense>
      <BakeShadows />
    </>
  );
}

export function ShowroomCanvas({ wallStyle }: { wallStyle: WallStyleKey }) {
  const breakpoint = useViewport();
  const rig = RIG_BY_BREAKPOINT[breakpoint];

  return (
    <Canvas
      shadows
      dpr={[1, 1.75]}
      camera={{ fov: rig.fov, position: [0.7, rig.camY, rig.camZ], near: 0.1, far: 50 }}
      gl={{ antialias: true }}
      onCreated={({ camera }) => camera.lookAt(0, 1.25, -1.4)}
    >
      <SceneContents wallStyle={wallStyle} lateral={rig.lateral} />
    </Canvas>
  );
}
