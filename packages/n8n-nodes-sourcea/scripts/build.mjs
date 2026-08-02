/**
 * Copy node sources into dist/ for n8n custom extension loading.
 * Nodes ship as plain JS so Docker/Railway mounts need no TypeScript build chain.
 */
import { cpSync, mkdirSync, writeFileSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const dist = join(root, "dist");
mkdirSync(dist, { recursive: true });
cpSync(join(root, "nodes"), join(dist, "nodes"), { recursive: true });
cpSync(join(root, "credentials"), join(dist, "credentials"), { recursive: true });
cpSync(join(root, "src"), join(dist, "src"), { recursive: true });
writeFileSync(join(dist, "index.js"), "module.exports = {};\n");
if (!existsSync(join(root, "index.js"))) {
  writeFileSync(join(root, "index.js"), "module.exports = {};\n");
}
console.log("built n8n-nodes-sourcea → dist/");
