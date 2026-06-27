import { bootstrapForgeEnv, ensureRedis } from "@sourcea/forge-core";

import { startWorker } from "./processor.js";

bootstrapForgeEnv();
await ensureRedis();

const worker = startWorker();

console.log("forge-core-worker started");

async function shutdown(): Promise<void> {
  await worker.close();
  process.exit(0);
}

process.on("SIGINT", () => {
  void shutdown();
});
process.on("SIGTERM", () => {
  void shutdown();
});
