// Derives public/models/decor-flower.glb (a standalone potted-flower accent piece)
// from the same CC-BY-4.0 "Modern Apartment" source as living-room-set.glb —
// see extract-livingroom.mjs for the shared pipeline notes.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune, dedup } from '@gltf-transform/functions';

const KEEP_PREFIXES = ['Flower'];
const SRC_PATH = '/Users/anushka/Desktop/modern_apartment/scene.gltf';
const OUT_PATH = '/tmp/flower_raw.glb';

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
