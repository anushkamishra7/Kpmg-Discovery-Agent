// One-off pipeline used to derive public/models/living-room-set.glb from the
// "Modern Apartment" source model (CC-BY-4.0, see public/models/CREDIT.txt):
// 1. keep only the CouchSet + Flower node groups (drops bed/bath/kitchen/office)
// 2. run `gltf-transform optimize --compress draco --texture-compress webp --texture-size 1024`
//    on the result (119MB -> 1.35MB)
//
// Baseboard/Windows/Plane were considered too, but each is a single mesh that spans
// the *entire* apartment perimeter (~20m), not a per-room segment — there's no clean
// node-level way to crop just the living-room portion, so those stay out and the
// room-depth cues (baseboard trim, side walls) are built procedurally instead.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup } from '@gltf-transform/functions';

const KEEP_PREFIXES = ['CouchSet', 'Flower'];
const SRC_PATH = '/Users/anushka/Desktop/modern_apartment/scene.gltf';
const OUT_PATH = '/tmp/livingroom_raw.glb';

const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const document = await io.read(SRC_PATH);
const scene = document.getRoot().listScenes()[0];

function shouldKeep(name) {
  return KEEP_PREFIXES.some((prefix) => name.startsWith(prefix));
}

function disposeSubtree(node) {
  for (const child of node.listChildren()) disposeSubtree(child);
  node.dispose();
}

// Root passthrough nodes (Sketchfab_model > *.fbx > RootNode) hold the real groups as children.
function findGroupContainer(node) {
  const children = node.listChildren();
  if (children.length === 1 && (children[0].getName() === 'RootNode' || children[0].getName().endsWith('.fbx'))) {
    return findGroupContainer(children[0]);
  }
  return node;
}

let kept = 0;
let removed = 0;
for (const top of scene.listChildren()) {
  const container = findGroupContainer(top);
  for (const group of [...container.listChildren()]) {
    if (shouldKeep(group.getName())) {
      kept++;
    } else {
      disposeSubtree(group);
      removed++;
    }
  }
}

console.log(`kept ${kept} groups, removed ${removed} groups`);

await document.transform(prune(), dedup());
await io.write(OUT_PATH, document);
console.log(`wrote ${OUT_PATH}`);
