import { getGeminiKey, getGeminiModel } from "@sourcea/forge-core";
export async function executeGemini(prompt) {
    const apiKey = getGeminiKey();
    const model = getGeminiModel();
    if (!apiKey) {
        return { ok: false, provider: "gemini", model, error: "gemini_key_missing" };
    }
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            contents: [{ parts: [{ text: prompt.slice(0, 8000) }] }],
        }),
        signal: AbortSignal.timeout(90_000),
    });
    if (!response.ok) {
        const body = await response.text();
        return {
            ok: false,
            provider: "gemini",
            model,
            error: `gemini_http_${response.status}:${body.slice(0, 200)}`,
        };
    }
    const row = (await response.json());
    return {
        ok: true,
        provider: "gemini",
        model,
        text: row.candidates?.[0]?.content?.parts?.[0]?.text ?? "",
        usage: row.usageMetadata,
    };
}
