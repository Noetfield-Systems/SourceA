import { getOpenRouterKey, getOpenRouterModel } from "@sourcea/forge-core";

export interface LlmResult {
  ok: boolean;
  provider: string;
  model?: string;
  stub?: boolean;
  text?: string;
  usage?: Record<string, unknown>;
  error?: string;
}

export async function executeLlm(prompt: string, model?: string): Promise<LlmResult> {
  const apiKey = getOpenRouterKey();
  const chosenModel = model?.trim() || getOpenRouterModel();

  if (!apiKey) {
    return {
      ok: false,
      provider: "openrouter",
      model: chosenModel,
      error:
        "openrouter_key_missing — expected ~/.sina/secrets.env or ~/.sourcea-secrets/*.env",
    };
  }

  try {
    const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sourcea.io/forge",
        "X-Title": "SourceA Forge MVP",
      },
      body: JSON.stringify({
        model: chosenModel,
        messages: [{ role: "user", content: prompt.slice(0, 8000) }],
      }),
      signal: AbortSignal.timeout(90_000),
    });

    if (!response.ok) {
      const body = await response.text();
      return {
        ok: false,
        provider: "openrouter",
        model: chosenModel,
        error: `openrouter_http_${response.status}:${body.slice(0, 300)}`,
      };
    }

    const row = (await response.json()) as {
      choices?: Array<{ message?: { content?: string } }>;
      usage?: Record<string, unknown>;
    };

    return {
      ok: true,
      provider: "openrouter",
      model: chosenModel,
      text: row.choices?.[0]?.message?.content ?? "",
      usage: row.usage,
    };
  } catch (error) {
    return {
      ok: false,
      provider: "openrouter",
      model: chosenModel,
      error: error instanceof Error ? error.message : "openrouter_failed",
    };
  }
}
