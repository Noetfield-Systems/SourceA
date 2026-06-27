import { getOpenAiKey, getOpenAiModel } from "@sourcea/forge-core";
export async function executeOpenAi(prompt) {
    const apiKey = getOpenAiKey();
    const model = getOpenAiModel();
    if (!apiKey) {
        return { ok: false, provider: "openai", model, error: "openai_key_missing" };
    }
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
            Authorization: `Bearer ${apiKey}`,
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            model,
            messages: [{ role: "user", content: prompt.slice(0, 8000) }],
        }),
        signal: AbortSignal.timeout(90_000),
    });
    if (!response.ok) {
        const body = await response.text();
        return {
            ok: false,
            provider: "openai",
            model,
            error: `openai_http_${response.status}:${body.slice(0, 200)}`,
        };
    }
    const row = (await response.json());
    return {
        ok: true,
        provider: "openai",
        model,
        text: row.choices?.[0]?.message?.content ?? "",
        usage: row.usage,
    };
}
