import { spawn } from "node:child_process";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { GovernDecisionSchema, getGovernanceCliPath, getScriptsDir, getStateRoot, } from "@sourcea/forge-core";
const RATE_WINDOW_MS = 60_000;
const DEFAULT_RATE_LIMIT = Number(process.env.FORGE_RATE_LIMIT_PER_MIN?.trim() || "60");
const DEFAULT_COST_LIMIT_USD = Number(process.env.FORGE_COST_LIMIT_USD?.trim() || "5");
function rateLimitFile() {
    return join(getStateRoot(), "governance", "rate-limit.json");
}
function costFile() {
    return join(getStateRoot(), "governance", "cost-total.json");
}
function checkRateLimit(agentId) {
    mkdirSync(join(getStateRoot(), "governance"), { recursive: true });
    const now = Date.now();
    let rows = [];
    const path = rateLimitFile();
    if (existsSync(path)) {
        try {
            rows = JSON.parse(readFileSync(path, "utf8"));
        }
        catch {
            rows = [];
        }
    }
    rows = rows.filter((row) => now - row.at < RATE_WINDOW_MS);
    const count = rows.filter((row) => row.agent_id === agentId).length;
    if (count >= DEFAULT_RATE_LIMIT) {
        return { status: "DENY", reason: "rate_limit_exceeded" };
    }
    rows.push({ agent_id: agentId, at: now });
    writeFileSync(path, JSON.stringify(rows), "utf8");
    return { status: "ALLOW", reason: "rate_limit_ok" };
}
function checkCostLimit(estimatedCost = 0.05) {
    mkdirSync(join(getStateRoot(), "governance"), { recursive: true });
    const path = costFile();
    let total = 0;
    if (existsSync(path)) {
        try {
            total = Number(JSON.parse(readFileSync(path, "utf8")).total_usd || 0);
        }
        catch {
            total = 0;
        }
    }
    if (total + estimatedCost > DEFAULT_COST_LIMIT_USD) {
        return { status: "DENY", reason: "cost_limit_exceeded" };
    }
    writeFileSync(path, JSON.stringify({ total_usd: total + estimatedCost, updated_at: new Date().toISOString() }), "utf8");
    return { status: "ALLOW", reason: "cost_limit_ok" };
}
function runKernel(request) {
    return new Promise((resolve, reject) => {
        const child = spawn("python3", [getGovernanceCliPath()], {
            env: { ...process.env, PYTHONPATH: getScriptsDir() },
            stdio: ["pipe", "pipe", "pipe"],
        });
        let stdout = "";
        child.stdout.on("data", (chunk) => {
            stdout += chunk.toString();
        });
        child.on("error", reject);
        child.on("close", () => {
            try {
                resolve(JSON.parse(stdout));
            }
            catch (error) {
                reject(error);
            }
        });
        child.stdin.write(JSON.stringify({
            ...request,
            dry_run: request.dry_run ?? true,
            legal_review: false,
        }));
        child.stdin.end();
    });
}
export async function governTask(request) {
    const checks = [];
    const rate = checkRateLimit(request.agent_id);
    checks.push({ name: "rate_limit", status: rate.status, reason: rate.reason });
    const cost = checkCostLimit();
    checks.push({ name: "cost_limit", status: cost.status, reason: cost.reason });
    const kernel = await runKernel(request);
    const allowed = kernel.status === "ALLOW"
        ? { status: "ALLOW", reason: String(kernel.reason || "allowed_action_ok") }
        : { status: "DENY", reason: String(kernel.reason || "allowed_action_denied") };
    checks.push({ name: "allowed_action", status: allowed.status, reason: allowed.reason });
    const denied = checks.find((check) => check.status === "DENY");
    const decision = {
        status: denied ? "DENY" : "ALLOW",
        reason: denied?.reason || "approved",
        checks,
        kernel,
    };
    return GovernDecisionSchema.parse(decision);
}
