import { ensureRedis } from "./ensure-redis.js";
async function main() {
    const url = await ensureRedis();
    console.log(`[forge] REDIS_URL=${url}`);
    console.log("[forge] redis ready — keep this process running");
    await new Promise(() => {
        // Keep embedded Redis alive when run as a standalone helper.
    });
}
main().catch((error) => {
    const message = error instanceof Error ? error.message : String(error);
    console.error(`[forge] redis bootstrap failed: ${message}`);
    process.exit(1);
});
