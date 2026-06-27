import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { Hono } from "hono";

import {
  bootstrapForgeEnv,
  ensureRedis,
  getApiPort,
  getRegistryPath,
} from "@sourcea/forge-core";

import { createTaskRoutes } from "./routes/tasks.js";

const app = new Hono();

app.get("/health", (c) =>
  c.json({
    ok: true,
    service: "forge-core-api",
    version: "1.0.0",
    phase: "forge-mvp-runtime",
    at: new Date().toISOString(),
  }),
);

app.get("/agents", async (c) => {
  try {
    const raw = await readFile(getRegistryPath(), "utf8");
    return c.json(JSON.parse(raw));
  } catch (error) {
    return c.json(
      {
        ok: false,
        error: error instanceof Error ? error.message : "registry_missing",
      },
      500,
    );
  }
});

app.route("/", createTaskRoutes());

export { app };

const isMain = process.argv[1] === fileURLToPath(import.meta.url);
if (isMain) {
  bootstrapForgeEnv();
  await ensureRedis();
  const { serve } = await import("@hono/node-server");
  const port = getApiPort();
  serve(
    {
      fetch: app.fetch,
      port,
    },
    (info) => {
      console.log(`forge-core-api listening on http://127.0.0.1:${info.port}`);
    },
  );
}
