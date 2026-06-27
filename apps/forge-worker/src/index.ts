import { bootstrapForgeEnv, ensureRedis } from "@sourcea/forge-core";

import { startQueueWorker } from "./queue/worker.js";

bootstrapForgeEnv();
await ensureRedis();

const worker = startQueueWorker();
console.log("forge-worker started");

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
