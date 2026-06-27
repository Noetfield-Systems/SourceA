import {
  existsSync,
  mkdirSync,
  readFileSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import net from "node:net";

import { getRedisUrl, getStateRoot } from "./paths.js";

let embeddedServer: { stop: () => Promise<boolean> } | null = null;

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

function redisUrlFile(): string {
  return `${getStateRoot()}/redis.url`;
}

function redisLockFile(): string {
  return `${getStateRoot()}/redis.lock`;
}

function parseRedisUrl(url: string): { host: string; port: number } {
  const parsed = new URL(url);
  return {
    host: parsed.hostname || "127.0.0.1",
    port: Number(parsed.port || 6379),
  };
}

export async function pingRedis(url = getRedisUrl()): Promise<boolean> {
  const { host, port } = parseRedisUrl(url);
  return new Promise((resolve) => {
    const socket = net.connect({ host, port });
    socket.setTimeout(1500);
    socket.once("connect", () => {
      socket.destroy();
      resolve(true);
    });
    socket.once("timeout", () => {
      socket.destroy();
      resolve(false);
    });
    socket.once("error", () => {
      socket.destroy();
      resolve(false);
    });
  });
}

function readSharedRedisUrl(): string | null {
  const path = redisUrlFile();
  if (!existsSync(path)) {
    return null;
  }
  const url = readFileSync(path, "utf8").trim();
  return url || null;
}

async function startEmbeddedRedis(): Promise<string> {
  const { RedisMemoryServer } = await import("redis-memory-server");

  const server = new RedisMemoryServer({
    instance: {
      port: Number(process.env.FORGE_REDIS_PORT?.trim() || 6379),
    },
    autoStart: false,
  });

  await server.start();
  embeddedServer = server;

  const host = await server.getHost();
  const port = await server.getPort();
  const url = `redis://${host}:${port}`;
  process.env.REDIS_URL = url;

  mkdirSync(getStateRoot(), { recursive: true });
  writeFileSync(redisUrlFile(), `${url}\n`, "utf8");

  console.log(`[forge] embedded redis started at ${url} (no Docker required)`);
  return url;
}

async function waitForSharedRedis(maxSeconds = 90): Promise<string | null> {
  for (let attempt = 0; attempt < maxSeconds; attempt += 1) {
    const shared = readSharedRedisUrl();
    if (shared && (await pingRedis(shared))) {
      process.env.REDIS_URL = shared;
      return shared;
    }

    const configured = getRedisUrl();
    if (await pingRedis(configured)) {
      return configured;
    }

    await sleep(1000);
  }
  return null;
}

/** Ensure Redis is reachable — waits for peer boot, then starts embedded dev Redis once. */
export async function ensureRedis(): Promise<string> {
  const configured = getRedisUrl();
  if (await pingRedis(configured)) {
    return configured;
  }

  const immediateShared = readSharedRedisUrl();
  if (immediateShared && (await pingRedis(immediateShared))) {
    process.env.REDIS_URL = immediateShared;
    return immediateShared;
  }

  mkdirSync(getStateRoot(), { recursive: true });
  const lockPath = redisLockFile();
  const lockHeldByPeer = existsSync(lockPath);

  if (lockHeldByPeer) {
    const shared = await waitForSharedRedis();
    if (shared) {
      return shared;
    }
  }

  if (process.env.FORGE_EMBEDDED_REDIS === "0") {
    const shared = await waitForSharedRedis(15);
    if (shared) {
      return shared;
    }
    throw new Error(
      `Redis unavailable at ${configured}. Start: node apps/forge-core/dist/ensure-redis-cli.js`,
    );
  }

  try {
    writeFileSync(lockPath, `${process.pid}\n`, "utf8");
    const sharedAfterLock = await waitForSharedRedis(3);
    if (sharedAfterLock) {
      return sharedAfterLock;
    }
    return await startEmbeddedRedis();
  } finally {
    try {
      unlinkSync(lockPath);
    } catch {
      // ignore
    }
  }
}

export async function stopEmbeddedRedis(): Promise<void> {
  if (embeddedServer) {
    await embeddedServer.stop();
    embeddedServer = null;
  }
}
