import { bootstrapForgeEnv, getGeminiKey, getOpenAiKey, } from "@sourcea/forge-core";
import { executeGemini } from "./providers/gemini.js";
import { executeOpenAi } from "./providers/openai.js";
function pickDefaultProvider() {
    const env = process.env.FORGE_EXECUTOR_PROVIDER?.trim();
    if (env === "openai" || env === "gemini") {
        return env;
    }
    if (getOpenAiKey()) {
        return "openai";
    }
    if (getGeminiKey()) {
        return "gemini";
    }
    return "openai";
}
/** Single prompt in → single response out. Falls back openai → gemini on failure. */
export async function executePrompt(prompt, provider) {
    bootstrapForgeEnv();
    const primary = provider || pickDefaultProvider();
    const secondary = primary === "openai" ? "gemini" : "openai";
    const first = primary === "openai"
        ? await executeOpenAi(prompt)
        : await executeGemini(prompt);
    if (first.ok) {
        return first;
    }
    const fallback = secondary === "openai"
        ? await executeOpenAi(prompt)
        : await executeGemini(prompt);
    if (fallback.ok) {
        return { ...fallback, fallback_from: primary };
    }
    return {
        ok: false,
        provider: primary,
        error: `${first.error || "primary_failed"}; fallback:${fallback.error || "failed"}`,
    };
}
