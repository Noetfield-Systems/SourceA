import { existsSync, readFileSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
let bootstrapped = false;
function normalizeOpenRouterKey(value) {
    let key = value.trim().replace(/^["']|["']$/g, "");
    if (key.startsWith("ysk-or-")) {
        key = key.slice(1);
    }
    return key;
}
function parseEnvFile(path) {
    if (!existsSync(path)) {
        return {};
    }
    const out = {};
    const orCandidates = [];
    for (const rawLine of readFileSync(path, "utf8").split(/\r?\n/)) {
        const line = rawLine.trim();
        if (!line || line.startsWith("#") || !line.includes("=")) {
            continue;
        }
        const eq = line.indexOf("=");
        const name = line.slice(0, eq).trim();
        const value = normalizeOpenRouterKey(line.slice(eq + 1).trim());
        if (!name || !value) {
            continue;
        }
        if (name === "OPENROUTER_API_KEY") {
            orCandidates.push(value);
            continue;
        }
        out[name] = value;
    }
    if (orCandidates.length > 0) {
        const valid = orCandidates.filter((candidate) => candidate.startsWith("sk-or-v1-"));
        out.OPENROUTER_API_KEY = valid.at(-1) ?? orCandidates.at(-1) ?? "";
    }
    const forge = out.OPENROUTER_API_KEY_FORGE ?? "";
    const primary = out.OPENROUTER_API_KEY ?? "";
    const evalKey = out.OPENROUTER_API_KEY_EVAL ?? "";
    if (forge.startsWith("sk-or-v1-")) {
        out.OPENROUTER_API_KEY = forge;
    }
    else if (primary.startsWith("sk-or-v1-")) {
        out.OPENROUTER_API_KEY = primary;
    }
    else if (evalKey.startsWith("sk-or-v1-")) {
        out.OPENROUTER_API_KEY = evalKey;
    }
    return out;
}
function applyEnv(keys) {
    for (const [name, value] of Object.entries(keys)) {
        if (value) {
            process.env[name] = value;
        }
    }
    const gemini = keys.GEMINI_API_KEY || keys.GOOGLE_API_KEY;
    if (gemini) {
        process.env.GEMINI_API_KEY = gemini;
        process.env.GOOGLE_API_KEY = gemini;
    }
    const openrouter = keys.OPENROUTER_API_KEY_FORGE ||
        keys.OPENROUTER_API_KEY ||
        keys.OPENROUTER_API_KEY_EVAL;
    if (openrouter) {
        process.env.OPENROUTER_API_KEY = openrouter;
    }
}
function collectVaultPaths() {
    const paths = [join(homedir(), ".sina", "secrets.env")];
    const sourceaSecrets = join(homedir(), ".sourcea-secrets");
    if (existsSync(sourceaSecrets)) {
        for (const name of readdirSync(sourceaSecrets).sort()) {
            if (name.endsWith(".env")) {
                paths.push(join(sourceaSecrets, name));
            }
        }
    }
    paths.push(join(homedir(), "Desktop", "SinaPromptOS", "secrets.env"));
    return paths;
}
/** Load SourceA vault keys into process.env */
export function bootstrapForgeEnv() {
    if (bootstrapped) {
        return;
    }
    const merged = {};
    for (const path of collectVaultPaths()) {
        Object.assign(merged, parseEnvFile(path));
    }
    applyEnv(merged);
    bootstrapped = true;
}
export function getOpenRouterKey() {
    bootstrapForgeEnv();
    return (process.env.OPENROUTER_API_KEY_FORGE?.trim() ||
        process.env.OPENROUTER_API_KEY?.trim() ||
        process.env.OPENROUTER_API_KEY_EVAL?.trim() ||
        "");
}
export function getOpenRouterModel() {
    bootstrapForgeEnv();
    return (process.env.OPENROUTER_MODEL?.trim() ||
        process.env.OPENROUTER_MODEL_FORGE?.trim() ||
        "google/gemini-2.5-flash");
}
export function getOpenAiKey() {
    bootstrapForgeEnv();
    return process.env.OPENAI_API_KEY?.trim() || "";
}
export function getGeminiKey() {
    bootstrapForgeEnv();
    return (process.env.GEMINI_API_KEY?.trim() ||
        process.env.GOOGLE_API_KEY?.trim() ||
        "");
}
export function getOpenAiModel() {
    bootstrapForgeEnv();
    return process.env.OPENAI_MODEL?.trim() || "gpt-4.1-mini";
}
export function getGeminiModel() {
    bootstrapForgeEnv();
    return process.env.GEMINI_MODEL?.trim() || "gemini-2.5-flash";
}
export function secretsReady() {
    return (getOpenAiKey().startsWith("sk-") ||
        getGeminiKey().length > 10 ||
        getOpenRouterKey().startsWith("sk-or-v1-"));
}
